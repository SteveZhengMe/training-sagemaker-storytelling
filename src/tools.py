import os
import numpy as np
import pandas as pd


def create_sample_data():
    """Create sample data for DWAPipeline-Scenario-2"""
    np.random.seed(42)

    data = {
        'date': pd.date_range('2023-01-01', periods=1000, freq='D'),
        'product_id': np.random.choice(['A001', 'A002', 'A003', 'B001', 'B002'], 1000),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], 1000),
        'sales_amount': np.random.uniform(10, 1000, 1000).round(2),
        'quantity': np.random.randint(1, 20, 1000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
        'customer_age': np.random.randint(18, 80, 1000),
        'discount_rate': np.random.uniform(0, 0.3, 1000).round(3)
    }

    df = pd.DataFrame(data)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(f'{current_dir}/../input/sales_data.csv', index=False)
    print(f"Created sample data with {len(df)} rows")
    print("Sample data preview:")
    print(df.head())

    return df


def test_local_spark_server():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master(
        "local[*]").appName("Test").getOrCreate()
    print("Spark started successfully!")
    spark.stop()


if __name__ == "__main__":
    # create_sample_data()
    # test_local_spark_server()
    pass
