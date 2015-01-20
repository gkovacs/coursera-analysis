#!/usr/bin/env python
# md5: 5a64f3e862a7ef8e212384db54b2873f
# coding: utf-8

#from coursera_lib_common import parseOptions
#from navigation_events import SeekChain
from video_annotations import ml_004 as vid
#from lectures_to_viewers import getViewersToLectures
from coursera_analytics_common import getSeekChains


import cPickle as pickle
import jsonpickle
import json
import os

for lecture_id in vid.video_lengths.keys():
  pfile = 'seek_chains_' + str(lecture_id) + '.pickle'
  jfile = 'seek_chains_' + str(lecture_id) + '.json'
  if not os.path.exists(jfile):
    print lecture_id
    seek_chains = getSeekChains(lecture_id)
    pickle.dump(seek_chains, open(pfile, 'w'), pickle.HIGHEST_PROTOCOL)
    json.dump(jsonpickle.encode(seek_chains), open(jfile, 'w'))




