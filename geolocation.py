#!/usr/bin/env python
# md5: 5cc73a35e51b3dafc1c1e3cac6059813
# coding: utf-8

import MySQLdb
import sqlite3
import json
import gzip

from ujson import loads

from pandas import DataFrame
from pandas.io.sql import read_frame

#datastage_login = jsonload(open('datastage_login.json'))

#database = MySQLdb.connect(host='datastage.stanford.edu', user=datastage_login['user'], passwd=datastage_login['passwd'])





geodb_connection = sqlite3.connect('ipdb.sqlite')
geodb_table = 'country_blocks'

def getTableNameSqlite():
  return geodb_table

def getDatabaseSqlite():
  return geodb_connection

def listFieldsSqlite(fieldnames, extraquery=''):
  fieldnameString = ','.join(fieldnames)
  data = read_frame("select " + fieldnameString + " from " + getTableNameSqlite() + " " + extraquery, getDatabaseSqlite())
  return data.itertuples(index=False)

def numeric_ip_to_address(num):
  base = 16777216 # 256**3
  first = num // base
  num -= first * base
  base = 65536 # 256**2
  second = num // base
  num -= second * base
  base = 256
  third = num // base
  num -= third * base
  fourth = num
  return '.'.join([str(x) for x in first,second,third,fourth])

def address_to_numeric_ip(address):
  num = 0
  base = 1
  for val in reversed(address.split('.')):
    num += base * int(val)
    base *= 256
  return num

def normalize_ip(ip_address):
  return '.'.join([str(int(x)) for x in ip_address.split('.')])

#16777471 -> 1.0.0.255
print numeric_ip_to_address(16777471)
print address_to_numeric_ip('1.0.0.255')

ip_block_to_country_code = {}
country_code_to_name = {}

def joinNums(num1, num2=None, num3=None, num4=None):
  if num4:
    return '.'.join([str(x) for x in [num1,num2,num3,num4]])
  if num3:
    return '.'.join([str(x) for x in [num1,num2,num3]])
  if num2:
    return '.'.join([str(x) for x in [num1,num2]])
  return str(num1)

for country_code,ip_start_str,ip_end_str in listFieldsSqlite(['country_code', 'ip_start_str', 'ip_end_str']):
  ip_start = [int(x) for x in ip_start_str.split('.')]
  ip_end = [int(x) for x in ip_end_str.split('.')]
  if ip_start[0] != ip_end[0]:
    for ip0 in range(ip_start[0], ip_end[0]+1):
      ip_block_to_country_code[joinNums(ip0)] = country_code
  else:
    ip0 = ip_start[0]
    if ip_start[1] != ip_end[1]:
      for ip1 in range(ip_start[1], ip_end[1]+1):
        ip_block_to_country_code[joinNums(ip0,ip1)] = country_code
    else:
      ip1 = ip_start[1]
      if ip_start[2] != ip_end[2]:
        for ip2 in range(ip_start[2], ip_end[2]+1):
          ip_block_to_country_code[joinNums(ip0,ip1,ip2)] = country_code
      else:
        ip2 = ip_start[2]
        if ip_start[3] != ip_end[3]:
          for ip3 in range(ip_start[3], ip_end[3]+1):
            ip_block_to_country_code[joinNums(ip0,ip1,ip2,ip3)] = country_code
        else:
          ip3 = ip_start[3]
          ip_block_to_country_code[joinNums(ip0,ip1,ip2,ip3)] = country_code

def country_code_for_ip(ip_address):
  parts = [int(x) for x in ip_address.split('.')]
  b2 = joinNums(parts[0],parts[1],parts[2])
  if b2 in ip_block_to_country_code:
    return ip_block_to_country_code[b2]
  b3 = joinNums(parts[0],parts[1],parts[2],parts[3])
  if b3 in ip_block_to_country_code:
    return ip_block_to_country_code[b3]
  b1 = joinNums(parts[0],parts[1])
  if b1 in ip_block_to_country_code:
    return ip_block_to_country_code[b1]
  b0 = joinNums(parts[0])
  if b0 in ip_block_to_country_code:
    return ip_block_to_country_code[b0]
  raise Exception('no code found for: ' + ip_address)


