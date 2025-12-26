from util.database import fetch_student_by_reg
from flask import make_response, jsonify

def parse_branch_from_reg(reg: str):
    if not reg:
        return None
    prefix = reg.split('/')[0]
    if '-' in prefix:
        return prefix.split('-')[-1]
    return prefix
def findStudent(regNo: str):
    reg = regNo.split('/')[1]
    session, number = reg.split('-')

    branch_code = parse_branch_from_reg(regNo)
    data = fetch_student_by_reg(branch_code, int(session), regNo)
    l = [
        data.get("stuadmn"),
        data.get("formrecv"),
        data.get("reenroll"),
        data.get("marks"),
        data.get("instreg"),
    ]
    receipts = data.get("receipts", [])
    l.extend(receipts)
    ret = {}
    for i in l:
        if not i:
            continue
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
