    
import os

import requests

import pandas as pd


from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

def results_df():


    """
    This function fetches the data from the endpoint and save it in a dataframe
    """

    base_url = 'https://api.weatherbit.io/v2.0/history/daily?'
    key = os.getenv("api_key") 
    print(key)
    
    params = {
        "postal_code": 27601,
        "country": "US",
        "start_date": "2025-06-07",
        "end_date": "2025-06-08",
        "key": key
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        response_url = response.json()
        print(response_url)
        data = response_url["data"]
        results_df = pd.DataFrame(data)

        # Add extraction timestamp to DataFrame
        extraction_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        results_df.name = f"weather_data_{extraction_time}"
        
    else:
        print("Error: Unable to fetch data from the API", response.status_code)


    return results_df


df = results_df()

print(df)