#print ip_block_to_country_code['128']
#print ip_block_to_country_code['128.12']
#print ip_block_to_country_code['128.12.245']
#print ip_block_to_country_code['128.12.245.5']


print country_code_for_ip('128.12.245.5')



databases = {}

databasename = 'pgm-003_clickstream_video.sqlite'
tablename = 'videos'

def getTableName():
  return tablename

def getDatabaseName():
  return databasename

def getDatabase():
  if databasename not in databases:
    databases[databasename] = sqlite3.connect(databasename) #MySQLdb.connect(host='datastage.stanford.edu', user=datastage_login['user'], passwd=datastage_login['passwd'], db=databasename)
  return databases[databasename]

def listDistinct(fieldname, extraquery=''):
  data = read_frame("select distinct " + fieldname + " from " + getTableName() + " " + extraquery, getDatabase())
  return [x[0] for x in data[[fieldname]].itertuples(index=False)]

def listFields(fieldnames, extraquery=''):
  fieldnameString = ','.join(fieldnames)
  data = read_frame("select " + fieldnameString + " from " + getTableName() + " " + extraquery, getDatabase())
  return data.itertuples(index=False)


get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot
import matplotlib.pylab as pylab
import numpy

def binsum(inp):
  output = []
  for i in range(len(inp)):
    curbin = inp[i-2:i+3]
    val = sum(curbin)
    output.append(val)
  return output

def barPlotWithStderr(means, stderrs=None, x_tick_labels=None, xlabel='', ylabel='', title='', addLabels=True):
    if stderrs:
        assert len(means) == len(stderrs)
    if x_tick_labels:
        assert len(means) == len(x_tick_labels)
        x_tick_labels = [str(x) for x in x_tick_labels]
    else:
        x_tick_labels = [str(x) for x in range(len(means))]
    N = len(means)
    ind = numpy.arange(N) # the x locations for the groups
    width = 0.35 # the width of the bars
    fig, ax = matplotlib.pyplot.subplots()
    if stderrs:
        rects1 = ax.bar(ind, means, width, color='r', yerr=stderrs)
    else:
        rects1 = ax.bar(ind, means, width, color='r')
    
    if ylabel and not title:
        title = ylabel
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xticks(ind+width)
    ax.set_xticklabels( x_tick_labels )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            #ax.text('foobar', 1.05*height, '%d'%int(height), ha='center', va='bottom')
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height), ha='center', va='bottom')
    if addLabels:
      autolabel(rects1)

def plotBarDictionary(datadict, xlabel='', ylabel='', title='', x_tick_label_map=None):
    keys = datadict.keys()
    keys.sort()
    means = [datadict[k] for k in keys]
    if not x_tick_label_map:
      x_tick_labels = keys
    else:
      x_tick_labels = [x_tick_label_map[key] for key in keys]
    barPlotWithStderr(means, x_tick_labels=x_tick_labels, xlabel=xlabel, ylabel=ylabel, title=title)


def plotEventTimes(target_event_type, dbname, lecturenum):
  global databasename

  databasename = dbname

  user_to_events = {}
  for anon_username,event_timestamp,event_type,curr_time in listFields(['anon_username', 'event_timestamp', 'event_type', 'curr_time'], 'where lecture_id=' + str(lecturenum)):
    if anon_username not in user_to_events:
      user_to_events[anon_username] = []
    user_to_events[anon_username].append((anon_username,event_timestamp,event_type,curr_time))

  videoLength = max([max([int(curr_time) for anon_username,event_timestamp,event_type,curr_time in events]) for user,events in user_to_events.iteritems()])

  numStarts = [0]*(videoLength+1)

  for user,events in user_to_events.iteritems():
    for anon_username,event_timestamp,event_type,curr_time in sorted(events, key=lambda x: x[1]):
      curr_time = int(round(curr_time))
      if event_type == target_event_type:
        if curr_time == 0:
          continue
        numStarts[curr_time] += 1

  matplotlib.pyplot.plot(numStarts)
  matplotlib.pyplot.title(target_event_type + ' events (' + dbname + ' lecture ' + str(lecturenum) + ')')
  matplotlib.pyplot.xlabel('video time, seconds')
  matplotlib.pyplot.ylabel('num ' + target_event_type + ' events at this point')
  matplotlib.pyplot.show()

