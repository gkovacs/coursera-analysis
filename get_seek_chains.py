#!/usr/bin/env python
# md5: 7f9f4de77b80e0e0316d053e1fb5ddbc
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
  return json.load(open(jfile))

