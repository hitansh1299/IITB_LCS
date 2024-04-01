import pandas as pd
import requests
from db_scripts import insert_live_data
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
