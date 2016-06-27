
# coding: utf-8

# In[17]:

# IMPORT NECESSARY PACKAGES
import json
import numpy as np
import lda
from nltk.tokenize import wordpunct_tokenize 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import string
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim


# In[18]:

# SHAMELESSLY STOLEN FROM STACK OVERFLOW
def translate_non_alphanumerics(to_translate, translate_to=u' '):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)


# In[19]:

# THE DATA YOU SCRAPED IS IN A BAD FORMAT; CORRECT THE FORMAT
# this section takes out punctuation, puts all the words in a document together and assembles a corpus
with open('scraped_data/metadata/forLDA0_1000') as ldaf:
    forlda = json.load(ldaf)

with open('scraped_data/metadata/forLDA') as ldaf2:
    forlda2 = json.load(ldaf2)

for i in range(len(forlda2)):
    forlda.append(forlda2[i])

doc_set = []
title = []

for debate in range(len(forlda)):
    title.append(forlda[debate][0])
    words = ""
    for word in range(len(forlda[debate][1])):
        try:
            words = words + " " + translate_non_alphanumerics(forlda[debate][1][word])
        except:
            print forlda[debate][1][word]
    doc_set.append(words)


# In[5]:

# MAKE CUSTOM STOPWORDS LIST
tfidf_vectorizer = TfidfVectorizer(use_idf = True, max_df =0.55, min_df = 0.0001)
v = tfidf_vectorizer.fit(doc_set)
stopw = v.stop_words_
stopw.update('a')
stopw.update('i')


# In[6]:

# PERFORM THE LDA
tokenizer = RegexpTokenizer(r'\w+')

# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()

# list for tokenized documents in loop
texts = []

# loop through document list
for i in doc_set:
    
    # clean and tokenize document string
    raw = i.lower()
    tokens = tokenizer.tokenize(raw)

    # remove stop words from tokens
    stopped_tokens = [i for i in tokens if not i in stopw]
    
    # stem tokens
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    
    # add tokens to list
    texts.append(stemmed_tokens)

# turn our tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(texts)
    
# convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in texts]

# generate LDA model
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=30, id2word = dictionary, passes=20)


# In[7]:

# FIGURE OUT WHICH TOPIC GOES WITH WHICH DOCUMENT
# Presumably there is an automatic way of doing this, god knows what it is though
alltopics = []
doctops = ldamodel.get_document_topics(corpus)
wrong = 0
for doc in range(len(doctops)):
    probvals = []
    print doc
    try:
        for i in range(len(doctops[doc])):
            probvals.append(doctops[doc][i][1])
        which_max = probvals.index(max(probvals))
        alltopics.append(doctops[doc][which_max][0])
    except:
        alltopics.append(999)
        print 'error'
        
print alltopics


# In[8]:

final_topics = [title, alltopics]
with open('scraped_data/metadata/topiclist', 'w') as f:
    json.dump(alltopics, f)


# In[16]:

for i in ldamodel.show_topics(num_topics = 31):
    print i

