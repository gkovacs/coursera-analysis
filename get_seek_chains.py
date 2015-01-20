#!/usr/bin/env python
# md5: e8c1e6b1814e78ebaf4628ae8a37d95a
# coding: utf-8

from memoized import memoized
import cPickle as pickle
import os

@memoized
def getSeekChainsFast(lecture_id):
  pfile = 'seek_chains_' + str(lecture_id) + '.pickle'
  if not os.path.exists(pfile):
    raise 'file does not exist: ' + pfile
  return pickle.load(open(pfile))

