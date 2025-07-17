import math
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def calculate_car_temperature(ambient_temp, sunlight_intensity, minutes, humidity=50, car_color='dark'):
    """
    Beräkna bilens inre temperatur baserat på:
    - ambient_temp: Ute-temperaturen i °C
    - sunlight_intensity: Solens intensitet (0-1, där 1 är full sol)
    - minutes: Tid i minuter
    - humidity: Luftfuktighet i % (standard 50)
    - car_color: 'light' eller 'dark' (standard 'dark')
    
    Returnerar temperatur i °C
    """
    # Basfaktorer
    if car_color == 'dark':
        heat_absorption = 0.8  # Mörka bilar absorberar mer värme
    else:
        heat_absorption = 0.6  # Ljusa bilar absorberar mindre värme
    
    # Beräkna temperaturökning (förenklad modell)
    # Denna formel är en approximation baserad på forskning om bilvärme
    temp_increase = (ambient_temp * heat_absorption * sunlight_intensity * 
                     (1 + math.log(minutes + 1)/10) * (1 + (humidity - 50)/100))
    
    car_temp = ambient_temp + temp_increase
    
    # Säkerhetsgräns - temperatur kan inte bli lägre än omgivningstemperaturen
    return max(car_temp, ambient_temp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    try:
        ambient_temp = float(data['ambient_temp'])
        sunlight_intensity = float(data['sunlight_intensity'])
        minutes = float(data['minutes'])
        car_color = data.get('car_color', 'dark')
        humidity = float(data.get('humidity', 50))
        
        car_temp = calculate_car_temperature(
            ambient_temp, sunlight_intensity, minutes, humidity, car_color
        )
        
        # Bedöm risknivå
        if car_temp > 40:
            risk = "FARLIGT - Livshotande för hundar"
        elif car_temp > 30:
            risk = "HÖG RISK - Farligt varmt för hundar"
        else:
            risk = "LÅG RISK - Acceptabelt men övervaka"
        
        return jsonify({
            'car_temperature': round(car_temp, 1),
            'risk_level': risk,
            'message': f"Efter {minutes} minuter: {round(car_temp, 1)}°C ({risk})"
        })
    
    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)