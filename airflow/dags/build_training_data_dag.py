from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from ml.data_prep.build_f1_ml_table import build_f1_ml_table

default_args = {
    "owner": "manohar",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="build_f1_training_data",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    build_ml_table = PythonOperator(
        task_id="build_f1_ml_table",
        python_callable=build_f1_ml_table
    )
