import pandas as pd
import requests
from db_scripts import insert_live_data, get_table_data, insert_df
from datetime import datetime, timedelta

def fetch_atmos_data():
    from config import ATMOS_IMEI, ATMOS_API_KEY
    import requests
    import pandas as pd
    from io import StringIO
    import pytz
    import time
    retries = 0
    last_update = {'dt_time': 'NULL'}
    while True:
        imei_id = ATMOS_IMEI
        IST = pytz.timezone('Asia/Kolkata')
        enddate = datetime.now(IST).strftime('%Y-%m-%dT%H:%M:%S')
        startdate = (datetime.now(IST) - timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%S')
        print("FETCHING ATMOS DATA")

        # print(startdate, enddate)

        avg_ref = 'mm'
        avg_period = '1'
        api_key = ATMOS_API_KEY

        url = f"https://atmos.urbansciences.in/adp/v4/getDeviceDataParam/imei/{imei_id}/params/pm1cnc,pm2.5cnc,pm10cnc,temp,humidity,lat,lon/startdate/{startdate}/enddate/{enddate}/ts/{avg_ref}/avg/{avg_period}/api/{api_key}?gaps=1"
        # print(url)
        res = requests.get(url)
        # print(res.text)
        records = pd.read_csv(StringIO(res.text)).sort_values(by='dt_time', ascending=False).fillna(value='NULL').to_dict(orient='records')
        # print(records)
        
        latest_update = None
        for i in records:
            if i['pm1cnc'] == 'NULL' and i['pm2.5cnc'] == 'NULL' and i['pm10cnc'] == 'NULL':
                continue
            else:
                latest_update = i.copy()
                break
        else:
            retries += 1
            if retries <= 5:
                print('NO ATMOS DATA FOR: ',enddate, 'RETYING AFTER 5 SECONDS...')
                time.sleep(5)
                continue
            print('NO ATMOS DATA FOR: ',enddate, 'RETRYING LIMIT REACHED | PLEASE CHECK SENSOR')
            time.sleep(60)
            continue


        # print('LATEST UPDATE', latest_update)
        retries = 0
        if latest_update['dt_time'] != last_update['dt_time']:
            last_update = latest_update
            insert_live_data('live_atmos', latest_update['dt_time'], latest_update['pm1cnc'], latest_update['pm2.5cnc'], latest_update['pm10cnc'], latest_update['temp'], latest_update['humidity'], f"{{'lat':{latest_update['lat']}, 'lon':{latest_update['lon']}}}")
            time.sleep(60)
        else :
            print('NO NEW DATA | RETRYING AFTER 30 SECONDS...')
            time.sleep(30)


def update_cotimed_data() -> None:
    last_update = {'dt_time': 'NULL'} #TODO: Fetch last update from db
    start = '2000-01-01 00:00:00'
    end = '2099-01-01 00:00:00'
    purpleair = get_table_data('clean_purpleair', start=start, end=end).sort_values(by='timestamp')
    purpleair['timestamp'] = pd.to_datetime(purpleair['timestamp'])
    purpleair.rename(columns={'pm2.5': 'pm2.5_purpleair', 'pm10': 'pm10_purpleair', 'pm1': 'pm1_purpleair', 'location':'location_purpleair', 'filename':'filename_purpleair'}, inplace=True)
    
    n3 = get_table_data('clean_n3', start=start, end=end).sort_values(by='timestamp')
    n3['timestamp'] = pd.to_datetime(n3['timestamp'])
    n3.rename(columns={'pm2.5': 'pm2.5_n3', 'pm10': 'pm10_n3', 'pm1': 'pm1_n3', 'location':'location_n3', 'filename':'filename_n3'}, inplace=True)
    
    grimm = get_table_data('clean_grimm', start=start, end=end).sort_values(by='timestamp')
    grimm['timestamp'] = pd.to_datetime(grimm['timestamp'])
    grimm.rename(columns={'pm2.5': 'pm2.5_grimm', 'pm10': 'pm10_grimm', 'pm1': 'pm1_grimm', 'location':'location_grimm', 'filename':'filename_grimm'}, inplace=True)

    atmos = get_table_data('clean_atmos', start=start, end=end).sort_values(by='timestamp')
    atmos['timestamp'] = pd.to_datetime(atmos['timestamp'])
    atmos.rename(columns={'pm2.5': 'pm2.5_atmos', 'pm10': 'pm10_atmos', 'pm1': 'pm1_atmos', 'location':'location_atmos', 'filename':'filename_atmos'}, inplace=True)

    cotimed_data = pd.merge_asof(grimm, n3, 
                                 on='timestamp', 
                                 direction='nearest', 
                                 tolerance=pd.Timedelta('3m')).dropna(subset=['pm2.5_grimm', 'pm2.5_n3', 'pm10_grimm', 'pm10_n3', 'pm1_grimm', 'pm1_n3'])
    cotimed_data = pd.merge_asof(cotimed_data, purpleair, 
                                 on='timestamp', 
                                 direction='nearest', 
                                 tolerance=pd.Timedelta('3m')).dropna(subset=['pm2.5_purpleair', 'pm10_purpleair', 'pm1_purpleair'])
    cotimed_data = pd.merge_asof(cotimed_data, atmos, 
                                on='timestamp', 
                                direction='nearest', 
                                tolerance=pd.Timedelta('3m')).dropna(subset=['pm2.5_atmos', 'pm10_atmos', 'pm1_atmos'])
    print(cotimed_data)
    cotimed_data.to_csv('cotimed_data.csv', index=False)
    insert_df(cotimed_data, 'cotimed_data')
if __name__ == '__main__':
    # fetch_atmos_data()
    update_cotimed_data()