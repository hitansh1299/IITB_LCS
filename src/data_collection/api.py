import pandas as pd
import re
import os
from datetime import datetime, timedelta
import numpy as np
import json
from db_scripts import insert_df, get_table_data, get_pm_data, delete_by_filename, insert_live_data, get_latest_datapoints
import config
import threading

def __process_grimm__(df):
    df['pm2.5'] = df['pm2_5']
    df = df[['timestamp', 'pm2.5', 'pm1', 'pm10', 'filename', 'location']]
    insert_df(df, 'clean_grimm')

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
    df['filename'] = filepath.split('/')[-1]
    df[([*df.drop('location', axis=1).columns,'location'])].to_csv(filepath.replace('.xlsx', '') + '_clean.csv', index=False)
    insert_df(df, 'Grimm')
    threading.Thread(target=__process_grimm__, args=(df,)).start()

def __process_purpleair__(df):
    df['pm2.5'] = (df['pm2_5_cf_1'] + df['pm2_5_cf_1_b'])/2
    df['pm1'] = (df['pm1_0_cf_1'] + df['pm1_0_cf_1_b'])/2
    df['pm10'] = (df['pm10_0_cf_1'] + df['pm10_0_cf_1_b'])/2
    df = df[['timestamp', 'pm2.5', 'pm1', 'pm10', 'filename', 'location']]
    insert_df(df, 'clean_purpleair')

def clean_purple_air(path:str, filename:str):
    filepath = os.path.join(path, filename)
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
    lcs.timestamp = lcs.timestamp = lcs.timestamp.dt.tz_localize(None).dt.round('S')
    lcs['filename'] = filename
    lcs['location'] = get_metadata(path,filename)['location']
    filename = filepath.replace('.xlsx', '') 
    filename = filename.replace('.csv', '') + '_clean.csv'
    lcs.to_csv(filename, index=False) 
    insert_df(lcs, 'PurpleAir')
    threading.Thread(target=__process_purpleair__, args=(lcs,)).start() 
    # print(lcs.columns)

def __process_n3__(df: pd.DataFrame):
    filename, location = df['filename'][0], df['location'][0]
    df.drop(columns=['filename','location'], inplace=True)
    df['pm2.5'] = df['PM_2.500']
    df['pm1'] = df['PM_1.000']
    df['pm10'] = df['PM_10.000']
    df = df[['timestamp', 'pm2.5', 'pm1', 'pm10']]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df = df.resample('2T').mean()
    df.reset_index(inplace=True)
    df['filename'] = filename
    df['location'] = location
    print(df)
    insert_df(df, 'clean_n3')

def clean_n3(path:str, filename: str):
    # filepath = '../Data/CCD 25.10.2023/OPC2_010.CSV'
    df = pd.read_csv(os.path.join(path, filename), skiprows=[*range(0,14)])
    df['timestamp'] = np.nan
    df.at[0, 'timestamp'] = datetime.strptime(get_metadata(path, filename)['start'], '%Y-%m-%dT%H:%M')
    df.at[df.index.max(), 'timestamp'] = datetime.strptime(get_metadata(path, filename)['end'], '%Y-%m-%dT%H:%M')
    df['timestamp'] = df['timestamp'].astype(dtype='datetime64[ms]').interpolate(method='linear')
    df['timestamp'] = df['timestamp'].dt.round('S')
    df.insert(0, 'timestamp', df.pop('timestamp'))
    df['filename'] = filename
    df['location']  = get_metadata(path,filename)['location']
    df.rename(columns=dict(zip(df.columns.tolist(), [re.sub("[\(\[].*?[\)\]]", "", x) for x in df.columns.tolist()])), inplace=True)
    df.rename(columns=dict(zip(df.columns.tolist(), [re.sub("#", "", x) for x in df.columns.tolist()])), inplace=True)
    # df.drop('LaserStatus')
    df.to_csv(os.path.join(path, filename).replace('.csv', '') + '_clean.csv', index=False)
    insert_df(df, 'N3')
    threading.Thread(target=__process_n3__, args=(df,)).start()
    
    # print(df['PM_2.500'])

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

