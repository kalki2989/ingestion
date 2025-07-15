stored_procs_set_a = [
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
        "project": "project_xyz",
        "dataset": "dataset_xyz",
        "procedure": "my_proc2",
        "arguments": {
            "id": "123",
            "status": "'bar'"
        }
    }
]

stored_procs_set_b = [
    {
        "run_id": "run3",
        "project": "project_abc",
        "dataset": "dataset_abc",
        "procedure": "my_proc3",
        "arguments": {
            "year": "2025",
            "quarter": "'Q3'"
        }
    }
]


from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
}

with DAG(
    dag_id='parallel_stored_procs_with_barrier',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    default_args=default_args,
    tags=['bigquery', 'stored_procs'],
) as dag:

    # Barrier dummy task
    barrier = EmptyOperator(
        task_id='barrier_between_sets'
    )

    # ---- SET A ----
    set_a_tasks = []
    for proc in stored_procs_set_a:
        run_id = proc["run_id"]
        proc_name = proc["procedure"]
        project = proc["project"]
        dataset = proc["dataset"]
        arguments = proc["arguments"]

        # Build arguments string
        arguments_list = [
            f"{key} => {value}" for key, value in arguments.items()
        ]
        arguments_str = ', '.join(arguments_list)

        sql = f"CALL `{project}.{dataset}.{proc_name}`({arguments_str});"

        task_id = f"call_{proc_name}_{run_id}"

        task = BigQueryInsertJobOperator(
            task_id=task_id,
            configuration={
                "query": {
                    "query": sql,
                    "useLegacySql": False
                }
            },
            location="US",
        )

        set_a_tasks.append(task)

    # ---- SET B ----
    set_b_tasks = []
    for proc in stored_procs_set_b:
        run_id = proc["run_id"]
        proc_name = proc["procedure"]
        project = proc["project"]
        dataset = proc["dataset"]
        arguments = proc["arguments"]

        arguments_list = [
            f"{key} => {value}" for key, value in arguments.items()
        ]
        arguments_str = ', '.join(arguments_list)

        sql = f"CALL `{project}.{dataset}.{proc_name}`({arguments_str});"

        task_id = f"call_{proc_name}_{run_id}"

        task = BigQueryInsertJobOperator(
            task_id=task_id,
            configuration={
                "query": {
                    "query": sql,
                    "useLegacySql": False
                }
            },
            location="US",
        )

        set_b_tasks.append(task)

    # ---- Dependencies ----

    # All set A → barrier
    set_a_tasks >> barrier

    # Barrier → all set B
    barrier >> set_b_tasks


