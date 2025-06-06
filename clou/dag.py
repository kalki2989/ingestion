from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
from airflow.models import Variable
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator



def run_processor_for_segment(bucket_suffix, segment):
    processor = ParquetToBigQueryProcessor(
        bucket_name=f"",
        project=,
        dataset='raw',
        state_table_name='',
        segments=[segment],
        suffix=bucket_suffix
    )
    processor.process_segment(segment)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 10,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'punch_raw_to_bq',
    default_args=default_args,
    description='A DAG to process cloudsql tables and load into BigQuery in parallel for each segment',
    schedule_interval=schedule,
    catchup=False, 
)

start = DummyOperator(
    task_id='start',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

segments = [
    ""
]


for suffix in suffixes:
    for segment in segments:
        task = PythonOperator(
            task_id=f'process_{segment}{suffix.replace("-", "_")}',
            python_callable=run_processor_for_segment,
            op_args=[suffix, segment],
            dag=dag,
        )
        start >> task >> end



from airflow.sensors.external_task import ExternalTaskSensor

wait_for_latest_dag_success = ExternalTaskSensor(
    task_id='wait_for_latest_dag_success',
    external_dag_id='target_dag_id',  # The DAG you want to wait for
    external_task_id=None,  # Wait for any task in the DAG to complete
    allowed_states=['success'],  # Wait for the DAG run to succeed
    failed_states=['failed'],  # Fail if the DAG run fails
    poke_interval=300,  # Check every 5 minutes
    timeout=1800,  # Timeout after 30 minutes
    mode='poke',  # Use the poke mode to check periodically
    dag=dag,
)
