from airflow import DAG

from datetime import timedelta, datetime

from airflow.operators.python_operator import PythonOperator

from project import upload_to_aws as upload_to_aws_func

import boto3


#defining my default arguments
default_args = {
        'owner' : 'airflow',
        'start_date' : datetime(2024, 11, 12)
}

#defining my DAG parameters
dag = DAG(
    dag_id = "google_spreadsheet_dag",
    description='spreadsheet_dag',
    default_args=default_args,
    catchup=False
)


#defining my task parameter using Python Operator
#this task 
fetch_and_save_in_df = PythonOperator(
    python_callable = results_df,
    dag=dag,
    task_id = 'fetch_and_save_in_df'
)

#this task 
upload_to_aws_task = PythonOperator(
    python_callable = upload_to_aws_func,
    dag=dag,
    task_id = 'upload_to_aws_task'
)

fetch_and_save_in_df >> upload_to_aws_task