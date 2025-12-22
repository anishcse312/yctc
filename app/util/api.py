from util.authentication import find_auth
from util.database import get_sessions
from flask import make_response, jsonify, request


def getSessions():
    sessions = get_sessions()
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
    if admin:
        admin.pop("password", None)
        admin.pop("auth_token", None)
    #ret = {'username':admin.get('username'), 'employeeId':admin.get('id'),'firstName':admin.get('firstName'),'lastName':admin.get('lastName'), 'email':admin.get('email')}
    res = make_response(jsonify(admin))
    res.headers['X-Content-Type-Options'] = "nosniff"
    res.status_code=200
    if f == False:
        return res
    else:
        return admin
