from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count, when, year, month
import os


def print_folder(path: str) -> None:
    # For debugging
    print(f"Listing {path} contents:")
    for root, dirs, files in os.walk(path):
        level = root.replace(path, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

    print("========== Listing Done ==========")


def main(input_path: str, output_path: str):
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--input-path", type=str, required=True)
    # parser.add_argument("--output-path", type=str, required=True)
    # args = parser.parse_args()

    # 初始化 Spark Session
    spark = SparkSession.builder.appName("SalesDataProcessing").getOrCreate()

    print("Starting PySpark processing...")

    print_folder("/opt/ml/processing")

    try:
        # read csv
        # KW：默认使用hdfs协议读取，出现错误Error during processing: Path does not exist: hdfs://10.0.113.90/opt/ml/processing/input/sales_data.csv，这里需要file协议
        df = spark.read.option("header", "true").option(
            "inferSchema", "true").csv(f"file://{input_path}")

        print(
            f"Loaded data with {df.count()} rows and {len(df.columns)} columns")
        print("Schema:")
        df.printSchema()

        # Analysis
        # 1. product
        product_summary = df.groupBy("product_id", "category").agg(
            spark_sum("sales_amount").alias("total_sales"),
            spark_sum("quantity").alias("total_quantity"),
            avg("sales_amount").alias("avg_sales_amount"),
            count("*").alias("transaction_count"),
            avg("discount_rate").alias("avg_discount_rate")
        ).orderBy(col("total_sales").desc())

        # 2. region
        region_summary = df.groupBy("region").agg(
            spark_sum("sales_amount").alias("total_sales"),
            avg("sales_amount").alias("avg_sales_amount"),
            count("*").alias("transaction_count")
        ).orderBy(col("total_sales").desc())

        # 3. date
        df_with_date = df.withColumn("year", year(col("date"))) \
            .withColumn("month", month(col("date")))

        monthly_summary = df_with_date.groupBy("year", "month").agg(
            spark_sum("sales_amount").alias("monthly_sales"),
            count("*").alias("monthly_transactions"),
            avg("sales_amount").alias("avg_monthly_sales")
        ).orderBy("year", "month")

        # 4. customer
        age_summary = df.withColumn(
            "age_group",
            when(col("customer_age") < 25, "18-24")
            .when((col("customer_age") >= 25) & (col("customer_age") < 35), "25-34")
            .when((col("customer_age") >= 35) & (col("customer_age") < 45), "35-44")
            .when((col("customer_age") >= 45) & (col("customer_age") < 55), "45-54")
            .when((col("customer_age") >= 55) & (col("customer_age") < 65), "55-64")
            .otherwise("65+")
        ).groupBy("age_group").agg(
            spark_sum("sales_amount").alias("total_sales"),
            avg("sales_amount").alias("avg_sales_amount"),
            count("*").alias("customer_count")
        ).orderBy(col("total_sales").desc())

        # save
        print("Saving processed data...")

        # if output_path does not exist, create it
        os.makedirs(output_path, exist_ok=True)

        # KW：同样，需要file://，否则无法保存文件到/opt/ml/processing/output，进而也无法上传到S3
        product_summary.coalesce(1).write.mode("overwrite").option(
            "header", "true").csv(f"file://{output_path}/product_summary")
        region_summary.coalesce(1).write.mode("overwrite").option(
            "header", "true").csv(f"file://{output_path}/region_summary")
        monthly_summary.coalesce(1).write.mode("overwrite").option(
            "header", "true").csv(f"file://{output_path}/monthly_summary")
        age_summary.coalesce(1).write.mode("overwrite").option(
            "header", "true").csv(f"file://{output_path}/age_summary")

        print("Processing completed successfully!")

        # print summary
        print("\\n=== Processing Summary ===")
        print(f"Total records processed: {df.count()}")
        print(
            f"Total sales amount: ${df.agg(spark_sum('sales_amount')).collect()[0][0]:,.2f}")
        print(
            f"Average sales amount: ${df.agg(avg('sales_amount')).collect()[0][0]:.2f}")

        print("\\nTop 5 products by sales:")
        product_summary.show(5)

        print("\\nSales by region:")
        region_summary.show()

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise e
    finally:
        print_folder("/opt/ml/processing")
        spark.stop()


if __name__ == "__main__":
    input_path = "/opt/ml/processing/input/sales_data.csv"
    output_path = "/opt/ml/processing/output"
    main(input_path, output_path)
