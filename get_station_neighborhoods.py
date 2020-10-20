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


def find_poly(pt, lst):
    # output = []
    # for pt in pts:
    for poly in lst:
        if pt.within(poly[1]):
            return poly[0]
            # output.append(poly[0])
            #     break
    # return pd.DataFrame.from_records(output)


def series_point(X, Y):
    assert(len(X) == len(Y))
    return pd.Series((Point(x,y) for x, y in zip(X, Y)))


def get_station_neighborhoods(station_url=station_url, base_path=base_path, to_file=True):
    sf = shapefile.Reader(base_path)
    polys = (Polygon(s.points) for s in sf.shapes())
    poly_names = list(zip(((r.ntaname, r.boro_name) for r in sf.records()), polys))

    with urllib.request.urlopen(station_url) as url:
        stations = json.loads(url.read().decode())['data']['stations']

    station_df = pd.DataFrame.from_records(stations)
    station_df = station_df.assign(point=lambda x: series_point(x.lon, x.lat))
    station_df['neighborhood'], station_df['borough'] = station_df.point.apply(lambda x: find_poly(x, poly_names)).str

#     stations_with_hoods = []
#     for station in station_pts:
#         for poly in poly_names:
#             if station[2].within(poly[1]):
#                 x, y = station[2].xy
#                 # station_name, _id, hood & boro, x, y
#                 stations_with_hoods.append((station[0], station[1], poly[0], x[0], y[0], station[3]))
#                 # print('{} in {}'.format(station[0], poly[0]))
#                 break
#    cols = ['station_name', 'station_id', 'neighborhood', 'borough', 'longitude', 'latitude', 'capacity']
#    df = pd.DataFrame.from_records(((x, y, *z, w, u, v) for x, y, z, w, u, v in stations_with_hoods), columns=cols)
    station_df.to_csv('stations-with-hoods.csv', index=False)

    # CSVs to import to DB
    if to_file:
        station_df[['neighborhood', 'borough']].to_csv('neighborhoods.csv', index=False)
        station_df[['station_id', 'name', 'capacity']].to_csv('station_names.csv', index=False)
        station_df[['station_id', 'neighborhood', 'lon', 'lat']].to_csv('locations.csv', index=False)
