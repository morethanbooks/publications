# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 10:24:30 2016

@author: jose
"""

#
import understanding_delta as ud

# Where are your texts? Are they in txt? My texts were in a folder called in a ubuntu system
inpath = "/home/jose/cligs/textbox/es/novela-espanola/txt/"

# We call the functions that counts everything
freqmatrix = ud.countWordfrequencies(inpath)


# We calculate the zscores!
zscorematrix = ud.getZscore(freqmatrix)
# We calculate delta for the whole corpus
delta_matrix = ud.delta(zscorematrix)

# We calculate Delta just for some words
delta_word_matrix = ud.delta_word(zscorematrix, ["lo","hecho"])

# We calculate the dendogram
linkage_object = ud.create_dendogram(delta_matrix)

# We visualize the dendogram
visualize_dendogram = ud.visualize_dendogram(linkage_object,delta_matrix)
