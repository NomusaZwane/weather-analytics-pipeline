# simple_dashboard.py - Works without Plotly!
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="🌤️ Real-time Weather Analytics",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS
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
        
        # Get historical data for charts
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

def create_simple_chart(data, x_col, y_col, title, color='blue'):
    """Create a simple matplotlib chart"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data[x_col], data[y_col], color=color, linewidth=2, marker='o')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(y_col.replace('_', ' ').title())
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🌤️ Real-time Weather Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("### Live weather data from major cities worldwide • Built with Python & Streamlit")
    
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
    
    # Main dashboard - Current Conditions
    st.markdown("## 🌡️ Current Weather Conditions")
    
    # Get selected city data
    city_data = df_latest[df_latest['city'] == selected_city].iloc[0]
    
    # Create metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### Temperature")
        st.markdown(f'<div class="metric-card"><h2>{city_data["temperature"]:.1f}°C</h2>'
                   f'<p>Feels like: {city_data["feels_like"]:.1f}°C</p></div>', 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Humidity & Pressure")
        st.markdown(f'<div class="metric-card">'
                   f'<p><strong>Humidity:</strong> {city_data["humidity"]}%</p>'
                   f'<p><strong>Pressure:</strong> {city_data["pressure"]} hPa</p>'
                   f'</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### Wind")
        st.markdown(f'<div class="metric-card">'
                   f'<p><strong>Speed:</strong> {city_data["wind_speed"]} m/s</p>'
                   f'<p><strong>Direction:</strong> {city_data["wind_direction"]}°</p>'
                   f'</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown("#### Conditions")
        st.markdown(f'<div class="metric-card">'
                   f'<p><strong>Weather:</strong> {city_data["weather_condition"]}</p>'
                   f'<p><strong>Cloudiness:</strong> {city_data["cloudiness"]}%</p>'
                   f'<p><strong>Quality Score:</strong> {city_data["data_quality_score"]}/100</p>'
                   f'</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Section
    st.markdown("## 📈 Historical Trends")
    
    if not df_historical.empty:
        city_historical = df_historical[df_historical['city'] == selected_city]
        
        if not city_historical.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### Temperature Trend - {selected_city}")
                if len(city_historical) > 1:
                    fig_temp = create_simple_chart(
                        city_historical, 'timestamp', 'temperature', 
                        f'Temperature Trend in {selected_city}', 'red'
                    )
                    st.pyplot(fig_temp)
                else:
                    st.info("Need more data points for trend analysis")
            
            with col2:
                st.markdown(f"#### Humidity Trend - {selected_city}")
                if len(city_historical) > 1:
                    fig_humidity = create_simple_chart(
                        city_historical, 'timestamp', 'humidity',
                        f'Humidity Trend in {selected_city}', 'blue'
                    )
                    st.pyplot(fig_humidity)
                else:
                    st.info("Need more data points for trend analysis")
    
    # City Comparison
    st.markdown("## 🌍 Global City Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Temperatures")
        
        # Create a simple bar chart using Streamlit's native bar_chart
        temp_data = df_latest.set_index('city')['temperature'].sort_values(ascending=False)
        st.bar_chart(temp_data)
    
    with col2:
        st.markdown("#### Weather Conditions")
        
        # Display conditions in a table
        conditions_df = df_latest[['city', 'weather_condition', 'temperature']].copy()
        conditions_df['temperature'] = conditions_df['temperature'].round(1)
        conditions_df = conditions_df.sort_values('temperature', ascending=False)
        
        st.dataframe(
            conditions_df.style.highlight_max(subset=['temperature'], color='lightgreen'),
            use_container_width=True
        )
    
    # Raw Data Table
    st.markdown("## 📋 Latest Weather Data")
    
    display_columns = ['city', 'country', 'temperature', 'humidity', 
                      'weather_condition', 'wind_speed', 'timestamp']
    
    display_df = df_latest[display_columns].copy()
    display_df['temperature'] = display_df['temperature'].round(1)
    display_df.rename(columns={
        'city': 'City', 'country': 'Country', 'temperature': 'Temp (°C)',
        'humidity': 'Humidity (%)', 'weather_condition': 'Condition',
        'wind_speed': 'Wind (m/s)', 'timestamp': 'Last Update'
    }, inplace=True)
    
    st.dataframe(display_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🛠️ Built with Python • Streamlit • OpenWeatherMap API • "
        "Data updates every 2 hours"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()