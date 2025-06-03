from flask import Flask, send_file, make_response, request, render_template, redirect, url_for
from functools import wraps
from util.helper import *
from util.authentication import *
from datetime import datetime
from util.database import *
from bson.objectid import ObjectId
from util.api import *
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
)
mail = Mail(app)
# --- Login Required Decorator ---
def login_required_http(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        user = find_auth(token) if token else None
        if user is None:
            if request.path.startswith('/api/'):
                 return jsonify({"message": "Authentication required"}), 401
            else:
                 return redirect(url_for('adminlogin', next=request.url))
        # Inject user into request context if needed later (optional)
        # from flask import g
        # g.user = user
        return f(*args, **kwargs)
    return decorated_function
# --- End Decorator ---


LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'requests.log')
FULL_LOG_FILE = os.path.join(LOGS_DIR, 'server.log')




@app.before_request
def log_raw():
    try:
        if request.path.startswith('/login') or request.path.startswith('/register'):
            # Only log headers for login/register to avoid password logging
            raw = f"HEADERS:\n{dict(request.headers)}"
        else:
            body = request.get_data(as_text=True)[:2048]
            raw = f"HEADERS:\n{dict(request.headers)}\nBODY:\n{body}"
        clean = redact_tokens_and_passwords(raw)
        with open(FULL_LOG_FILE, 'a') as f:
            f.write(f"--- REQUEST {request.method} {request.path} ---\n{clean}\n")
    except Exception as e:
        print(f"Request logging failed: {e}")
 

@app.after_request
def log_raw_response(response):
    try:
        body = response.get_data(as_text=True)[:2048]
        raw = f"HEADERS:\n{dict(response.headers)}\nBODY:\n{body}"
        clean = redact_tokens_and_passwords(raw)
        with open(FULL_LOG_FILE, 'a') as f:
            f.write(f"--- RESPONSE {request.method} {request.path} ---\n{clean}\n")
    except Exception as e:
        print(f"Response logging failed: {e}")
    return response

import urllib.parse

def redact_tokens_and_passwords(raw: str) -> str:
    # Define sensitive keys
    sensitive_keys = ['authorization', 'auth_token', 'password']

    # First, try to parse as URL-encoded form data
    try:
        parsed = urllib.parse.parse_qsl(raw, keep_blank_values=True)
        redacted = [(k, v) for k, v in parsed if all(s not in k.lower() for s in sensitive_keys)]
        if redacted:
            return urllib.parse.urlencode(redacted)
    except Exception:
        pass  # Fall back to line-by-line filtering

    # Fallback: remove lines containing sensitive fields
    lines = raw.splitlines()
    filtered = []
    for line in lines:
        if any(s in line.lower() for s in sensitive_keys):
            continue
        filtered.append(line)
    return "\n".join(filtered)

@app.before_request 
def log_req():
    if not os.path.exists(LOGS_DIR):
        try:
            os.makedirs(LOGS_DIR)
        except OSError as e:
            print(f"Error creating logs directory {LOGS_DIR}: {e}")
            return
    dt = datetime.now() # Use datetime.datetime explicitly
    dt_str = dt.strftime('%m-%d-%Y %H:%M:%S') # Use standard time format
    ip = request.headers.get('X-Real-IP') or request.remote_addr
    method = request.method
    path = request.path
    auth_token = request.cookies.get('auth_token',None)
    username = None
    if auth_token != None:
        user = find_auth(auth_token)
        username = user.get('username')
    if username == None or auth_token ==None:
        log = f'[{dt_str}]: {ip} {method} {path}'
    else:
        log = f'[{dt_str}]: {ip} ({username}) {method} {path}'
    print(log) # Keep console log
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log)
    except Exception as e:
        print(f"Error writing to log file {LOG_FILE}: {e}")

@app.after_request
def after_req_resp(response):
    resp_code = str(response.status_code)
    with open(LOG_FILE, 'a') as f:
        f.write(" -> "+resp_code+'\n')
    return response

@app.route('/')
def send_home():
    msg = Message("Test", recipients=['banerji.anish@gmail.com'])
    msg.body = "Hello. This is a test message"
    mail.send(msg)
    return send_file('public/html/home.html',mimetype='text/html')


@app.route('/public/js/<filename>', methods = ['GET'])
def sendJS(filename):
    return send_file('public/js/'+filename, mimetype='text/javascript')
@app.route('/public/images/<filename>')
def send_img(filename):
    mimetype = getmimetype(filename)
    return send_file("public/images/"+filename,mimetype=mimetype)

@app.route('/admin-login', methods = ['GET'])
def send_adminLogin():
    return send_file('public/html/admin-login.html',mimetype='text/html')



@app.route('/admin-register',methods=['GET'])
def send_adminReg():
    return send_file('public/html/admin-reg.html',mimetype='text/html')




@app.route('/admin-register', methods=['POST'])
def adminRegister():
    return adminReg()

@app.route('/admin-login',methods=['POST'])
def adminlogin():
    return admin_login()

@app.route('/otp',methods=['GET'])
def sendOtp():
    return send_file('public/html/otp.html',mimetype='text/html')

@app.route('/forgot',methods=['GET'])
def sendForgot():
    return send_file('public/html/forgot.html',mimetype='text/html')

@app.route('/set-new-password',methods=['GET'])
def sendNewPass():
    return send_file('public/html/set-new-pass.html',mimetype='text/html')

@app.route('/admin/dashboard', methods=['GET'])
@login_required_http
def admin_dashboard():
    return send_file('public/html/template.html', mimetype='text/html')

app.add_url_rule('/forgot','forgot',forgot,methods=['POST'])
@app.route('/forgot',methods=['POST'])
def serveForgot():
    ret = forgot()
    if ret != True:
        return ret
    
app.add_url_rule('/otp','otp',otp,methods=['POST'])
app.add_url_rule('/set-new-password','new-pass',set_new_pass,methods=['POST'])
app.add_url_rule('/api/sessions',"getSessions",login_required_http(getSessions),methods=['GET'])
app.add_url_rule('/api/my-branch','getBranch',login_required_http(getBranch),methods=['GET'])
app.add_url_rule('/logout','logout',login_required_http(logout),methods=['POST'])

@app.route('/api/me',methods = ['GET'])
def me():
    return getMe(False)



@app.route('/partials/<page>', methods=['GET'])
def load_partial(page):
    safe_pages = {"dashboard", "settings"}  # whitelist allowed partials
    if page not in safe_pages:
        abort(404)
    filepath = f'public/html/admin-{page}.html'
    if not os.path.exists(filepath):
        abort(404)
    return send_file(filepath, mimetype='text/html')




if __name__ == "__main__":
    app.run()
