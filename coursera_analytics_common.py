#!/usr/bin/env python
# md5: 6a153f4264440ad6b72ef56258965664
# coding: utf-8

try:
  import MySQLdb
except:
  import pymysql as MySQLdb
import sqlite3
import json
import gzip
import os
import cPickle as pickle

from memoized import memoized

# For autoreloading of modules (%autoreload, %aimport)    
import video_annotations
reload(video_annotations)
import video_annotations
from video_annotations import ml_004 as vid

from json import loads, dumps

from pandas import DataFrame
from pandas.io.sql import read_frame, write_frame

datastage_login = json.load(open('datastage_login.json'))

from memoized import memoized

#database = MySQLdb.connect(host='datastage.stanford.edu', user=datastage_login['user'], passwd=datastage_login['passwd'])


databases = {}

from get_database_name import *

#databasename = 'ml-004_clickstream_video.sqlite'
tablename = 'videos'

def listVideosReal(dbname):
  output_set = set()
  output = []
  for lecture_id in listDistinct('lecture_id'):
    if lecture_id not in output_set:
      output_set.add(lecture_id)
      output.append(lecture_id)
  return sorted(output)

@memoized
def listVideosJsonMemoized(dbname):
  jsonfile = dbname + '_videolist.json'
  if not os.path.exists(jsonfile):
    json.dump(listVideosReal(dbname), open(jsonfile, 'w'))
  return json.load(open(jsonfile))

def listVideos():
  return listVideosJsonMemoized(getDatabaseName())

def getTableName():
  return tablename

def getDatabasePath():
  return '/lfs/local/0/geza/' + databasename

def getDatabaseNameForLectureNum(lectureid):
  return getDatabaseName().replace('.sqlite', '_lecture-' + str(lectureid) + '.sqlite')

def getDatabasePathForLectureNum(lectureid):
  return getDatabasePath().replace('.sqlite', '_lecture-' + str(lectureid) + '.sqlite')

def getDatabaseNameForLectureNumAndUser(lectureid, userid):
  return getDatabaseName().replace('.sqlite', '_lecture-' + str(lectureid) + '_user-' + str(userid) + '.sqlite')

def getDatabasePathForLectureNumAndUser(lectureid, userid):
  return getDatabasePath().replace('.sqlite', '_lecture-' + str(lectureid) + '_user-' + str(userid) + '.sqlite')

def getColumns():
  return list(read_frame("select * from " + getTableName() + " limit 1", getDatabase()).columns.values)

def getDatabase():
  if databasename not in databases and 'sqlite' in databasename:
    databases[databasename] = sqlite3.connect('/lfs/local/0/geza/' + databasename)
  elif databasename not in databases:
    MySQLdb.connect(host='datastage.stanford.edu', user=datastage_login['user'], passwd=datastage_login['passwd'], db=databasename)
  return databases[databasename]

def getDatabaseForLectureNum(lectureid):
  if 'sqlite' not in databasename:
    raise Exception('can only use getDatabaseForLectureNum feature on sqlite databases')
  real_database_name = getDatabasePathForLectureNum(lectureid)
  if real_database_name not in databases:
    databases[real_database_name] = sqlite3.connect(real_database_name)
  return databases[real_database_name]

def getDatabaseForLectureNumAndUser(lectureid, userid):
  if 'sqlite' not in databasename:
    raise Exception('can only use getDatabaseForLectureNumAndUser feature on sqlite databases')
  real_database_name = getDatabasePathForLectureNumAndUser(lectureid, userid)
  if real_database_name not in databases:
    databases[real_database_name] = sqlite3.connect(real_database_name)
  return databases[real_database_name]

def listDistinctForDatabase(fieldname, database_instance, extraquery=''):
  data = read_frame("select distinct " + fieldname + " from " + getTableName() + " " + extraquery, database_instance)
  return [x[0] for x in data[[fieldname]].itertuples(index=False)]

def listDistinct(fieldname, extraquery=''):
  return listDistinctForDatabase(fieldname, getDatabase(), extraquery)

def listDistinctForLecture(fieldname, lectureid, extraquery=''):
  if not os.path.exists(getDatabasePathForLectureNum(lectureid)):
    cacheLecture(lectureid)
  return listDistinctForDatabase(fieldname, getDatabaseForLectureNum(lectureid), extraquery)

