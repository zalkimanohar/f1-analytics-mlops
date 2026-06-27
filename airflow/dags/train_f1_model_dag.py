from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from ml.training.train_f1_model import train_model

default_args = {
    "owner": "manohar",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="train_f1_model",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    train_task = PythonOperator(
        task_id="train_f1_winner_model",
        python_callable=train_model
    )

