import sqlite3
from datetime import datetime, date
from typing import List
from models import Area, Forecast

class WeatherDatabase:
    def __init__(self, db_path: str = "weather.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS areas (area_code TEXT PRIMARY KEY, area_name TEXT NOT NULL)')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT NOT NULL,
                forecast_date TEXT NOT NULL,
                weather_code TEXT,
                temp_max INTEGER,
                temp_min INTEGER,
                pop INTEGER,
                wind TEXT,
                fetched_at TEXT NOT NULL,
                UNIQUE(area_code, forecast_date, fetched_at)
            )
        ''')
        conn.commit()
        conn.close()

    def save_areas(self, areas: List[Area]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for area in areas:
            cursor.execute('INSERT OR REPLACE INTO areas (area_code, area_name) VALUES (?, ?)', (area.area_code, area.area_name))
        conn.commit()
        conn.close()

    def get_all_areas(self) -> List[Area]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT area_code, area_name FROM areas ORDER BY area_name')
        rows = cursor.fetchall()
        conn.close()
        return [Area(area_code=row[0], area_name=row[1]) for row in rows]

    def save_forecasts(self, forecasts: List[Forecast]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for f in forecasts:
            cursor.execute('''
                INSERT OR REPLACE INTO forecasts 
                (area_code, forecast_date, weather_code, temp_max, temp_min, pop, wind, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f.area_code, f.forecast_date.isoformat(), f.weather_code, f.temp_max, f.temp_min, f.pop, f.wind, f.fetched_at.isoformat()))
        conn.commit()
        conn.close()