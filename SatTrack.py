from flask import Flask, render_template
import requests
import datetime
import pytz

app = Flask(__name__)

def get_radio_passes(satellite_id, observer_lat, observer_lng, observer_alt, days, min_elevation, api_key):
    url = f"https://api.n2yo.com/rest/v1/satellite/radiopasses/{satellite_id}/{observer_lat}/{observer_lng}/{observer_alt}/{days}/{min_elevation}/&apiKey={api_key}"
    response = requests.get(url)
    return response.json()

def get_current_position(satellite_id, observer_lat, observer_lng, observer_alt, api_key):
    url = f"https://api.n2yo.com/rest/v1/satellite/positions/{satellite_id}/{observer_lat}/{observer_lng}/{observer_alt}/1/&apiKey={api_key}"
    response = requests.get(url)
    return response.json()

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    utc_time = datetime.datetime.utcfromtimestamp(value)
    central_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("US/Central"))
    return central_time.strftime(format)

@app.template_filter('elevation_color')
def elevation_color(elevation):
    max_elevation = 90
    red = int((1 - elevation / max_elevation) * 255)
    green = int(elevation / max_elevation * 255)
    return f'rgb({red},{green},0)'

@app.route('/')
def index():
    api_key = "LLHTCT-83W7RG-EGDBFH-562H"
    satellites = [
        {"name": "NOAA 18", "id": 28654},
        {"name": "NOAA 15", "id": 25338},
        {"name": "NOAA 19", "id": 33591}
    ]
    observer = {"lat": 29.7604, "lng": -95.3698, "alt": 12}
    all_passes = [sat_pass for satellite in satellites for sat_pass in get_radio_passes(satellite["id"], observer["lat"], observer["lng"], observer["alt"], 10, 10, api_key).get("passes", [])]
    all_passes.sort(key=lambda x: x["startUTC"])
    satellite_positions = [get_current_position(satellite["id"], observer["lat"], observer["lng"], observer["alt"], api_key) for satellite in satellites]
    return render_template('index.html', next_pass=all_passes[0] if all_passes else None, all_passes=all_passes, satellite_positions=satellite_positions, elevation_color=elevation_color)

if __name__ == '__main__':
    app.run(debug=True)