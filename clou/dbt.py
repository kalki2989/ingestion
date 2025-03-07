
https://docs.getdbt.com/guides/airflow-and-dbt-cloud?step=1


from airflow import DAG
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator
from datetime import datetime

# Define default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 7),
    'retries': 1,
}

# Initialize the DAG
with DAG(
    'dbt_cloud_job_dag',
    default_args=default_args,
    schedule_interval='@daily',  # Adjust as needed
    catchup=False,
) as dag:

    # Define the task to run the dbt Cloud job
    dbt_run_job = DbtCloudRunJobOperator(
        task_id='run_dbt_cloud_job',
        dbt_cloud_conn_id='dbt_cloud_default',
        job_id='your_dbt_cloud_job_id',  # Replace with your dbt Cloud job ID
        check_interval=10,
        timeout=600,
        wait_for_termination=True,
    )

    # Set task dependencies (if any)
    dbt_run_job
