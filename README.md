# Description

This branch is used to experiment with the following features:

## 1. Execute Python code for "Creating Sagemaker Pipeline" on CodeBuild - ScriptProcessor
- Whether it can be created
- Whether the Pipeline can be run via CLI after creation
- Whether creation takes a long time
- How to retrieve output results
- Error information and how to monitor
- See [pipeline.py](src/dwa_1/pipeline.py)
- Notes:
  - Add the following Policy to IAM CodeBuild Execution Role: AmazonSageMakerServiceCatalogProductsCodeBuildServiceRolePolicy and the custom one below
    ```yaml
        # In policies
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iam:PassRole",
                    "Resource": "arn:aws:iam::959750740416:role/sagemaker-codebuild-execution-role"
                }
            ]
        }
        # In Trust Relationships
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "codebuild.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ```
    - When using DevContainer, Docker-Outside-Docker cannot be used, otherwise Python files cannot be injected. Only docker-in-docker can be used.

## 2. Execute Python code for "Creating Sagemaker Pipeline" on CodeBuild - PySparkProcessor
- Use PySparkProcessor to start a Spark Server in the container, process data, and then return the output to S3
- This is a real example using tools.py to generate csv data
- See [pipeline.py](src/dwa_2/pipeline.py)
- Notes:
    - If you want to view logs in CloudWatch, add CloudWatch Log permissions to Sagemaker's execution role

## 3. Support for multiple files in Pipeline Steps
- Regardless of which Processor is used, ProcessingStep only supports one Python file as source code
- If ProcessingStep contains multiple Python files not in the same directory, with dependencies or a requirements.txt file, then the input script needs to run `pip -r` and dynamically import within Python
- See [pipeline.py](src/dwa_3/pipeline.py)

## Other

### A. Finding data sources
- Requirements for data sources:
    - Require standard ETL tasks like handling nulls, etc.
    - Require Preprocessing with joblib support, such as standardization
    - Data should be simple for generating dummy data to test Quality, Drift, Bias, etc., or large enough to easily generate 20x variations
- Plan S3 directory structure such as input, output, etc.
- Write programs that can generate new data or provide a batch of data on execution