def plotEventTimesNoDuplicatesPerUser(target_event_type, dbname, lecturenum):
  global databasename

  databasename = dbname

  user_to_events = {}
  for anon_username,event_timestamp,event_type,curr_time in listFields(['anon_username', 'event_timestamp', 'event_type', 'curr_time'], 'where lecture_id=' + str(lecturenum)):
    if anon_username not in user_to_events:
      user_to_events[anon_username] = []
    user_to_events[anon_username].append((anon_username,event_timestamp,event_type,curr_time))

  videoLength = max([max([int(curr_time) for anon_username,event_timestamp,event_type,curr_time in events]) for user,events in user_to_events.iteritems()])

  numStarts = [0]*(videoLength+1)

  for user,events in user_to_events.iteritems():
    numStartsUser = [0]*(videoLength+1)
    for anon_username,event_timestamp,event_type,curr_time in sorted(events, key=lambda x: x[1]):
      if event_type == target_event_type:
        if curr_time == 0:
          continue
        numStartsUser[curr_time] += 1
    for i in range(len(numStarts)):
      if numStartsUser[i] > 0:
        numStarts[i] += 1

  matplotlib.pyplot.plot(numStarts)
  matplotlib.pyplot.title(target_event_type + ' events, no duplicates per user (' + dbname + ' lecture ' + str(lecturenum) + ')')
  matplotlib.pyplot.xlabel('video time, seconds')
  matplotlib.pyplot.ylabel('num ' + target_event_type + ' events at this point (each user counted at most 1 time)')
  matplotlib.pyplot.show()
  
#matplotlib.pyplot.plot(binsum(numStarts))
#matplotlib.pyplot.title('start events within 3 seconds')
#matplotlib.pyplot.xlabel('video time, seconds')
#matplotlib.pyplot.ylabel('num start events from this point (or within 3 seconds)')
#matplotlib.pyplot.show()


def extractPlayedSpans(events, endTime=None):
  isPlaying = False
  playedSpans = []
  playStartTime = 0
  playStartTimeStamp = 0
  prevEventType = ''
  for anon_username,event_timestamp,event_type,curr_time in sorted(events, key=lambda x: x[1]):
    curr_time = int(round(curr_time))
    if event_type == 'play':
      isPlaying = True
      playStartTime = curr_time
      playStartTimeStamp = event_timestamp
    if event_type == 'pause':
      isPlaying = False
      playedSpans.append((playStartTime, curr_time))
    if event_type == 'seeked':
      if isPlaying:
        playDurationMillisecs = event_timestamp - playStartTimeStamp
        playDurationSeconds = int(playDurationMillisecs/1000.0)
        playEndTime = playStartTime + playDurationSeconds
        if (endTime and playEndTime > endTime) or playDurationSeconds > 600:
          isPlaying = False
          continue
        playedSpans.append((playStartTime, playEndTime))
      playStartTime = curr_time
      playStartTimeStamp = event_timestamp
    prevEventType = event_type
  if endTime and isPlaying:
    playedSpans.append((playStartTime, endTime))
  return playedSpans


#plotEventTimes('play', 'pgm-003_clickstream_video.sqlite', 2)
plotEventTimes('play', 'ml-004_clickstream_video.sqlite', 2)


#plotEventTimes('ratechange', 'pgm-003_clickstream_video.sqlite', 2)
plotEventTimes('ratechange', 'ml-004_clickstream_video.sqlite', 2)


