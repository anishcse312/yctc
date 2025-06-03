from database import *

a = admins.find_one({'firstName':'Aayush'},{'_id':0})
print(a)