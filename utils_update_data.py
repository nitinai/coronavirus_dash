__author__ = "Nitin Patil"

import argparse
import datetime as dt
from datetime import datetime
import os
#import requests 
import numpy as np
import pandas as pd
#from bs4 import BeautifulSoup
import shutil
import model

cwd = os.path.dirname(os.path.realpath(__file__))

def last_update():
    with open("./data/LastUpdate.txt", "w") as f:
        today_dt = datetime.now()
        # '%d/%m/%Y, %H:%M'     DD/MM/YYYY HH:MM
        # '%d-%m-%Y, %H:%M %p'  DD-MM-YYYY HH:MM AM/PM
        # '%d-%b-%Y, %H:%M'     DD-MonthShort-YYYY HH:MM
        # '%d-%b-%Y, %H:%M'     DD-MonthFull-YYYY HH:MM
        update_date = today_dt.today().strftime('%d %B %Y, %H:%M')
        f.write(f"""Last updated on {update_date} GMT+5:30""")
        

def clean_data(df):
    print("clean_data")
    now  = datetime.now()
    df['Last_Update'] = now.strftime("%m/%d/%Y") 
    df['Last_Update'] = pd.to_datetime(df['Last_Update'], format='%m/%d/%Y')

    # latitude and longitude information
    # ----------------------------------
    lat = {'Delhi':28.7041,
        'Haryana':29.0588,
        'Kerala':10.8505,
        'Rajasthan':27.0238,
        'Telangana':18.1124,
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
        "Manipur":24.6637,
        "Mizoram":23.1645,
        "Goa":15.2993,
        "Andaman and Nicobar Islands":11.7401,
        "Assam": 26.2006,
        "Jharkhand":23.6102,
        "Arunachal Pradesh":28.2180,
        "Tripura":23.9408,
        "Nagaland":26.1584,
        "Meghalaya": 25.467,
        "Sikkim":27.533,
        "Dadar Nagar Haveli": 20.1809,
        "Daman & Diu" : 20.4283,
        "Dadra and Nagar Haveli and Daman and Diu": 20.1809,
        }

    long = {'Delhi':77.1025,
            'Haryana':76.0856,
            'Kerala':76.2711,
            'Rajasthan':74.2179,
            'Telangana':79.0193,
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
        "Manipur":93.9063,
        "Mizoram":92.9376,
        "Goa":74.1240,
        "Andaman and Nicobar Islands":92.6586,
        "Assam": 92.9376,
        "Jharkhand":85.2799,
        "Arunachal Pradesh":94.7278,
        "Tripura":91.9882,
        "Nagaland":94.5624,
        "Meghalaya": 91.3662,
        "Sikkim": 88.5122,
        "Dadar Nagar Haveli": 73.0169,
        "Daman & Diu" : 72.8397,
        "Dadra and Nagar Haveli and Daman and Diu": 73.0169,

        }

    df['Lat'] = df['Province_State'].map(lat)
    df['Long_'] = df['Province_State'].map(long)

    #assert(df.isna().sum().values.sum() == 0)

    return df

def scrap_BeautifulSoup():
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

    return df

def scrap_pandas():
    try:
        df = pd.read_html("https://www.mohfw.gov.in")
        df = df[0]
        
        df.drop("S. No.", axis=1, inplace=True)

        df.columns = ['Province_State', "Active",
                'Recovered', 'Deaths', 'Confirmed']
        
        
        df["Country_Region"] = "India"

        #df.drop(df.tail(1).index,inplace=True)
        
        if len(df[df["Province_State"] == "Total number of confirmed cases in India"]) > 0:
            df.drop(df[df["Province_State"] == "Total number of confirmed cases in India"].index, inplace=True)
        if len(df[df["Province_State"] == "*States wise distribution is subject to further verification and reconciliation"]) > 0:
            df.drop(df[df["Province_State"] == "*States wise distribution is subject to further verification and reconciliation"].index, inplace=True)

        if len(df[df["Province_State"] == "Total#"]) > 0:
            start_ind = df[df["Province_State"] == "Total#"].index.values[0]
            index_list = list(range(start_ind, len(df)))
            df.drop(index_list, inplace=True)

        df["Deaths"].fillna(0, inplace=True)
        df["Recovered"].fillna(0, inplace=True)
        
    except Exception as ex:
        print("Error while dropping total count row : ", str(ex))   

    return df

