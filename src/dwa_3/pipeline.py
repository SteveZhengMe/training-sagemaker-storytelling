import os
import dotenv
import argparse

from sagemaker import image_uris
from sagemaker.session import get_execution_role, Session
from sagemaker.processing import (
    ScriptProcessor,
    ProcessingInput,
    ProcessingOutput,
)
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.pipeline_definition_config import PipelineDefinitionConfig
from sagemaker.workflow.parameters import ParameterString


def prepare_pipeline(cmd_parameter_args) -> dict:
    dotenv.load_dotenv()
    env = {}
    env["local_run"] = cmd_parameter_args.local
    env["bucket_name"] = os.getenv("DWA_BUCKET_NAME", "")
    if not env["bucket_name"]:
        raise ValueError("Please set the DWA_BUCKET_NAME environment variable.")

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

    if role == "arn:aws:iam::":
        raise ValueError(
            "Please set the SAGEMAKER_EXECUTION_ROLE environment variable."
        )

    env["role"] = role
    env["region"] = region

    # set variables
    # KW: 指定input不是一个好实践，Sagemaker会将inputs=[]下面定义的自动拷贝到Image中
    env["input"] = (
        "./input" if env["local_run"] else f"s3://{env['bucket_name']}/input/"
    )
    # KW: 不需要定义output
    # env["output"] = (
    #     "./output" if env["local_run"] else f"s3://{env['bucket_name']}/output/"
    # )
    env["code"] = "./src/dwa_3/processing"

    return env


def create_pipeline(pipeline_name: str, env: dict) -> Pipeline:
    # KW: 一定要定义ParameterString，否则output目录下的内容不会被拷贝到宿主机或者S3中
    data_output_param = ParameterString(
        name="DataOutputPath",
        default_value=f's3://{env.get("bucket_name")}/{pipeline_name}/output/',
    )

    script_processor = ScriptProcessor(
        # see all the image_uris and versions here: https://docs.aws.amazon.com/sagemaker/latest/dg-ecr-paths/ecr-us-east-1.html#spark-us-east-1
        image_uri=image_uris.retrieve(
            framework="spark",  # Compatible with the code exported from Glue
            region=env.get("region"),
            version="3.2",
            image_scope="processing",
        ),
        command=["python3"],
        role=env.get("role"),
        instance_count=1,
        instance_type="local" if env.get("local_run") else "ml.t3.medium",
    )

    processing_step = ProcessingStep(
        name="dwa_3_processing_step",
        processor=script_processor,
        code="src/dwa_3/processing/processing.py",
        job_arguments=[
            "--input_csv",
            "/opt/ml/processing/input/dwa_3_source.csv",
            "--source_dir",
            "/opt/ml/processing/code",
        ],
        # KW: 定义输入目录和Code，然后Sagemaker才知道把他们拷贝到Image的/opt/ml/processing下（自动建立子目录）。注意：尽量不要使用其他的目录，不是所有目录Sagemaker都可以操作的。
        inputs=[
            ProcessingInput(
                source=env.get("input"), destination="/opt/ml/processing/input"
            ),
            ProcessingInput(
                source=env.get("code"), destination="/opt/ml/processing/code"
            ),
        ],
        # KW: 要把destination作为一个ParameterString传入，否则Sagemaker不会将/opt/ml/processing/output目录下的内容拷贝到宿主机或者S3中
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output",
                destination=data_output_param,
            )
        ],
    )

    pipeline = Pipeline(
        name=pipeline_name,
        steps=[processing_step],
        sagemaker_session=(
            LocalPipelineSession() if env.get("local_run") else Session()
        ),
        # KW: 设定需要传入的参数（这个例子中就只有output path)
        parameters=[data_output_param],
        pipeline_definition_config=PipelineDefinitionConfig(
            use_custom_job_prefix=True,
        ),
    )

    pipeline.upsert(role_arn=str(env.get("role")))
    return pipeline


def execute_pipeline(pipeline: Pipeline):
    # KW: 由于是本地运行，直接指定本地目录，本地目录要以file://开头，否则出现错误信息：Invalid destination URI, must be s3:// or file://
    # KW: Step完成后，Sagemaker会自动将/opt/ml/processing/output目录下的文件上传Host机器或者S3，这句话是有前提条件的，就是要将output作为Pipeline的参数，创建Pipeline的时候，也需要：parameters=[data_output_param],
    execution = pipeline.start({"DataOutputPath": "file://./output"})

    # KW: 如果本地运行，则不会有arn参数，所以这里需要hasattr检查
    if hasattr(execution, "arn"):
        print(f"Execution ARN: {execution.arn}")

    # Monitoring when running
    status = execution.describe()
    print(f"Current Status: {status['PipelineExecutionStatus']}")

    if status["PipelineExecutionStatus"] in ["Executing", "Stopping"]:
        print("\n🚀 Pipeline is running. Monitor options:")

        try:
            steps = execution.list_steps()
            print("\n📋 Current step status:")
            for step in steps:
                step_name = step.get("StepName", "Unknown")
                step_status = step.get("StepStatus", "Unknown")
                print(f"   - {step_name}: {step_status}")
        except Exception as e:
            print(f"   Could not retrieve step details: {e}")

    # show final results when execution is done
    print("Waiting until pipeline execution completes... ...")
    # KW: 如果本地运行，则不会有wait参数，所以这里需要hasattr检查
    if hasattr(execution, "wait"):
        execution.wait()
    try:
        final_status = execution.describe()
        print(f"\n🏁 Final Status: {final_status['PipelineExecutionStatus']}")

        if final_status["PipelineExecutionStatus"] == "Succeeded":
            print("✅ Pipeline completed successfully!")
        else:
            print("❌ Pipeline execution failed or was stopped.")

    except Exception as e:
        print(f"Error getting execution results: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local",
        type=bool,
        required=False,
        default=False,
        help="Set True if run locally when testing",
    )

    env = prepare_pipeline(parser.parse_args())

    pipeline = create_pipeline("DWAPipeline-Scenario-3", env)

    if env.get("local_run"):
        # if local, run it
        execute_pipeline(pipeline)
    else:
        print("Run tools/run_pipeline.sh to execute the remote pipeline.")
