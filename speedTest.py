import time
import subprocess
from speedtest import Speedtest
import requests
import csv
from datetime import datetime


#Returns download speed in mbps
def test_download_speed():
    s = Speedtest()
    return s.download() / 1_000_000  # bits -> Mbps


# Get current Weather Data
def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)

    # Debugging output 
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code != 200:
        raise Exception(f"Error fetching weather data: {response.status_code} - {response.text}")

    data = response.json()
    wind_speed = data['wind']['speed']               # in m/s
    humidity = data['main']['humidity']              # in %
    temperature_c = data['main']['temp'] - 273.15    # Kelvin to Celsius
    weather_main = data['weather'][0]['main']        # e.g. 'Rain', 'Clouds'

    return wind_speed, humidity, temperature_c, weather_main



# Get Wifi Status
def get_wifi_info():

    airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    result = subprocess.run([airport_path, "-I"], capture_output=True, text=True)
    output = result.stdout

    wifi_channel = None
    wifi_rssi = None

    for line in output.split("\n"):
        line = line.strip().lower()
        if "channel:" in line:
            # e.g. "channel: 149,80"
            # Sometimes it's "channel: 149 (5GHz)", sometimes "149,80" etc.
            parts = line.split(":")
            if len(parts) == 2:
                # channel_part might be "149,80" or "36" etc.
                channel_part = parts[1].strip()
                # Split by comma or space, take the first chunk
                channel_str = channel_part.split(",")[0].split()[0]
                try:
                    wifi_channel = int(channel_str)
                except ValueError:
                    wifi_channel = channel_str  # fallback if it's not a number

        if "agrctlrssi:" in line:
            # e.g. "agrCtlRSSI: -53"
            parts = line.split(":")
            if len(parts) == 2:
                try:
                    wifi_rssi = int(parts[1].strip())
                except ValueError:
                    wifi_rssi = None

    return wifi_channel, wifi_rssi


#Input Data into CSV
def log_data(filename, speed, channel, rssi, wind_speed, humidity, temperature, weather_main):
    file_exists = False
    try:
        with open(filename, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp","download_mbps","wifi_channel","wifi_rssi","wind_speed","humidity","temperature_c","weather_main"
            ])

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Format to 2 decimal place
        writer.writerow([
            timestamp,
            f"{speed:.2f}",       # Download speed
            channel,              # Wi-Fi channel (integer)
            rssi,                 # RSSI (integer)
            f"{wind_speed:.2f}",  # Wind speed
            humidity,             # humidity (int or float, your choice)
            f"{temperature:.2f}", # Temperature
            weather_main
        ])


if __name__ == "__main__":
    LATITUDE = 57.494733
    LONGITUDE = 2.256437
    API_KEY = "7aa8416bc5a5270146aaa3a23034ec27"
    FILENAME = "wifi_log.csv"  

    while True:
        try:
            # 1. Measure Wi-Fi speed
            speed_mbps = test_download_speed()

            # 2. Get Wi-Fi channel & RSSI
            wifi_channel, wifi_rssi = get_wifi_info()

            # 3. Get weather data
            wind_speed, humidity, temperature, weather_main = get_weather_data(LATITUDE, LONGITUDE, API_KEY)

            # 4. Print for immediate feedback
            print("Wi-Fi Download Speed:", f"{speed_mbps:.2f}", "Mbps",
                  "| Wi-Fi Channel:", wifi_channel,
                  "| RSSI:", wifi_rssi, "dBm",
                  "| Wind Speed:", wind_speed, "m/s",
                  "| Temp:", f"{temperature:.1f} °C")

            # 5. Log to CSV
            log_data(
                FILENAME,
                speed_mbps,
                wifi_channel,
                wifi_rssi,
                wind_speed,
                humidity,
                temperature,
                weather_main
            )
        except Exception as e:
            print("Error:", e)

        # Wait ~8 minutes before the next iteration (500 seconds)
        time.sleep(400)