# web scrapping
def download_India_data():
    
    print("download_India_data")
    df = scrap_pandas()

    #df = clean_data(df)
    # saving data
    
    # -----------
    now  = datetime.now()
    file_name = now.strftime("%m-%d-%Y")+'_India.csv'
    DATA_PATH = os.path.join(cwd, "data_sources\covid-19-india-data", file_name).replace('\\', '/')
    #df.to_csv(DATA_PATH, index=False)
    #print("Data is same as previous. Still new file is saved at :", DATA_PATH)
    try:
        PREVIOUS_DATA_PATH = os.path.join(cwd, "data_sources\covid-19-india-data", file_name).replace('\\', '/')
        if(not os.path.exists(PREVIOUS_DATA_PATH)):
            prev = now - dt.timedelta(days=1)
            prev_file_name = prev.strftime("%m-%d-%Y")+'_India.csv'
            PREVIOUS_DATA_PATH = os.path.join(cwd, "data_sources\covid-19-india-data", prev_file_name).replace('\\', '/')
            
        if(os.path.exists(PREVIOUS_DATA_PATH)):
            prev_df = pd.read_csv(PREVIOUS_DATA_PATH)

            #columns = ['Total Confirmed cases (Indian National)',
            #            'Total Confirmed cases ( Foreign National )',
            #            'Cured/Discharged/Migrated', 'Death']

            #columns = ['Total Confirmed cases *',
            #            'Cured/Discharged/Migrated', 'Death']

            columns = ['Province_State',
            'Confirmed',
            'Recovered', 'Deaths']

        #for c in columns:
        #    df[c] = df[c].astype(int)

            # if anything has changed
            if (np.array_equal(df[columns].sum().values, prev_df[columns].sum().values)):
                df.to_csv(DATA_PATH, index=False)
                print("Data is same as previous. Still new file is saved at :", DATA_PATH)

            else:
                df.to_csv(DATA_PATH, index=False)
                print("Data saved to: ", DATA_PATH)
                
                if df.isna().sum().values.sum() != 0: 
                    print("Some data is NULL")

                last_update()

    except Exception as ex:
        print("Error while saving India data : ", str(ex))

    return df


def save(df, filename, index=False):
    PATH = "./data"
    DATA_PATH = f"{PATH}/{filename}.csv"
    if(os.path.exists(DATA_PATH)):
        DST = f"./archieve/{filename}_backup.csv"
        shutil.copy2(DATA_PATH, DST)
    df.to_csv(DATA_PATH, index=index)
    print("Data saved to: ", DATA_PATH)


def replace_province_names(df, provinceCol):
    df[provinceCol].replace({
        "Azad Jammu and Kashmir": "Pak Occupied Kashmir",
        },inplace=True)
    return df


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

def load_world_latest_data():

    print("load latest world data")
    df_world = pd.read_csv(model.get_latest_day_data_file())

    df_world["Province_State"].fillna("", inplace=True)
    #df_world["Country_Region"].replace({"Mainland China": "China","Taiwan*":"Taiwan", "Korea, South": "South Korea", "US":"United States"},inplace=True)
    df_world = replace_country_names(df_world, "Country_Region")
    df_world = replace_province_names(df_world, "Province_State")
    
    #df_world["Province_State"] = df_world["Province_State"].map(lambda x : x+", " if x else x)
    #df_world["hover_name"] = df_world["Province_State"] + df_world["Country_Region"]
    #df_world.drop(df_world[df_world["Confirmed"]==0].index,inplace=True)

    return df_world

def load_US_data():
    print("load latest US data")
    df_us = pd.read_csv(model.get_latest_day_data_file("./data_sources/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us"))

    df_us = replace_country_names(df_us, "Country_Region")

    df_us.drop(df_us[df_us["Province_State"] == "Recovered"].index, inplace=True)

    #df_us.drop(df_us[df_us["Country_Region"] != "US"].index, inplace=True)
    
    return df_us

