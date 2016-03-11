#!/usr/bin/python
#! coding: utf-8
'''
Created on 11.03.2016

@author: vsuess
'''

if __name__ == '__main__':
    aa = {}
    aa[100] = 102
    aa['test2'] = 'jslkd'
    aa[u'olaü'] = u'Müller'
    print type(aa),aa
    bb = repr(aa)
    print type(bb), bb
    cc = eval(bb)
    print type(cc),cc
    print cc[u'olaü']
    
    pass