def __process_atmos__(df):
    #Using the ALT method (the same one in PurpleAir) to figure out PM values
    #https://sci-hub.se/https://doi.org/10.1016/j.atmosenv.2021.118432
    #Coeffs: 0.00030418	0.0018512	0.02069706	0.023140015	0.185120122
    filename, location = df['filename'][0], df['location'][0]
    df['pm2.5'] = df['PM_1_CNC']
    df['pm1'] = df['PM_2.5_CNC']
    df['pm10'] = df['PM_10_CNC']
    df = df[['timestamp', 'pm2.5', 'pm1', 'pm10']]
    df = df.groupby('timestamp')[['pm2.5', 'pm1', 'pm10']].mean().reset_index()
    df['filename'] = filename
    df['location'] = location
    print('Cleaned DF')
    print(df)
    insert_df(df, 'clean_atmos')


def clean_atmos(path: str, filename:str):
    filepath = os.path.join(path, filename)
    df = pd.read_csv(filepath,parse_dates=True, date_format='%m/%d/%YT%H:%M:%S')
    df = df[df.Time != '85/165/20165T25:165:00']
    df['Time'] = pd.to_datetime(df['Time'])
    try:
        start = datetime.strptime(get_metadata(path, filename)['start'], '%Y-%m-%dT%H:%M')
    except ValueError as e:
        start = datetime.strptime('2020-01-01T00:00', '%Y-%m-%dT%H:%M')
    
    try:
        end = datetime.strptime(get_metadata(path, filename)['end'], '%Y-%m-%dT%H:%M')
    except ValueError as e:
        end = datetime.strptime('2030-01-01T00:00', '%Y-%m-%dT%H:%M')
    df = df[(df['Time'] >= start) & (df['Time'] <= end)]
    df['location'] = get_metadata(path,filename)['location']
    df['filename'] = filename
    df.rename(columns={'Time':'timestamp'}, inplace=True)
    df.to_csv(os.path.join(path, filename).replace('.csv', '') + '_clean.csv', index=False)
    insert_df(df, 'Atmos')
    threading.Thread(target=__process_atmos__, args=(df,)).start()

def get_data(table, raw):
    if raw != 'raw':
        sensor_tables = {
            'PurpleAir':'clean_purpleair',
            'N3':'clean_n3',
            'Grimm':'clean_grimm',
            'Partector':'Partector',
            'Atmos':'clean_atmos'
        }

        table = sensor_tables[table]
    df = get_table_data(table)
    d = df.to_dict(orient='records')
    return d

def delete_file(file):
    if get_metadata(config.UPLOAD_FOLDER, file):
        delete_by_filename(file)
    os.remove(os.path.join(config.UPLOAD_FOLDER, file))
    try:
        os.remove(os.path.join(config.UPLOAD_FOLDER, file.replace('.'+file.split('.')[-1], '_clean.csv')))
    except FileNotFoundError as e:
        pass
    
    

