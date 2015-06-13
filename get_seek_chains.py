#!/usr/bin/env python
# md5: 737667fea08e49f39f1ae66bfe5a2ccd
# coding: utf-8

from memoized import memoized
import cPickle as pickle
import os
import json

@memoized
def getSeekChainsFast(lecture_id):
  pfile = '/lfs/local/0/geza/seek_chains_' + str(lecture_id) + '.pickle'
  if not os.path.exists(pfile):
    raise 'file does not exist: ' + pfile
  return pickle.load(open(pfile))

@memoized
def getPartsPlayedFast(lecture_id):
  jfile = '/lfs/local/0/geza/video_to_parts_played.json'
  if not os.path.exists(jfile):
    raise 'file does not exist: ' + jfile
  return json.load(open(jfile))[str(lecture_id)]

