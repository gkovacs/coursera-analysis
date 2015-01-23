#!/usr/bin/env python
# md5: 83b963b6324ab9d55182984d75a1f962
# coding: utf-8

from coursera_analytics_common import *
import os
import json


video_to_user_to_end_events = {}

count = 0
if os.path.exists('video_to_user_to_end_events.json'):
  video_to_user_to_end_events = json.load(open('video_to_user_to_end_events.json'))
else:
  #for videonumber in listVideos():
  #  video_to_user_to_end_events[videonumber] = {}
  for user,lectures in getViewersToLectures().iteritems():
    for lecture_id in lectures:
      if lecture_id not in video_to_user_to_end_events:
        video_to_user_to_end_events[lecture_id] = {}
      video_length = vid.video_lengths[int(lecture_id)]
      #print video_length
      try:
        all_events = extractAllEventsForUserInLecture(lecture_id, user)
        if all_events == None:
          continue
      except DataException as e:
        continue
      for event in all_events:
        if event.event_type == 'pause' and abs(event.start - video_length) < 5:
          if user not in video_to_user_to_end_events[lecture_id]:
            video_to_user_to_end_events[lecture_id][user] = []
          video_to_user_to_end_events[lecture_id][user].append(event.timestamp)
  json.dump(video_to_user_to_end_events, open('video_to_user_to_end_events.json', 'w'))
    

