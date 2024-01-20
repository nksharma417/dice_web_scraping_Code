# %%
import pandas as pd 
import numpy as np          ### Importing the necessary libraries
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
from urllib.parse import urlparse, parse_qs
import re
import json
import csv
import sys
from datetime import datetime

import requests
from loguru import logger

# %%
def parse_dice_url(url):            ### Creating a function which I am gonna use later.         
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    q = query_params.get('q', [None])[0]
    location = query_params.get('location', [None])[0]
    latitude = query_params.get('latitude', [None])[0]
    longitude = query_params.get('longitude', [None])[0]

    return q, location, latitude, longitude

# %%
headers = {         ### Giving the headers according to the website
    "authority": "job-search-api.svc.dhigroupinc.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-api-key": "1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8",
}

# %%
output_csv = input("Enter CSV fidle name you want as output: ") + ".csv"        ### Asking the name you want to save the file
search_type=input('If you want to just search the jobs directly by entering keyword without location enter 1 otherwise enter 2')       ### Asking whether you will search by keyword or url
if search_type=='1':
    search_query = input('Enter the job title/ company name/ skill:')   
    params = {
        "q": search_query,
        "countryCode2": "US",
        "radius": "30",
        "radiusUnit": "mi",
        "page": "1",
        "pageSize": "100",
        "facets": "employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote",
        "fields": "id|jobId|guid|summary|title|postedDate|modifiedDate|jobLocation.displayName|detailsPageUrl|salary|clientBrandId|companyPageUrl|companyLogoUrl|positionId|companyName|employmentType|isHighlighted|score|easyApply|employerType|workFromHomeAvailability|isRemote|debug",
        "culture": "en",
        "recommendations": "true",
        "interactionId": "0",
        "fj": "true",
        "includeRemote": "true",
    }

elif search_type == "2":
    url=input('Please enter the url from where you want to collect the data :')
    q, location, latitude, longitude = parse_dice_url(url)


    params = {
        "countryCode2": "US",
        "radius": "100",
        "radiusUnit": "mi",
        "page": "1",
        "q":q,
        "locationPrecision":'city',
        "latitude":latitude,
        "longitude":longitude,
        "pageSize": "100",
        "facets": "employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote",
        # "filters.clientBrandNameFilter": clientBrandNameFilter,
        "fields": "id|jobId|guid|summary|title|postedDate|modifiedDate|jobLocation.displayName|detailsPageUrl|salary|clientBrandId|companyPageUrl|companyLogoUrl|positionId|companyName|employmentType|isHighlighted|score|easyApply|employerType|workFromHomeAvailability|isRemote|debug",
        "culture": "en",
        "recommendations": "true",
        "interactionId": "0",
        "fj": "true",
        "includeRemote": "true",
    }

if not search_type and not output_csv:
    logger.error("You didn't make a choice, Exiting...")
    sys.exit()


# %%
response = requests.get(        ### Collecting the data
    "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search",           
    params=params,
    headers=headers,
    timeout=30,
).json()
try:
    data = response["data"]
except:
    print('Sorry could not get the data :')


# %%
column_mapping = {
    'id': 'Job_id',
    'companyName': 'Vendor company name',
    'title': 'Job title',
    'employmentType': 'Job type',
    'salary': 'Pay rate',
    'detailsPageUrl': 'Job posting url',
    'jobLocation': 'Job location',
    'postedDate': 'Job posting date',
    'isRemote': 'Work type(remote) (True or false)',
    'workFromHomeAvailability': 'Work from availability',
    'modifiedDate':'Modified Date'
}

# %%
if data:
    # Create DataFrame
    df = pd.DataFrame(data)
    df['jobLocation'] = df['jobLocation'].apply(lambda x: x['displayName'] if isinstance(x, dict) and 'displayName' in x else None)
    df1=df[['id','title','postedDate','detailsPageUrl','jobLocation','salary','companyName','employmentType','workFromHomeAvailability','isRemote','modifiedDate']]
    df1.rename(columns=column_mapping, inplace=True)
    df1['Current date time'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    df1.to_csv(output_csv,index=False)
    print('Successfully saved the data')
else:
    print("Sorry we can't get the data. Please try again with correct url or keywords")
    


