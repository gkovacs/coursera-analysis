import MySQLdb
import sqlite3

from pandas.io.sql import read_frame

import json

datastage_login = json.load(open('datastage_login.json'))

databases = {}
tablename = 'VideoInteraction'
databasename = 'Edx'

def getTableName():
  return tablename

def getDatabaseName():
  return databasename

def getDatabase():
  if databasename not in databases:
    databases[databasename] = MySQLdb.connect(host='datastage.stanford.edu', user=datastage_login['user'], passwd=datastage_login['passwd'], db=databasename)
  return databases[databasename]

data = read_frame('select * from ' + getTableName() + ' limit 100', getDatabase())
print data