def plotSegmentViews(dbname, lecturenum):

  global databasename
  databasename = dbname #'coursera_eventing_pgm-003'

  user_to_events = {}
  for anon_username,event_timestamp,event_type,curr_time in listFields(['anon_username', 'event_timestamp', 'event_type', 'curr_time'], 'where lecture_id=' + str(lecturenum)):
    if anon_username not in user_to_events:
      user_to_events[anon_username] = []
    user_to_events[anon_username].append((anon_username,event_timestamp,event_type,curr_time))
  
  videoLength = max([max([int(curr_time) for anon_username,event_timestamp,event_type,curr_time in events]) for user,events in user_to_events.iteritems()])
  
  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    for start,end in extractPlayedSpans(events, endTime=videoLength):
      #print end, len(numPlayTimes)
      for sec in range(start, end):
        if sec >= len(numPlayTimes) or sec < 0:
          break
        numPlayTimes[sec] += 1
  
  #matplotlib.pyplot.plot(numPlayTimes)
  
  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    for start,end in extractPlayedSpans(events, endTime=None):
      for sec in range(start,end):
        if sec >= len(numPlayTimes) or sec < 0:
          break
        numPlayTimes[sec] += 1
  
  #barPlotWithStderr(numPlayTimes, addLabels=False)
  matplotlib.pyplot.plot(numPlayTimes, label='total num times segment was watched, over all users')

  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    playTimes = [0]*(videoLength+1)
    for start,end in extractPlayedSpans(events, endTime=None):
      for sec in range(start,end):
        if sec >= len(numPlayTimes) or sec < 0:
          break
        playTimes[sec] += 1
        if playTimes[sec] > 1:
          numPlayTimes[sec] += 1
  
  #barPlotWithStderr(numPlayTimes, addLabels=False)
  matplotlib.pyplot.plot(numPlayTimes, label='total number of times video was re-watched, over all users')
  
  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    playTimes = [0]*(videoLength+1)
    for start,end in extractPlayedSpans(events, endTime=None):
      for sec in range(start,end):
        if sec >= len(numPlayTimes) or sec < 0:
          continue
        playTimes[sec] += 1
    for i in range(len(numPlayTimes)):
      if playTimes[i] >= 1:
        numPlayTimes[i] += 1
  
  
  #barPlotWithStderr(numPlayTimes, addLabels=False)
  matplotlib.pyplot.plot(numPlayTimes, label='number unique users who watched the segment at least once')
  
  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    playTimes = [0]*(videoLength+1)
    for start,end in extractPlayedSpans(events, endTime=None):
      for sec in range(start,end):
        if sec >= len(numPlayTimes) or sec < 0:
          continue
        playTimes[sec] += 1
    for i in range(len(numPlayTimes)):
      if playTimes[i] >= 2:
        numPlayTimes[i] += 1
  
  #barPlotWithStderr(numPlayTimes, addLabels=False)
  matplotlib.pyplot.plot(numPlayTimes, label='number unique users who watched the segment at least twice')
  

  numPlayTimes = [0]*(videoLength+1)
  
  for user,events in user_to_events.iteritems():
    playTimes = [0]*(videoLength+1)
    for start,end in extractPlayedSpans(events, endTime=None):
      for sec in range(start,end):
        if sec >= len(numPlayTimes) or sec < 0:
          continue
        playTimes[sec] += 1
    for i in range(len(numPlayTimes)):
      if playTimes[i] == 1:
        numPlayTimes[i] += 1
  
  #barPlotWithStderr(numPlayTimes, addLabels=False)
  matplotlib.pyplot.plot(numPlayTimes, label='number unique users who watched the segment exactly once')  
  
  
  
  matplotlib.pyplot.title('video segments viewed (' + dbname + ' lecture ' + str(lecturenum) + ')')
  matplotlib.pyplot.legend(bbox_to_anchor=(2.3, 0.8))
  matplotlib.pyplot.xlabel('video time, seconds')
  matplotlib.pyplot.ylabel('number of times viewed')
  matplotlib.pyplot.show()


