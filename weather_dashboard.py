# weather_dashboard.py - Interactive Weather Dashboard
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="🌤️ Real-time Weather Analytics",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 5px;
    }
    .city-header {
        color: #2e86ab;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def load_weather_data():
    """Load data from SQLite database"""
    try:
        conn = sqlite3.connect('weather_data.db')
        
        # Get latest data for each city
        latest_query = """
        SELECT wh1.* FROM weather_history wh1
        INNER JOIN (
            SELECT city, MAX(timestamp) as max_timestamp 
            FROM weather_history 
            GROUP BY city
        ) wh2 ON wh1.city = wh2.city AND wh1.timestamp = wh2.max_timestamp
        """
        
        df_latest = pd.read_sql_query(latest_query, conn)
        
        # Get historical data for charts (last 3 days)
        historical_query = """
        SELECT * FROM weather_history 
        WHERE timestamp >= datetime('now', '-3 days')
        ORDER BY timestamp
        """
        
        df_historical = pd.read_sql_query(historical_query, conn)
        conn.close()
        
        return df_latest, df_historical
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🌤️ Real-time Weather Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("### Live weather data from major cities worldwide • Updated every 2 hours")
    
    # Load data
    df_latest, df_historical = load_weather_data()
    
    if df_latest.empty:
        st.warning("🚨 No weather data available. Run the ETL pipeline first!")
        st.info("💡 Run this in your terminal: `python weather_etl.py`")
        return
    
    # Sidebar
    st.sidebar.title("🔧 Dashboard Controls")
    st.sidebar.markdown("---")
    
    selected_city = st.sidebar.selectbox("📍 Select City", df_latest['city'].unique())
    
    # Last update time
    latest_timestamp = pd.to_datetime(df_latest['timestamp']).max()
    st.sidebar.markdown(f"**Last Updated:** {latest_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dataset Info")
    st.sidebar.markdown(f"**Cities Tracking:** {len(df_latest)}")
    st.sidebar.markdown(f"**Total Records:** {len(df_historical)}")
    st.sidebar.markdown(f"**Data Quality Avg:** {df_latest['data_quality_score'].mean():.1f}/100")
    
    # Main dashboard layout - TOP ROW: Current Conditions
    st.markdown("## 🌡️ Current Weather Conditions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get selected city data
    city_data = df_latest[df_latest['city'] == selected_city].iloc[0]
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Temperature", 
            value=f"{city_data['temperature']:.1f}°C",
            delta=f"Feels like {city_data['feels_like']:.1f}°C"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Humidity", 
            value=f"{city_data['humidity']}%"
        )
        st.metric(
            label="Pressure", 
            value=f"{city_data['pressure']} hPa"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Wind Speed", 
            value=f"{city_data['wind_speed']} m/s"
        )
        st.metric(
            label="Wind Direction", 
            value=f"{city_data['wind_direction']}°"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Condition", 
            value=city_data['weather_condition']
        )
        st.metric(
            label="Cloudiness", 
            value=f"{city_data['cloudiness']}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown("---")
    
    # MIDDLE ROW: Charts
    st.markdown("## 📈 Historical Trends")
    
    if not df_historical.empty:
        # Filter data for selected city
        city_historical = df_historical[df_historical['city'] == selected_city]
        
        if not city_historical.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Temperature trend
                fig_temp = px.line(
                    city_historical, 
                    x='timestamp', 
                    y='temperature',
                    title=f'🌡️ Temperature Trend in {selected_city}',
                    labels={'temperature': 'Temperature (°C)', 'timestamp': 'Time'}
                )
                fig_temp.update_traces(line=dict(color='red', width=3))
                st.plotly_chart(fig_temp, use_container_width=True)
                
            with col2:
                # Humidity trend
                fig_humidity = px.line(
                    city_historical, 
                    x='timestamp', 
                    y='humidity',
                    title=f'💧 Humidity Trend in {selected_city}',
                    labels={'humidity': 'Humidity (%)', 'timestamp': 'Time'}
                )
                fig_humidity.update_traces(line=dict(color='blue', width=3))
                st.plotly_chart(fig_humidity, use_container_width=True)
    
    # BOTTOM ROW: City Comparison
    st.markdown("## 🌍 Global City Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature comparison chart
        fig_bar = px.bar(
            df_latest.sort_values('temperature', ascending=False),
            x='city',
            y='temperature',
            title='🔥 Current Temperatures by City',
            color='temperature',
            color_continuous_scale='RdYlBu_r',
            labels={'temperature': 'Temperature (°C)', 'city': 'City'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Weather conditions pie chart
        condition_counts = df_latest['weather_condition'].value_counts()
        fig_pie = px.pie(
            values=condition_counts.values,
            names=condition_counts.index,
            title='☁️ Weather Conditions Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Data table section
    st.markdown("## 📋 Latest Weather Data")
    
    # Create a nice display table
    display_columns = ['city', 'country', 'temperature', 'humidity', 
                      'weather_condition', 'wind_speed', 'timestamp', 'data_quality_score']
    
    display_df = df_latest[display_columns].copy()
    display_df['temperature'] = display_df['temperature'].round(1)
    display_df.rename(columns={
        'city': 'City',
        'country': 'Country', 
        'temperature': 'Temp (°C)',
        'humidity': 'Humidity (%)',
        'weather_condition': 'Condition',
        'wind_speed': 'Wind (m/s)',
        'timestamp': 'Last Update',
        'data_quality_score': 'Quality Score'
    }, inplace=True)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🛠️ Built with Python • Streamlit • Plotly • OpenWeatherMap API • "
        "Data updates every 2 hours"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()