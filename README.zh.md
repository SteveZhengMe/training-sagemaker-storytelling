# 说明

这个分支用来尝试下面的功能：

## 1、在CodeBuild上执行“创建Sagemaker Pipeline”的Python代码
- 是否可以建
- 建好后是否可以使用CLI运行这个Pipeline
- 创建是否要等很久
- 如何得知输出结果
- 错误信息和如何监控
- 参见[buildspec_1.yml](buildspec_1.yml)

## 2、Pipeline中Step对于多文件的支持
- Step中有多个Python文件，并且不在一个目录下，它们之间有调用关系
- Step中有requirements.txt文件，Step能否自动安装他们
- 参见[buildspec_2.yml](buildspec_2.yml)

## 3、寻找合适的数据源，上传到S3
- 数据源的要求：
    - 有普通ETL的需求。如处理null等
    - 有Preprocessing的需求，需要joblib支持。如standardization等
    - 数据源简单，便于造出假数据满足Quality、Drift、Bias等测试；或者，数据源足够大，可以轻松造出20次的数据
- 规划S3的目录结构，如input、output等
- 编写程序，运行就可以造新数据或者给一批数据

## 4、编写DWA
- Pipeline支持三个参数：input、output、是否包含target列
- 代码既要满足在Training Pipeline的Preprocessing以前执行，也要满足Inference Pipeline
- 参见[buildspec_3.yml](buildspec_3.yml)