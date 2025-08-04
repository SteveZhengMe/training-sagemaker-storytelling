# 说明

这个分支用来尝试下面的功能：

## 1、在CodeBuild上执行“创建Sagemaker Pipeline”的Python代码 - ScriptProcessor
- 是否可以建
- 建好后是否可以使用CLI运行这个Pipeline
- 创建是否要等很久
- 如何得知输出结果
- 错误信息和如何监控
- 参见[buildspec.yml](buildspec.yml)和[pipeline.py](src/dwa_1/pipeline.py)
- 笔记：
  - IAM CodeBuild Execution Role增加Policy: AmazonSageMakerServiceCatalogProductsCodeBuildServiceRolePolicy和下面的Customized
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
    - 使用DevContainer的时候，不能使用Docker-Outside-Docker，否则Python文件无法注入，只能使用docker-in-docker方式

## 2、在CodeBuild上执行“创建Sagemaker Pipeline”的Python代码 - PySparkProcessor
- 使用PySparkProcessor，在Container中启动Spark Server，处理数据，然后将输出返回到S3
- 这是一个真实的例子，使用tools.py生成csv数据
- 参见[pipeline.py](src/dwa_2/pipeline.py)
- 笔记：
    - 如果希望在CloudWatch查看Log，要给Sagemaker的execution role增加CloudWatch Log的权限

## 3、Pipeline中Step对于多文件的支持
- 不论使用哪个Processor，使用ProcessingStep的时候，都只支持一个Python文件作为源代码。
- 如果ProcessingStep中有多个Python文件，并且不在一个目录下，它们之间有调用关系，或者有requirements.txt文件，则需要这个输入文件使用Python的方式运行`pip -r`以及动态import
- 参见[pipeline.py](src/dwa_3/pipeline.py)

## 其他

### A、寻找数据源
- 数据源的要求：
    - 有普通ETL的需求。如处理null等
    - 有Preprocessing的需求，需要joblib支持。如standardization等
    - 数据源简单，便于造出假数据满足Quality、Drift、Bias等测试；或者，数据源足够大，可以轻松造出20次的数据
- 规划S3的目录结构，如input、output等
- 编写程序，运行就可以造新数据或者给一批数据
