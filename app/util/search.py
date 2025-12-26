from util.authentication import find_auth
from util.database import (
    fetch_student_by_reg,
    get_sessions,
    get_sessions_for_branches,
    list_branch_codes,
    search_stuadmn_by_name,
)
from flask import make_response, jsonify, Response, request
import numpy as np

def parse_branch_from_reg(reg: str):
    if not reg:
        return None
    prefix = reg.split('/')[0]
    if '-' in prefix:
        return prefix.split('-')[-1]
    return prefix

def resolve_branch_from_cookie():
    return request.cookies.get("branch")

def normalize_branches(branch_field):
    if branch_field is None:
        return []
    if isinstance(branch_field, list):
        branches = branch_field
    elif isinstance(branch_field, str):
        branches = [branch_field]
    else:
        branches = list(branch_field)
    return [str(item).strip() for item in branches if str(item).strip()]

def resolve_allowed_branches():
    auth_token = request.cookies.get("auth_token")
    admin = find_auth(auth_token) if auth_token else None
    branches = normalize_branches(admin.get("branch") if admin else None)
    if not branches:
        return []
    if branches[0].lower() == "master":
        return list_branch_codes()
    return [b.upper() for b in branches]

def search_by_name(name: str):
    allowed_branches = resolve_allowed_branches()
    if not allowed_branches:
        return Response("Forbidden", status=403, mimetype="text/plain")
    branch_code = resolve_branch_from_cookie()
    if branch_code and branch_code != "All":
        if branch_code not in allowed_branches:
            return Response("Forbidden", status=403, mimetype="text/plain")
        search_branches = [branch_code]
        sessions = get_sessions(branch_code)
    else:
        search_branches = allowed_branches
        sessions = get_sessions_for_branches(search_branches)
    ses = [s[0] for s in sessions]
    all_stu = []
    for branch in search_branches:
        for session_num in ses:
            matches = search_stuadmn_by_name(branch, session_num, name)
            if not matches:
                continue
            enriched = []
            for row in matches:
                data = fetch_student_by_reg(branch, session_num, row["reg_no"])
                formrecv = data.get("formrecv") or {}
                row["dob"] = formrecv.get("dob")
                enriched.append(row)
            all_stu.append(enriched)
    return generate_student_table_html(all_stu)

