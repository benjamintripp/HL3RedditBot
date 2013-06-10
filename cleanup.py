#I don't have access to add these queries to be scheduled
#basicaly each week store the current contents of the already updated table
#delete out week old post ids and repoplulate the cleanup table

import pymysql


db = pymysql.connect(host='hostaddress', port=3306, user='username', passwd='password', db='databasename')
cursor = db.cursor()


DELETE = "DELETE FROM hl3bot WHERE PostId in (SELECT * FROM hl3cleanup)"

truncate = "truncate hl3cleanup"

insert = "insert into hl3cleanup (select * from hl3bot)"

cursor.execute(DELETE)
cursor.execute(truncate)
cursor.execute(insert)

db.close()
