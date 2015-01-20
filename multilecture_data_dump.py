#!/usr/bin/env python
# md5: ba0e242d80fb98106e855dd2c44efc48
# coding: utf-8

from coursera_analytics_common import *


video_to_all_seek_destinations = {}

if os.path.exists('video_to_all_seek_destinations.json'):
  video_to_all_seek_destinations = json.load(open('video_to_all_seek_destinations.json'))
else:
  for videonumber in listVideos():
    if videonumber in video_to_all_seek_destinations:
      continue
    print 'processing video ' + str(videonumber)
    resetNumDataExceptions()
    skipped_users = set()
    successful_users = set()
    allSeekDestinations = getAllSeekDestinations(videonumber, skipped_users=skipped_users, successful_users=successful_users)
    video_to_all_seek_destinations[videonumber] = allSeekDestinations
    print 'finished processing video ' + str(videonumber) + ' errors: ' + str(getNumDataExceptions()) + ' skipped: ' + str(len(skipped_users)) + ' successful: ' + str(len(successful_users))
  print 'making json dump'
  json.dump(video_to_all_seek_destinations, open('video_to_all_seek_destinations.json', 'w'))
  print 'finished'


video_to_all_seek_sources = {}

if os.path.exists('video_to_all_seek_sources.json'):
  video_to_all_seek_sources = json.load(open('video_to_all_seek_sources.json'))
else:
  for videonumber in listVideos():
    if videonumber in video_to_all_seek_sources:
      continue
    print 'processing video ' + str(videonumber)
    resetNumDataExceptions()
    skipped_users = set()
    successful_users = set()
    allSeekSources = getAllSeekSources(videonumber, skipped_users=skipped_users, successful_users=successful_users)
    video_to_all_seek_sources[videonumber] = allSeekSources
    print 'finished processing video ' + str(videonumber) + ' errors: ' + str(getNumDataExceptions()) + ' skipped: ' + str(len(skipped_users)) + ' successful: ' + str(len(successful_users))
  print 'making json dump'
  json.dump(video_to_all_seek_sources, open('video_to_all_seek_sources.json', 'w'))
  print 'finished'


video_to_parts_skipped_forward_over = {}

if os.path.exists('video_to_parts_skipped_forward_over.json'):
  video_to_parts_skipped_forward_over = json.load(open('video_to_parts_skipped_forward_over.json'))
else:
  for videonumber in listVideos():
    if videonumber in video_to_parts_skipped_forward_over:
      continue
    print 'processing video ' + str(videonumber)
    resetNumDataExceptions()
    skipped_users = set()
    successful_users = set()
    dataforvid = getPartsSkippedForwardOver(videonumber, skipped_users=skipped_users, successful_users=successful_users)
    video_to_parts_skipped_forward_over[videonumber] = dataforvid
    print 'finished processing video ' + str(videonumber) + ' errors: ' + str(getNumDataExceptions()) + ' skipped: ' + str(len(skipped_users)) + ' successful: ' + str(len(successful_users))
  print 'making json dump'
  json.dump(video_to_parts_skipped_forward_over, open('video_to_parts_skipped_forward_over.json', 'w'))
  print 'finished'


video_to_parts_skipped_back_over = {}

if os.path.exists('video_to_parts_skipped_back_over.json'):
  video_to_parts_skipped_back_over = json.load(open('video_to_parts_skipped_back_over.json'))
else:
  for videonumber in listVideos():
    if videonumber in video_to_parts_skipped_back_over:
      continue
    print 'processing video ' + str(videonumber)
    resetNumDataExceptions()
    skipped_users = set()
    successful_users = set()
    dataforvid = getPartsSkippedBackOver(videonumber, skipped_users=skipped_users, successful_users=successful_users)
    video_to_parts_skipped_back_over[videonumber] = dataforvid
    print 'finished processing video ' + str(videonumber) + ' errors: ' + str(getNumDataExceptions()) + ' skipped: ' + str(len(skipped_users)) + ' successful: ' + str(len(successful_users))
  print 'making json dump'
  json.dump(video_to_parts_skipped_back_over, open('video_to_parts_skipped_back_over.json', 'w'))
  print 'finished'


video_to_user_to_startzero_events = {}

count = 0
if os.path.exists('video_to_user_to_startzero_events.json'):
  video_to_user_to_startzero_events = json.load(open('video_to_user_to_startzero_events.json'))
else:
  for videonumber in listVideos():
    video_to_user_to_startzero_events[videonumber] = {}
  for user,lectures in getViewersToLectures().iteritems():
    for lecture_id in lectures:
      try:
        all_events = extractAllEventsForUserInLecture(lecture_id, user)
        if all_events == None:
          continue
      except DataException as e:
        continue
      for event in all_events:
        if event.event_type == 'play' and event.start == 0:
          if user not in video_to_user_to_startzero_events[lecture_id]:
            video_to_user_to_startzero_events[lecture_id][user] = []
          video_to_user_to_startzero_events[lecture_id][user].append(event.timestamp)
  json.dump(video_to_user_to_startzero_events, open('video_to_user_to_startzero_events.json', 'w'))
    


import cPickle as pickle

video_to_user_to_seek_chains = {}

count = 0
if os.path.exists('video_to_user_to_seek_chains.pickle'):
  video_to_user_to_seek_chains = pickle.load(open('video_to_user_to_seek_chains.pickle'))
else:
  for lecture_id in listVideos():
    video_to_user_to_seek_chains[lecture_id] = {}
  for user,lectures in getViewersToLectures().iteritems():
    for lecture_id in lectures:
      try:
        seek_chains = getSeekChains(lecture_id, user)
        if seek_chains == None:
          continue
      except DataException as e:
        continue
      video_to_user_To_seek_chains[lecture_id][user] = seek_chains
  pickle.dump(video_to_user_to_startzero_events, open('video_to_user_to_startzero_events.pickle', 'w'))
    