def listFieldsForDatabase(fieldnames, database_instance, extraquery=''):
  fieldnameString = ','.join(fieldnames)
  data = read_frame("select " + fieldnameString + " from " + getTableName() + " " + extraquery, database_instance)
  return data.itertuples(index=False)

def listFields(fieldnames, extraquery=''):
  return listFieldsForDatabase(fieldnames, getDatabase(), extraquery)

def cacheLecture(lectureid):
  if os.path.exists(getDatabasePathForLectureNum(lectureid)):
    return
  print 'caching lecture:', lectureid
  data = read_frame('select * from ' + getTableName() + ' where lecture_id=' + str(lectureid), getDatabase())
  write_frame(data, getTableName(), getDatabaseForLectureNum(lectureid))

def listFieldsForLecture(fieldnames, lectureid, extraquery=''):
  if not os.path.exists(getDatabasePathForLectureNum(lectureid)):
    cacheLecture(lectureid)
  return listFieldsForDatabase(fieldnames, getDatabaseForLectureNum(lectureid), extraquery)

@memoized
def getFrameForLectureReal(dbmame, lectureid):
  if not os.path.exists(getDatabasePathForLectureNum(lectureid)):
    cacheLecture(lectureid)
  return read_frame('select * from ' + getTableName(), getDatabaseForLectureNum(lectureid))

def getFrameForLecture(lectureid):
  return getFrameForLectureReal(getDatabaseName(), lectureid)

@memoized
def getUserToEventsForLectureReal(dbname, lectureid):
  lecture_frame = getFrameForLectureReal(dbname, lectureid)
  return frameToDictByKey(lecture_frame, 'anon_username')

def getFrameForLectureUser(lectureid, userid):
  user_to_events = getUserToEventsForLectureReal(getDatabaseName(), lectureid)
  if userid in user_to_events:
    return user_to_events[userid]
  else:
    return None

def frameToDictByKey(frame, key):
  output = {}
  for k,grouped_frame in frame.groupby(key):
    output[k] = grouped_frame
  return output

#def cacheLectureUser(lectureid, userid):
#  #if os.path.exists(getDatabasePathForLectureNumAndUser(lectureid, userid)):
#  #  return
#  print 'caching lecture and user id:', lectureid, userid
#  #data = read_frame('select * from ' + getTableName() + ' where lecture_id=' + str(lectureid) + ' and anon_username="' + str(userid) + '"', getDatabaseForLectureNum(lectureid))
#  #frame = getFrameForLecture(lectureid)
#  #data = frame[frame.anon_username == userid]
#  data = getFrameForLectureAndUser(lectureid, userid)
#  #write_frame(data, getTableName(), getDatabaseForLectureNumAndUser(lectureid, userid))


def getLectureEndTime(lectureid):
  pause_to_counts = {}
  lecture_end_time = 0
  for event_type,curr_time in listFieldsForLecture(['event_type', 'curr_time'], lectureid, 'where event_type="pause"'):
    if curr_time > 3600: # there are no lectures more than an hour long, if have such a result is bugggy data
      continue
    if curr_time not in pause_to_counts:
      pause_to_counts[curr_time] = 1
    else:
      pause_to_counts[curr_time] += 1
    if pause_to_counts[curr_time] >= 10:
      lecture_end_time = max(curr_time, lecture_end_time)
  return lecture_end_time

def getLectureEndTimesReal(dbname):
  output = {}
  for lectureid in listVideos():
    output[lectureid] = getLectureEndTime(lectureid)
  return output

@memoized
def getLectureEndTimesJsonMemoized(dbname):
  jsonfile = dbname + '_videoendtimes.pickle'
  if not os.path.exists(jsonfile):
    pickle.dump(getLectureEndTimesReal(dbname), open(jsonfile, 'w'))
  return pickle.load(open(jsonfile))

def getLectureEndTimes():
  return getLectureEndTimesJsonMemoized(getDatabaseName())


def getUsersWhoWatchedLecture(lectureid):
  return listDistinctForLecture('anon_username', lectureid)

def getLecturesToViewersReal(dbname):
  output = {}
  for lectureid in listVideos():
    output[lectureid] = getUsersWhoWatchedLecture(lectureid)
  return output

