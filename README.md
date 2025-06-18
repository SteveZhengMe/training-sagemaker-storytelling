# Description

This branch is used to test the following features:

## 1. Execute Python code for "Creating a SageMaker Pipeline" on CodeBuild
- Can it be built?
- After building, can the Pipeline be run using the CLI?
- Does the creation process take a long time?
- How to obtain the output results?
- Error messages and how to monitor them
- Refer to [buildspec_1.yml](buildspec_1.yml)

## 2. Support for multiple files in Pipeline Steps
- The Step contains multiple Python files, located in different directories, with dependencies between them
- The Step includes a requirements.txt file; can the Step automatically install these dependencies?
- Refer to [buildspec_2.yml](buildspec_2.yml)

## 3. Find a suitable data source and upload it to S3
- Data source requirements:
    - Requires general ETL operations, such as handling null values
    - Requires preprocessing with joblib support, such as standardization
    - The data source should be simple, making it easy to generate fake data for Quality, Drift, Bias, etc., tests; or, the data source should be large enough to easily be split to 20 subsets
- Plan the S3 directory structure, such as input, output, etc.
- Write a program that can generate new data or process a batch of data when executed

## 4. Write DWA
- The Pipeline supports three parameters: input, output, and whether it includes a target column
- The code must support execution before Preprocessing Step in the Training Pipeline and also satisfy the Inference Pipeline
- Refer to [buildspec_3.yml](buildspec_3.yml)