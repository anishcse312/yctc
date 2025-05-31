import bcrypt
import hashlib
from util.database import *
from flask import make_response, request, jsonify, abort
import secrets

def validate_password(password: str):
    special_characters = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    valid_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&()-_=')
    if len(password) < 8:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in special_characters for char in password):
        return False
    if not all(char in valid_characters for char in password):
        return False
    return True

def admin_login():
    try:
        data = (request.get_data()).decode()
        usr, pas = data.split('&')
        usr = usr.split('=')[1]
        pas = pas.split('=')[1]

        admin_data = admins.find_one({"username":usr})
        if validate_password(pas) == False:
            res = make_response(jsonify({"message":"invalid password"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 400
            return res
        if admin_data == None:
            res = make_response(jsonify({"message":"user does not exist"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 400
            return res
        if bcrypt.checkpw(pas.encode(),admin_data['password']) == False:
            res = make_response(jsonify({"message":"invalid password"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 400
            return res
        auth = secrets.token_hex(10)
        auth_token = hashlib.sha256(auth.encode()).hexdigest()
        res = make_response(jsonify({"message":"Logged In"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status=200
        res.set_cookie(key="auth_token",value=auth_token, max_age=10000, path="/admin", httponly=True)
        return res
    except:
        print("Fail")
    return make_response(jsonify({"message":"Internal Server Error"}))

def adminReg():
    form = request.form
    password = form.get("password")
    emp_id = form.get("employee_id")
    username = form.get("username")

    admin_info = admins.find_one({'id':emp_id})
    if admin_info == None:
        res = make_response(jsonify({"message":"invalid employee id"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 400
        return res
    if validate_password(password) == False:
        res = make_response(jsonify({"message":"invalid password"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 400
        return res
    
