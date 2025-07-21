from database import *

name="SOMNATH SAMADDER"
with open('session.json','r') as f:
    data = json.load(f)
sessions = data.get('sessions')
sessions.sort(key=lambda x: x[0])
ses = [s[0] for s in sessions]
all_stu={}
for i in ses:
    dbname = 'N24'+str(i)
    formrecv = mongo_client[dbname]['FORMRECV'].find({'name':name},{'_id':0,'name':1,'dob':1,'f_name':1,'reg_no':1}).to_list()
    if not (formrecv == []):
        all_stu[i]=formrecv
print(all_stu)