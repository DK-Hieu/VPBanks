'''
Code theo OOP dánh cho nhiều server > 1 proc 
'''

import dask.dataframe as dd
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import time
import json
import ast
from tqdm.auto import tqdm
import requests
import warnings
warnings.filterwarnings('ignore') # turn off warnings

import redshift_connector

# proc = coreproc(
#                     host= 'prod-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
#                     database= 'vpbanks_dwh'
#                )

# krx = coreproc(
#                     host= 'prod-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
#                     database= 'vpbanks_dwh_krx'
#               )

class coreconn:
    from tqdm.auto import tqdm

    # conn = redshift_connector.connect(
    #         host='prod-redshift-cluster.cuxeoz0lhusr.ap-southeast-1.redshift.amazonaws.com',
    #         database='vpbanks_dwh',
    #         port=5439,
    #         user='hieudd',
    #         password='Ani#2024'
    #     )
    # cursor = conn.cursor()
    
    def __init__(self, host, database,user,password):
        self.conn = redshift_connector.connect(
            host=host,
            database=database,
            port=5439,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
    
    
    
    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("Disconnected from database.")
        except Exception as e:
            print(f"Lỗi khi đóng kết nối: {e}")    
        
    def selectdf(self,query):
        df = pd.read_sql(query, self.conn)
        df = df.replace([None],[np.nan])
        return df
    
    def truncate_table(self,sql_table_name):
        sql_query = f'truncate table {sql_table_name}'
        self.cursor.execute(sql_query)
        self.conn.commit()        
    
    def sql_insert_py(self,sql_table_name,python_table,inplace):
        
        python_table.replace([np.nan], [None],inplace=True)
        
        if inplace == True:
            self.truncate_table(sql_table_name)
        else:
            pass
                
        sql = f"INSERT INTO {sql_table_name} VALUES ({','.join(['%s'] * len(python_table.columns))})"

        data = [tuple(row) for _, row in tqdm(python_table.iterrows(), total=len(python_table), desc="Preparing data")]

        # Chèn dữ liệu với xử lý lỗi
        for row in tqdm(data, total=len(data), desc="Inserting rows"):
            try:
                self.cursor.execute(sql, row)
            except Exception as e:
                print(f"Lỗi khi chèn dòng {row}: {e}")
                self.conn.rollback()  # Hủy giao dịch khi có lỗi, tránh PostgreSQL khóa transaction

        # Sau khi xong thì commit lại
        self.conn.commit()
        self.disconnect()
        print("PUSH DATA: DONE")