from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Area:
    area_code: str
    area_name: str

@dataclass
class Forecast:
    area_code: str
    forecast_date: date
    weather_code: str = "100"
    temp_max: int = None
    temp_min: int = None
    pop: int = 0
    wind: str = "おだやか"
    fetched_at: datetime = None