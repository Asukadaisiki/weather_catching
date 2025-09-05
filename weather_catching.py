import requests
import json
import time
import jwt
import csv
import os
from datetime import datetime
import pandas as pd

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

def flatten_weather_data(data):
    """
    展平嵌套的天气数据
    """
    flattened = data.copy()  # 复制原始数据
    
    # 展平now字段
    if 'now' in flattened and isinstance(flattened['now'], dict):
        for key, value in flattened['now'].items():
            flattened[f'now_{key}'] = value
        del flattened['now']  # 删除原始的now字段
    
    # 展平refer字段
    if 'refer' in flattened and isinstance(flattened['refer'], dict):
        # 处理sources数组
        if 'sources' in flattened['refer']:
            flattened['refer_sources'] = ', '.join(flattened['refer']['sources'])
        # 处理license数组
        if 'license' in flattened['refer']:
            flattened['refer_license'] = ', '.join(flattened['refer']['license'])
        del flattened['refer']  # 删除原始的refer字段
    
    return flattened


def append_weather_data(new_data, filename):
    """
    处理嵌套数据并追加到文件
    """
    new_data['record_time'] = datetime.now().isoformat()
    
    # 展平数据
    flattened_data = flatten_weather_data(new_data)
    
    # 转换为DataFrame
    new_df = pd.DataFrame([flattened_data])
    
    if not os.path.exists(filename):
        # 保存为Excel（更适合表格数据）
        new_df.to_excel(filename.replace('.json', '.xlsx'), index=False)
        # 同时保存JSON备份
        new_df.to_json(filename, orient='records', force_ascii=False, indent=4)
        print(f"创建文件并添加第一条数据")
    else:
        try:
            # 读取现有数据
            existing_df = pd.read_json(filename, encoding='utf-8')
            # 追加新数据
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            # 保存
            combined_df.to_excel(filename.replace('.json', '.xlsx'), index=False)
            combined_df.to_json(filename, orient='records', force_ascii=False, indent=4)
            print(f"数据已追加到 {filename}")
        except Exception as e:
            print(f"错误: {e}")
            new_df.to_excel(filename.replace('.json', '.xlsx'), index=False)
            new_df.to_json(filename, orient='records', force_ascii=False, indent=4)



def find_city (city):
    try:
        with open('D:/LocationList/China-City-List-latest.csv','r',encoding='utf-8') as file :
            next(file)
            reader =csv.DictReader(file)

            for row in reader:
                if row['Location_Name_ZH']==city:
                    return row["Location_ID"]
        return None
    except FileNotFoundError:
        print("文件未找到，请确认文件路径和名称是否正确")
        return None



def get_weather(jwt_token,location_code):

    url=f"https://{API_Host}/v7/weather/now?location={location_code}"
    
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
    city = input("请输入地区名称: ")
    location_code=find_city(city)
    print(f"📍 地区: {city} (代码: {location_code})")
    weather_data=get_weather(encoded_jwt,location_code)
    append_weather_data(weather_data,'weather_data.json')

    temp = weather_data['now']['temp']  # 温度
    feels_like = weather_data['now']['feelsLike']  # 体感温度
    humidity = weather_data['now']['humidity']  # 湿度
    weather_text = weather_data['now']['text']  # 天气状况
    wind_dir = weather_data['now']['windDir']  # 风向
    wind_speed = weather_data['now']['windSpeed']  # 风速
        
    # 格式化输出
    print("🌤️ 实时天气信息")
    print("=" * 30)
    print(f"🌡️ 温度: {temp}°C")
    print(f"🤔 体感温度: {feels_like}°C")
    print(f"💧 湿度: {humidity}%")
    print(f"☁️ 天气状况: {weather_text}")
    print(f"🌬️ 风向: {wind_dir}")
    print(f"💨 风速: {wind_speed} km/h")
    print(f"🕐 观测时间: {weather_data['now']['obsTime']}")
    


if __name__ == "__main__":
    main()