#plotSegmentViews('pgm-003_clickstream_video.sqlite', 2)
plotSegmentViews('ml-004_clickstream_video.sqlite', 50)


lecture_end_times = {}
lecture_pause_to_counts = {}

for event_type,curr_time,lecture_id in listFields(['event_type', 'curr_time', 'lecture_id'], 'where event_type="pause"'):
  if curr_time > 3600: # there are no lectures more than an hour long, if have such a result is bugggy data
    continue
  if lecture_id not in lecture_end_times:
    lecture_end_times[lecture_id] = curr_time
    lecture_pause_to_counts[lecture_id] = {curr_time: 1}
  else:
    if curr_time not in lecture_pause_to_counts[lecture_id]:
      lecture_pause_to_counts[lecture_id][curr_time] = 0
    lecture_pause_to_counts[lecture_id][curr_time] += 1
    if (lecture_pause_to_counts[lecture_id][curr_time] >= 10):
      lecture_end_times[lecture_id] = max(curr_time, lecture_end_times[lecture_id])


numLectures = 0
for lecture_id, in listFields(['max(lecture_id)']):
  numLectures = lecture_id + 1
print numLectures


lecture_to_user_to_playback_rates = [{} for i in range(numLectures)]

for anon_username,event_type,lecture_id,playback_rate in listFields(['anon_username', 'event_type', 'lecture_id', 'playback_rate'], 'where event_type="pause"'):
  if anon_username not in lecture_to_user_to_playback_rates[lecture_id]:
    lecture_to_user_to_playback_rates[lecture_id][anon_username] = []
  lecture_to_user_to_playback_rates[lecture_id][anon_username].append(playback_rate)


print lecture_to_user_to_playback_rates


lecture_to_num_075 = [0]*numLectures
lecture_to_num_100 = [0]*numLectures
lecture_to_num_125 = [0]*numLectures
lecture_to_num_150 = [0]*numLectures
lecture_to_num_175 = [0]*numLectures
lecture_to_num_200 = [0]*numLectures

for lecture in range(len(lecture_to_user_to_playback_rates)):
  for user,playback_rates in lecture_to_user_to_playback_rates[lecture].iteritems():
    for playback_rate in playback_rates:
      if 0.74 <= playback_rate <= 0.76:
        lecture_to_num_075[lecture] += 1
      if 0.99 <= playback_rate <= 1.01:
        lecture_to_num_100[lecture] += 1
      if 1.24 <= playback_rate <= 1.26:
        lecture_to_num_125[lecture] += 1
      if 1.49 <= playback_rate <= 1.51:
        lecture_to_num_150[lecture] += 1
      if 1.74 <= playback_rate <= 1.76:
        lecture_to_num_175[lecture] += 1
      if 1.99 <= playback_rate <= 2.01:
        lecture_to_num_200[lecture] += 1

print 'all lectures'

total_events = sum(lecture_to_num_075) + sum(lecture_to_num_100) + sum(lecture_to_num_125) + sum(lecture_to_num_150) + sum(lecture_to_num_175) + sum(lecture_to_num_200)
print total_events

print sum(lecture_to_num_075), sum(lecture_to_num_075)/float(total_events)
print sum(lecture_to_num_100), sum(lecture_to_num_100)/float(total_events)
print sum(lecture_to_num_125), sum(lecture_to_num_125)/float(total_events)
print sum(lecture_to_num_150), sum(lecture_to_num_150)/float(total_events)
print sum(lecture_to_num_175), sum(lecture_to_num_175)/float(total_events)
print sum(lecture_to_num_200), sum(lecture_to_num_200)/float(total_events)

print 'lectures before 70'

total_events = sum(lecture_to_num_075[:70]) + sum(lecture_to_num_100[:70]) + sum(lecture_to_num_125[:70]) + sum(lecture_to_num_150[70:]) + sum(lecture_to_num_175[:70]) + sum(lecture_to_num_200[:70])
print total_events

