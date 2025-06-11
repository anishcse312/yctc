from util.database import *
from flask import make_response, jsonify
def findStudent(regNo: str):
    reg = regNo.split('/')[1]
    session, number = reg.split('-')

    dbname = 'N24'+str(session)
    stuadmn = mongo_client[dbname]['STUADMN'].find_one({'reg_no':regNo},{'_id':0})
    form = mongo_client[dbname]['FORMRECV'].find_one({'reg_no':regNo},{'_id':0})
    reenroll = mongo_client[dbname]['REENROLL'].find_one({'reg_no':regNo},{'_id':0})
    receipt = mongo_client[dbname]['RECEIPT'].find_one({'reg_no':regNo},{'_id':0})
    marks = mongo_client[dbname]['MARKS'].find_one({'reg_no':regNo},{'_id':0})
    instreg = mongo_client[dbname]['INSTREG'].find_one({'reg_no':regNo},{'_id':0})
    l = [stuadmn,form,reenroll,receipt,marks,instreg]
    ret = {}
    for i in l:
        for key, value in i.items():
            ret[key]=value
    res = make_response(jsonify(ret))
    res.status_code = 200
    res.headers['X-Content-Type-Options'] = "nosniff"
    return res


def getmimetype(filename):
    mimetypes = {'jpg':'images/jpeg',
                 'jpeg':'images/jpeg',
                 'png':'images/png',
                 'html':'text/html'}
    ext = filename.split('.')[1]
    return mimetypes[ext]