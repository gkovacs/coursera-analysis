#!/usr/bin/env python
# md5: 21498762ba3f958722e62e9a196d1ad3
# coding: utf-8

def parseOptions(options, lst):
  if options == None:
    return tuple([None for x in lst])
  for key in options:
    assert key in lst, 'provided option ' + str(key) + ' is not in acceptable options ' + str(lst)
  output = []
  for x in lst:
    if x in options:
      output.append(options[x])
    else:
      output.append(None)
  return tuple(output)

