from flask import Flask, send_file, make_response, request, render_template
from util.helper import *
from util.authentication import *
from datetime import datetime
from util.database import *

app = Flask(__name__)

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
    admins.insert_one({"id":"123456","username":"","password":"","auth_token":""})
    return send_file('public/html/home.html',mimetype='text/html')

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


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    return send_file('public/html/template.html', mimetype='text/html')

@app.route('/partials/<page>', methods=['GET'])
def load_partial(page):
    safe_pages = {"dashboard", "profile", "settings"}  # whitelist allowed partials
    if page not in safe_pages:
        abort(404)
    filepath = f'public/html/admin-{page}.html'
    if not os.path.exists(filepath):
        abort(404)
    return send_file(filepath, mimetype='text/html')


if __name__ == "__main__":
    app.run()