'''
@memoized
def getLecturesToViewersJsonMemoized(dbname):
  jsonfile = dbname + '_lecturestoviewers.pickle'
  if not os.path.exists(jsonfile):
    pickle.dump(getLecturesToViewersReal(dbname), open(jsonfile, 'w'))
  return pickle.load(open(jsonfile))
'''

@memoized
def getLecturesToViewersJsonMemoized(dbname):
  jsonfile = dbname + '_lecturestoviewers.json'
  if not os.path.exists(jsonfile):
    json.dump(getLecturesToViewersReal(dbname), open(jsonfile, 'w'))
  return json.load(open(jsonfile))

def getLecturesToViewers():
  return getLecturesToViewersJsonMemoized(getDatabaseName())

def getViewersToLecturesReal(dbname):
  output = {}
  for lectureid,users in getLecturesToViewers().iteritems():
    for user in users:
      if user not in output:
        output[user] = []
      else:
        output[user].append(lectureid)
  return output

'''
@memoized
def getViewersToLecturesJsonMemoized(dbname):
  jsonfile = dbname + '_viewerstolectures.pickle'
  if not os.path.exists(jsonfile):
    pickle.dump(getViewersToLecturesReal(dbname), open(jsonfile, 'w'))
  return pickle.load(open(jsonfile))
'''

@memoized
def getViewersToLecturesJsonMemoized(dbname):
  jsonfile = dbname + '_viewerstolectures.json'
  if not os.path.exists(jsonfile):
    json.dump(getViewersToLecturesReal(dbname), open(jsonfile, 'w'))
  return json.load(open(jsonfile))

def getViewersToLectures():
  return getViewersToLecturesJsonMemoized(getDatabaseName())

@memoized
def getViewersWhoWatchedMostLecturesReal(dbname):
  output = []
  numlectures = len(listVideos())
  for user,lectures_watched in getViewersToLectures().iteritems():
    if len(lectures_watched) >= numlectures/2:
      output.append(user)
  return output

def getViewersWhoWatchedMostLectures():
  return getViewersWhoWatchedMostLecturesReal(getDatabaseName())

@memoized
def getViewersWhoWatchedMostLecturesSetReal(dbname):
  return frozenset(getViewersWhoWatchedMostLecturesReal(dbname))

def getViewersWhoWatchedMostLecturesSet():
  return getViewersWhoWatchedMostLecturesSetReal(getDatabaseName())

#print len(getViewersToLectures().keys())
#print len(getViewersWhoWatchedMostLectures())


from navigation_events import *

from math import isnan

num_data_exceptions = 0
    
def getNumDataExceptions():
  return num_data_exceptions

def resetNumDataExceptions():
  global num_data_exceptions
  num_data_exceptions = 0

class DataException(Exception):
  def __init__(self, message):
    # Call the base class constructor with the parameters it needs
    global num_data_exceptions
    num_data_exceptions += 1
    Exception.__init__(self, message)

def extractAllEvents(frame, ignore_errors=False):
  output = []
  prev_timestamp = None
  prev_curr_time = None
  playback_rate = 1.0
  paused = 0
  for index,row in frame.iterrows():
    if prev_timestamp != None:
      assert row['event_timestamp'] >= prev_timestamp # needs to be sorted
    if row['event_type'] == 'play':
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      if not isnan(row['playback_rate']) and 0.75 <= row['playback_rate'] <= 2.0:
        playback_rate = row['playback_rate']
      #paused = row['paused']
      #assert paused == 0
      paused = 0
      output.append(PlayEvent(row['event_timestamp'], row['curr_time'], playback_rate))
    if row['event_type'] == 'ratechange':
      playback_rate = row['playback_rate']
      if isnan(playback_rate) or not 0.75 <= playback_rate <= 2.0:
        if ignore_errors:
          continue
        raise DataException('incorrect playback rate - ' + str(playback_rate))
      #assert not isnan(playback_rate) and 0.75 <= playback_rate <= 2.0, 'playback_rate is ' + str(playback_rate)
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      #paused = row['paused']
      #assert not isnan(paused)
      output.append(RateChangeEvent(row['event_timestamp'], row['curr_time'], playback_rate, paused))
    if row['event_type'] == 'pause':
      #paused = row['paused']
      #assert paused == 1, 'expected paused to be 1, is actually ' + str(paused)
      paused = 1
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      if not isnan(row['playback_rate']) and 0.75 <= row['playback_rate'] <= 2.0:
        playback_rate = row['playback_rate']
      output.append(PauseEvent(row['event_timestamp'], row['curr_time']))
    if row['event_type'] == 'seeked':
      #assert prev_timestamp != None
      if prev_timestamp == None:
        if ignore_errors:
          continue
        raise DataException('prev_timestamp is None - did not have start event prior to seeked')
      #if prev_timestamp == None: # did not have any start event for user, cannot determine where the seek started! discard it.
      #  prev_timestamp = row['event_timestamp']
      #  prev_curr_time = row['curr_time']
      #  continue
      seek_source = prev_curr_time
      if paused == 0:
        time_since_last_event_milliseconds = row['event_timestamp'] - prev_timestamp
        time_since_last_event_seconds = time_since_last_event_milliseconds / 1000.0
        seconds_video_played_since_last_event = time_since_last_event_seconds * playback_rate
        assert seconds_video_played_since_last_event >= 0, 'time since last event is ' + str(time_since_last_event_seconds) + ' playback rate is ' + str(playback_rate)
        seek_source = prev_curr_time + seconds_video_played_since_last_event
      seekEvent = SeekEvent(row['event_timestamp'], seek_source, row['curr_time'], paused)
      output.append(seekEvent)
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      #paused = row['paused']
      #assert not isnan(paused)
  return output

