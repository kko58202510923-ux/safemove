from flask import Flask, request, jsonify, render_template
from threading import Lock

app = Flask(__name__)

# 전역 변수 + 락 (멀티 스레드 환경 대비)
gps_data = {}
lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pedestrian')
def pedestrian():
    return render_template('pedestrian.html')

@app.route('/driver')
def driver():
    user_id = get_or_create_user_id()
    return render_template('driver.html', user_id=user_id)

# 운전자 모드가 위치 데이터를 보냄 (JSON)
@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    with lock:
        gps_data['lat'] = data['lat']
        gps_data['lng'] = data['lng']

    return jsonify({'status': 'Location updated'})

# 보행자 모드가 좌표 요청
@app.route('/get_location', methods=['GET'])
def get_location():
    with lock:
        if 'lat' in gps_data and 'lng' in gps_data:
            return jsonify({'lat': gps_data['lat'], 'lng': gps_data['lng']})
        else:
            return jsonify({'error': 'No location data'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True)