def load_time_series_data():
    """
    These files were deprecated from 24 Mar 2020
    time_series_19-covid-Confirmed.csv
    time_series_19-covid-Deaths.csv
    time_series_19-covid-Recovered.csv
    """
    PATH = "./data_sources/COVID-19/csse_covid_19_data/csse_covid_19_time_series"
    #DATA_PATH = os.path.join(PATH,"time_series_19-covid-Confirmed.csv")
    DATA_PATH = os.path.join(PATH,"time_series_covid19_confirmed_global.csv")
    df_confirmed = pd.read_csv(DATA_PATH)
    
    DATA_PATH = os.path.join(PATH,"time_series_covid19_recovered_global.csv")
    df_recovered = pd.read_csv(DATA_PATH)
    
    DATA_PATH = os.path.join(PATH,"time_series_covid19_deaths_global.csv")
    df_deaths = pd.read_csv(DATA_PATH)
    
    df_confirmed.drop(["Lat","Long"], axis=1, inplace=True)
    df_recovered.drop(["Lat","Long"], axis=1, inplace=True)
    df_deaths.drop(["Lat","Long"], axis=1, inplace=True)

    #df_confirmed.iloc[:,4:].fillna(0, inplace=True)
    #df_recovered.iloc[:,4:].fillna(0, inplace=True)
    #df_deaths.iloc[:,4:].fillna(0, inplace=True)

    #df_confirmed.iloc[:,4:] = df_confirmed.iloc[:,4:].astype(int)
    #df_recovered.iloc[:,4:] = df_recovered.iloc[:,4:].astype(int)
    #df_deaths.iloc[:,4:] = df_deaths.iloc[:,4:].astype(int)

    # Mismatch in Date column formating
    df_recovered.columns = df_confirmed.columns
    
    return df_confirmed, df_recovered, df_deaths

INDIA_SPECIAL_PROCESS = False

def process_data():
    print("process_data")

    ###############################
    # Read India data
    ###############################
    if INDIA_SPECIAL_PROCESS:
        now  = datetime.now()
        file_name = now.strftime("%m-%d-%Y")+'_India.csv'
        INDIA_DATA = os.path.join("./data_sources/covid-19-india-data", file_name)
        df_India = pd.read_csv(INDIA_DATA)
        print("India data : ", INDIA_DATA)

    ###############################
    # Read world data and infuse India data in it
    ###############################
    df_world = load_world_latest_data()
    if INDIA_SPECIAL_PROCESS:
        df_world.drop(df_world[df_world["Country_Region"] == "India"].index, inplace=True)


    ###############################
    # infuse US data as well
    ###############################
    df_us = load_US_data()
    df_world.drop(df_world[df_world["Country_Region"] == "United States"].index, inplace=True)

    COMMON_COLS = ["Province_State","Confirmed","Recovered","Deaths","Country_Region","Last_Update","Lat","Long_"]

    if INDIA_SPECIAL_PROCESS:
        df_world = pd.concat([df_world, df_India, df_us[COMMON_COLS]], ignore_index=True)
    else:
        df_world = pd.concat([df_world, df_us[COMMON_COLS]], ignore_index=True)

    df_world.dropna(how="all", inplace=True) # drop rows with all null values
    df_world["Province_State"].fillna("", inplace=True)
    df_world["Confirmed"].fillna(0, inplace=True)
    df_world["Deaths"].fillna(0, inplace=True)
    df_world["Recovered"].fillna(0, inplace=True)

    #print("df_world.columns : ", df_world.columns)
    
    #save(df_world, "world_latest_intermediate")

    # Process
    COLS = ['Confirmed', 'Deaths', 'Recovered']
    for c in COLS:
        #print("Converting type for ", c)
        df_world[c] = df_world[c].astype(float)
        df_world[c] = df_world[c].astype(int)

    df_world["Active"]= df_world["Confirmed"]-df_world["Recovered"]-df_world["Deaths"]
    df_world["Active"] = df_world["Active"].astype(int)
    df_world["Active"].clip(lower=0, inplace=True)


    df_world["Recovery rate"] = df_world['Recovered']/df_world['Confirmed']
    df_world["Death rate"] = df_world['Deaths']/df_world['Confirmed']

    
    df_world["hover_name"] = ""
    for i in range(len(df_world)):
        if df_world.at[i,'Province_State']:
            df_world.at[i,'hover_name'] = df_world.at[i,'Province_State'] + ", " + df_world.at[i,'Country_Region']
        else:
            df_world.at[i,'hover_name'] = df_world.at[i,'Country_Region']


    # To show correct tabel and statistics for selected country. For that we are grouping on 
    # Province/State
    for i in range(len(df_world)):
        if not df_world.at[i,'Province_State']:
            df_world.at[i,'Province_State'] = df_world.at[i,'Country_Region']

    COL_MAP = {'Province_State':'Province/State', "Country_Region":"Country/Region", 'Confirmed':'Total Cases'}
    df_world.rename(columns=COL_MAP, inplace=True)

    # All columns ['FIPS', 'Admin2', 'Province/State', 'Country/Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active','Combined_Key', 'Death rate', 'hover_name']
    # Delete columns we are not using
    df_world.drop(['FIPS', 'Admin2','Last_Update','Combined_Key'], axis=1, inplace=True)

    #save(df_world, "world_latest_x1")
    ###############################
    # Time series data
    ###############################
    df_co, df_re, df_de = load_time_series_data()
    
    if INDIA_SPECIAL_PROCESS:
        conf_val = df_India["Confirmed"].sum()
        rec_val = df_India["Recovered"].sum()
        death_val = df_India["Deaths"].sum()

        cidx = df_co[df_co["Country/Region"]=="India"].index[0]
        ridx = df_re[df_re["Country/Region"]=="India"].index[0]
        didx = df_de[df_de["Country/Region"]=="India"].index[0]

        df_co.iloc[cidx,-1] = conf_val
        df_re.iloc[ridx,-1] = rec_val
        df_de.iloc[didx,-1] = death_val

    #isConfLess, isRecLess, isDeathLess = (False, False, False)
    #if df_co.iloc[cidx,-1] <= conf_val:
    #    df_co.iloc[cidx,-1] = conf_val
    #else:
    #    isConfLess = True
