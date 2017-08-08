# -*- coding: utf-8 -*-
"""
Created on Fri Aug 4 07:31:15 2017
by @author: jose

This script loads a Zotero bibliography that has been exported as CSV and creates the necessary files (edges and nodes) to create a nice graph.
The output files are optimized for Gephi.

Parameters:
* wdir: (string) where are your subfolders
* data: (string) subfolder of the wdir where the CSV exported Zotero file is
* results: (string) subfolder of wdir where you want the exported files (edges and nodes)

Example of how to use it:
main(
    wdir = "./",
     data = "data/",
     results = "results/"
     )
     
"""

import pandas as pd
import glob
from collections import Counter
import re
import os

def load_bibliography(doc):
    """
    This function opens the files as dataframe, filters only the authors, delete the empty ones and make a list of list from them, in which every article is a sub-list and every author is a value of the sub-list
    """
    bibliography = pd.read_csv(doc, encoding="utf-8", sep=",")
    
    authors_articles = bibliography["Author"]

    authors_articles = authors_articles.dropna()

    authors_articles = authors_articles.str.split(";").tolist()

    return authors_articles

def clean_authors_articles(authors_articles, file_name, wdir, results):
    """
    This function gets the list of articles and modify the names (takes only the capital of the first name, replace white space with ephans...)
    """
    clean_authors_articles = []
    for article in authors_articles:
        new_article = []
        for author in article:
            author = re.sub(r'^ +(.*?)', r'\1', author, flags=re.MULTILINE)
            author = re.sub(r'(.*?) +$', r'\1', author, flags=re.MULTILINE)
            author = re.sub(r'(.*?), (.).*', r'\1_\2', author)
            author = re.sub(r' ', r'-', author)
            author = re.sub(r'^ +(.*?)', r'\1', author, flags=re.MULTILINE)
            author = re.sub(r'(.*?) +$', r'\1', author, flags=re.MULTILINE)
            new_article.append(author)
        clean_authors_articles.append(new_article)
    authors_articles = clean_authors_articles
    with open (wdir+results+file_name+".txt", "w", encoding="utf-8") as fout:
        fout.write(str(authors_articles))
    #print(authors_articles)
    return authors_articles

def create_authors(authors_articles, file_name, wdir, results):
    """
    This function creates a list of the nodes, that means, the authors.
    """
    authors =  [author for article in authors_articles for author in article]
    authors = pd.DataFrame(list(Counter(authors).items()), columns=["Id","Weight"]).sort_values(by="Weight")

    authors["Weight"] = authors["Weight"]

    authors["Label"] = authors["Id"]
    authors.sort_values(by="Weight", ascending=False).to_csv(wdir+results+file_name+"_authors.csv", sep='\t', encoding='utf-8', index=True)
    #print(authors)

    return authors

def create_edges(authors_articles, file_name, wdir,results, self_loop = True):
    """
    This function creates the list of edges. Every author is connected to the rest of the co-authors of an article a single time.
    If an article was written by a single author, this author gets a self loop (it is questionable if that is the best way since we already have this information in the table of nodes, but Gephi doesn't allow to modify the size of the nodes based on attributes of the nodes, I wanted to use this information to not penalise those authors that have published a lot by themself.)
    
    """
    edges = []
    for article in authors_articles:
        article.sort()
        #print("\n",article)
        old_authors = []
        for author1 in article:
            if self_loop == True:
                if len(article) == 1:
                    edges.append((author1,author1))
            #print(author1)
            old_authors.append(author1)
            for author2 in article:
                #print(author2)
                if author2 not in old_authors and author1 != author2:
                    #print(author1,author2)
                    edges.append((author1,author2))
    edges = Counter(edges)
    edges = [ [key[0],key[1],value] for key, value in edges.items()]

    edges = pd.DataFrame(edges, columns=["Source","Target","Weight"]).sort_values(by="Weight")
    edges["Type"] = "Undirected" 
    #print(edges)    
    edges.sort_values(by="Weight", ascending=False).to_csv(wdir+results+file_name+"_edges.csv", sep='\t', encoding='utf-8', index=True)
    return edges

def main(wdir, data, results):
    """
    Main function. It gets the strings for folder and subfolder and calls the rest of the functions.
    """
    for doc in glob.glob(wdir+data+"*.csv"):
        file_name = os.path.splitext(os.path.split(doc)[1])[0]
        print(doc)
        authors_articles = load_bibliography(doc)
        authors_articles = clean_authors_articles(authors_articles, file_name, wdir, results)
        authors = create_authors(authors_articles, file_name, wdir, results)
        edges = create_edges(authors_articles, file_name, wdir,results)
        print("done")
"""
main(
    wdir = "./",
     data = "data/",
     results = "results/"
     )      
"""