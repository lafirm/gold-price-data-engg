import requests
import pandas as pd
from datetime import datetime
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')

def extract_goldrate_data() -> pd.DataFrame:
    goldrate_url = 'https://www.goodreturns.in/gold-rates/'
    response = requests.get(goldrate_url)
    dfs = pd.read_html(response.text, header=0)
    dfs[2].insert(loc=0, column='Country', value='India')
    return pd.concat([dfs[2], dfs[3]])


def extract_inr_conv_rate() -> pd.DataFrame:
    inr_conv_url = 'https://www.x-rates.com/table/?from=INR&amount=1'
    response = requests.get(inr_conv_url)
    dfs = pd.read_html(response.text)
    return dfs[1]


def transform(goldrate_raw: pd.DataFrame, inr_data_raw: pd.DataFrame) -> pd.DataFrame:
    req_cities = ['Chennai', 'Mumbai', 'Kerala']
    req_countries = ['Singapore', 'Malaysia', 'Qatar', 'Saudi Arabia', 'United Arab Emirates', 'United States']
    goldrate_df_mid = goldrate_raw[goldrate_raw.City.isin(req_cities) | goldrate_raw.Country.isin(req_countries)]
    goldrate_df_mid.columns = [col.lower().replace(' ', '_') for col in goldrate_df_mid.columns]
    goldrate_df_mid.loc[:, '22k_today'] = goldrate_df_mid.loc[:, '22k_today'].str.replace('₹ ', 'INR')
    goldrate_df_mid.loc[:, '24k_today'] = goldrate_df_mid.loc[:, '24k_today'].str.replace('₹ ', 'INR')
    goldrate_df_mid.insert(loc=0, column='timestamp', value=datetime.now(tz=ist_tz))
    countries_curr_dict = {'India': 'INR', 'Singapore': 'SGD',
                           'Malaysia': 'MYR', 'Qatar': 'QAR',
                           'Saudi Arabia': 'SAR', 'United Arab Emirates': 'AED',
                           'United States': 'USD'}
    goldrate_df_final = goldrate_df_mid.copy()
    goldrate_df_final['currency'] = goldrate_df_final['country'].map(countries_curr_dict)

    inr_data_raw.columns = ['currency_fullname', 'inr_to', 'to_inr_rate']
    inr_data_raw.loc[len(inr_data_raw.index)] = ['Indian Rupee', 1.0, 1.0]

    curr_abbr_dict = {'Indian Rupee': 'INR', 'Singapore Dollar': 'SGD',
                      'Malaysian Ringgit': 'MYR', 'Qatari Riyal': 'QAR',
                      'Saudi Arabian Riyal': 'SAR', 'Emirati Dirham': 'AED',
                      'US Dollar': 'USD'}

    inr_data_raw['currency'] = inr_data_raw['currency_fullname'].map(curr_abbr_dict)
    inr_data_raw.dropna(inplace=True)
    merged_df = pd.merge(goldrate_df_final, inr_data_raw[['currency', 'to_inr_rate']], on='currency', how='left')

    conv_to_inr = lambda x, col: round((float(x[col][3:].replace(',', '')) * float(x['to_inr_rate'])) / 10, 2)
    merged_df['22k_inr_per_gram'] = merged_df.apply(conv_to_inr, col='22k_today', axis=1)
    merged_df['24k_inr_per_gram'] = merged_df.apply(conv_to_inr, col='24k_today', axis=1)

    req_cols = ['timestamp', 'country', 'city', 'to_inr_rate', '22k_inr_per_gram', '24k_inr_per_gram']

    return merged_df[req_cols]


def load(df: pd.DataFrame) -> None:
    print(df.loc[0])
    return None

if __name__ == '__main__':
    transformed_data = transform(goldrate_raw=extract_goldrate_data(), inr_data_raw=extract_inr_conv_rate())
    load(transformed_data)
