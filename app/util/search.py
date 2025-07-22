from util.database import *
from flask import make_response, jsonify, Response
import numpy as np

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

def search_by_reg(reg: str):
    regno = reg.split('/')[1]
    ses, no = regno.split('-')
    dbname = 'N24'+str(ses)

    stuadmn = mongo_client[dbname]['STUADMN'].find_one({'reg_no':reg},{'_id':0,'name':1,'f_name':1,"course_id":1,"batch":1,"scholar":1,"lateral":1,'OtherYCTC':1,'FrontLine':1,"pre_reg":1,"remarks":1})
    formrecv =mongo_client[dbname]['FORMRECV'].find_one({'reg_no':reg},{'_id':0,"sex":1,"caste":1,"dob":1,"add_1":1,"add_2":1,"po":1,"district":1,"pin":1,"phone":1,"mobile":1,"GQ1":1,'GQ2':1,'GQ3':1,'GQ4':1,'TQ':1,"remarks":1})
    receipts = list(mongo_client[dbname]['RECEIPT'].find({'reg_no':reg},{'_id':0,"recpt_type":1,"instalment":1,"recptdate":1,"receiptno":1,"amount":1,"remarks":1}))
    marks = mongo_client[dbname]['MARKS'].find_one({'reg_no':reg},{'_id':0,'trans_date':1,'certi_date':1})
    prev_infos = []
    '''
    preg = stuadmn['pre_reg']
    while (True):
        if np.isnan(preg):
            break
    '''
    return generate_student_profile_html(stuadmn,formrecv,receipts,marks,prev_infos)




from flask import Response
import numpy as np

