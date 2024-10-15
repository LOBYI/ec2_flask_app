import jwt, random, hashlib
from datetime import datetime,timedelta
from flask import jsonify, render_template,request

JWT_SECRET_KEY = bytes([random.randrange(0, 256) for _ in range(0, 16)])

def new_jwt_token():
    id = request.form.get('username')
    pw = request.form.get('password')
    
    payload = {
         'id': id,
         'pw' : pw,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return jsonify({'result': 'success', 'token': token})

def check_jwt():
    token = request.cookies.get('token') 
    try:
        payload = jwt.decode(token, SECRECT_KEY, algorithms=['HS256'])
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
    	return '<script>alert("session expired or no loggined");</script>'