#!/usr/bin/env python
# md5: 47cbeec79c2fc7f3fa366f9a2db13a58
# coding: utf-8

class OneIndexedArray(object):
  def __init__(self, data):
    self.__array__ = [None] + data
  def __len__(self):
    return len(self.__array__) - 1
  def __getitem__(self, i):
    return self.__array__[i]
  def __setitem__(self, i, v):
    self.__array__[i] = v
  def __str__(self):
    return self.__array__[1:].__str__()
  def __repr__(self):
    return self.__array__[1:].__repr__()