def generate_student_profile_html(stuadmn, formrecv, receipts, marks, prev_infos):
    def fmt(value):
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return " - "
        s = str(value).strip()
        return s if s else " - "

    def parse_qual(qual_string):
        if not qual_string or not isinstance(qual_string, str):
            return None
        parts = qual_string.strip().split("#")
        if len(parts) == 4:
            return parts
        return None
    def format_number(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()


    html = '''
<div style="max-height: 90vh; overflow-y: auto; font-family: monospace; background: #f5f5f5; padding: 20px; white-space: pre-wrap; font-size: 14px;">
<b>General Information:</b>
'''

    def add_v(a):
        if isinstance(a, float) and np.isnan(a):
            return ""
        return str(a).strip()

    # Basic Info
    name = fmt(stuadmn.get("name"))
    fname = fmt(stuadmn.get("f_name"))
    sex = fmt(formrecv.get("sex"))
    caste = fmt(formrecv.get("caste"))
    dob = fmt(formrecv.get("dob"))

    address = formrecv.get("add_1", "")
    address += '\n\t\t  ' + add_v(formrecv.get("add_2"))
    address += f"\n\t\t  Post-{fmt(formrecv.get('po'))}"
    address += f"\n\t\t  Dist-{fmt(formrecv.get('district'))}."
    address += f"\n\t\t  Pin -{fmt(formrecv.get('pin'))}"

    phones = [format_number(formrecv.get("phone")), format_number(formrecv.get("mobile"))]
    phones = [p for p in phones if p != " - "]

    phone_numbers = ", ".join([p for p in phones if p != " - "])

    html += f'''Name            : {name}\t\t\tSex   : {sex}
Father's Name   : {fname}\t\t\tCaste : {caste}

Address         : {address}
Date of Birth   : {dob}

Phone           : {phone_numbers}

<b>Qualification : (General)</b>
<table style="width: 100%; border-collapse: collapse; margin-top: 5px; margin-bottom: 10px;">
  <thead>
    <tr style="background-color: #ddd;">
      <th style="border: 1px solid #999; padding: 5px;">Exam. Passed</th>
      <th style="border: 1px solid #999; padding: 5px;">Year</th>
      <th style="border: 1px solid #999; padding: 5px;">Board/University</th>
      <th style="border: 1px solid #999; padding: 5px;">Marks</th>
    </tr>
  </thead>
  <tbody>
'''

    for key in ["GQ1", "GQ2", "GQ3", "GQ4"]:
        qual = parse_qual(formrecv.get(key))
        if qual:
            exam, year, board, mark = qual
            html += f'''
    <tr>
      <td style="border: 1px solid #ccc; padding: 5px;">{exam}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{year}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{board}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{mark}</td>
    </tr>
'''

    html += '''
  </tbody>
</table>
<b>Qualification : (Technical)</b>
<table style="width: 100%; border-collapse: collapse; margin-top: 5px; margin-bottom: 10px;">
  <thead>
    <tr style="background-color: #ddd;">
      <th style="border: 1px solid #999; padding: 5px;">Exam. Passed</th>
      <th style="border: 1px solid #999; padding: 5px;">Year</th>
      <th style="border: 1px solid #999; padding: 5px;">Board/University</th>
      <th style="border: 1px solid #999; padding: 5px;">Marks</th>
    </tr>
  </thead>
  <tbody>
'''

    tq = parse_qual(formrecv.get("TQ"))
    if tq:
        exam, year, board, mark = tq
        html += f'''
    <tr>
      <td style="border: 1px solid #ccc; padding: 5px;">{exam}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{year}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{board}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{mark}</td>
    </tr>
'''
    else:
        html += '''
    <tr>
      <td colspan="4" style="border: 1px solid #ccc; padding: 5px; text-align: center;">No technical qualification found</td>
    </tr>
'''

    html += '''
  </tbody>
</table>
'''

    # Other Information
    html += "\n<b>Other Information:</b>\n"
    course = stuadmn.get("course_id", " - ")
    batch = stuadmn.get("batch", " - ")
    html += f"Course          : {fmt(course)}        Batch : {fmt(batch)}\n"
    for key in ['scholar', 'lateral', 'OtherYCTC', 'FrontLine']:
        html += f"{key.capitalize():<16}: {fmt(stuadmn.get(key))}\n"
    html += f"\nTranscript       : {fmt(marks.get('trans_date'))} \nCertificate      : {fmt(marks.get('certi_date'))}\n"

    # Previous Information (Commented Placeholder)
    html += "\n<!-- Previous Information block goes here -->\n"

    # Fees as a Table
    html += "\n<hr style='border: 0; border-top: 1px solid blue;'>\n"
    html += "<b>Details of Admission and Instalment Fees:</b>\n"
    html += '''
<table style="width: 100%; border-collapse: collapse; margin-top: 5px; margin-bottom: 10px;">
  <thead>
    <tr style="background-color: #ddd;">
      <th style="border: 1px solid #999; padding: 5px;">Receipt For</th>
      <th style="border: 1px solid #999; padding: 5px;">Date</th>
      <th style="border: 1px solid #999; padding: 5px;">Receipt No</th>
      <th style="border: 1px solid #999; padding: 5px;">Amount</th>
    </tr>
  </thead>
  <tbody>
'''

    for r in receipts:
        rec_type = r.get("recpt_type")
        label = "Admission" if rec_type == "A" else f"Instalment : {r.get('instalment')}"
        date = fmt(r.get("recptdate"))
        recno = format_number(r.get("receiptno"))
        amount = fmt(r.get("amount"))
        html += f'''
    <tr>
      <td style="border: 1px solid #ccc; padding: 5px;">{label}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{date}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{recno}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{amount}</td>
    </tr>
'''

    html += '''
  </tbody>
</table>
'''

    # Remarks Section
    html += "\n<hr style='border: 0; border-top: 1px solid blue;'>\n"
    html += "<b>Details of Remarks:</b>\n"

    if stuadmn.get("remarks") not in [None, "", " - "] and not (isinstance(stuadmn.get("remarks"), float) and np.isnan(stuadmn.get("remarks"))):
        html += f"- Student Admission Remark : {stuadmn['remarks']}\n"
    if formrecv.get("remarks") not in [None, "", " - "] and not (isinstance(formrecv.get("remarks"), float) and np.isnan(formrecv.get("remarks"))):
        html += f"- Form Submission Remark   : {formrecv['remarks']}\n"

    for r in receipts:
        remark = r.get("remarks")
        if remark and not (isinstance(remark, float) and np.isnan(remark)):
            label = "Admission" if r.get("recpt_type") == "A" else f"Installment {r.get('instalment')}"
            html += f"- Receipt ({label}) Remark : {remark}\n"

    html += "</div>"

    return Response(html, mimetype='text/html')




def generate_student_table_html(data):
    html = '''
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
<style>
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        background-color: white;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 10px 14px;
        text-align: left;
    }
    thead {
        background-color: #e0f7ff;
    }
    tr:hover {
        background-color: #f1f1f1;
        cursor: pointer;
    }
</style>
    '''

    return Response(html, mimetype='text/html')
