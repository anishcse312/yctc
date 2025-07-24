from database import *
import numpy as np
reg = "YS-N24/78-7600081/2024"

def search_by_reg(reg: str):
    regno = reg.split('/')[1]
    ses, no = regno.split('-')
    dbname = 'N24'+str(ses)

    stuadmn = mongo_client[dbname]['STUADMN'].find_one({'reg_no':reg},{'_id':0,'name':1,'f_name':1,"course_id":1,"batch":1,"scholar":1,"lateral":1,'OtherYCTC':1,'FrontLine':1,"pre_reg":1,"remarks":1})
    formrecv =mongo_client[dbname]['FORMRECV'].find_one({'reg_no':reg},{'_id':0,"sex":1,"caste":1,"dob":1,"add_1":1,"add_2":1,"po":1,"district":1,"pin":1,"phone":1,"mobile":1,"GQ1":1,'GQ2':1,'GQ3':1,'GQ4':1,'TQ':1,"remarks":1})
    receipts = list(mongo_client[dbname]['RECEIPT'].find({'reg_no':reg},{'_id':0,"recpt_type":1,"instalment":1,"recptdate":1,"receiptno":1,"amount":1,"remarks":1}))
    marks = mongo_client[dbname]['MARKS'].find_one({'reg_no':reg},{'_id':0,'trans_date':1,'certi_date':1,'Remarks':1})
    prev_infos={}
    preg = stuadmn['pre_reg']
    i=0
    while (True):
        if preg is None or (isinstance(preg, float) and np.isnan(preg)):
            break
        preg = str(preg).strip()
        i+=1
        ses1, no1 = ((preg.split('/'))[1]).split('-')
        dbname1 = 'N24'+str(ses1)
        marks1 = mongo_client[dbname1]['MARKS'].find_one({'reg_no':preg},{'_id':0,'p1s1':1,'p2s1':1,'p3s1':1,'grade':1,'trans_date':1,'certi_date':1,'Remarks':1})
        stuadmn1 = mongo_client[dbname1]['STUADMN'].find_one({'reg_no':preg},{'_id':0,'pre_reg':1,'course_id':1,'batch':1,'scholar':1,'lateral':1,'OtherYCTC':1,'FrontLine':1,'reg_no':1})
        prev_infos[i]={'marks':marks1,'stuadmn':stuadmn1}
        preg = stuadmn1['pre_reg']
    
    return prev_infos

print(search_by_reg(reg))
