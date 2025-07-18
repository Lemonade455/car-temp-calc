from flask import Flask, request, jsonify, render_template
from datetime import datetime
import math
from geopy.geocoders import Nominatim

app = Flask(__name__)
geolocator = Nominatim(user_agent="car_temp_calc")

def calculate_car_temp(ambient_temp, sun_intensity, minutes, humidity=50, car_color='dark', window_open=False, wind_speed=0, uv_index=0):
    """Calculate estimated car temperature"""
    try:
        color_factor = 0.8 if car_color == 'dark' else 0.6
        ventilation = 0.7 if window_open else 1.0
        uv_factor = 1 + (uv_index / 10)
        wind_factor = max(0.5, 1 - (wind_speed / 20))
        
        temp_rise = (ambient_temp * color_factor * sun_intensity * uv_factor * 
                   (1 + math.log(minutes + 1)/8) * 
                   (1 + (humidity - 50)/120) * 
                   ventilation * wind_factor)
        
        return round(max(ambient_temp, min(ambient_temp + temp_rise, 80)), 1)
    except Exception:
        return ambient_temp

@app.route('/')
def home():
    return render_template('index.html', year=datetime.now().year)

@app.route('/get_weather', methods=['POST'])
def get_weather():
    # https://ensemble-api.open-meteo.com/v1/ensemble?latitude=61.007&longitude=14.5432&daily=temperature_2m_mean,temperature_2m_min,temperature_2m_max,apparent_temperature_mean,apparent_temperature_min,apparent_temperature_max,wind_speed_10m_mean,wind_speed_10m_min,wind_speed_10m_max,wind_direction_10m_dominant,wind_gusts_10m_mean,wind_gusts_10m_min,wind_gusts_10m_max,cloud_cover_mean,cloud_cover_max,cloud_cover_min,precipitation_sum,precipitation_hours,rain_sum,pressure_msl_min,pressure_msl_mean,pressure_msl_max&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,surface_pressure,pressure_msl,wind_speed_10m,wind_speed_80m,wind_direction_10m,wind_direction_80m,wind_gusts_10m,temperature_80m&models=icon_seamless&past_days=7
    pass

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    try:
        data = request.json
        temp = float(data.get('temp', 20))
        sun = float(data.get('sun', 1))
        mins = int(data.get('mins', 30))
        
        result = calculate_car_temp(
            temp, sun, mins,
            humidity=int(data.get('humidity', 50)),
            car_color=data.get('color', 'dark'),
            window_open=data.get('window', 'false') == 'true',
            wind_speed=int(data.get('wind', 0)),
            uv_index=int(data.get('uv', 0))
        )
        
        return jsonify({
            'temp': result[0],
            'range': (max(result[0]-5, temp), min(result[0]+5, 80)),
            'warning': get_warning(result[0], mins)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_warning(temp, mins):
    if temp > 50: return "EXTREMT FARLIGT! Ring 112 omedelbart"
    elif temp > 40: return "Farligt varmt - Risk för värmeslag"
    elif temp > 30: return "Varmt - Övervaka noga"
    return "Acceptabelt men kan fortfarande vara riskabelt"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)