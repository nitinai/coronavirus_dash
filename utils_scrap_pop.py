__author__ = "Nitin Patil"

import argparse
import datetime as dt
from datetime import datetime
import os
import requests 
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import shutil
import csv

cwd = os.path.dirname(os.path.realpath(__file__))

url = "https://www.worldometers.info/world-population/population-by-country/"


def countries():
    link = 'https://www.worldometers.info/world-population/population-by-country/'
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "html.parser")

    countries = soup.find_all("table")[0]
    df = pd.read_html(str(countries))[0]

    df = replace_country_names(df, "Country (or dependency)")
    df["Country (or dependency)"] = df["Country (or dependency)"].apply(lambda x : x.replace("&", "and"))
    save(df, "pop_countries")

    return df

def indian_states():

    dfs = pd.read_html("https://en.wikipedia.org/wiki/List_of_states_and_union_territories_of_India_by_population")
    save(dfs[1], "pop_india_states")

def usa_states():

    dfs = pd.read_html("https://simple.wikipedia.org/wiki/List_of_U.S._states_by_population")
    df = pd.DataFrame(dfs[0])
    save(df, "pop_usa_states")


def save(df, filename):
    PATH = "./data_sources"
    DATA_PATH = f"{PATH}/{filename}.csv"
    if(os.path.exists(DATA_PATH)):
        DST = f"./archieve/{filename}_backup.csv"
        shutil.copy2(DATA_PATH, DST)
    df.to_csv(DATA_PATH, index=False)
    print("Data saved to: ", DATA_PATH)

def replace_country_names(df, countryCol):
    df[countryCol].replace({
        "Mainland China": "China",
        "Taiwan*":"Taiwan", 
        "Korea, South": "South Korea", 
        "US":"United States",
        "CÃ´te d'Ivoire": "Cote d'Ivoire",
        "RÃ©union":"Réunion", 
        "CuraÃ§ao": "Curaçao",
        "Saint Vincent and the Grenadines":"St. Vincent & Grenadines",

        },inplace=True)
    return df


if __name__ == '__main__':

    #countries()
    #indian_states()
    usa_states()
