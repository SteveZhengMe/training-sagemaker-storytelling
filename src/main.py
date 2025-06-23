from abc import ABC, abstractmethod
import argparse
import sagemaker
from sagemaker.processing import (
    Processor,
    ScriptProcessor,
    ProcessingInput,
    ProcessingOutput,
)
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline_definition_config import PipelineDefinitionConfig
import os
import dotenv
from botocore.exceptions import ClientError


class DWAPipeline(ABC):
    def __init__(self, bucket_name: str, local_run=True):
        self.env = {}
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

        self.env["role"] = role
        self.env["region"] = region

        # set variables
        self.env["input"] = "./input" if local_run else f"s3://{bucket_name}/input/"
        self.env["output"] = "./output" if local_run else f"s3://{bucket_name}/output/"

        self.env["local_run"] = local_run

    def _init_processor(self) -> Processor:
        return ScriptProcessor(
            # see all the image_uris and versions here: https://docs.aws.amazon.com/sagemaker/latest/dg-ecr-paths/ecr-us-east-1.html#spark-us-east-1
            image_uri=sagemaker.image_uris.retrieve(
                framework="spark",  # Compatible with the code exported from Glue
                region=self.env.get("region"),
                version="3.2",
                image_scope="processing",
            ),
            command=["python3"],
            role=self.env.get("role"),
            instance_count=1,
            instance_type="local" if self.env.get("local_run") else "ml.t3.medium",
        )

    @abstractmethod
    def _init_processing_step(
        self,
        step_name: str,
        processor: Processor,
        job_arguments: list,
        input_output: list,
    ):
        pass

    def create_pipeline(self, pipeline_name: str) -> Pipeline:
        bucket_name_param = ParameterString(name="bucket_name")
        sleep_param = ParameterString(name="sleep")

        pipeline = Pipeline(
            name=pipeline_name,
            steps=[
                self._init_processing_step(
                    "DWAStep",
                    self._init_processor(),
                    [
                        "--bucket_name",
                        bucket_name_param,
                        "--sleep",
                        sleep_param,
                    ],
                    [self.env.get("input"), self.env.get("output")],
                )
            ],
            sagemaker_session=(
                LocalPipelineSession()
                if self.env.get("local_run")
                else sagemaker.Session()
            ),
            parameters=[bucket_name_param, sleep_param],
            pipeline_definition_config=PipelineDefinitionConfig(
                use_custom_job_prefix=True,
            ),
        )

        self._check_remote_existing(pipeline_name)

        pipeline.create(role_arn=self.env.get("role"))
        return pipeline

    def _check_remote_existing(self, pipeline_name: str) -> None:
        if not self.env.get("local_run"):
            try:
                response = sagemaker.Session().sagemaker_client.delete_pipeline(
                    PipelineName=pipeline_name
                )
                print(f"Pipeline ARN: {response['PipelineArn']}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFound":
                    print(
                        f"Pipeline '{pipeline.name}' does not exist, nothing to delete"
                    )
                else:
                    print(f"✗ Error deleting pipeline: {e}")
                    raise
            except Exception:
                raise


class DWAPipeline_1(DWAPipeline):
    def _init_processing_step(self, step_name, processor, job_arguments, input_output):
        return ProcessingStep(
            name=step_name,
            processor=processor,
            code="src/dwa_1.py",
            job_arguments=job_arguments,
            inputs=[
                ProcessingInput(
                    source=input_output[0], destination="/opt/ml/processing/input"
                )
            ],
            outputs=[
                ProcessingOutput(
                    source="/opt/ml/processing/output", destination=input_output[1]
                )
            ],
        )


class DWAPipeline_2(DWAPipeline):
    def _init_processing_step(self, step_name, processor, job_arguments, input_output):
        return ProcessingStep(
            name=step_name,
            processor=processor,
            code="src/dwa_2.py",
            job_arguments=job_arguments,
            inputs=[
                ProcessingInput(
                    source=input_output[0], destination="/opt/ml/processing/input"
                )
            ],
            outputs=[
                ProcessingOutput(
                    source="/opt/ml/processing/output", destination=input_output[1]
                )
            ],
        )


class DWAPipeline_3(DWAPipeline):
    def _init_processing_step(self, step_name, processor, job_arguments, input_output):
        pass


class DWAPipeline_4(DWAPipeline):
    def _init_processing_step(self, step_name, processor, job_arguments, input_output):
        pass


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
    scenario = os.getenv("MAIN_SCENARIO", "1")

    if not bucket_name:
        raise ValueError("Please set the DWA_BUCKET_NAME environment variable.")

    # Dynamically create DWAPipeline_# instance based on scenario
    try:
        pipeline_class = globals()[f"DWAPipeline_{scenario}"]
        dwa_pipeline = pipeline_class(bucket_name, local_run=args.local)
    except KeyError:
        raise ValueError(f"Unknown scenario: {scenario}")

    pipeline = dwa_pipeline.create_pipeline(f"DWAPipeline-S-{scenario}")
    if args.local:
        # if local, run it
        execution = pipeline.start(
            parameters={"bucket_name": bucket_name, "sleep": "0"}
        )
    else:
        print("Run tools/run_pipeline.sh to execute the remote pipeline.")
