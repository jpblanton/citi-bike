import urllib.request
import json

status_url = 'https://gbfs.citibikenyc.com/gbfs/en/station_information.json'

with urllib.request.urlopen(status_url) as url:
    stations = json.loads(url.read().decode())['data']['stations']
capacities = [(s['station_id'], s['capacity']) for s in stations]
