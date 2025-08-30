from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from threading import Lock
import uuid

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'  # 세션 기능을 위한 비밀키, 꼭 변경하세요

gps_data = {}
lock = Lock()

def get_or_create_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pedestrian')
def pedestrian():
    user_id = get_or_create_user_id()  # 세션 기반 사용자ID 생성/조회
    return render_template('pedestrian.html', user_id=user_id)
@app.route('/get_all_locations', methods=['GET'])
def get_all_locations():
    with lock:
        all_locations = gps_data.copy()  # 모든 user_id 위치 정보 반환
    return jsonify(all_locations)

@app.route('/driver')
def driver():
    user_id = get_or_create_user_id()
    return render_template('driver.html', user_id=user_id)

@app.route('/update_location', methods=['POST'])
def update_location():
    if 'user_id' not in session:
        return jsonify({'error': 'User ID not found in session'}), 403

    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    user_id = session['user_id']
    with lock:
        gps_data[user_id] = {'lat': data['lat'], 'lng': data['lng']}

    return jsonify({'status': 'Location updated', 'user_id': user_id})

@app.route('/get_location', methods=['GET'])
def get_location():
    # 쿼리 파라미터로 user_id 요청 가능, 없으면 세션의 user_id로 조회
    query_user_id = request.args.get('user_id')
    user_id = query_user_id or session.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    with lock:
        loc = gps_data.get(user_id)
        if loc:
            return jsonify(loc)
        else:
            return jsonify({'error': 'No location data for this user'}), 404

if __name__ == '__main__':
    # 포트 443은 관리자 권한 필요, 일반 테스트용은 8080 등 권장
    app.run(host='0.0.0.0', port=80, debug=True)
