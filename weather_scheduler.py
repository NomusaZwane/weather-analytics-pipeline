# weather_scheduler.py - Automated Pipeline Runner
import schedule
import time
from weather_etl import WeatherETL
import sqlite3
import pandas as pd
from datetime import datetime

class WeatherScheduler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.pipeline = WeatherETL(api_key)
        
    def run_scheduled_etl(self):
        """Run ETL pipeline with timestamp"""
        print(f"\n⏰ SCHEDULED RUN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        self.pipeline.run_pipeline()
        self.generate_daily_report()
        
    def generate_daily_report(self):
        """Generate a simple daily summary report"""
        try:
            conn = sqlite3.connect('weather_data.db')
            
            # Get today's data
            today = datetime.now().strftime('%Y-%m-%d')
            query = f"SELECT * FROM weather_history WHERE timestamp LIKE '{today}%'"
            df = pd.read_sql_query(query, conn)
            
            if not df.empty:
                print(f"\n📈 TODAY'S WEATHER SUMMARY ({today})")
                print("=" * 40)
                
                hottest_city = df.loc[df['temperature'].idxmax()]
                coldest_city = df.loc[df['temperature'].idxmin()]
                
                print(f"🔥 Hottest: {hottest_city['city']} ({hottest_city['temperature']:.1f}°C)")
                print(f"❄️  Coldest: {coldest_city['city']} ({coldest_city['temperature']:.1f}°C)")
                print(f"📊 Total records today: {len(df)}")
                print(f"⭐ Average data quality: {df['data_quality_score'].mean():.1f}/100")
                
            conn.close()
            
        except Exception as e:
            print(f"Report generation error: {e}")
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        print("🔄 STARTING WEATHER SCHEDULER")
        print("⏰ Scheduled runs: Every 2 hours")
        print("📍 Tracking cities: London, New York, Tokyo, Sydney, Paris")
        print("=" * 60)
        
        # Schedule jobs
        schedule.every(2).hours.do(self.run_scheduled_etl)
        
        # Run immediately first time
        self.run_scheduled_etl()
        
        print("\n✅ Scheduler started! Press Ctrl+C to stop.")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

# Run the scheduler
if __name__ == "__main__":
    API_KEY = "2b40a61dc1e6f45c58df3c10258a211f"
  # Replace with your key
    
    scheduler = WeatherScheduler(API_KEY)
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")