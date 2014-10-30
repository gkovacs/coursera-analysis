#!/usr/bin/env python
# md5: 725ef5ac2f70a616caeb05ccbf8e8b43
# coding: utf-8

import matplotlib.pyplot
import matplotlib.pylab as pylab
import numpy

def binsum(inp):
  output = []
  for i in range(len(inp)):
    curbin = inp[i-2:i+3]
    val = sum(curbin)
    output.append(val)
  return output

def binavg(inp):
  output = []
  for i in range(len(inp)):
    curbin = inp[i-2:i+3]
    if len(curbin) == 0:
      output.append(0)
      continue
    val = sum(curbin) / float(len(curbin))
    output.append(val)
  return output

def barPlotWithStderr(means, stderrs=None, x_tick_labels=None, xlabel='', ylabel='', title='', addLabels=True):
    if stderrs:
        assert len(means) == len(stderrs)
    if x_tick_labels:
        assert len(means) == len(x_tick_labels)
        x_tick_labels = [str(x) for x in x_tick_labels]
    else:
        x_tick_labels = [str(x) for x in range(len(means))]
    N = len(means)
    ind = numpy.arange(N) # the x locations for the groups
    width = 0.35 # the width of the bars
    fig, ax = matplotlib.pyplot.subplots()
    if stderrs:
        rects1 = ax.bar(ind, means, width, color='r', yerr=stderrs)
    else:
        rects1 = ax.bar(ind, means, width, color='r')
    
    if ylabel and not title:
        title = ylabel
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_xticks(ind+width)
    ax.set_xticklabels( x_tick_labels )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            #ax.text('foobar', 1.05*height, '%d'%int(height), ha='center', va='bottom')
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height), ha='center', va='bottom')
    if addLabels:
      autolabel(rects1)

def plotBarDictionary(datadict, xlabel='', ylabel='', title='', x_tick_label_map=None):
    keys = datadict.keys()
    keys.sort()
    means = [datadict[k] for k in keys]
    if not x_tick_label_map:
      x_tick_labels = keys
    else:
      x_tick_labels = [x_tick_label_map[key] for key in keys]
    barPlotWithStderr(means, x_tick_labels=x_tick_labels, xlabel=xlabel, ylabel=ylabel, title=title)

