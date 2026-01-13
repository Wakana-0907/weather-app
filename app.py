from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, date
import webbrowser
from threading import Timer
from database import WeatherDatabase
from models import Area, Forecast

app = Flask(__name__)
db = WeatherDatabase()

def fetch_weather_from_api(area_code: str):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    try:
        data = requests.get(url).json()
        forecast_dict = {}
        now = datetime.now()
        
        # 1. 短期予報(今日・明日)の取得
        if len(data) > 0:
            for series in data[0]['timeSeries']:
                times = series['timeDefines']
                areas = series['areas']
                target_area = next((a for a in areas if a['area']['code'] == area_code), areas[0])
                
                for i, t in enumerate(times):
                    d_str = t[:10]
                    if d_str not in forecast_dict:
                        forecast_dict[d_str] = Forecast(area_code=area_code, forecast_date=date.fromisoformat(d_str), fetched_at=now)
                    
                    f = forecast_dict[d_str]
                    if 'weatherCodes' in target_area: f.weather_code = target_area['weatherCodes'][i]
                    if 'winds' in target_area: f.wind = target_area['winds'][i]
                    if 'pops' in target_area: f.pop = int(target_area['pops'][i]) if target_area['pops'][i] else 0
                    if 'temps' in target_area:
                        val = int(target_area['temps'][i])
                        if i == 0: f.temp_max = val
                        else: f.temp_min = val

        # 2. 週間予報の取得(上書き・補完)
        if len(data) > 1:
            week_series = data[1]['timeSeries']
            # 天気・降水確率
            w_area = next((a for a in week_series[0]['areas'] if a['area']['code'] == area_code), week_series[0]['areas'][0])
            for i, t in enumerate(week_series[0]['timeDefines']):
                d_str = t[:10]
                if d_str not in forecast_dict:
                    forecast_dict[d_str] = Forecast(area_code=area_code, forecast_date=date.fromisoformat(d_str), fetched_at=now)
                f = forecast_dict[d_str]
                f.weather_code = w_area['weatherCodes'][i]
                f.pop = int(w_area['pops'][i]) if w_area['pops'][i] else 0
            
            # 気温
            t_area = next((a for a in week_series[1]['areas'] if a['area']['code'] == area_code), week_series[1]['areas'][0])
            for i, t in enumerate(week_series[1]['timeDefines']):
                d_str = t[:10]
                if d_str in forecast_dict:
                    f = forecast_dict[d_str]
                    f.temp_min = int(t_area['tempsMin'][i]) if t_area['tempsMin'][i] else f.temp_min
                    f.temp_max = int(t_area['tempsMax'][i]) if t_area['tempsMax'][i] else f.temp_max

        return sorted(forecast_dict.values(), key=lambda x: x.forecast_date)
    except Exception as e:
        print(f"API Error: {e}")
        return []

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/areas')
def get_areas():
    areas = db.get_all_areas()
    if not areas:
        res = requests.get("https://www.jma.go.jp/bosai/common/const/area.json").json()
        areas = [Area(code, info['name']) for code, info in res['offices'].items()]
        db.save_areas(areas)
    return jsonify({'areas': [{'code': a.area_code, 'name': a.area_name} for a in areas]})

@app.route('/api/weather/<area_code>')
def get_weather(area_code):
    forecasts = fetch_weather_from_api(area_code)
    if forecasts: db.save_forecasts(forecasts)
    return jsonify({'forecasts': [{'date': f.forecast_date.isoformat(), 'weather_code': f.weather_code, 'temp_max': f.temp_max, 'temp_min': f.temp_min, 'pop': f.pop, 'wind': f.wind} for f in forecasts]})

if __name__ == '__main__':
    Timer(1.5, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(debug=True, port=5000, use_reloader=False)