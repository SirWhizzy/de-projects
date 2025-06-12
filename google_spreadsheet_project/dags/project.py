import pandas as pd

import gspread 

import os

import awswrangler as wr

from datetime import datetime

import boto3

from airflow.models import Variable


def google_sheet_data():
    gc = gspread.service_account(filename='C:/Users/Ademi/Documents/DE/projects/google_spreadsheet_project/credentials.json')
    sh = gc.open('mentee_data')
    worksheet = sh.worksheet('data')

    dataframe = pd.DataFrame(worksheet.get_all_records())

    dataframe.rename(columns={'first name': 'first_name', 'Last namE': 'last_name', ' State of Origin ': 'state_of_origin'}, inplace=True)

    return

df = google_sheet_data()

def upload_to_aws(**context):
    access_key = Variable.get("aws_access_key")
    secret_key = Variable.get("aws_secret_key")
    region = Variable.get("region")

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

   
    time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = f"s3://toludebuckets/gspread" + f"/{time_stamp}"
    wr.s3.to_parquet(
        df=df,
        path=path,
        dataset=True,
        mode="append",
        boto3_session=session
    )
    return
