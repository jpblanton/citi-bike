import os

import pandas as pd
import psycopg2

from get_station_neighborhoods import get_station_neighborhoods


# this script will populate the database
# .sql script should be run first to build db


def get_station_capacity(stat):
    return (stat['num_ebikes_available']
            + stat['num_docks_disabled']
            + stat['num_bikes_available']
            + stat['num_bikes_disabled']
            + stat['num_docks_available'])


if not os.path.exists('stations-with-hoods.csv'):
    print('creating CSV files')
    get_station_neighborhoods()

station_locations = pd.read_csv('stations-with-hoods.csv')
station_ids = set(station_locations['station_id'])
manhattan_stations = station_locations[station_locations['borough'] == 'Manhattan']
manhattan_ids = set(manhattan_stations['station_id'])
# when I was building capacity from the station_status JSON instead of information
# status_url = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'
# 
# with urllib.request.urlopen(status_url) as url:
#     stations = json.loads(url.read().decode())['data']['stations']
# 
# capacities = [(s['station_id'], s['capacity']) for s in stations]
# manhattan = [s for s in capacities if int(s[0]) in manhattan_ids]
# capacity_df = pd.DataFrame.from_records(capacities, columns=['station_id', 'station_cap'])
# names = pd.read_csv('station_names.csv')
# names_and_caps = names.join(capacity_df, on='station_id', rsuffix='_', how='outer')
# try:
#     names_and_caps = names_and_caps.drop('station_id_', axis=1)
# except KeyError:
#     pass
# try:
#     names_and_caps = names_and_caps.drop('station_cap_', axis=1)
# except KeyError:
#     pass
# names_and_caps.fillna(-1, inplace=True)
# names_and_caps.to_csv('station_names.csv', index=False)

conn = psycopg2.connect('postgres://postgres@localhost/nyc_data')

with conn.cursor() as cur:
    with open('neighborhoods.csv', 'r') as f:
        next(f)
        cur.copy_from(f, 'boroughs', sep=',')
    with open('station_names.csv', 'r') as f:
        next(f)
        cur.copy_from(f, 'names', sep=',')
    with open('locations.csv', 'r') as f:
        next(f)
        cur.copy_from(f, 'location', sep=',')
conn.commit()
