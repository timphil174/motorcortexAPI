from motorcortex_tools import datalogger
import numpy as np
import pandas as pd
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS
import json
from sqlalchemy import create_engine
import time


def get_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config


def main():
    # configuration to fill in
    config = get_config()
    #   we setting up different API connections
    #   MySQL
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                           .format(host=config['mysqlconfig']['host'], db=config['mysqlconfig']['database'],
                                   user=config['mysqlconfig']['user'], pw=config['mysqlconfig']['password'])
                           )

    #   InfluxDB
    client = InfluxDBClient(url=config['InfluxAPI']['url'], token=config['InfluxAPI']['token'],
                            org=config['InfluxAPI']['org'])
    write_api = client.write_api(write_options=ASYNCHRONOUS)

    #   Motorcortex
    params = config['motorcortexAPI']['parameters']
    nbr_param = len(params)
    logger = datalogger.DataLogger(config['motorcortexAPI']['url'], config['motorcortexAPI']['parameters'],
                                   divider=config['motorcortexAPI']['divider'])
    logger.start()  # data_subscription starts
    batch_size = config['batch_size']
    seconds = 0
    while True:
        if len(logger.traces[params[0]]["t"]) >= batch_size:   # batch is full so ready to be sent to DB
            values = {}
            t = np.array(logger.traces[params[0]]["t"][:batch_size])
            for i in range(nbr_param):
                values['{}'.format(params[i])] = np.array(logger.traces[params[i]]["y"][0][:batch_size])
            df = pd.DataFrame(values, index=t)

            #   write to MySQL and InfluxDB
            df.to_sql(config['mysqlconfig']['table_name'], engine, if_exists='append', index=True, index_label="time")
            write_api.write(bucket=config['InfluxAPI']['bucket'], record=df, data_frame_measurement_name='root')

            #   release of memory
            for a in range(nbr_param):
                del logger.traces[params[a]]["y"][0][:batch_size]
                del logger.traces[params[a]]["t"][:batch_size]
            seconds += 1
            print('seconds wrote:', 10*seconds)


main()
# client.close()
# logger.close()
