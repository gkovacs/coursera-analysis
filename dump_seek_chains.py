#!/usr/bin/env python
# md5: 164bd37634eb4feb071d7c90c05a112c
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
  pfile = '/lfs/local/0/geza/new_seek_chains/seek_chains_' + str(lecture_id) + '.pickle'
  jfile = '/lfs/local/0/geza/new_seek_chains/seek_chains_' + str(lecture_id) + '.json'
  if not os.path.exists(pfile):
    print lecture_id
    seek_chains = getSeekChains(lecture_id)
    pickle.dump(seek_chains, open(pfile, 'w'), pickle.HIGHEST_PROTOCOL)
    #json.dump(jsonpickle.encode(seek_chains), open(jfile, 'w'))


if not os.path.exists('/lfs/local/0/geza/new_seek_chains/video_to_seek_chains.pickle'):
  video_to_seek_chains = {}
  for lecture_id in vid.video_lengths.keys():
    print lecture_id
    pfile = '/lfs/local/0/geza/new_seek_chains/seek_chains_' + str(lecture_id) + '.pickle'
    seek_chains = pickle.load(open(pfile))
    video_to_seek_chains[lecture_id] = seek_chains
  print 'dumping'
  pickle.dump(video_to_seek_chains, open('/lfs/local/0/geza/new_seek_chains/video_to_seek_chains.pickle', 'w'), pickle.HIGHEST_PROTOCOL)
  #json.dump(jsonpickle.encode(video_to_seek_chains), open('/lfs/local/geza/0/new_seek_chains/video_to_see_chains.json', 'w'))