def extractSeekEvents(frame):
  output = []
  prev_timestamp = None
  prev_curr_time = None
  playback_rate = 1.0
  paused = True
  for index,row in frame.iterrows():
    if prev_timestamp != None:
      assert row['event_timestamp'] >= prev_timestamp # needs to be sorted
    if row['event_type'] == 'play':
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      if not isnan(row['playback_rate']) and 0.75 <= row['playback_rate'] <= 2.0:
        playback_rate = row['playback_rate']
      #paused = row['paused']
      #assert paused == 0
      paused = False
    if row['event_type'] == 'ratechange':
      playback_rate = row['playback_rate']
      if isnan(playback_rate) or not 0.75 <= playback_rate <= 2.0:
        raise DataException('incorrect playback rate - ' + str(playback_rate))
      #assert not isnan(playback_rate) and 0.75 <= playback_rate <= 2.0, 'playback_rate is ' + str(playback_rate)
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      #paused = row['paused']
      #assert not isnan(paused)
    if row['event_type'] == 'pause':
      #paused = row['paused']
      #assert paused == 1, 'expected paused to be 1, is actually ' + str(paused)
      paused = True
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      if not isnan(row['playback_rate']) and 0.75 <= row['playback_rate'] <= 2.0:
        playback_rate = row['playback_rate']
    if row['event_type'] == 'seeked':
      #assert prev_timestamp != None
      if prev_timestamp == None:
        raise DataException('prev_timestamp is None - did not have start event prior to seeked')
      #if prev_timestamp == None: # did not have any start event for user, cannot determine where the seek started! discard it.
      #  prev_timestamp = row['event_timestamp']
      #  prev_curr_time = row['curr_time']
      #  continue
      seek_source = prev_curr_time
      if paused == 0:
        time_since_last_event_milliseconds = row['event_timestamp'] - prev_timestamp
        time_since_last_event_seconds = time_since_last_event_milliseconds / 1000.0
        seconds_video_played_since_last_event = time_since_last_event_seconds * playback_rate
        assert seconds_video_played_since_last_event >= 0, 'time since last event is ' + str(time_since_last_event_seconds) + ' playback rate is ' + str(playback_rate)
        seek_source = prev_curr_time + seconds_video_played_since_last_event
      seekEvent = SeekEvent(row['event_timestamp'], seek_source, row['curr_time'], paused, row['anon_username'])
      #print seekEvent
      #break
      output.append(seekEvent)
      prev_timestamp = row['event_timestamp']
      prev_curr_time = row['curr_time']
      #paused = row['paused']
      #assert not isnan(paused)
  return output

