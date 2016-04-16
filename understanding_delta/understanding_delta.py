# -*- coding: utf-8 -*-
"""
    This script defines the functions for Delta that understanding_delta_workflow is going to use.
    To use this scripts in a normal way you don't have to change anything here
    If you want to see the stage of the data in any some, just delete the # signal in the lines likes "#print(filename)"
    
    Script made by José Calvo Tello
"""
# The modules that are needed are imported
import pandas as pd
from collections import Counter
import re
import glob
import os
import numpy as np
from scipy.cluster.hierarchy import linkage
import scipy.cluster.hierarchy  as sch

# So Pandas use 0 for vertical and 1 for horizontal, so let's work with nicer names
horizontal = 1
vertical = 0


def countWordfrequencies(inpath):
    """
        With this function we count the frequencies of a group of texts. In our case from the folder refranes
    """
    # First we create one dictionary for the files and counters
    docs_counts = {}
    
    # We import the texts from txt folder and for each...
    for doc in glob.glob(inpath+"*.txt"):
            
        # We split between the name of the file and its extension    
        filename,extesion = os.path.basename(doc).split(".")
        #print(filename)
        
        # We open the document and read it
        with open(doc, "r", encoding = "utf-8") as fin:
            content = fin.read()
            
            # We split it (or tokenize it) using a regular expression
            tokens_content = re.split("[\W]+",content)
            #print(type(tokens_content))
            
            # We count how many times a word (or token) comes in the document
            doccounts = Counter(tokens_content)
            #print(doccounts)
            
            # We put that data in a dictionary with the name of the file together
            docs_counts[filename] = doccounts
            #print(doccounts)
        fin.close
        
    #print(len(docs_counts))
    
    # Now that we have all the information about the frecuency of each token, we create a matrix from the dictionary
    freqmatrix = pd.DataFrame.from_dict(docs_counts, orient = 'columns')
    #print(freqmatrix)
    #print(freqmatrix.shape)
    
    # We replace the NaN with zeros
    freqmatrix = freqmatrix.fillna(0)
    #print(freqmatrix)
    
    # We sum how many words are in each text and we put that in a Serie 
    doclen = freqmatrix.sum(axis = vertical)
    # We put to this Serie a name: doclen
    doclen = pd.Series(doclen, name = "doclen")
    #print(doclen)
    
    # We rotate the table so the Serie doclen can fit in
    freqmatrix = freqmatrix.T
    
    # We sum how many times appear one word in the whole corpus to have the MFW of the corpus
    sumfrequencies = np.sum(freqmatrix, axis = vertical)
    sumfrequencies  = pd.Series(sumfrequencies, name = "sumfrequencies")
    #print(sumfrequencies)

    # We order the token list of the corpus by frequency
    sumfrequencies = sumfrequencies.order(ascending=False)
    
    
    # Now we divide the frequency through the length of the whole text in order to get relative frequencies
    freqmatrix = freqmatrix.apply(lambda x: x / doclen)
    #print(freqmatrix)
    
    # We add that to the table
    freqmatrix = freqmatrix.append(sumfrequencies)
    #print(freqmatrix)

    # We rotate it
    freqmatrix = freqmatrix.T

    #And we sort it by frequency
    freqmatrix = freqmatrix.sort(["sumfrequencies"], ascending=False)
    print(freqmatrix)

    # If you want, you can print the first 10 words of each document
    #print(freqmatrix.iloc[0:10,:])
    #print(freqmatrix[0:10])
    
    # We cut the table in case there are more than 5000 words in the corpus
    freqmatrix = freqmatrix.head(5000)
    print(freqmatrix)

    # We drop (delete) the sumfrequencies!
    freqmatrix = freqmatrix.drop("sumfrequencies", axis=horizontal)
    
    # We rotate it
    freqmatrix = freqmatrix.T

    #print("\n\n\n\nHere it is the frequency matrix!")
    print(freqmatrix)
    print(freqmatrix.shape)

    return freqmatrix


def getZscore(freqmatrix):
    """
    With this function we want to obtain the z-scores
    """
    # We obtain the mean and we save it as Serie    
    means = freqmatrix.mean(axis = vertical)
    #print(means)
    
    # We obtain the standard devitation and we save it as Serie    
    stds = freqmatrix.std(axis = vertical)   
    #print(stds)
    
    # And now we calculate the zscores
    zscorematrix = (freqmatrix - means) / stds
    
    print("\n\n\n\nHere are the z-scores!")
    print(zscorematrix)
    return zscorematrix



def delta(zscorematrix):
    """
        This function calculate delta for the whole corpus
    """
    # We take names of the columns of the dataframe, that means, the tokens
    tokens = list(zscorematrix.columns.values)
    #print(tokens)
    
    # We take names of the columns of the dataframe, that means, the names of the files
    indexs = list(zscorematrix.index)
    #print(indexs)
    
    # We creata an empty dataframe whose columns and rows are the names of the files
    delta_matrix = pd.DataFrame(columns=indexs,index=indexs)
    # We take a text
    for index1 in indexs:
        #print (index1)
        # We take another text
        for index2 in indexs:
            # We create a variable for saving the distance between the texts
            text_distance = 0         
            #print(index2)
            
            # Now that we have two texts, we take a token
            for token in tokens:
                # And we see the value of this token in both texts
                value1=zscorematrix.loc[index1,token]
                value2=zscorematrix.loc[index2,token]
                # We calculate the distance between them. The form would be |text_value_1 - text_value_2|
                text_distance = text_distance+abs(value1-value2)
                # We sum all the values for every peer of texts in order to get the distance between two texts in all the dimensions, in all the words 
                delta_matrix.at[index1,index2] = text_distance
            #print(text_distance)
    print("\n\n\n\nHere it ist, the delta matrix for the corpus!")
    print(delta_matrix)
    return delta_matrix



def delta_word(zscorematrix,interesting_tokens):
    """
    This function is not very important, but it could be interesting.
    We are going to implement Delta but not for the whole corpus, but for each word that we might find interesing.
    The idea is try to understand Delta better, not only in the whole corpus, but in each word
    Sure there are 34 more efficient ways to do that ;) I am trying to very clear, not very eficient
    """
    
    # We take names of the columns of the dataframe, that means, the names of the files
    indexs = list(zscorematrix.index)
    
    # We take a token
    for token in interesting_tokens:
        print("\n\n\naquí va una nueva palabra: "+token)
        # We creata an empty dataframe whose columns and rows are the names of the files
        delta_matrix_word= pd.DataFrame(columns=indexs,index=indexs)
        #  We take a text
        for index1 in indexs:
            # We take another text
            for index2 in indexs:
                #print(index2)
                
                # And we see the value of this token in both texts
                value1=zscorematrix.loc[index1,token]
                value2=zscorematrix.loc[index2,token]
                # We calculate the distance between them. The form would be |text_value_1 - text_value_2|
                text_distance_word = abs(value1-value2)
                # We save it in the delta matrix 
                delta_matrix_word.at[index1,index2] = text_distance_word

        print("\nHere are the delta matrix for the word "+token+"!")
        print(delta_matrix_word)
    return delta_matrix_word



def create_dendogram(delta_matrix):
    # We use the cluster mehod ward and create and object with this information
    linkage_object = linkage(delta_matrix, method='ward')
    print("\n\n\n\nHere it is the data for you dendongram!")
    print(linkage_object)
    return linkage_object



def visualize_dendogram(linkage_object,delta_matrix):
    
    d = sch.dendrogram(Z=linkage_object, labels = delta_matrix.index, orientation='right')
    print("\n\n\n\nAnd here it ist your dendogram!!!!")
    print(d)