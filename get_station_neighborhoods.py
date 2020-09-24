import json
import urllib.request

import shapefile
import pandas as pd
from shapely.geometry import Point
from shapely.geometry import Polygon

base_path = 'shapefiles/geo_export_f75953cc-50cc-4d35-b1e6-3c4d99398fdd'
station_url = 'https://gbfs.citibikenyc.com/gbfs/en/station_information.json'


def get_station_capacity(stat):
    return (stat['num_ebikes_available']
            + stat['num_docks_disabled']
            + stat['num_bikes_available']
            + stat['num_bikes_disabled']
            + stat['num_docks_available'])


def get_station_neighborhoods(station_url=station_url, base_path=base_path, to_file=True):
    sf = shapefile.Reader(base_path)
    polys = (Polygon(s.points) for s in sf.shapes())
    poly_names = list(zip(((r.ntaname, r.boro_name) for r in sf.records()), polys))

    with urllib.request.urlopen(station_url) as url:
        stations = json.loads(url.read().decode())['data']['stations']

    # redo this section - compress whole list into df
    # then create column of Point objects
    # df.Point.apply for in test

    station_pts = ((s['name'], s['station_id'], Point((s['lon'], s['lat'])), s['capacity']) for s in stations)

    stations_with_hoods = []
    for station in station_pts:
        for poly in poly_names:
            if station[2].within(poly[1]):
                x, y = station[2].xy
                # station_name, _id, hood & boro, x, y
                stations_with_hoods.append((station[0], station[1], poly[0], x[0], y[0], station[3]))
                # print('{} in {}'.format(station[0], poly[0]))
                break
    cols = ['station_name', 'station_id', 'neighborhood', 'borough', 'longitude', 'latitude', 'capacity']
    df = pd.DataFrame.from_records(((x, y, *z, w, u, v) for x, y, z, w, u, v in stations_with_hoods), columns=cols)
    df.to_csv('stations-with-hoods.csv', index=False)

    # CSVs to import to DB
    if to_file:
        df[['neighborhood', 'borough']].to_csv('neighborhoods.csv', index=False)
        df[[ 'station_id', 'station_name']].to_csv('station_names.csv', index=False)
        df[['station_id', 'neighborhood', 'longitude', 'latitude']].to_csv('locations.csv', index=False)
