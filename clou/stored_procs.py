from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
}

stored_procedures = [
    {
        "run_id": "run1",
        "project": "project_abc",
        "dataset": "dataset_abc",
        "procedure": "my_proc1",
        "arguments": {
            "start_date": "'2025-07-01'",
            "region": "'foo'"
        }
    },
    {
        "run_id": "run2",
        "project": "project_abc",
        "dataset": "dataset_abc",
        "procedure": "my_proc1",
        "arguments": {
            "start_date": "'2025-07-02'",
            "region": "'bar'"
        }
    },
    {
        "run_id": "run1",
        "project": "project_xyz",
        "dataset": "dataset_xyz",
        "procedure": "my_proc2",
        "arguments": {
            "id": "123",
            "status": "'baz'"
        }
    }
]

with DAG(
    dag_id='call_bigquery_stored_procs_multiple_runs',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    default_args=default_args,
    tags=['bigquery', 'stored_procs'],
) as dag:

    for proc in stored_procedures:
        run_id = proc["run_id"]
        proc_name = proc["procedure"]
        project = proc["project"]
        dataset = proc["dataset"]
        arguments = proc["arguments"]

        # Build argument list
        arguments_list = [
            f"{key} => {value}" for key, value in arguments.items()
        ]
        arguments_str = ', '.join(arguments_list)

        sql = f"CALL `{project}.{dataset}.{proc_name}`({arguments_str});"

        # Build unique task_id
        task_id = f'call_{proc_name}_{run_id}'

        BigQueryInsertJobOperator(
            task_id=task_id,
            configuration={
                "query": {
                    "query": sql,
                    "useLegacySql": False
                }
            },
            location="US",
        )