def groupEventsAsPlaySpans(all_events):
  output = []
  playback_rate = 1.0
  play_start = None
  play_start_timestamp = None
  paused = True
  for event in all_events:
    if event.event_type == 'play':
      paused = False
      play_start = event.start
      play_start_timestamp = event.timestamp
      playback_rate = event.playback_rate
    elif event.event_type == 'pause':
      if not paused:
        playSpan = PlaySpan(play_start_timestamp, event.timestamp, play_start, event.start, playback_rate)
        output.append(playSpan)
      play_start = None
      play_start_timestamp = None
      paused = True
    elif event.event_type == 'seeked':
      if not paused:
        playSpan = PlaySpan(play_start_timestamp, event.timestamp, play_start, event.start, playback_rate)
        output.append(playSpan)
      #paused = event.paused
      if not paused:
        play_start = event.end
        play_start_timestamp = event.timestamp
    elif event.event_type == 'ratechange':
      if not paused:
        playSpan = PlaySpan(play_start_timestamp, event.timestamp, play_start, event.start, playback_rate)
        output.append(playSpan)
      playback_rate = event.playback_rate
      #paused = event.paused
    else:
      assert False, 'unexpected event type in groupEventsAsPlaySpans: ' + event.event_type
  return output

'''
#frame = getFrameForLectureUser(1, 'abcea9860ecfb2fef5140bc9e504f529ed33eb39')
#print frame.sort('event_timestamp')
#print frame
idx = 0
for user in getViewersToLectures().keys():
  frame = getFrameForLectureUser(1, user)
  if type(frame) == type(None):
    continue
  if frame.empty:
    continue
  if frame.index == None:
    continue
  if len(frame.index) <= 2:
    continue
  frame = frame.sort('event_timestamp')
  seek_events = extractSeekEvents(frame)
  print groupSeekEventsAsSeekChains(seek_events)
  idx += 1
  if idx > 100:
    break
'''


from coursera_lib_common import parseOptions

def incrementPartsSkippedForwardOver(seek_chain, output):
  if seek_chain.direction != 'forward':
    return
  if not 0 <= int(round(seek_chain.end)) < len(output):
    return
  if not 0 <= int(round(seek_chain.start)) < len(output):
    return
  for i in range(int(round(seek_chain.start)), int(round(seek_chain.end))):
    if not 0 <= i < len(output):
      continue
    output[i] += 1

def getLectureLength(lecture_id):
  if lecture_id in video_annotations.video_lengths_ml_004:
    return video_annotations.video_lengths_ml_004[lecture_id]
  return getLectureEndTimes()[lecture_id]

'''
def getPartsSkippedForwardOver(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      incrementPartsSkippedForwardOver(seek_chain, output)
    if successful_users != None:
      successful_users.add(user)
  return output
'''

