import os

import awswrangler as wr

import requests

import pandas as pd

from datetime import datetime

import boto3

from airflow.models import Variable

def results_df():


    """
    This function fetches the data from the endpoint and save it in a dataframe
    """

    base_url = 'https://api.weatherbit.io/v2.0/history/daily?key=9c243a0d8e9a4c8b83e18bc7ddca7b28'
    
    params = {
        "postal_code": 27601,
        "country": "US",
        "start_date": "2025-06-07",
        "end_date": "2025-06-08"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        response_url = response.json()
        data = response_url["data"]
        results_df = pd.DataFrame(data)

        # Add extraction timestamp to DataFrame
        extraction_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        results_df.name = f"weather_data_{extraction_time}"
        
    else:
        print("Error: Unable to fetch data from the API", response.status_code)


    return results_df


df = results_df()  


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
    path = f"s3://toludebuckets/weather_api" + f"/{time_stamp}"
    wr.s3.to_parquet(
        df=df,
        path=path,
        dataset=True,
        mode="append",
        boto3_session=session
    )
    return