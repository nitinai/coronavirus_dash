__author__ = "Nitin Patil"

from datetime import datetime
import os
import requests 
import pandas as pd
from bs4 import BeautifulSoup
import shutil

def clean_data(df):
    now  = datetime.now()
    df['Date'] = now.strftime("%m/%d/%Y") 
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    # latitude and longitude information
    # ----------------------------------
    lat = {'Delhi':28.7041,
        'Haryana':29.0588,
        'Kerala':10.8505,
        'Rajasthan':27.0238,
        'Telengana':18.1124,
        'Uttar Pradesh':26.8467,
        'Ladakh':34.2996,
        'Tamil Nadu':11.1271,
        'Jammu and Kashmir':33.7782,
        'Punjab':31.1471,
        'Karnataka':15.3173,
        'Maharashtra':19.7515,
        'Andhra Pradesh':15.9129, 
        'Odisha':20.9517, 
        'Uttarakhand':30.0668, 
        'West Bengal':22.9868, 
        'Puducherry': 11.9416, 
        'Chandigarh': 30.7333, 
        'Chhattisgarh':21.2787, 
        'Gujarat': 22.2587, 
        'Himachal Pradesh': 31.1048, 
        'Madhya Pradesh':  22.9734,
        "Bihar":25.0961,
        "Manipur":24.6637}

    long = {'Delhi':77.1025,
            'Haryana':76.0856,
            'Kerala':76.2711,
            'Rajasthan':74.2179,
            'Telengana':79.0193,
            'Uttar Pradesh':80.9462,
            'Ladakh':78.2932,
            'Tamil Nadu':78.6569,
            'Jammu and Kashmir':76.5762,
            'Punjab':75.3412,
            'Karnataka':75.7139,
            'Maharashtra':75.7139,
            'Andhra Pradesh':79.7400, 
            'Odisha':85.0985, 
            'Uttarakhand':79.0193, 
            'West Bengal':87.8550, 
            'Puducherry': 79.8083, 
            'Chandigarh': 76.7794, 
            'Chhattisgarh':81.8661, 
            'Gujarat': 71.1924, 
            'Himachal Pradesh': 77.1734, 
            'Madhya Pradesh':  78.6569,
        "Bihar": 85.3131,
        "Manipur":93.9063}

    df['Latitude'] = df['Name of State / UT'].map(lat)
    df['Longitude'] = df['Name of State / UT'].map(long)

    assert(df.isna().sum().values.sum() == 0)

    return df


# web scrapping
def download_India_data():
    link = 'https://www.mohfw.gov.in/'
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "html.parser")

    thead = soup.find_all("thead")
    columns = []

    for th in  thead[-1].find_all('th'):
        columns.append(th.text)

    # Table body
    tbody = soup.find_all('tbody')[-1]

    # All row data
    rows = tbody.find_all('tr')

    all_rows = []
    for row in rows[:-1]:
        row_cont = []
        for td in  row.find_all('td'):
            row_cont.append(td.text)
            
        all_rows.append(row_cont)

    df = pd.DataFrame(data=all_rows, columns=columns)

    df.drop("S. No.", axis=1, inplace=True)

    df = clean_data(df)
    # saving data
    # -----------
    if df.isna().sum().values.sum() == 0:
        now  = datetime.now()
        file_name = now.strftime("%m-%d-%Y")+'_India.csv'
        DATA_PATH = os.path.join("./data_sources/covid-19-india-data/", file_name)
        df.to_csv(DATA_PATH, index=False)

        return DATA_PATH

    return None

if __name__ == '__main__':
    DATA_PATH = download_India_data()

    if not DATA_PATH:
        folder, filename = os.path.split(DATA_PATH)
        DST = os.path.join("./data/", filename)
        shutil.copyfile(DATA_PATH, DST)
        print(DST)
