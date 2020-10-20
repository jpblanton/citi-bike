import psycopg2
import pandas as pd
import plotly.express as px

#look at using timescaledb to make sure each time value has all stations
#can fill forward for nulls

con = psycopg2.connect('postgres://postgres@localhost/nyc_data')
sql = """SELECT A.station_id, (C.bikes_available + C.ebikes_available) / A.station_cap AS metric,
B.longitude, B.latitude, A.station_name, A.station_cap, C.time FROM names A JOIN location B ON A.station_id = B.station_id JOIN status C ON B.station_id = C.station_id"""
# df = pd.read_sql('select * from test', con)
df = pd.read_sql(sql, con)
df = df.replace({'metric': 
df['metric-bucket'] = pd.qcut(df['metric'], 4)
df = df[df['metric'] > 0]
# fig = px.scatter_geo(df, lon=df['longitude'], lat=df['latitude'], color='metric')
# can pass animation_frame to get an easy animation based on that column
# will need to load from `status` table and decide intervals
fig = px.scatter_mapbox(df, lat='latitude', lon='longitude',
                        hover_name='station_name', color='metric', zoom=11,
                        animation_frame=df.time.astype(str))
fig.update_layout(mapbox_style="open-street-map")
fig.write_html('test.html')
"""
SELECT a.station_id,
    a.station_name,
        (c.bikes + c.ebikes) / a.station_cap AS metric,
            a.station_cap,
                c.bikes,
                    c.ebikes,
                        b.longitude,
                            b.latitude
                               FROM names a,
                                   location b,
                                       ( SELECT status.station_id,
                                                    last(status.bikes_available, status."time") AS bikes,
                                                    last(status.ebikes_available, status."time") AS ebikes
                                                   FROM status
                                                  GROUP BY status.station_id) c
                                         WHERE a.station_id = b.station_id AND a.station_id = c.station_id
                                         """
# want to have over time
sql = """SELECT A.station_id, (C.bikes_available + C.ebikes_available) / A.station_cap AS metric,
B.longitude, B.latitude FROM names A JOIN location B ON station_id JOIN status C ON station_id"""
