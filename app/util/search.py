from util.database import *
from flask import make_response, jsonify, Response

def search_by_name(name: str):
    with open('util/session.json','r') as f:
        data = json.load(f)
    sessions = data.get('sessions')
    sessions.sort(key=lambda x: x[0])
    ses = [s[0] for s in sessions]
    all_stu=[]
    for i in ses:
        dbname = 'N24'+str(i)
        formrecv = list(mongo_client[dbname]['FORMRECV'].find({'name':name},{'_id':0,'name':1,'dob':1,'f_name':1,'reg_no':1,'session':1}))
        if not (formrecv == []):
            all_stu.append(formrecv)
    return generate_student_table_html(all_stu)

def search_by_reg(regno: str):
    return findStudent(regno)

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

def generate_student_table_html(data):
    html = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        table {
            width: 100%%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        tr:hover {
            background-color: #f1f1f1;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>Reg No</th>
                <th>Name</th>
                <th>Father's Name</th>
                <th>DOB</th>
                <th>Session</th>
            </tr>
        </thead>
        <tbody>
    '''

    for record_list in data:
        if not record_list:
            continue
        student = record_list[0]
        html += f'''
            <tr onclick="postRegNo('{student["reg_no"]}')">
                <td>{student["reg_no"]}</td>
                <td>{student["name"]}</td>
                <td>{student["f_name"]}</td>
                <td>{student["dob"]}</td>
                <td>{student["session"]}</td>
            </tr>
        '''

    html += '''
        </tbody>
    </table>
</body>
</html>
    '''

    return Response(html, mimetype='text/html')
