#!/usr/bin/env python
# md5: c0bd9cd599f0d5553e41d52ebefa3ad8
# coding: utf-8

from memoized import memoized
import cPickle as pickle
import os
import json

@memoized
def getSeekChainsFast(lecture_id):
  pfile = 'seek_chains_' + str(lecture_id) + '.pickle'
  if not os.path.exists(pfile):
    raise 'file does not exist: ' + pfile
  return pickle.load(open(pfile))

@memoized
def getPartsPlayedFast(lecture_id):
  jfile = 'video_to_parts_played.json'
  if not os.path.exists(jfile):
    raise 'file does not exist: ' + jfile
  return json.load(open(jfile))[str(lecture_id)]