'''
@params:
start and end must be strings of type YYYY-MM-DD HH:mm:ss
'''
def __get_sensor_charting_data__(sensor: str, start: str, end: str, pm:list):
    print('Getting charting data for', sensor, start, end, pm)
    columns = {
        'PurpleAir':{'pm2.5':'p_2_5_um', 'pm1':'p_1_0_um', 'pm10':'p_10_0_um'},
        'N3':'"PM_2.500"',
        'Grimm':'pm2_5',
        'Atmos':'PM_2.5_CNC',
    }
    if sensor.startswith('clean'):
        column = pm
    else:
        column = columns[sensor]
    df = get_pm_data(sensor, column, start=start, end=end)
    #remove single quotes and capitalize the column names except timestamp
    df.rename(columns={x: x.replace('"', "").upper() for x in df.columns if x != 'timestamp'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    time_diff = df['timestamp'].diff()
    split_indices = (abs(time_diff) > pd.Timedelta(minutes=10)) 
    split_indices = split_indices.loc[split_indices == True]
    df['timestamp'] = df.timestamp.dt.strftime('%Y-%m-%d %H:%M:%S')
    split_dataframes = [df.iloc[i:j] for i, j in zip([0] + split_indices.index.tolist(), split_indices.index.tolist() + [None])]
    return [df.to_dict(orient='list') for df in split_dataframes]


def __get_charting_data__(sensors: list, start: str, end: str, pm:list):
    sensor_tables = {
        'PurpleAir':'clean_purpleair',
        'N3':'clean_n3',
        'Grimm':'clean_grimm',
        'Partector':'Partector',
        'Atmos':'clean_atmos'
    }
    if not start: start = '2020-01-01'
    if not end: end = '2100-01-01'
    start = start.replace('T',' ')
    end = end.replace('T',' ')
    if not sensors:
        return {}
    d = {}
    for sensor in sensors:
        sensor = sensor_tables[sensor]
        d[sensor] = __get_sensor_charting_data__(sensor, start=start, end=end, pm=pm)
    return d

def get_coefficients(df: pd.DataFrame):
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    sensors = ['grimm', 'purpleair', 'n3', 'atmos']
    params = {}
    for sensor in sensors:
        lr = LinearRegression()
        score = r2_score(df['pm2.5_grimm'], df['pm2.5_'+sensor])
        lr.fit(df['pm2.5_grimm'].values.reshape(-1,1),df['pm2.5_'+sensor].values.reshape(-1,1))
        cf = float(lr.coef_[0][0])
        ic = float(lr.intercept_[0])
        ref_mn, ref_mx = float(df['pm2.5_grimm'].min()), float(df['pm2.5_grimm'].max())
        params[sensor] = {'coeff':cf, 'intercept':ic, 'x':[ref_mn, ref_mx], 'y':[ref_mn*cf+ic,ref_mx*cf+ic], 'r2_score':score}
    print(params)
    return params
    
def get_regression_data():
    PLOT_REGRESSION_FOR_ROWS = 100
    df = get_latest_datapoints('cotimed_data', rows=PLOT_REGRESSION_FOR_ROWS)
    params = get_coefficients(df)
    d = df.to_dict(orient='list')
    d['params'] = params
    return d

def get_metadata(path:str, filename: str):
    with open(os.path.join(path, 'log.json'), 'r') as f:
        metadata = json.load(f)
    return metadata.get(filename, {})

def process_file(path:str, filename: str):
    if "purple_air" in filename:
        clean_purple_air(path = path, filename=filename)
    elif "reference" in filename:
        clean_reference(path = path, filename=filename)
    elif "n3" in filename:
        clean_n3(path=path, filename=filename)
    elif 'partector' in filename:
        clean_partector(path=path, filename=filename)
    elif 'atmos' in filename:
        clean_atmos(path=path, filename=filename)

def process_live_input(sensor, data): 
    if sensor == 'N3':
        insert_live_data('live_n3', data['timestamp'], data['pm1'], data['pm2.5'], data['pm10'], data['temperature'], data['humidity'], data['location'])
    if sensor == 'PurpleAir':
        print(data)
        # insert_live_data('live_purpleair', data['timestamp'], data['pm2.5'], data['pm1'], data['pm10'], data['location'])






def get_live_data(sensor):
    df = {}
    if sensor == 'N3':
        table = 'live_n3'
        df = get_latest_datapoints(table).tail(1).to_dict(orient='records')[0]
    if sensor == 'Atmos':
        table = 'live_atmos'
        df = get_latest_datapoints(table).tail(1).to_dict(orient='records')[0]
    if sensor == 'Grimm':
        table = 'clean_grimm'
        df = get_latest_datapoints(table).tail(1).to_dict(orient='records')[0]
    return df