def search_by_reg(reg: str):
    regno = reg.split('/')[1]
    print("regno=",regno)
    ses, no = regno.split('-')
    print("ses, no = ",ses,no)
    session_num = int(ses)
    branch_code = parse_branch_from_reg(reg) or resolve_branch_from_cookie()
    allowed_branches = resolve_allowed_branches()
    selected_branch = resolve_branch_from_cookie()
    if not branch_code or not allowed_branches:
        return Response("Forbidden", status=403, mimetype="text/plain")
    if selected_branch and selected_branch != "All" and branch_code != selected_branch:
        return Response("Forbidden", status=403, mimetype="text/plain")
    if branch_code not in allowed_branches:
        return Response("Forbidden", status=403, mimetype="text/plain")
    data = fetch_student_by_reg(branch_code, session_num, reg)
    stuadmn = data.get("stuadmn") or {}
    formrecv = data.get("formrecv") or {}
    receipts = data.get("receipts", [])
    marks = data.get("marks") or {}

    if not stuadmn and not formrecv:
        return Response("Student not found", status=404, mimetype="text/plain")
    prev_infos={}
    preg = stuadmn.get('pre_reg')
    i=0
    while (True):
        if preg is None or (isinstance(preg, float) and np.isnan(preg)):
            break
        preg = str(preg).strip()
        i+=1
        ses1, no1 = ((preg.split('/'))[1]).split('-')
        dbname1 = 'N24'+str(ses1)
        prev_branch = parse_branch_from_reg(preg) or branch_code
        prev_data = fetch_student_by_reg(prev_branch, int(ses1), preg)
        marks1 = prev_data.get("marks") or {}
        stuadmn1 = prev_data.get("stuadmn") or {}
        prev_infos[i] = {"marks": marks1, "stuadmn": stuadmn1}
        preg = stuadmn1.get('pre_reg')

    
    return generate_student_profile_html(stuadmn,formrecv,receipts,marks,prev_infos)



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
        if value is None or (isinstance(value, float) and np.isnan(value)):
            return ""
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

    for key in ["gq1", "gq2", "gq3", "gq4"]:
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

    tq = parse_qual(formrecv.get("tq"))
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
    for key in ['scholar', 'lateral', 'otheryctc', 'frontline']:
        html += f"{key.capitalize():<16}: {fmt(stuadmn.get(key))}\n"
    html += f"\nTranscript       : {fmt(marks.get('trans_date'))} \nCertificate      : {fmt(marks.get('certi_date'))}\n"

    # Previous Information (Commented Placeholder)
        # Previous Information Section
        # Previous Information Section
    if prev_infos:
        html += "\n<hr style='border: 0; border-top: 1px solid blue;'>\n"
        html += "<b>Previous Information:</b>\n"

        for i, info in enumerate(prev_infos.values(), start=1):
            if not isinstance(info, dict):
                continue

            pm = info.get('marks', {}) or {}
            ps = info.get('stuadmn', {}) or {}

            pm = pm if isinstance(pm, dict) else {}
            ps = ps if isinstance(ps, dict) else {}

            html += f"<b>Previous Information ({i})</b>\n"
            html += '''
<table style="width: 100%; border-collapse: collapse; margin-top: 5px; margin-bottom: 10px;">
  <thead>
    <tr style="background-color: #ddd;">
      <th style="border: 1px solid #999; padding: 5px;">RegNo</th>
      <th style="border: 1px solid #999; padding: 5px;">Course</th>
      <th style="border: 1px solid #999; padding: 5px;">Batch</th>
      <th style="border: 1px solid #999; padding: 5px;">Scholar</th>
      <th style="border: 1px solid #999; padding: 5px;">Lateral</th>
      <th style="border: 1px solid #999; padding: 5px;">OtherYCTC</th>
      <th style="border: 1px solid #999; padding: 5px;">FrontLine</th>
      <th style="border: 1px solid #999; padding: 5px;">Paper-1</th>
      <th style="border: 1px solid #999; padding: 5px;">Paper-2</th>
      <th style="border: 1px solid #999; padding: 5px;">Paper-3</th>
      <th style="border: 1px solid #999; padding: 5px;">Grade</th>
      <th style="border: 1px solid #999; padding: 5px;">Transcript</th>
      <th style="border: 1px solid #999; padding: 5px;">Certificate</th>
      <th style="border: 1px solid #999; padding: 5px;">Remarks</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border: 1px solid #ccc; padding: 5px;">{reg}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{course}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{batch}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{scholar}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{lateral}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{otheryctc}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{frontline}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{p1}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{p2}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{p3}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{grade}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{trans}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{certi}</td>
      <td style="border: 1px solid #ccc; padding: 5px;">{remark}</td>
    </tr>
  </tbody>
</table>
'''.format(
    reg=fmt(ps.get('reg_no')),
    course=fmt(ps.get('course_id')),
    batch=fmt(ps.get('batch')),
    scholar=fmt(ps.get('scholar')),
    lateral=fmt(ps.get('lateral')),
    otheryctc=fmt(ps.get('otheryctc')),
    frontline=fmt(ps.get('frontline')),
    p1=fmt(pm.get('p1s1')),
    p2=fmt(pm.get('p2s1')),
    p3=fmt(pm.get('p3s1')),
    grade=fmt(pm.get('grade')),
    trans=fmt(pm.get('trans_date')),
    certi=fmt(pm.get('certi_date')),
    remark=fmt(pm.get('remarks')),
)



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
    if marks.get("remarks") not in [None, "", " - "] and not (isinstance(marks.get("remarks"), float) and np.isnan(marks.get("remarks"))):
        html += f"- Trans/Certi Remark   : {marks['remarks']}\n"
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


if __name__ == "__main__":
    reg_no = 'YS-N24/35-3300356/2013'
    r = search_by_reg(reg_no)
