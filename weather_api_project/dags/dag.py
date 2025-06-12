from airflow import DAG

from datetime import timedelta, datetime

from airflow.operators.python_operator import PythonOperator

from project1 import results_df, upload_to_aws as upload_to_aws_func

import boto3

from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook

hook = AwsBaseHook(aws_conn_id='my_aws_conn_id', client_type='s3')
client = hook.get_client_type('s3')


#defining my default arguments
default_args = {
        'owner' : 'airflow',
        'start_date' : datetime(2024, 11, 12)
}

#defining my DAG parameters
dag = DAG(
    dag_id = "weather_api_dag",
    description='my_first_dag',
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