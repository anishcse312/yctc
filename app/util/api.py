from util.authentication import *
from util.database import *
from flask import make_response, jsonify


def getSessions():
    with open('util/session.json','r') as f:
        data = json.load(f)
    sessions = data.get('sessions')
    sessions.sort(key=lambda x: x[0])
    res = make_response(jsonify(sessions))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    return res


def getBranch():
    admin = getMe(True)
    branch = admin.get('branch')
    res = make_response(jsonify({"branch":branch})) 
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    return res


def getMe(f: bool):
    auth_token = request.cookies.get('auth_token')
    admin = find_auth(auth_token)
    #ret = {'username':admin.get('username'), 'employeeId':admin.get('id'),'firstName':admin.get('firstName'),'lastName':admin.get('lastName'), 'email':admin.get('email')}
    res = make_response(jsonify(admin))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    if f == False:
        return res
    else:
        return admin