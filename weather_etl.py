# weather_etl.py - Core ETL Pipeline
import sqlite3
import requests
import pandas as pd
from datetime import datetime
import time
import json

class WeatherETL:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.cities = ['London', 'New York', 'Tokyo', 'Sydney', 'Paris']
        
    def extract_data(self, city):
        """EXTRACT: Get live weather data from API"""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            print(f"✅ Successfully extracted data for {city}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error for {city}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {city}: {e}")
            return None
    
    def transform_data(self, raw_data, city):
        """TRANSFORM: Clean and structure the weather data"""
        if not raw_data:
            return None
            
        try:
            transformed = {
                'city': city,
                'country': raw_data['sys']['country'],
                'temperature': raw_data['main']['temp'],
                'feels_like': raw_data['main']['feels_like'],
                'humidity': raw_data['main']['humidity'],
                'pressure': raw_data['main']['pressure'],
                'wind_speed': raw_data['wind']['speed'],
                'wind_direction': raw_data['wind'].get('deg', 0),
                'weather_condition': raw_data['weather'][0]['main'],
                'weather_description': raw_data['weather'][0]['description'],
                'cloudiness': raw_data['clouds']['all'],
                'visibility': raw_data.get('visibility', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_quality_score': self.calculate_quality_score(raw_data)
            }
            
            print(f"   🔄 Transformed data for {city}")
            return transformed
            
        except KeyError as e:
            print(f"❌ Data transformation error for {city}: Missing key {e}")
            return None
    
    def calculate_quality_score(self, data):
        """Calculate data quality score (0-100)"""
        score = 100
        
        if data.get('visibility') is None:
            score -= 10
            
        if data['wind'].get('deg') is None:
            score -= 5
            
        required_fields = ['main', 'wind', 'weather', 'clouds']
        for field in required_fields:
            if field not in data:
                score -= 20
                
        return max(score, 0)
    
    def load_data(self, transformed_data):
        """LOAD: Store data in SQLite database"""
        if not transformed_data:
            return False
            
        try:
            conn = sqlite3.connect('weather_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                country TEXT,
                temperature REAL,
                feels_like REAL,
                humidity INTEGER,
                pressure INTEGER,
                wind_speed REAL,
                wind_direction INTEGER,
                weather_condition TEXT,
                weather_description TEXT,
                cloudiness INTEGER,
                visibility INTEGER,
                timestamp TEXT,
                data_quality_score INTEGER
            )
            ''')
            
            cursor.execute('''
            INSERT INTO weather_history 
            (city, country, temperature, feels_like, humidity, pressure, 
             wind_speed, wind_direction, weather_condition, weather_description,
             cloudiness, visibility, timestamp, data_quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transformed_data['city'],
                transformed_data['country'],
                transformed_data['temperature'],
                transformed_data['feels_like'],
                transformed_data['humidity'],
                transformed_data['pressure'],
                transformed_data['wind_speed'],
                transformed_data['wind_direction'],
                transformed_data['weather_condition'],
                transformed_data['weather_description'],
                transformed_data['cloudiness'],
                transformed_data['visibility'],
                transformed_data['timestamp'],
                transformed_data['data_quality_score']
            ))
            
            conn.commit()
            conn.close()
            
            print(f"   💾 Loaded data for {transformed_data['city']} to database")
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def run_pipeline(self):
        """Run complete ETL pipeline for all cities"""
        print("🚀 STARTING WEATHER ETL PIPELINE")
        print("=" * 50)
        
        successful_records = 0
        
        for city in self.cities:
            print(f"\n🌍 Processing {city}...")
            
            raw_data = self.extract_data(city)
            if not raw_data:
                continue
                
            transformed_data = self.transform_data(raw_data, city)
            if not transformed_data:
                continue
                
            if self.load_data(transformed_data):
                successful_records += 1
        
        print(f"\n" + "=" * 50)
        print(f"✅ ETL PIPELINE COMPLETED!")
        print(f"📊 Successful records: {successful_records}/{len(self.cities)}")
        return successful_records

# Test the pipeline
if __name__ == "__main__":
    API_KEY = "2b40a61dc1e6f45c58df3c10258a211f"
    
    pipeline = WeatherETL(API_KEY)
    pipeline.run_pipeline()