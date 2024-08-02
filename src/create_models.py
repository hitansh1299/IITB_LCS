from sklearn.linear_model import LinearRegression
import sqlite3
import pandas as pd
import pickle
if __name__ == '__main__':
    # df = pd.read_sql('SELECT * FROM cotimed_data', sqlite3.connect('Data/database.db'))
    df = pd.read_csv('cotimed_data.csv')
    LR_atmos = LinearRegression().fit(df['pm2.5_atmos'].values.reshape(-1,1), df['pm2.5_grimm'])
    LR_purpleair = LinearRegression().fit(df['pm2.5_purpleair'].values.reshape(-1,1), df['pm2.5_grimm'])
    LR_n3 = LinearRegression().fit(df['pm2.5_n3'].values.reshape(-1,1), df['pm2.5_grimm'])

    print(LR_atmos.coef_, LR_atmos.intercept_)
    print(LR_purpleair.coef_, LR_purpleair.intercept_)
    print(LR_n3.coef_, LR_n3.intercept_)

    #save all models as pickle files
    model_dir = 'src/models/'
    with open(model_dir+'LR_atmos.pkl', 'wb') as f:
        pickle.dump(LR_atmos, f)
    with open(model_dir+'LR_purpleair.pkl', 'wb') as f:
        pickle.dump(LR_purpleair, f)
    with open(model_dir+'LR_n3.pkl', 'wb') as f:
        pickle.dump(LR_n3, f)