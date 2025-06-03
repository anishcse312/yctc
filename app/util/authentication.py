import bcrypt
import hashlib
from util.database import *
from flask import make_response, request, jsonify, abort
import secrets
import traceback

def find_auth(auth_token:str):
    auth_token = auth_token.encode('UTF-8')
    hash = hashlib.sha256(auth_token)
    user = admins.find_one({"auth_token":hash.hexdigest()},{'_id':0})
    if user != None:
        return user
    else:
        return None
    
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
        data = request.get_json()
        usr = data.get("username")
        pas = data.get("password")
        admin_data = admins.find_one({"username":usr})
        if validate_password(pas) == False:
            res = make_response(jsonify({"message":"invalid password"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 401
            return res
        if admin_data == None:
            res = make_response(jsonify({"message":"user does not exist"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 401
            return res
        if bcrypt.checkpw(pas.encode(),admin_data['password'].encode()) == False:
            res = make_response(jsonify({"message":"invalid password"}))
            res.headers['X-Content-Type-Options'] = "nosniff"
            res.status_code = 401
            return res
        auth = secrets.token_hex(10)
        auth_token = hashlib.sha256(auth.encode()).hexdigest()
        updated = {'auth_token':auth_token}
        admins.update_one({'username':usr},{'$set':updated})
        res = make_response(jsonify({"message":"Logged In"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.headers['Content-Type']="applicaiton/json"
        res.status_code=200
        res.set_cookie(key="auth_token",value=auth, max_age=10000, httponly=True)
        return res
    except Exception as e:
        print("Fail")
        res = make_response(jsonify({"message":str(e)}))
        res.status_code=400
        res.headers['X-Content-Type-Options'] = "nosniff"
        return res

def adminReg():
    form = request.form
    password = form.get("password")
    emp_id = form.get("employee_id")
    username = form.get("username")

    admin_info = admins.find_one({'employeeId':emp_id})
    if admin_info == None:
        res = make_response(jsonify({"message":"invalid employee id"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    if validate_password(password) == False:
        res = make_response(jsonify({"message":"invalid password"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    if admin_info.get('username') != "" and admin_info.get('username') != None:
        res = make_response(jsonify({"message":"user already registered"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    usernames = [doc.get("username") for doc in admins.find({}, {"username": 1, "_id": 0})]
    if username in usernames:
        res = make_response(jsonify({"message":"username already taken"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    hashed_pas = bcrypt.hashpw(password.encode(),bcrypt.gensalt())
    hashed_pas = hashed_pas.decode()
    update_fields = {"username":username, "password":hashed_pas}
    admins.update_one({"employeeId":emp_id},{'$set':update_fields})
    res = make_response(jsonify({"message":"user registered successfully"}))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code = 200
    return res

def logout():
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    if user == None:
        res = make_response(jsonify({"message":"user not logged in"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    
    res = make_response(jsonify({"message":"logout successfull"}))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code = 200
    res.set_cookie(key="auth_token",value=auth_token,max_age=0)
    res.set_cookie(key="branch",max_age=0)
    res.set_cookie(key="session",max_age=0)
    updated = {"auth_token":""}
    admins.update_one({"auth_token":auth_token},{"$set":updated})
    return res

def forgot():
    data = request.get_json()
    empid = data.get('employeeId')
    last = data.get('lastName')

    user = admins.find_one({'employeeId':empid},{'_id':0})
    if user == None:
        res = make_response(jsonify({"message":"employee id not found"}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 404
        return res
    if user.get('lastName') != last:
        res = make_response(jsonify({'message':'inavlid credentials'}))
        res.headers['X-Content-Type-Options'] = "nosniff"
        res.status_code = 401
        return res
    return True, user
def otp():
    pass
def set_new_pass():
    pass