print sum(lecture_to_num_075[:70]), sum(lecture_to_num_075[:70])/float(total_events)
print sum(lecture_to_num_100[:70]), sum(lecture_to_num_100[:70])/float(total_events)
print sum(lecture_to_num_125[:70]), sum(lecture_to_num_125[:70])/float(total_events)
print sum(lecture_to_num_150[:70]), sum(lecture_to_num_150[:70])/float(total_events)
print sum(lecture_to_num_175[:70]), sum(lecture_to_num_175[:70])/float(total_events)
print sum(lecture_to_num_200[:70]), sum(lecture_to_num_200[:70])/float(total_events)

print 'lectures after 70'

total_events = sum(lecture_to_num_075[70:]) + sum(lecture_to_num_100[70:]) + sum(lecture_to_num_125[70:]) + sum(lecture_to_num_150[70:]) + sum(lecture_to_num_175[70:]) + sum(lecture_to_num_200[70:])
print total_events

print sum(lecture_to_num_075[70:]), sum(lecture_to_num_075[70:])/float(total_events)
print sum(lecture_to_num_100[70:]), sum(lecture_to_num_100[70:])/float(total_events)
print sum(lecture_to_num_125[70:]), sum(lecture_to_num_125[70:])/float(total_events)
print sum(lecture_to_num_150[70:]), sum(lecture_to_num_150[70:])/float(total_events)
print sum(lecture_to_num_175[70:]), sum(lecture_to_num_175[70:])/float(total_events)
print sum(lecture_to_num_200[70:]), sum(lecture_to_num_200[70:])/float(total_events)


for lecture in range(len(lecture_to_user_to_playback_rates)):
  total_watches = 


pylab.plot(lecture_to_num_075)
pylab.plot(lecture_to_num_100)
pylab.plot(lecture_to_num_125)
pylab.plot(lecture_to_num_150)
pylab.plot(lecture_to_num_175)
pylab.plot(lecture_to_num_200)


def arraySum(l):
  output = None
  for x in l:
    if output == None:
      output = x
    else:
      output = numpy.add(output, x)
  return output

lecture_to_total = arraySum([lecture_to_num_075,lecture_to_num_100,lecture_to_num_125,lecture_to_num_150,lecture_to_num_175,lecture_to_num_200])
lecture_to_frac_075 = numpy.true_divide(lecture_to_num_075, lecture_to_total)
lecture_to_frac_100 = numpy.true_divide(lecture_to_num_100, lecture_to_total)
lecture_to_frac_125 = numpy.true_divide(lecture_to_num_125, lecture_to_total)
lecture_to_frac_150 = numpy.true_divide(lecture_to_num_150, lecture_to_total)
lecture_to_frac_175 = numpy.true_divide(lecture_to_num_175, lecture_to_total)
lecture_to_frac_200 = numpy.true_divide(lecture_to_num_200, lecture_to_total)

pylab.plot(lecture_to_frac_075)
pylab.plot(lecture_to_frac_100)
pylab.plot(lecture_to_frac_125)
pylab.plot(lecture_to_frac_150)
pylab.plot(lecture_to_frac_175)
pylab.plot(lecture_to_frac_200)






lecture_to_user_to_start_timestamps = [{} for i in range(numLectures)]
lecture_to_user_to_finish_timestamps = [{} for i in range(numLectures)]
lecture_to_user_to_seek_timestamps = [{} for i in range(numLectures)]
lecture_to_user_to_ratechange_timestamps = [{} for i in range(numLectures)]

lecture_to_user_to_seek_times = [{} for i in range(numLectures)]

for anon_username,event_type,curr_time,lecture_id,event_timestamp in listFields(['anon_username', 'event_type', 'curr_time', 'lecture_id', 'event_timestamp'], 'where event_type="play" and curr_time=0'):
  if anon_username not in lecture_to_user_to_start_timestamps[lecture_id]:
    lecture_to_user_to_start_timestamps[lecture_id][anon_username] = []
  lecture_to_user_to_start_timestamps[lecture_id][anon_username].append(event_timestamp)

