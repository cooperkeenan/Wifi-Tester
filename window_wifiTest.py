import time
import subprocess
from speedtest import Speedtest
import requests
import csv
from datetime import datetime

# Returns download speed in mbps using the "best" server
def test_download_speed():
    s = Speedtest()
    best_server = s.get_best_server()  # This picks the server with the lowest ping
    speed_bps = s.download()  # download speed in bits per second
    return speed_bps / 1_000_000  # convert bits -> megabits

# Get current Weather Data
def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)

    # Debugging output (you can comment these out later if everything is working)
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

# Get Wi-Fi Status on Windows using netsh
def get_wifi_info():
    """
    Runs 'netsh wlan show interfaces' to get current Wi-Fi info on Windows.
    Parses out the 'Channel' and 'Signal' percentage.
    """
    wifi_channel = None
    wifi_signal_percent = None

    cmd = ["netsh", "wlan", "show", "interfaces"]
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
    # Go through each line to find 'Channel:' and 'Signal:'
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.lower().startswith("channel"):
            # Example line: "Channel                : 48"
            parts = line.split(":")
            if len(parts) == 2:
                channel_str = parts[1].strip()
                try:
                    wifi_channel = int(channel_str)
                except ValueError:
                    wifi_channel = None
        
        if line.lower().startswith("signal"):
            # Example line: "Signal                 : 98%"
            parts = line.split(":")
            if len(parts) == 2:
                signal_str = parts[1].strip().rstrip("%").strip()
                try:
                    wifi_signal_percent = int(signal_str)
                except ValueError:
                    wifi_signal_percent = None
    
    # Return the channel and the signal as a percentage
    return wifi_channel, wifi_signal_percent

# Input Data into CSV
def log_data(filename, speed, channel, signal_percent, wind_speed, humidity, temperature, weather_main):
    file_exists = False
    try:
        with open(filename, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp",
                "download_mbps",
                "wifi_channel",
                "wifi_signal_percent",
                "wind_speed",
                "humidity",
                "temperature_c",
                "weather_main"
            ])

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Round numeric fields to 2 decimal places (where it makes sense)
        writer.writerow([
            timestamp,
            f"{speed:.2f}",        # Download speed
            channel,               # Channel (int)
            signal_percent,        # Wi-Fi signal in %
            f"{wind_speed:.2f}",   # Wind speed (m/s)
            humidity,              # Humidity (%)
            f"{temperature:.2f}",  # Temperature (°C)
            weather_main
        ])

if __name__ == "__main__":
    LATITUDE = 57.494733
    LONGITUDE = 2.256437
    API_KEY = "7aa8416bc5a5270146aaa3a23034ec27"
    FILENAME = "wifi_log.csv"

    while True:
        try:
            # 1. Measure Wi-Fi speed (forcing best server)
            speed_mbps = test_download_speed()

            # 2. Get Wi-Fi channel & signal strength (percentage)
            wifi_channel, wifi_signal_percent = get_wifi_info()

            # 3. Get weather data
            wind_speed, humidity, temperature, weather_main = get_weather_data(LATITUDE, LONGITUDE, API_KEY)

            # 4. Print for immediate feedback
            print("Wi-Fi Download Speed:", f"{speed_mbps:.2f}", "Mbps",
                  "| Wi-Fi Channel:", wifi_channel,
                  "| Signal:", f"{wifi_signal_percent}%",
                  "| Wind Speed:", wind_speed, "m/s",
                  "| Temp:", f"{temperature:.1f} °C")

            # 5. Log to CSV
            log_data(
                FILENAME,
                speed_mbps,
                wifi_channel,
                wifi_signal_percent,
                wind_speed,
                humidity,
                temperature,
                weather_main
            )
        except Exception as e:
            print("Error:", e)

        # Wait ~6.7 minutes (400 seconds) before the next iteration
        time.sleep(400)


