import requests
import json
import time
import jwt

location_code='101280803'#南海
API_Host='nf6vhf4knm.re.qweatherapi.com'
PROJECT_ID='39KVBQYAB9'
KEY_ID='CBB6BT4W4W'
# Open PEM
private_key = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIH3QWpVUtC+OzsDkNTAPavY4qj0qZl9Zy6X+cr5l57B6
-----END PRIVATE KEY-----
"""

payload = {
    'iat': int(time.time()) - 30,
    'exp': int(time.time()) + 900,
    'sub': PROJECT_ID
}
headers = {
    'kid': KEY_ID
}

# Generate JWT
encoded_jwt = jwt.encode(payload, private_key, algorithm='EdDSA', headers = headers)

print(f"JWT:  {encoded_jwt}")

url=f"https://{API_Host}/v7/weather/now?location={location_code}"

def get_weather(url,jwt_token):
    
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept-Encoding': 'gzip, deflate'  # 
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:  #
            weather_data = response.json()
            print("请求成功！")
            print("返回数据：", weather_data)
            return weather_data  # 建议返回数据以便后续使用
        else:
            print(f"请求失败，状态码: {response.status_code}")  # 
            print("错误信息：", response.text)
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except ValueError as e:
        print(f"JSON 解析错误: {e}")
        return None


def main():
    weather_data=get_weather(url,encoded_jwt)
    temp = weather_data['now']['temp']  # 温度
    feels_like = weather_data['now']['feelsLike']  # 体感温度
    humidity = weather_data['now']['humidity']  # 湿度
    weather_text = weather_data['now']['text']  # 天气状况
    wind_dir = weather_data['now']['windDir']  # 风向
    wind_speed = weather_data['now']['windSpeed']  # 风速
        
    # 格式化输出
    print("🌤️ 实时天气信息")
    print("=" * 30)
    print(f"📍 地区: 南海 (代码: {location_code})")
    print(f"🌡️ 温度: {temp}°C")
    print(f"🤔 体感温度: {feels_like}°C")
    print(f"💧 湿度: {humidity}%")
    print(f"☁️ 天气状况: {weather_text}")
    print(f"🌬️ 风向: {wind_dir}")
    print(f"💨 风速: {wind_speed} km/h")
    print(f"🕐 观测时间: {weather_data['now']['obsTime']}")
    


if __name__ == "__main__":
    main()