def getPartsSkippedForwardOver(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist,filter_func = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    try:
      seek_events = extractSeekEventsForUserInLecture(lecture_id, user, filter_func)
      if seek_events == None:
        continue
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      incrementPartsSkippedForwardOver(seek_chain, output)
    if successful_users != None:
      successful_users.add(user)
  return output


def incrementPartsSkippedBackOver(seek_chain, output):
  if seek_chain.direction != 'back':
    return
  if not 0 <= int(round(seek_chain.end)) < len(output):
    return
  if not 0 <= int(round(seek_chain.start)) < len(output):
    return
  for i in range(int(round(seek_chain.end)), int(round(seek_chain.start))):
    if not 0 <= i < len(output):
      continue
    output[i] += 1

'''
def getPartsSkippedBackOver(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      incrementPartsSkippedBackOver(seek_chain, output)
    if successful_users != None:
      successful_users.add(user)
  return output
'''

def getPartsSkippedBackOver(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist,filter_func = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    try:
      seek_events = extractSeekEventsForUserInLecture(lecture_id, user, filter_func)
      if seek_events == None:
        continue
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      incrementPartsSkippedBackOver(seek_chain, output)
    if successful_users != None:
      successful_users.add(user)
  return output

def incrementPartsPlayed(play_span, output):
  assert play_span.end >= play_span.start, 'play span end is ' + str(play_span.end) + ' while start is ' + str(play_span.start)
  if not 0 <= int(round(play_span.end)) < len(output):
    return
  if not 0 <= int(round(play_span.start)) < len(output):
    return
  for i in range(int(round(play_span.start)), int(round(play_span.end))):
    if not 0 <= i < len(output):
      continue
    output[i] += 1

def extractSeekEventsForUserInLecture(lecture_id, user_id, filter_func=None):
  frame = getFrameForLectureUser(lecture_id, user_id)
  if type(frame) == type(None):
    return None
  if frame.empty:
    return None
  frame = frame.sort('event_timestamp')
  all_events = extractSeekEvents(frame)
  if filter_func == None:
    return all_events
  return filter_func(all_events, lecture_id, user_id)
    
def extractAllEventsForUserInLecture(lecture_id, user_id, filter_func=None, ignore_errors=False):
  frame = getFrameForLectureUser(lecture_id, user_id)
  if type(frame) == type(None):
    return None
  if frame.empty:
    return None
  frame = frame.sort('event_timestamp')
  all_events = extractAllEvents(frame, ignore_errors=ignore_errors)
  if filter_func == None:
    return all_events
  return filter_func(all_events, lecture_id, user_id)

'''
def getPartsPlayed(lecture_id, **kwargs):
  #skipped_users,successful_users,user_whitelist,filter_func,limitnum = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func', 'limitnum'])
  lecture_id = 13
  lecture_length = 600 #getLectureLength(lecture_id)
  limitnum = 100
  output = [0]*int(round(lecture_length+1))
  usernum = 0
  for user in getViewersToLectures().keys():
    usernum += 1
    if usernum == 22:
      print 'user 22!'
    if usernum > limitnum:
      break
    try:
      all_events = extractAllEventsForUserInLecture(lecture_id, user, None)
      if all_events == None:
        continue
    except:
      #print 'exception!'
      continue
    play_spans = groupEventsAsPlaySpans(all_events)
    skip_user = False
    for playspan in play_spans:
      if not playspan.end >= playspan.start:
        skip_user = True
    if skip_user:
      continue
    print len(play_spans)
    for playspan in play_spans:
      incrementPartsPlayed(playspan, output)
  return output
'''

def getPartsPlayedMoreThanOnce(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist,filter_func,limitnum = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func', 'limitnum'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  usernum = 0
  for user in getViewersToLectures().keys():
    usernum += 1
    if limitnum and usernum > limitnum:
      break
    try:
      all_events = extractAllEventsForUserInLecture(lecture_id, user, filter_func)
      if all_events == None:
        continue
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    play_spans = groupEventsAsPlaySpans(all_events)
    skip_user = False
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        skip_user = True
    if skip_user:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    user_seen_once = [0]*int(round(lecture_length+1))
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        continue
      #incrementPartsPlayed(play_span, output)
      if round(play_span.end) >= len(output):
        continue
      if play_span.start < 0:
        continue
      for i in range(int(round(play_span.start)), int(round(play_span.end))):
        if user_seen_once[i] == 0:
          user_seen_once[i] = 1
        else:
          output[i] += 1
    if successful_users != None:
      successful_users.add(user)
  return output

def getPartsPlayedOncePerUser(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist,filter_func,limitnum = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func', 'limitnum'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  usernum = 0
  for user in getViewersToLectures().keys():
    usernum += 1
    if limitnum and usernum > limitnum:
      break
    try:
      all_events = extractAllEventsForUserInLecture(lecture_id, user, filter_func)
      if all_events == None:
        continue
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    play_spans = groupEventsAsPlaySpans(all_events)
    skip_user = False
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        skip_user = True
    if skip_user:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    user_seen_once = [0]*int(round(lecture_length+1))
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        continue
      #incrementPartsPlayed(play_span, output)
      if round(play_span.end) >= len(output):
        continue
      if play_span.start < 0:
        continue
      for i in range(int(round(play_span.start)), int(round(play_span.end))):
        if user_seen_once[i] == 0:
          user_seen_once[i] = 1
          output[i] += 1
        else:
          pass
    if successful_users != None:
      successful_users.add(user)
  return output

def getPartsPlayed(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist,filter_func,limitnum = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist', 'filter_func', 'limitnum'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  usernum = 0
  for user in getViewersToLectures().keys():
    usernum += 1
    if limitnum and usernum > limitnum:
      break
    try:
      all_events = extractAllEventsForUserInLecture(lecture_id, user, filter_func)
      if all_events == None:
        continue
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    play_spans = groupEventsAsPlaySpans(all_events)
    skip_user = False
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        skip_user = True
    if skip_user:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        continue
      if round(play_span.end) >= len(output):
        continue
      if play_span.start < 0:
        continue
      for i in range(int(round(play_span.start)), int(round(play_span.end))):
        output[i] += 1
    if successful_users != None:
      successful_users.add(user)
  return output

'''
def getPartsPlayed(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      all_events = extractAllEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    play_spans = groupEventsAsPlaySpans(all_events)
    skip_user = False
    for play_span in play_spans:
      if not play_span.end >= play_span.start:
        skip_user = True
    if skip_user:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    for play_span in play_spans:
      incrementPartsPlayed(play_span, output)
    if successful_users != None:
      successful_users.add(user)
  return output
'''


def groupSeekEventsAsSeekChains(seek_events):
  output = []
  prev_seek_timestamp = None
  current_seek_chain = []
  for seek_event in seek_events:
    if prev_seek_timestamp == None:
      prev_seek_timestamp = seek_event.timestamp
      current_seek_chain.append(seek_event)
    else:
      if seek_event.timestamp - prev_seek_timestamp > 5000: # has been at least 5 seconds since last seek, create new seek chain
        if len(current_seek_chain) > 0:
          output.append(SeekChain(current_seek_chain))
          current_seek_chain = []
        current_seek_chain.append(seek_event)
        prev_seek_timestamp = seek_event.timestamp
      else: # existing seek chain
        current_seek_chain.append(seek_event)
        prev_seek_timestamp = seek_event.timestamp
  if len(current_seek_chain) > 0:
    seek_chain = SeekChain(current_seek_chain)
    output.append(seek_chain)
    current_seek_chain = []
  return output

def getSeekChains(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  #lecture_length = getLectureLength(lecture_id)
  lecture_length = vid.video_lengths[lecture_id]
  output = []
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      if 0 <= seek_chain.start < lecture_length and 0 <= seek_chain.end < lecture_length:
        output.append(seek_chain)
  return output

def getSeekChainsToTwoArrays(lecture_id):
  seekchains = getSeekChains(lecture_id)
  starts = []
  ends = []
  for elem in seekchains:
    starts.append(round(elem.start))
    ends.append(round(elem.end))
  return starts,ends

def getSeekSources(lecture_id, start, end, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      if start <= seek_chain.end <= end:
        if 0 <= int(round(seek_chain.start)) < len(output):
          output[int(round(seek_chain.start))] += 1
    if successful_users != None:
      successful_users.add(user)
  return output

def getAllSeekSources(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      #if start <= seek_chain.end <= end:
      if True:
        if 0 <= int(round(seek_chain.start)) < len(output):
          output[int(round(seek_chain.start))] += 1
    if successful_users != None:
      successful_users.add(user)
  return output

def getSeekDestinations(lecture_id, start, end, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      if start <= seek_chain.start <= end:
        if 0 <= int(round(seek_chain.end)) < len(output):
          output[int(round(seek_chain.end))] += 1
    if successful_users != None:
      successful_users.add(user)
  return output

def getAllSeekDestinations(lecture_id, **kwargs):
  skipped_users,successful_users,user_whitelist = parseOptions(kwargs, ['skipped_users', 'successful_users', 'user_whitelist'])
  lecture_length = getLectureLength(lecture_id)
  output = [0]*int(round(lecture_length+1))
  for user in getViewersToLectures().keys():
    frame = getFrameForLectureUser(lecture_id, user)
    if type(frame) == type(None):
      continue
    if frame.empty:
      continue
    frame = frame.sort('event_timestamp')
    try:
      seek_events = extractSeekEvents(frame)
    except DataException as e:
      if skipped_users != None:
        skipped_users.add(user)
      continue
    seek_chains = groupSeekEventsAsSeekChains(seek_events)
    for seek_chain in seek_chains:
      #if start <= seek_chain.start <= end:
      if True:
        if 0 <= int(round(seek_chain.end)) < len(output):
          output[int(round(seek_chain.end))] += 1
    if successful_users != None:
      successful_users.add(user)
  return output


@memoized
def getFirstViewEventTimestampForUserInLecture(lecture_id, user_id):
  frame = getFrameForLectureUser(lecture_id, user_id)
  if type(frame) == type(None):
    return None
  if frame.empty:
    return None
  frame = frame.sort('event_timestamp')
  for index,row in frame.iterrows():
    return row['event_timestamp']

def filterReviewSessionOnly(events, lecture_id, user_id):
  start_timestamp = getFirstViewEventTimestampForUserInLecture(lecture_id, user_id)
  if start_timestamp == None:
    return None
  minimum_review_timestamp = start_timestamp + 3600 * 1000
  output = []
  for event in events:
    if event.timestamp >= minimum_review_timestamp:
      output.append(event)
  return output

