from abc import ABC, abstractmethod
import argparse
from typing import Any, Union
from sagemaker import image_uris
from sagemaker.session import get_execution_role, Session
from sagemaker.processing import (
    Processor,
    ScriptProcessor,
    ProcessingInput,
    ProcessingOutput,
)
from sagemaker.spark.processing import PySparkProcessor
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline_definition_config import PipelineDefinitionConfig
import os
import dotenv
from botocore.exceptions import ClientError


class DWAPipeline:
    def __init__(self, bucket_name: str, local_run=True):
        self.env = {}
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

        self.env["role"] = role
        self.env["region"] = region

        # set variables
        self.env["input"] = "./input" if local_run else f"s3://{bucket_name}/input/"
        self.env["output"] = "./output" if local_run else f"s3://{bucket_name}/output/"

        self.env["local_run"] = local_run

    def _init_processing_step(self, step_name, job_arguments, input_output):
        script_processor = ScriptProcessor(
            # see all the image_uris and versions here: https://docs.aws.amazon.com/sagemaker/latest/dg-ecr-paths/ecr-us-east-1.html#spark-us-east-1
            image_uri=image_uris.retrieve(
                framework="spark",  # Compatible with the code exported from Glue
                region=self.env.get("region"),
                version="3.2",
                image_scope="processing",
            ),
            command=["python3"],
            role=self.env.get("role"),
            instance_count=1,
            instance_type="local" if self.env.get(
                "local_run") else "ml.t3.medium",
        )

        return ProcessingStep(
            name=step_name,
            processor=script_processor,
            code="src/dwa_1/processing.py",
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

    def create_pipeline(self, pipeline_name: str) -> Pipeline:
        bucket_name_param = ParameterString(
            name="bucket_name", default_value=os.getenv("DWA_BUCKET_NAME", ""))
        sleep_param = ParameterString(name="sleep", default_value="0")

        pipeline = Pipeline(
            name=pipeline_name,
            steps=[
                self._init_processing_step(
                    "DWAStep",
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
                else Session()
            ),
            parameters=[bucket_name_param, sleep_param],
            pipeline_definition_config=PipelineDefinitionConfig(
                use_custom_job_prefix=True,
            ),
        )

        pipeline.upsert(role_arn=str(self.env.get("role")))
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
        raise ValueError(
            "Please set the DWA_BUCKET_NAME environment variable.")

    pipeline_class = DWAPipeline(bucket_name, local_run=args.local)
    pipeline = pipeline_class.create_pipeline("DWAPipeline-Scenario-1")

    if args.local:
        # if local, run it
        execution = pipeline.start(
            parameters={"bucket_name": bucket_name, "sleep": "0"}
        )
    else:
        print("Run tools/run_pipeline.sh to execute the remote pipeline.")