#
    #if df_re.iloc[ridx,-1] <= rec_val:
    #    df_re.iloc[ridx,-1] = rec_val
    #else:
    #    isRecLess = True
#
    #if df_de.iloc[didx,-1] <= death_val:
    #    df_de.iloc[didx,-1] = death_val
    #else:
    #    isDeathLess = True


    df_co = replace_country_names(df_co, "Country/Region")
    df_re = replace_country_names(df_re, "Country/Region")
    df_de = replace_country_names(df_de, "Country/Region")


    ###############################
    # Update df_world with Change information 
    ###############################
    grp_df_world = df_world.groupby(['Country/Region'])[['Total Cases', 'Recovered', 'Deaths']].sum()

    grp_co = get_new_cases(df_co, "Total Cases", "New Cases")
    check_data_discrepancy(grp_df_world, grp_co, "Total Cases")
    
    grp_re = get_new_cases(df_re, "Recovered", "New Recovered")
    check_data_discrepancy(grp_df_world, grp_re, "Recovered")

    grp_de = get_new_cases(df_de, "Deaths", "New Deaths")
    check_data_discrepancy(grp_df_world, grp_de, "Deaths")

    df_new = grp_co.join([grp_re, grp_de])

    # As of now we are showing the change only for contry level 
    # and not at province level, maybe will do later starting with India 
    df_world["New Cases"] = 0
    df_world["New Recovered"] = 0
    df_world["New Deaths"] = 0
    for country in df_new.index:
        idx = df_world[df_world["Country/Region"] == country].index[0]
        df_world.loc[idx, "New Cases"] = df_new.loc[country, "New Cases"]
        df_world.loc[idx, "New Recovered"] = df_new.loc[country, "New Recovered"]
        df_world.loc[idx, "New Deaths"] = df_new.loc[country, "New Deaths"]

    df_world["New Cases"].clip(lower=0, inplace=True)
    df_world["New Recovered"].clip(lower=0, inplace=True)
    df_world["New Deaths"].clip(lower=0, inplace=True)
    df_world['Total Cases'].clip(lower=0, inplace=True)
        
    ###############################
    # save
    ###############################
    
    
    save(df_world, "world_latest")
    save(df_co, "confirmed_global")
    save(df_re, "recovered_global")
    save(df_de, "deaths_global")

    prepare_world_table(df_world)
    last_update()

    #prepare_daily_trend_data(df_co)


