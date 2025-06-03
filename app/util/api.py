from util.authentication import *
from util.database import *
from flask import make_response, jsonify


def getSessions():
    allSessions = sessions.find_one()
    c=0
    for i in allSessions:
        c=c+1
    ret = [i for i in range(1,c+1)]
    res = make_response(jsonify(ret))
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