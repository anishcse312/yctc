from database import *
import numpy as np
reg = "YS-N24/79-7900067/2024"
regno = reg.split('/')[1]
ses, no = regno.split('-')
dbname = 'N24'+str(ses)

stuadmn = mongo_client[dbname]['STUADMN'].find_one({'reg_no':reg},{'_id':0,'name':1,'f_name':1,"course_id":1,"batch":1,"scholar":1,"lateral":1,'OtherYCTC':1,'FrontLine':1,"pre_reg":1,"remarks":1})
formrecv =mongo_client[dbname]['FORMRECV'].find_one({'reg_no':reg},{'_id':0,"sex":1,"caste":1,"dob":1,"add_1":1,"add_2":1,"po":1,"district":1,"pin":1,"phone":1,"mobile":1,"GQ1":1,'GQ2':1,'GQ3':1,'GQ4':1,'TQ':1,"remarks":1})
receipts = list(mongo_client[dbname]['RECEIPT'].find({'reg_no':reg},{'_id':0,"recpt_type":1,"instalment":1,"recptdate":1,"receiptno":1,"amount":1,"remarks":1}))

print("STUADMN: ")
print(stuadmn)
print()

print("formrecv: ")
print(formrecv)
print()

print("receipts:")
print(receipts)
print()

