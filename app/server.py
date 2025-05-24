from flask import Flask, send_file, make_response
from util.helper import *

app = Flask(__name__)

@app.route('/')
def send_home():
    return send_file('public/html/home.html',mimetype='text/html')

@app.route('/public/images/<filename>')
def send_img(filename):
    mimetype = getmimetype(filename)
    return send_file("public/images/"+filename,mimetype=mimetype)



if __name__ == "__main__":
    app.run()