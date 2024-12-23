import time
from speedtest import Speedtest
import requests
import csv
from datetime import datetime




def test_download_speed():
    s = Speedtest()
    return s.download() / 1_000_000  # bits -> Mbps


def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    
    # Debugging output
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching weather data: {response.status_code} - {response.text}")
    
    data = response.json()
    wind_speed = data['wind']['speed']              # in m/s
    humidity = data['main']['humidity']             # in %
    temperature_c = data['main']['temp'] - 273.15   # Kelvin to Celsius
    weather_main = data['weather'][0]['main']       # e.g. 'Rain', 'Clouds'
    
    return wind_speed, humidity, temperature_c, weather_main



def log_data(filename, speed, wind_speed, humidity, temperature, weather_main):
    file_exists = False
    try:
        with open(filename, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "download_mbps", "wind_speed", "humidity", "temperature_c", "weather_main"])
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([timestamp, speed, wind_speed, humidity, temperature, weather_main])



if __name__ == "__main__":
    LATITUDE = 57.494733
    LONGITUDE = 2.256437
    API_KEY = "7aa8416bc5a5270146aaa3a23034ec27"
    FILENAME = "wifi_weather_log.csv"

    while True:
        try:
            speed_mbps = test_download_speed()
            wind_speed, humidity, temperature, weather_main = get_weather_data(LATITUDE, LONGITUDE, API_KEY)
            
            # Print for immediate feedback
            print("Wi-Fi Download Speed:", speed_mbps, "Mbps",
                  "| Wind Speed:", wind_speed, "m/s",
                  "| Temperature:", temperature, "°C")

            # Log to CSV
            log_data(FILENAME, speed_mbps, wind_speed, humidity, temperature, weather_main)
        except Exception as e:
            print("Error:", e)
        
        # Wait 60 seconds before the next iteration
        time.sleep(60)

