#!/usr/bin/env python
# md5: 9d6c94b69895c80e144288b735ea722d
# coding: utf-8

from bokeh.plotting import *
#output_notebook()


def plotline(arr, title=''):
  p1 = figure(title=title)
  p1.line(
    range(len(arr)), # x coordinates
    arr, # y coordinates
    color='#ff0000',
    label='something',
  )
  show()

def plotlines(arrs, title=''):
  p1 = figure(title=title)
  colors = ['#ff0000', '#00ff00', '#0000ff', '#00ffff']
  for arr,color in zip(arrs,colors):
    p1.line(
      range(len(arr)), # x coordinates
      arr, # y coordinates
      color=color,
      label='something',
    )
  show()

