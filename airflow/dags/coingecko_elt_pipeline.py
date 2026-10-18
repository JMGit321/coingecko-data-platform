import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

sys.path.append('/opt/airflow/include/scripts')
from ingest_coingecko import fetch_and_load_coingecko_data

default_args = {
    'owner': 'analytics_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='coingecko_medallion_elt_pipeline',
    default_args=default_args,
    description='Automated ELT pipeline extracting CoinGecko data to MinIO and running dbt transformations',
    start_date=datetime(2026, 1, 1),
    schedule_interval='0 6 * * *',
    catchup=False,
    tags=['production', 'crypto', 'dbt', 'medallion']
) as dag:

    task_ingest_api = PythonOperator(
        task_id='ingest_api_to_minio_bronze',
        python_callable=fetch_and_load_coingecko_data,
    )

    task_dbt_run = BashOperator(
        task_id='dbt_run_models',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir .',
    )

    task_dbt_test = BashOperator(
        task_id='dbt_test_models',
        bash_command='cd /opt/airflow/dbt_project && dbt test --profiles-dir .',
    )

    task_ingest_api >> task_dbt_run >> task_dbt_test