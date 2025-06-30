from sagemaker.session import get_execution_role, Session
from sagemaker.spark.processing import PySparkProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.parameters import ParameterString
import os
import dotenv

dotenv.load_dotenv()

try:
    # Use it if you are running this script in a SageMaker Studio environment
    role = get_execution_role()
    region = Session().boto_region_name
except ValueError:
    # set the role manually if not in SageMaker Studio
    print("Not in SageMaker Studio, using environment variable for role.")
    role = os.getenv(
        "SAGEMAKER_EXECUTION_ROLE",
        "arn:aws:iam::",
    )
    region = os.getenv("SAGEMAKER_REGION", "us-east-1")


bucket = Session().default_bucket()
pipeline_folder = "DWAPipeline-Scenario-2"

# print(f"SageMaker role: {role}")
# print(f"S3 bucket: {bucket}")
# print(f"Region: {region}")


def prepare_pipeline():
    """Create SageMaker Pipeline"""

    output_data_param = ParameterString(
        name="OutputDataPath",
        default_value=f"s3://{os.getenv("DWA_BUCKET_NAME", "")}/{pipeline_folder}/output/"
    )

    # KW： 使用processor方式，而不是processor.run()方法，run是旧版本使用的方法
    pyspark_processor = PySparkProcessor(
        base_job_name="pyspark-s2-processing",
        framework_version="3.1",
        role=role,
        instance_count=1,
        # if ml.t3.medium is too small to run Spark, try ml.m5.large
        instance_type='ml.t3.medium',
        max_runtime_in_seconds=3600,
        sagemaker_session=Session()
    )

    processing_step = ProcessingStep(
        name="PySparkProcessingStep",
        processor=pyspark_processor,
        # KW：在Pipeline运行或者processor.run()调用时，数据才会从S3下载到Container。如果数据在本地，则也是在这个时候先上传S3，再下载到Container
        inputs=[
            ProcessingInput(
                # KW：这里可以是本地文件或者S3目录（ source="s3://your-bucket/path/to/data.csv"）。是否找到了本地上传的文件并不重要，因为最终数据是S3上另外的bucket里面的
                # KW：source可以是一个文件或者目录（则上传目录中所有的文件）
                source="input/sales_data.csv",
                # KW：设定了destination后，数据就会被下载到Container指定的目录，而不是根据input_name决定
                destination="/opt/ml/processing/input",
                # KW：如果数据在本地，则传到S3以input_name目录下，以保证多个Input保持互相独立，如果没有设定destination，则数据会被下载到Container的input_name目录下。如果不指定，则会按照input_1,2等方式
                input_name="sales_data"
            )
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output",
                # KW：S3上的这个目录（default_value=f"s3://{bucket}/{pipeline_folder}/output/"）不会自动建立，要自己建立
                destination=output_data_param,
                output_name="processed_data"
            )
        ],
        code="src/dwa_2/processing.py",
        # KW：如果仅仅是input或者output，则没必要跑设定job_arguments，在脚本中直接引用相应的/opt/ml/...中的文件就可以了
        # job_arguments=[
        #     "--input-path", "/opt/ml/processing/input/sales_data.csv",
        #     "--output-path", "/opt/ml/processing/output"
        # ]
    )

    pipeline = Pipeline(
        name=pipeline_folder,
        parameters=[output_data_param],
        steps=[processing_step],
        sagemaker_session=Session()
    )

    return pipeline


def creatge_pipeline():
    pipeline = prepare_pipeline()

    # KW：使用upsert而不是create方法，实现“没有就新建，有就更新”
    pipeline.upsert(role_arn=role)
    print(f"Pipeline '{pipeline.name}' created/updated successfully!")

    print(f"Pipeline Name: {pipeline.name}")
    print(f"Pipeline Steps: {len(pipeline.steps)}")
    print(f"Pipeline Parameters: {[p.name for p in pipeline.parameters]}")

    return pipeline


def execute_pipeline(pipeline, output_path=None):
    """run Pipeline and monitoring"""
    parameters = {}

    if output_path:
        parameters["OutputDataPath"] = output_path

    print(f"\nStarting pipeline execution...")
    if parameters:
        print(f"Parameters: {parameters}")

    execution = pipeline.start(parameters=parameters if parameters else None)

    print(f"Execution ARN: {execution.arn}")

    # Monitoring when running
    status = execution.describe()
    print(f"Current Status: {status['PipelineExecutionStatus']}")

    if status['PipelineExecutionStatus'] in ['Executing', 'Stopping']:
        print("\n🚀 Pipeline is running. Monitor options:")

        try:
            steps = execution.list_steps()
            print(f"\n📋 Current step status:")
            for step in steps:
                step_name = step.get('StepName', 'Unknown')
                step_status = step.get('StepStatus', 'Unknown')
                print(f"   - {step_name}: {step_status}")
        except Exception as e:
            print(f"   Could not retrieve step details: {e}")

    # show final results when execution is done
    print("Waiting until pipeline execution completes... ...")
    execution.wait()
    try:
        final_status = execution.describe()
        print(f"\n🏁 Final Status: {final_status['PipelineExecutionStatus']}")

        if final_status['PipelineExecutionStatus'] == 'Succeeded':
            print("✅ Pipeline completed successfully!")
            print(
                f"📁 Output location: s3://{bucket}/{pipeline_folder}/output/")
            print("\n📊 Generated reports:")
            print("   - product_summary/")
            print("   - region_summary/")
            print("   - monthly_summary/")
            print("   - age_summary/")
        else:
            print("❌ Pipeline execution failed or was stopped.")

    except Exception as e:
        print(f"Error getting execution results: {e}")


if __name__ == "__main__":
    print("PySparkProcessor does NOT support local mode.")
    pipeline = creatge_pipeline()

    if pipeline is None:
        exit(1)

    print(f"\n🎉 Pipeline {pipeline.name} created!")
