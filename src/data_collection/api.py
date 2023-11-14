
import pandas as pd
import re
import os
from datetime import datetime, timedelta
import numpy as np
import json
from db_scripts import insert_df, get_table_data, get_pm_data, delete_by_filename

# def __get_pm_column_name__(sensor:str, pm:str):
#     if sensor == 'partector':
#         pass
#     elif sensor == 'grimm':
#         pass
#     elif 

def clean_reference(path:str, filename: str):
    filepath = os.path.join(path, filename)
    refs = pd.read_excel(filepath, sheet_name=None,
                       header=4, keep_default_na=True, parse_dates=['date & time'], date_format='%d-%m-%Y %H:%M:%S')
    
    #Count Values
    count_values = refs['Count values']
    count_values.rename(columns={'date & time':'timestamp'})
    d = dict(zip(count_values.columns[1:], list(map(lambda x:  ('count_')+re.sub('[\. ]', '_', x),count_values.columns[1:]))))
    print(d)
    d['date & time'] = 'timestamp'
    count_values.rename(columns=d, inplace=True)
    count_values['location'] = get_metadata(path, filename)['location']
    count_values['timestamp'].dt.month_name()

    #Mass Values
    mass_values = refs['Mass values']
    mass_values.rename(columns={'date & time':'timestamp'})
    d = dict(zip(mass_values.columns[1:], list(map(lambda x:  ('mass_')+re.sub('[\. ]', '_', x),mass_values.columns[1:]))))
    d['date & time'] = 'timestamp'
    mass_values.rename(columns=d, inplace=True)
    mass_values['location'] = get_metadata(path, filename)['location']
    # mass_values.to_csv(filepath.replace('.xlsx', '') + '_mass_values_clean.csv', index=False)

    #PM Values
    pm_values = refs['PM values']
    pm_values.rename(columns={'date & time':'timestamp',
                            'PM10 [ug/m3]':'pm10',
                            'PM2.5 [ug/m3]':'pm2_5',
                            'PM1 [ug/m3]':'pm1'}, inplace=True)
    pm_values['location'] = get_metadata(path, filename)['location']
    pm_values = pm_values['timestamp pm1 pm2_5 pm10 location'.split()]
    # pm_values.to_csv(filepath.replace('.xlsx', '') + '_pm_values_clean.csv', index=False)
    
    df = pd.merge(count_values, mass_values, on=['timestamp', 'location']).merge(pm_values, on=['timestamp', 'location'])
    df['filename'] = filepath.split('[/]')[-1]
    df[([*df.drop('location', axis=1).columns,'location'])].to_csv(filepath.replace('.xlsx', '') + '_clean.csv', index=False)
    insert_df(df, 'Grimm')