for anon_username,event_type,curr_time,lecture_id,event_timestamp in listFields(['anon_username', 'event_type', 'curr_time', 'lecture_id', 'event_timestamp'], 'where event_type="pause"'):
  if curr_time != lecture_end_times[lecture_id]:
    continue
  if anon_username not in lecture_to_user_to_finish_timestamps[lecture_id]:
    lecture_to_user_to_finish_timestamps[lecture_id][anon_username] = []
  lecture_to_user_to_finish_timestamps[lecture_id][anon_username].append(event_timestamp)

for anon_username,event_type,curr_time,lecture_id,event_timestamp in listFields(['anon_username', 'event_type', 'curr_time', 'lecture_id', 'event_timestamp'], 'where event_type="ratechange"'):
  if anon_username not in lecture_to_user_to_ratechange_timestamps[lecture_id]:
    lecture_to_user_to_ratechange_timestamps[lecture_id][anon_username] = []
  lecture_to_user_to_ratechange_timestamps[lecture_id][anon_username].append(event_timestamp)
  
for anon_username,event_type,curr_time,lecture_id,event_timestamp in listFields(['anon_username', 'event_type', 'curr_time', 'lecture_id', 'event_timestamp'], 'where event_type="seeked" and curr_time<>0'):
  if curr_time == lecture_end_times[lecture_id]:
    continue
  if anon_username not in lecture_to_user_to_seek_timestamps[lecture_id]:
    lecture_to_user_to_seek_timestamps[lecture_id][anon_username] = []
    lecture_to_user_to_seek_times[lecture_id][anon_username] = []
  lecture_to_user_to_seek_timestamps[lecture_id][anon_username].append(event_timestamp)
  lecture_to_user_to_seek_times[lecture_id][anon_username].append(curr_time)


lecture_to_num_start = []
lecture_to_num_finish = []
lecture_to_num_seek = []
lecture_to_num_ratechange = []

for v in lecture_to_user_to_start_timestamps:
  lecture_to_num_start.append(sum([len(x) for x in v.values()]))

for v in lecture_to_user_to_finish_timestamps:
  lecture_to_num_finish.append(sum([len(x) for x in v.values()]))

for v in lecture_to_user_to_seek_timestamps:
  lecture_to_num_seek.append(sum([len(x) for x in v.values()]))

for v in lecture_to_user_to_ratechange_timestamps:
  lecture_to_num_ratechange.append(sum([len(x) for x in v.values()]))


pylab.plot(lecture_to_num_start)
pylab.xlabel('lecture num')
pylab.ylabel('number of view start events')
pylab.title('view start events over time')


user_to_lectures_watched = {}

for anon_username,lecture_id,event_type in listFields(['anon_username', 'lecture_id', 'event_type']):
  if anon_username not in user_to_lectures_watched:
    user_to_lectures_watched[anon_username] = set()
  if lecture_id not in user_to_lectures_watched[anon_username]:
    user_to_lectures_watched[anon_username].add(lecture_id)



num_lectures_watched_to_num_users = [0]*(numLectures)

for user,watched_lectures in user_to_lectures_watched.iteritems():
  num_lectures_watched_to_num_users[len(watched_lectures)] += 1

pylab.plot(num_lectures_watched_to_num_users)
pylab.xlabel('lecture num')
pylab.ylabel('num users who have watched it')
pylab.title('lecture num to num users who have watched it')


most_lectures_watched = max([len(lectures_watched) for user,lectures_watched in user_to_lectures_watched.iteritems()])

users_who_watched_all_lectures = [user for user,lectures_watched in user_to_lectures_watched.iteritems() if len(lectures_watched) >= most_lectures_watched/2 and max(lectures_watched) >= most_lectures_watched*3/4]
print len(users_who_watched_all_lectures)


#rates_videos_watched_at = [0]*

