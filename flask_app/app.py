from flask import Flask,render_template, request, render_template_string, redirect, session, url_for, g, send_file,make_response
import os,sqlite3,subprocess, urllib.request, base64, jwt, random, hashlib
from pathlib import Path
from models import db,User
from jwt_token import *
# from flask_jwt_extended import JWTManager
# from flask_jwt_extended import create_access_token




app = Flask(__name__)

# jwt = JWTManager(app)

basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'testDB.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'
app.app_context().push()
db.init_app(app)
db.app = app
db.create_all()

DATABASE = "testDB.db"
# db = sqlite3.connect(DATABASE)
# db.commit()
# db.close()

#jwt functions
# ====================================================================================================================================
JWT_SECRET_KEY = b'secret'

def new_jwt_token(username,password):   
    payload = {
        'id': username,
        'pw' : password,
        # 'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    print(token)
    return jsonify({'result': 'success', 'token': token})

def check_jwt():
    token = request.cookies.get('token') 
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
    	return '<script>alert("session expired or not loggined");</script>'
# ====================================================================================================================================

@app.route('/',methods=['GET','POST'])
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            username = request.form['username']
            return render_template('index.html', data=(username))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form.get('username')
        passw = request.form.get('password')
        try:
            db = sqlite3.connect(DATABASE)
            cur = db.cursor()
            data = cur.execute(f'select * from user where username="{name}" and password="{passw}"')
            rv = data.fetchall()
            cur.close()
            if data:
                session['logged_in'] = True
                session['login_user'] = name
                payload = {
                    'id': name,
                    'pw' : passw,
                    # 'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
                }
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                resp = make_response(render_template('index.html'))
                resp.set_cookie('token',token)
                return resp
                return redirect(url_for('home'))
            else:
                return f'wrong username or password'
        except Exception as e:
            return str(e)

	# """Login Form"""
	# if request.method == 'GET':
	# 	return render_template('login.html')
	# else:
	# 	name = request.form.get('username')
	# 	passw = request.form.get('password')
	# 	try:
	# 		db = sqlite3.connect(DATABASE)
	# 		cur = db.cursor()
	# 		data = cur.execute(f'select * from user where username="{name}" and password="{passw}"')
	# 		rv = data.fetchall()
	# 		cur.close()
    #         # db.close()
			
	# 		if data:
	# 			session['logged_in'] = True
    #             # new_jwt_token(name,passw)
	# 			session['login_user'] = name
	# 			return redirect(url_for('home'))
	# 		else:
	# 			return f'Wrong username or password'
	# 	except:
	# 		return "Error"

@app.route('/register/', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@app.route("/logout")
def logout():
	session['logged_in'] = False
	return redirect(url_for('home'))

@app.route('/board', methods=['GET', 'POST']) # 로그인 된 후 홈 화면
def board():
    if session['logged_in'] != True:
        return redirect(url_for('login'))
	
    error = None
    id = session['login_user'] # 세션에 저장했던 로그인 유저 아이디를 변수에 저장함
	

    if request.method == 'GET': # 처음 페이지가 로드되는 GET 통신
        db = sqlite3.connect(DATABASE)
        cur = db.cursor()
        data = cur.execute(f'select * from board')
        rv = data.fetchall()
        
        print(type(rv))
        data_list = []
	
        for row in rv:
            data_dic = { 
                'writer': row[0],
                'title': row[1],
                'content': row[2]
            }
            data_list.append(data_dic)
        cur.close()
        db.close()
		
        free_write = request.args.get('javascript')
        search = request.args.get('search')
 
        return render_template('board.html', error=error, name=id, data_list=data_list, free_write=free_write, search=search) 
 
    return render_template('board.html', error=error, name=id)

@app.route('/board_write', methods=['GET', 'POST']) 
def board_write():
    

	if request.method == 'POST':
		writer = request.form['writer']
		title = request.form['title']
		context = request.form['context']
		db = sqlite3.connect(DATABASE)
		cur = db.cursor()
		data = cur.execute(f'insert into board (username, title, context) values ("%s", "%s", "%s")' % (writer,title,context))
		rv = data.fetchall()
		if not rv:
			db.commit()
			return redirect(url_for("board_write"))
		
		cur.close()
		db.close()	
	return render_template('board_write.html')

#doesn't belong to login process
# ====================================================================================================================================
#lfi
@app.route("/file")
def file():
	IMAGE_FOLDER = Path("/")
	if "file" not in request.args:
		return "file not provided", 400
	
	file = IMAGE_FOLDER.joinpath(Path(request.args["file"]))
	if not file.is_relative_to(IMAGE_FOLDER):
		return "Invalid filename", 400
	f = open(file,'r')
	try:
        # f = open(file,'r')
		return "</br>".join(f.readlines())
	except FileNotFoundError:
		return "File does not exist", 400

#ssti
@app.route('/ssti',methods=['GET'])
def ssti():
    ssti = request.args.get('ssti')
    return render_template_string(ssti)

#eval - code execution(injection) 
@app.route('/eval',methods=['GET'])
def eval_func():
    eval_word = request.args.get('eval')
    if eval_word is not None:
        eval_word = eval(eval_word)
        return render_template("eval_word.html", result=eval_word)
	
    return "enter your word"

#ssrf
@app.route('/image')
def get_url():
    url = request.args.get('url', '')

    if url:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = ("data:" + response.headers['Content-Type'] + ";" + "base64," + base64.b64encode(response.read()).decode())
            ret = f"<img src='{data}'/>"
            return (ret)

    return "no param"

#python file execution
@app.route('/python',methods=['GET'])
def python_file_execution():
    cmd = ['python3'] + list(request.args.keys())
    cmd[1] += '.py'
    
    filter_codes = ['`', '$', '<', '>', '|', '&', '{', '}', '=', '*', '?', '!', ';', '"', ',', '\n']
    for filter_code in filter_codes:
        for arg in cmd:
            if filter_code in arg:
                return 'No'
    
    if os.path.exists(cmd[1]) == False:
        return 'No such file'
    
    response = subprocess.run(
        cmd, capture_output=True, text=True
    )
    return response.stdout
        
	
    
# ====================================================================================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)