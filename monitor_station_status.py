import re
import json
import urllib.request
import datetime

import psycopg2
import pandas as pd


def unix_to_ts(time):
    return datetime.datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')


def json_to_df(jdct):
    upd_time = unix_to_ts(jdct['last_updated'])
    actives = [s for s in jdct['data']['stations'] if s['station_status'] == 'active']
    values = ['station_id', 'station_status', 'num_bikes_available',
              'num_ebikes_available', 'num_bikes_disabled',
              'num_docks_available', 'num_docks_disabled']
    df_list = []
    for station in actives:
        cur = [upd_time]
        for v in values:
            cur.append(station.get(v, None))
        df_list.append(tuple(cur))
    cols = ['time'] + [re.sub('num_', '', v) for v in values]
    return pd.DataFrame.from_records(df_list, columns=cols)


def get_station_capacity(stat):
    return (stat['num_ebikes_available']
            + stat['num_docks_disabled']
            + stat['num_bikes_available']
            + stat['num_bikes_disabled']
            + stat['num_docks_available'])


station_locations = pd.read_csv('stations-with-hoods.csv')
manhattan_stations = station_locations[station_locations['borough'] == 'Manhattan']
manhattan_ids = set(manhattan_stations['station_id'])

status_url = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'

with urllib.request.urlopen(status_url) as url:
    stations = json.loads(url.read().decode())

x = json_to_df(stations)

actives = [s for s in stations['data']['stations'] if s['station_status'] == 'active']
capacities = [(s['station_id'], get_station_capacity(s)) for s in actives]
manhattan = [s for s in capacities if int(s[0]) in manhattan_ids]
# want to store total capacity for long term
# some kind of time stamped db for how many bikes there are

# timescale DB to store station status info
# store time retrieved, the get_station_capacity factors
# separate metadata table indexed on station ID & having lat/lon boro/hood
# metadata table does not need to be a hypertable
# look into grafana for visualizing instead of plotly

# create DB to store using timescaleDB
# connect w/ conn = psycopg2.connect(database="tutorial", user="postgres", host="127.0.0.1")
# will obviously need to create non-root user for this eventually

fn = 'backup/status_{}.csv'.format(stations['last_updated'])
x['time'] = pd.to_datetime(x['time'])
x.to_csv(fn, index=False)
conn = psycopg2.connect('postgres://postgres@localhost/nyc_data')
with conn.cursor() as cur:
    with open(fn, 'r') as f:
        next(f)
        cur.copy_from(f, 'status', sep=',')
conn.commit()
