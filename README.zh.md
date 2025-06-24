# 说明

这个分支用来尝试下面的功能：

## 1、在CodeBuild上执行“创建Sagemaker Pipeline”的Python代码
- 是否可以建
- 建好后是否可以使用CLI运行这个Pipeline
- 创建是否要等很久
- 如何得知输出结果
- 错误信息和如何监控
- 参见[buildspec_1.yml](buildspec_1.yml)和[main_1.py](src/main_1.py)
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

## 2、Pipeline中Step对于多文件的支持 - PySparkProcessor
- Step中有多个Python文件，并且不在一个目录下，它们之间有调用关系
- Step中有requirements.txt文件，Step能否自动安装他们
- 参见[buildspec_2.yml](buildspec_2.yml)和[main_2.py](src/main_2.py)

## 3、Pipeline中Step对于多文件的支持 - ScriptProcessor
- Step中有多个Python文件，并且不在一个目录下，它们之间有调用关系
- Step中有requirements.txt文件，Step能否自动安装他们
- 参见[buildspec_3.yml](buildspec_2.yml)和[main_3.py](src/main_2.py)


## 4、编写DWA
- Pipeline支持三个参数：input、output、是否包含target列
- 代码既要满足在Training Pipeline的Preprocessing以前执行，也要满足Inference Pipeline
- 参见[buildspec_4.yml](buildspec_3.yml)和[main_4.py](src/main_3.py)

## 其他

### A、寻找数据源
- 数据源的要求：
    - 有普通ETL的需求。如处理null等
    - 有Preprocessing的需求，需要joblib支持。如standardization等
    - 数据源简单，便于造出假数据满足Quality、Drift、Bias等测试；或者，数据源足够大，可以轻松造出20次的数据
- 规划S3的目录结构，如input、output等
- 编写程序，运行就可以造新数据或者给一批数据
