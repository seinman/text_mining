
# coding: utf-8

# In[14]:

# Import necessary packages
from bs4 import BeautifulSoup
import urllib
import time
import random
import json
import time
import re
import datetime
import os

# In[22]:

###############################################
# PREPARE LIST OF URLS TO SCRAPE
###############################################

#os.chdir('C:/Users/Sarah/Documents/Data science/text_mining')

# Open scraped list of urls
read = []
with open('scraped_data/metadata/listofurls', 'r') as f:
    listofdebates = json.load(f)

listofdebates = listofdebates[0:2000]
# In[23]:

print len(listofdebates)
print len(set(listofdebates))


# In[18]:


##############################################
# PREPARE SENTIMENT ANALYSIS DICTIONARIES
##############################################

# Import relevant packages
import csv
import numpy as np
from nltk import PorterStemmer
stemmer = PorterStemmer()

# Open Harvard IV sentiment dictionary
read = []
with open('harvard_iv.csv', 'rb') as csvfile:
    harvard_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in harvard_reader:
        read.append(row)
harvard = np.array(read)
harvard = harvard[1:np.shape(harvard)[0],:]

# stem the words in the sentiment dictionaries
stemmed_tokens = []
for word in harvard[:,0]:
    current_token = stemmer.stem(word)
    current_token = current_token.encode('utf-8')

    token_match = re.match('[A-Z]*', current_token)
    #print token_match
    final_token = token_match.group()
    #print final_token
    stemmed_tokens.append(final_token)
  


# In[24]:

#######################################################
# MAIN CODE
######################################################

iterate = 1

#  Create something to collect the paragraphs, the identifiers and the speakers
debateParagraphs = []
debateSentiments = []
debateIdentifiers = []
debateIDs = []
debateLengths = []
debateMembers = []
debateTitles = []
contributionMissing = []
contributionPartMissing = []
debateMissing = []

forLDA_all = []

for current in listofdebates:
    try:
        iterate += 1
        print iterate
        print datetime.datetime.now().time()
        # Add a randomised waiting time
        wt = random.uniform(1,3)
        time.sleep(wt)

        #######################################
        # PREPARE THE DEBATE FOR SOUPING
        #######################################
        # Soupify
        html = urllib.urlopen(current).read()

        #Create a beautifulSoup Object that will be used to retieve information from the target
        soup = BeautifulSoup(html)

        #########################################
        # EXTRACT META-DATA
        #########################################

        # Find the date
        divs = soup.find_all('div', {'class':'debate-date'})
        dates = divs[0]
        date = ""
        for ch in dates.children:
            date = date + ch.string

        # Find the title
        head1 =  soup.find('h1', {'class':'page-title'})
        title = ""
        for ch in head1.children:
            title = title + ch.string

        #########################################
        # START COLLECTING ACTUAL CONTRIBUTIONS
        #########################################

        sections = soup.find_all(name = 'li')

        # This bit of code extracts all the contributions
        contributions = []
        for section in sections:
            try:
                v = re.match('contribution', section['id'])
                contributions.append(section)
            except:
                None

        num_contributions = 0
        debateWords = []

        # Go through all the contributions, collect the text and speaker, analyse the sentiment and log failures
        for contribution in contributions:
            text = ""
            member = ""
            paragraphs = contribution.find_all(name = 'p')
            members = contribution.find(name = 'a')
            try:
                for para in paragraphs:
                    for ch in para.children:
                        try:
                            text = text + ch.string
                        except:
                            contributionPartMissing.append(contribution['id'])
                            debateMissing.append(current)
                            contributionMissing.append(0)

                for ch in members.children:
                    member = member + ch.string            
                    if text != "":
                        num_contributions += 1

                        # Analyse the sentiment
                        words = text.split()
                        sentiment = 0
                        for word in words:
                            word_stem = stemmer.stem(word)
                            word_stem = word_stem.upper()
                            debateWords.append(word_stem)
                            try:
                                wh = stemmed_tokens.index(word_stem)
                                if harvard[wh,3] == "Negativ":
                                    sentiment -= 1
                                if harvard[wh, 2] == "Positiv":
                                    sentiment += 1
                            except:
                                None

                        sentimentNormalised = float(sentiment) / float(len(words))
                        
                        debateTitles.append(title)
                        debateSentiments.append(sentimentNormalised)
                        debateParagraphs.append(text)
                        debateIdentifiers.append(contribution['id'])
                        debateLengths.append(len(words))
                        debateMembers.append(member)
                        debateIDs.append(current)

            except:
                contributionMissing.append(contribution['id'])
                debateMissing.append(current)
                contributionPartMissing.append(0)
            
        forLDA = [current, debateWords, title]
        forLDA_all.append(forLDA)
        
        #####################################################
        # PUT IT ALL TOGETHER
        #####################################################

        if iterate % 1000 == 0 and iterate != 0:
            print "WHOOP"
            
            # Write debate info
            full_debate =  [debateTitles, debateSentiments, debateParagraphs, 
                            debateIdentifiers, debateLengths, debateMembers, debateIDs]
            with open('scraped_data/metadata/all_debates_' + str(iterate) + '_' + str(iterate + 1000), 'w') as f:
                json.dump(full_debate, f)
                
            with open('scraped_data/metadata/forLDA'+ str(iterate - 1000) + '_' + str(iterate + 1000), 'w') as f:
                json.dump(forLDA_all, f)
            
            # Next we collect any contribution errors
            with open('scraped_data/metadata/missing'+ str(iterate - 1000) + '_' + str(iterate + 1000), 'w') as f:
                allmissing = [contributionPartMissing, contributionMissing, debateMissing]
                json.dump(allmissing, f)
            
            # And clear the memory
            debateParagraphs = []
            debateSentiments = []
            debateIdentifiers = []
            debateLengths = []
            debateMembers = []
            debateTitles = []
            debateIDs = []
            contributionMissing = []
            contributionPartMissing = []
            full_debate = []
            
    except:
        print "mushkila"
        
#############################################
# COLLECT FINAL DATA
############################################# 
# Write debate info
full_debate =  [debateTitles, debateSentiments, debateParagraphs, 
                debateIdentifiers, debateLengths, debateMembers, debateIDs]

with open('scraped_data/metadata/all_debates', 'w') as f:
    json.dump(full_debate, f)
    
with open('scraped_data/metadata/forLDA', 'w') as f:
    json.dump(forLDA_all, f)
           
# Next we collect any contribution errors
with open('scraped_data/metadata/missing', 'w') as f:
    allmissing = [contributionPartMissing, contributionMissing, debateMissing]
    json.dump(allmissing, f)
    

