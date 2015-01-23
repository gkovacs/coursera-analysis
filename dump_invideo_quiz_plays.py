#!/usr/bin/env python
# md5: afc8c8e5f43f4cfaf81aa95434babea8
# coding: utf-8

from coursera_analytics_common import *
import os
import json


video_to_user_to_quiz_play_events = {}

count = 0
if os.path.exists('video_to_user_to_quiz_play_events.json'):
  video_to_user_to_quiz_play_events = json.load(open('video_to_user_to_quiz_play_events.json'))
else:
  #for videonumber in listVideos():
  #  video_to_user_to_quiz_play_events[videonumber] = {}
  for user,lectures in getViewersToLectures().iteritems():
    for lecture_id in lectures:
      if lecture_id not in video_to_user_to_quiz_play_events:
        video_to_user_to_quiz_play_events[lecture_id] = {}
      #video_length = vid.video_lengths[int(lecture_id)]
      quizzes = vid.in_video_quiz_times[int(lecture_id)]
      #print video_length
      try:
        all_events = extractAllEventsForUserInLecture(lecture_id, user)
        if all_events == None:
          continue
      except DataException as e:
        continue
      for event in all_events:
        for quiz_idx,quiz_time in enumerate(quizzes):
          if event.event_type == 'play' and abs(event.start - quiz_time) < 5:
            if user not in video_to_user_to_quiz_play_events[lecture_id]:
              video_to_user_to_quiz_play_events[lecture_id][user] = [[] for i in range(len(quizzes))]
            video_to_user_to_quiz_play_events[lecture_id][user][quiz_idx].append(event.timestamp)
  json.dump(video_to_user_to_quiz_play_events, open('video_to_user_to_quiz_play_events.json', 'w'))