def clean_purple_air(filepath: str):
    lcs_cols = ['timestamp','current_temp_f','current_humidity','current_dewpoint_f','pressure','adc','pm1_0_cf_1','pm2_5_cf_1','pm10_0_cf_1',
                'pm1_0_atm','pm2_5_atm','pm10_0_atm','pm2_5_aqi_cf_1','pm2_5_aqi_atm','p_0_3_um','p_0_5_um','p_1_0_um','p_2_5_um','p_5_0_um','p_10_0_um','pm1_0_cf_1_b',
                'pm2_5_cf_1_b','pm10_0_cf_1_b','pm1_0_atm_b','pm2_5_atm_b','pm10_0_atm_b','pm2_5_aqi_cf_1_b','pm2_5_aqi_atm_b','p_0_3_um_b','p_0_5_um_b','p_1_0_um_b','p_2_5_um_b','p_5_0_um_b','p_10_0_um_b','location']

    if filepath.endswith('.csv'):
        lcs = pd.read_csv(filepath, header=0, parse_dates=['UTCDateTime'], index_col=False)
        print('read file')
    else:
        lcs = pd.read_excel(filepath, sheet_name=0, header=0,
                        keep_default_na=False, parse_dates=['UTCDateTime'])
    lcs.UTCDateTime = lcs.UTCDateTime.dt.tz_localize(
        'UTC').dt.tz_convert('Asia/Calcutta')
    lcs['location'] = filepath.split('/')[-1].split('_')[2]
    lcs.rename(columns={'UTCDateTime': 'timestamp',
                        'pm2.5_aqi_cf_1': 'pm2_5_aqi_cf_1',
                        'pm2.5_aqi_atm': 'pm2_5_aqi_atm',
                        'pm2.5_aqi_cf_1_b': 'pm2_5_aqi_cf_1_b',
                        'pm2.5_aqi_atm_b': 'pm2_5_aqi_atm_b',
                        'Location': 'location'}, inplace=True)
    lcs = lcs[lcs_cols]
    #remove all non numeric values
    numeric_cols = lcs.columns.drop(['timestamp','location'])
    lcs[numeric_cols] = lcs[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    lcs.timestamp = lcs.timestamp = lcs.timestamp.dt.tz_localize(None).dt.floor('min')
    lcs['filename'] = filepath.split('/')[-1]
    lcs.to_csv(filepath.replace('.xlsx', '') + '_clean.csv', index=False) 
    insert_df(lcs, 'PurpleAir')
    # print(lcs.columns)

def clean_n3(path:str, filename: str):
    # filepath = '../Data/CCD 25.10.2023/OPC2_010.CSV'
    df = pd.read_csv(os.path.join(path, filename), skiprows=[*range(0,14)])
    df['timestamp'] = np.nan
    df.at[0, 'timestamp'] = datetime.strptime(get_metadata(path, filename)['start'], '%Y-%m-%dT%H:%M')
    df.at[df.index.max(), 'timestamp'] = datetime.strptime(get_metadata(path, filename)['end'], '%Y-%m-%dT%H:%M')
    df['timestamp'] = df['timestamp'].astype(dtype='datetime64[ms]').interpolate(method='linear')
    df.insert(0, 'timestamp', df.pop('timestamp'))
    df['filename'] = filename
    df.rename(columns=dict(zip(df.columns.tolist(), [re.sub("[\(\[].*?[\)\]]", "", x) for x in df.columns.tolist()])), inplace=True)
    df.rename(columns=dict(zip(df.columns.tolist(), [re.sub("#", "", x) for x in df.columns.tolist()])), inplace=True)
    # df.drop('LaserStatus')
    df.to_csv(os.path.join(path, filename).replace('.csv', '') + '_clean.csv', index=False)
    insert_df(df, 'N3')

def clean_partector(path: str, filename: str):
    filepath = os.path.join(path, filename)
    df = pd.read_csv(filepath, sep='\t', skiprows=[*range(19)])
    start = datetime.strptime(get_metadata(path, filename)['start'], '%Y-%m-%dT%H:%M')
    df['time'] = start + pd.to_timedelta(df['time'], unit='second')
    df.rename({'time':'timestamp'}, axis=1, inplace=True)
    df['location']  = get_metadata(path,filename)['location']
    df['filename'] = filename
    df.to_csv(os.path.join(path, filename).replace('.txt', '') + '_clean.csv', index=False)
    insert_df(df, 'Partector')

def clean_atmos(path: str, filename:str):
    filepath = os.path.join(path, filename)
    df = pd.read_csv(filepath,parse_dates=True, date_format='%m/%d/%YT%H:%M:%S')
    df = df[df.Time != '85/165/20165T25:165:00']
    df['Time'] = pd.to_datetime(df['Time'])
    start = datetime.strptime(get_metadata(path, filename)['start'], '%Y-%m-%dT%H:%M')
    end = datetime.strptime(get_metadata(path, filename)['end'], '%Y-%m-%dT%H:%M')
    df = df[(df['Time'] >= start) & (df['Time'] <= end)]
    df['location'] = get_metadata(path,filename)['location']
    df['filename'] = filename
    df.rename(columns={'Time':'timestamp'}, inplace=True)
    df.to_csv(os.path.join(path, filename).replace('.csv', '') + '_clean.csv', index=False)
    insert_df(df, 'Atmos')

def get_data(table):
    import json
    df = get_table_data(table)
    # df = df[['timestamp',*df.drop(columns=['timestamp','filename','location']).columns,'location','filename']]
    d = df.to_dict(orient='records')
    return d

def delete_file(file):
    delete_by_filename(file)
    

'''
@params:
start and end must be strings of type YYYY-MM-DD HH:mm:ss
'''
def __get_charting_data__(sensors: str, start: str, end: str):
    if not start: start = '2020-01-01'
    if not end: end = '2100-01-01'
    column = 'pm2_5'
    start = start.replace('T',' ')
    end = end.replace('T',' ')
    d = {}
    d['PM2.5'] = get_pm_data('Grimm', column, start=start, end=end).to_dict(orient='list')[column]
    return d



def get_metadata(path:str, filename: str):
    with open(os.path.join(path, 'log.json'), 'r') as f:
        metadata = json.load(f)
    return metadata[filename]

def process_file(path:str, filename: str):
    filepath = os.path.join(path, filename)
    if "purple_air" in filename:
        clean_purple_air(filepath=filepath)
    elif "reference" in filename:
        clean_reference(path = path, filename=filename)
    elif "n3" in filename:
        clean_n3(path=path, filename=filename)
    elif 'partector' in filename:
        clean_partector(path=path, filename=filename)
    elif 'atmos' in filename:
        clean_atmos(path=path, filename=filename)
    
