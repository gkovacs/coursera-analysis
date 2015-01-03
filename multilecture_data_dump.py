#!/usr/bin/env python
# md5: d1760aedfc873ca05ec223133a7d68dc
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

