import MySQLdb as db
import sqlite3
from pandas import DataFrame
from pandas.io.sql import read_frame,write_frame
from pandas.io.pytables import HDFStore

dbname = 'coursera_eventing_12-002-ml'
tablename = 'videos'

print 'starting'
database = db.connect(host='datastage.stanford.edu', user='gkovacs', passwd='gkovacs_12956', db=dbname)
#sqlitedb = sqlite3.connect(dbname + '.sqlite3')
h5db = HDFStore(dbname + '.h5', 'w')

print 'reading num rows'
num_rows = int([x for i,x in read_frame('select count(*) from ' + tablename, database)[['count(*)']].itertuples()][0])

start_row = 0
step_size = 10000
end_row = min(num_rows, start_row + step_size)
#num_rows = 50000
while True:
  print start_row, 'of', num_rows
  data = read_frame('select * from ' + tablename + ' limit ' + str(start_row) + ',' + str(step_size), database)
  #print data
  #data.to_hdf(dbname + '.h5', tablename)
  h5db.append(tablename, data, min_itemsize = 255)
  if end_row >= num_rows:
    break
  start_row += step_size
  end_row += step_size

#data = read_frame('select * from ' + tablename, database)
#h5db[tablename] = data
#h5db.close()
#data.to_hdf(dbname + '.h5', tablename)

#write_frame(data, name=tablename, con=sqlitedb)
