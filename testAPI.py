import requests

LATITUDE = 57.494733
LONGITUDE = 2.256437
API_KEY = "7aa8416bc5a5270146aaa3a23034ec27"

url = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"
response = requests.get(url)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
