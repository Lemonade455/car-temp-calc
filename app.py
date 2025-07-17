from flask import Flask, request, jsonify, render_template
from datetime import datetime
import math

app = Flask(__name__)

def calculate_car_temperature(ambient_temp, sunlight_intensity, minutes, humidity=50, car_color='dark', window_open=False, wind_speed=0):
    """
    Förbättrad temperaturberäkning med vindhastighet
    """
    # Basfaktorer
    color_factor = 0.8 if car_color == 'dark' else 0.6
    ventilation_factor = 0.7 if window_open else 1.0
    
    # Vindfaktor (0-1 där 1 är vindstilla)
    wind_factor = 1 - (wind_speed / 20)  # Max 20 m/s som full effekt
    
    # Mer avancerad modell
    temp_increase = (ambient_temp * color_factor * sunlight_intensity * 
                    (1 + math.log(minutes + 1)/8) * 
                    (1 + (humidity - 50)/120) * 
                    ventilation_factor * wind_factor)
    
    car_temp = ambient_temp + temp_increase
    
    # Säkerhetsgränser
    car_temp = max(car_temp, ambient_temp)
    car_temp = min(car_temp, 80)  # Max 80°C som realistisk övre gräns
    
    return car_temp

@app.route('/')
def index():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    try:
        ambient_temp = float(data['ambient_temp'])
        sunlight_intensity = float(data['sunlight_intensity'])
        minutes = int(data['minutes'])
        car_color = data.get('car_color', 'dark')
        humidity = int(data.get('humidity', 50))
        window_open = data.get('window_open', 'false') == 'true'
        wind_speed = int(data.get('wind_speed', 0))
        
        car_temp = calculate_car_temperature(
            ambient_temp, sunlight_intensity, minutes, humidity, car_color, window_open, wind_speed
        )
        
        return jsonify({
            'car_temperature': round(car_temp, 1),
            'message': generate_warning_message(car_temp, minutes),
            'legal_info': get_legal_info(),
            'chart_data': generate_chart_data(ambient_temp, sunlight_intensity, humidity, car_color, wind_speed)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_warning_message(temp, minutes):
    """Generera användarvänliga varningar"""
    if temp > 50:
        return f"🚨 EXTREMT FARLIGT: {temp}°C efter {minutes} minuter - Livsfara för djur!"
    elif temp > 40:
        return f"⚠️ Farligt varmt: {temp}°C efter {minutes} minuter - Risk för värmeslag"
    elif temp > 30:
        return f"☀️ Varmt: {temp}°C efter {minutes} minuter - Övervaka noga"
    else:
        return f"🌤 Acceptabelt: {temp}°C efter {minutes} minuter"

def get_legal_info():
    """Returnera information om lagar"""
    return {
        'title': 'Lagligt att ingripa',
        'text': 'Enligt svensk lag (Djurskyddslagen 2018:1192) får man bryta sig in i en bil för att rädda ett djur i fara. Du måste dock: (1) Kontakta polis först om möjligt, (2) Endast använda nödvändig kraft, (3) Stanna kvar på plats och förklara för ägaren/polis.'
    }

# ... (andra hjälpfunktioner)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)