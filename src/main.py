import argparse
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline_definition_config import PipelineDefinitionConfig
import os
import dotenv
from botocore.exceptions import ClientError


def dwa_pipeline(bucket_name: str = "", local_run=True) -> Pipeline:
    try:
        # Use it if you are running this script in a SageMaker Studio environment
        role = sagemaker.get_execution_role()
        region = sagemaker.Session().boto_region_name
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

    # Define Pipeline Parameters
    bucket_name_param = ParameterString(name="bucket_name")
    sleep_param = ParameterString(name="sleep")

    # set variables
    input_define = "./input" if local_run else f"s3://{bucket_name}/input/"
    output_define = "./output" if local_run else f"s3://{bucket_name}/output/"
    instance_type_define = "local" if local_run else "ml.t3.medium"

    # ScriptProcessor
    script_processor = ScriptProcessor(
        # see all the image_uris and versions here: https://docs.aws.amazon.com/sagemaker/latest/dg-ecr-paths/ecr-us-east-1.html#spark-us-east-1
        image_uri=sagemaker.image_uris.retrieve(
            framework="spark",  # Compatible with the code exported from Glue
            region=region,
            version="3.2",
            image_scope="processing",
        ),
        command=["python3"],
        role=role,
        instance_count=1,
        instance_type=instance_type_define,
    )

    # ProcessingStep
    processing_step = ProcessingStep(
        name="DWAStep",
        processor=script_processor,
        code="src/dwa.py",
        job_arguments=[
            "--bucket_name",
            bucket_name_param,
            "--sleep",
            sleep_param,
        ],
        inputs=[
            ProcessingInput(source=input_define, destination="/opt/ml/processing/input")
        ],
        outputs=[
            ProcessingOutput(
                source="/opt/ml/processing/output", destination=output_define
            )
        ],
    )

    # Pipeline
    pipeline = Pipeline(
        name="DWAPipeline-Simple-Run",
        steps=[processing_step],
        sagemaker_session=(
            LocalPipelineSession() if local_run else sagemaker.Session()
        ),
        parameters=[bucket_name_param, sleep_param],
        pipeline_definition_config=PipelineDefinitionConfig(
            use_custom_job_prefix=True,
        ),
    )

    # if DWALocalPipeline is existing, delete it
    if not local_run:
        try:
            response = sagemaker.Session().sagemaker_client.delete_pipeline(
                PipelineName=pipeline.name
            )
            print(f"Pipeline ARN: {response['PipelineArn']}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFound":
                print(f"Pipeline '{pipeline.name}' does not exist, nothing to delete")
            else:
                print(f"✗ Error deleting pipeline: {e}")
                raise
        except Exception:
            raise

    pipeline.create(role_arn=role)
    return pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local",
        type=bool,
        required=False,
        default=False,
        help="Set True if run locally when testing",
    )

    args = parser.parse_args()

    dotenv.load_dotenv()
    bucket_name = os.getenv("DWA_BUCKET_NAME", "")
    if not bucket_name:
        raise ValueError("Please set the DWA_BUCKET_NAME environment variable.")

    pipeline = dwa_pipeline(bucket_name, local_run=args.local)
    if args.local:
        # if local, run it
        execution = pipeline.start(
            parameters={"bucket_name": bucket_name, "sleep": "0"}
        )
    else:
        print("Run tools/run_pipeline.sh to execute the remote pipeline.")
