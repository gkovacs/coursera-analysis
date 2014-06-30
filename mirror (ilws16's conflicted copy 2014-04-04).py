import MySQLdb as db
import sqlite3
from pandas import DataFrame
from pandas.io.sql import read_frame,write_frame
from pandas.io.pytables import HDFStore

dbname = 'coursera_eventing_12-002-ml'
tablename = 'videos'

database = db.connect(host='datastage.stanford.edu', user='gkovacs', passwd='gkovacs_12956', db=dbname)
#sqlitedb = sqlite3.connect(dbname + '.sqlite3')
#h5db = HDFStore(dbname + '.h5', 'w')
data = read_frame('select * from ' + tablename + ' limit 1000', database)
#h5db[tablename] = data
#h5db.close()
data.to_hdf(dbname + '.h5', tablename)
#write_frame(data, name=tablename, con=sqlitedb)
