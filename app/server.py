from flask import Flask, send_file, make_response
from util.helper import *
from util.authentication import *

app = Flask(__name__)

@app.route('/')
def send_home():
    return send_file('public/html/home.html',mimetype='text/html')

@app.route('/public/images/<filename>')
def send_img(filename):
    mimetype = getmimetype(filename)
    return send_file("public/images/"+filename,mimetype=mimetype)

@app.route('/admin-login', methods = ['GET'])
def send_adminLogin():
    return send_file('public/html/admin-login.html',mimetype='text/html')

@app.route('/admin-login',methods=['POST'])
def adminlogin():
    return admin_login()

if __name__ == "__main__":
    app.run()