def prepare_world_table(df_world):
    GRPBY = ['Total Cases', "New Cases", 'Active', 'Recovered', "New Recovered", 'Deaths', "New Deaths"]
    RATE_COLS = ['Recovery rate', 'Death rate']
    MAIN_COLS = ['Total Cases', "New Cases", 'Active', 'Recovered', "New Recovered", 'Deaths', "New Deaths"]
    PRESENT_COLS = ['Country/Region'] + MAIN_COLS + RATE_COLS

    POP_COLS = ['Cases/M pop', 'Deaths/M pop', "Population"]
    PRESENT_COLS+=POP_COLS
    INT_COLS = MAIN_COLS + POP_COLS

    df = df_world.groupby('Country/Region')[GRPBY].sum()
    df.reset_index(inplace=True)

    pop = pd.read_csv(os.path.join("./data_sources", "pop_countries.csv"),encoding='latin-1')
    df = df.merge(pop[["Country", "Population"]], how="outer", left_on=["Country/Region"], right_on=["Country"])

    #save(df, "world_table")
    #return
    df['Cases/M pop']=0
    df['Deaths/M pop'] = 0
    for i in range(len(df)):
        if df.loc[i,"Population"]:
            df.loc[i,'Cases/M pop'] = (df.loc[i,'Total Cases']/df.loc[i,"Population"])*1000000
            df.loc[i,'Deaths/M pop'] = (df.loc[i,'Deaths']/df.loc[i,"Population"])*1000000

    #df['Cases/M pop'] = (df['Total Cases']/df["Population"])*1000000
    #df['Deaths/M pop'] = (df['Deaths']/df["Population"])*1000000
    df['Cases/M pop'].fillna(0, inplace=True)
    df['Deaths/M pop'].fillna(0, inplace=True)
    df['Cases/M pop'] = df['Cases/M pop'].astype(int)
    df['Deaths/M pop'] = df['Deaths/M pop'].astype(int)
    df['Population'].fillna(0, inplace=True)
    df['Population'] = df['Population'].astype(int)

    for c in INT_COLS:
        #print("Converting type for ", c)
        df[c].fillna(0, inplace=True)
        df[c] = df[c].astype(float)
        df[c] = df[c].astype(int)


    df["Recovery rate"] = df['Recovered']/df['Total Cases']
    df["Death rate"] = df['Deaths']/df['Total Cases']
    df.drop("Country", axis=1, inplace=True)

    df.dropna(inplace=True)

    df = df.sort_values(by=['Active', 'Total Cases'], ascending=False)
    save(df, "world_table")


def prepare_daily_trend_data(df_co):


    COLS = df_co.columns
    s = df_co[list(COLS[2:])].sum()
    daily = s.diff()
    daily.fillna(0,inplace=True)
    x_axis_dates = [d for d in pd.to_datetime(s.index)]
    print(type(daily))
    country="World"
    df_co_daily = pd.DataFrame(data=[daily, daily.rolling(window=3).mean(), daily.rolling(window=7).mean()] ,
    columns=[country, f"{country}_3day_moving_avg", f"{country}_7day_moving_avg"],
    #index=x_axis_dates
    )
    
    save(df_co_daily, "daily_confirmed", index=True)


def check_data_discrepancy(df_w, grp, col):
    simialr = (df_w[col] == grp[col])
    if(simialr.sum() != len(df_w)):
        print(f"*** Data discrepancy for {col}")
        print("df_world")
        print(df_w[~simialr.values])
        print("Timeline data")
        print(grp[~simialr.values])

def get_new_cases(df, latest_col, diff_col):
    COLS = df.columns
    grp = df.groupby("Country/Region")[list(COLS[-2:])].sum()
    grp[diff_col] = grp.diff(axis=1).iloc[:,-1].astype(int)
    grp.rename(columns={COLS[-1]:latest_col}, inplace = True)
    grp.drop(COLS[-2], axis=1, inplace=True)
    return grp

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    #parser.add_argument('--a', type=bool, default=True, help=f"Perform all steps")
    parser.add_argument('--d', type=bool, default=False, help=f"Download data from source")
    parser.add_argument('--p', type=bool, default=False, help=f"Process data")

    opt = parser.parse_args()

    print("##########################################################################")
    print("Do remember to 'git pull' at './data_sources/COVID-19' to pull world data")
    print("##########################################################################")

    if opt.d and INDIA_SPECIAL_PROCESS:        
        df_India = download_India_data()
    if opt.p:
        process_data()

    #if not DATA_PATH:
    #    folder, filename = os.path.split(DATA_PATH)
    #    DST = os.path.join("./data/", filename)
    #    shutil.copyfile(DATA_PATH, DST)
    #    print(DST)
