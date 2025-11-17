import requests

API_KEY = "2b40a61dc1e6f45c58df3c10258a211f"
city = "London"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

print("🔍 Testing API Key...")
response = requests.get(url)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("🎉 API KEY IS WORKING!")
    print(f"🌡️  Temperature in {city}: {data['main']['temp']}°C")
    print(f"☁️  Condition: {data['weather'][0]['description']}")
else:
    print("❌ API Key Issue:")
    print(f"Error: {response.text}")