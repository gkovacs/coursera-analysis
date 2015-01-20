#!/usr/bin/env python
# md5: d2e5c6308304a98f68de8dac5eaba167
# coding: utf-8

import json
import os
from memoized import memoized
from get_database_name import getDatabaseName

@memoized
def getViewersToLecturesJsonMemoized(dbname):
  jsonfile = dbname + '_viewerstolectures.json'
  if not os.path.exists(jsonfile):
    raise "missing: " + jsonfile
    #json.dump(getViewersToLecturesReal(dbname), open(jsonfile, 'w'))
  return json.load(open(jsonfile))

def getViewersToLectures():
  return getViewersToLecturesJsonMemoized(getDatabaseName())

@memoized
def getLecturesToViewersJsonMemoized(dbname):
  jsonfile = dbname + '_lecturestoviewers.json'
  if not os.path.exists(jsonfile):
    raise 'missing: ' + jsonfile
    #json.dump(getLecturesToViewersReal(dbname), open(jsonfile, 'w'))
  return json.load(open(jsonfile))

def getLecturesToViewers():
  return getLecturesToViewersJsonMemoized(getDatabaseName())

