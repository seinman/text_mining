
# coding: utf-8

# In[30]:

# IMPORT NECESSARY MODULES
import json
import csv
import string
import re


# In[31]:

# OPEN DATA FILES
with open('scraped_data/metadata/all_debates_0_1000', 'r') as f:
    debates = json.load(f)

with open('scraped_data/metadata/all_debates', 'r') as f:
    debates2 = json.load(f)

names = []    
with open('baby-names.csv', 'r') as f:
    reader = csv.reader(f, delimiter=' ', quotechar='|')
    for row in reader:
        names.append(row)


# In[32]:

# SEPARATE INTO MALE AND FEMALE NAMES
# This is for removing the excess punctuation
trans = string.maketrans(string.punctuation, " " * len(string.punctuation))

m = []
f = []

for i in range(len(names)):
#for i in range(10):
    new = names[i][0].split(',')
    if new[3] == '"boy"' and float(new[2])>0.001:
        m.append(new[1].translate(trans).strip())
    if new[3] == '"girl"'and float(new[2])>0.001:
        f.append(new[1].translate(trans).strip())
f_set = set(f)
m_set = set(m)

print len(f_set)
print len(m_set)

# A couple of names have escaped; add these
f_set.update(['Deidre', 'Philippa' , "Mims", "Cat", "Chi", 'Mhairi', 'Liz', "Natascha", 'Thangam', "Priti",
             "Nusrat", "Luciana", 'Tania', 'Fiona', 'Lyn', 'Meg', 'Nadine', 'Karin', 'Nia', 'Rupa', 'Kirsty',
             'Nicola', 'Harriett', 'Eilidh', 'Siobhain', 'Seema', 'Imran', 'Kirsten', 'Suella', 'Rushanara',
             'Yasmin', 'Gill', 'Lilian', 'Justine', 'Naz', 'Tulip', 'Shabana'])
m_set.update(['Simon', 'Pete', "Geraint", 'Neil', 'Nigel', 'Huw', 'Alistair', 'Rob', 'Clive', 
              'Stuart', "Nick", 'Keir', 'Andy', 'Calum', 'Callum', 'Nic', 'Wes', 'Kit', 'Crispin',
             'Angus', 'Hywel', 'Matt', 'Alberto', 'Alun', 'Gareth', 'Graham', 'Glyn', 'Guto', 'Royston',
             'Desmond', 'Toby', 'Stewart', 'Geoffrey', 'Alasdair', 'Conor', 'Martyn', 'Kelvin', 'Sajid',
             'Fabian', 'Byron', 'Hilary', 'Rehman', 'Rishi', 'Kris', 'Tristram', 'Nadhim', 'Kwasi', 'Boris',
             'Alok'])

# FIX REMAINING NAMES
leftover_f = ['Coffey', 'Whitford', 'Mathias', 'Huq', 'Blackman', 'Whiteford', 'Wollaston' ]
leftover_m = ['Prime', 'Fox', 'Chairman', 'Offord', 'Whitehead', 'Solicitor', 'Attorney', 'Davies', 'Murrison',
             'Monaghan', 'McDonnell', 'Poulter']


# In[33]:

# A CONVOLUTED WAY OF TRYING TO SORT THIS SORRY MESS OUT
members = []
speakers = debates[5]
for i in debates2[5]:
    speakers.append(i)

def translate_non_alphanumerics(to_translate, translate_to=u' '):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)

num_g = 0
for i in range(len(speakers)):
#for i in range(50):
    member = translate_non_alphanumerics(debates[5][i]).split()
    if len(set(member) & set(['Mrs', 'Ms', 'Miss', 'Lady', 'Madam'])) > 0:
        members.append('F')
    elif len(set(member) & set(['Mr'])) > 0:
        members.append('M')
    else:
        counter = 0
        for word in range(len(member)):
            if member[word] in f_set:
                na = 'F'
                counter += 1
                break
            if member[word] in m_set:
                na = 'M'
                counter += 1
                break
            if member[word] in leftover_f:
                na = 'F'
                counter += 1
                break
            if member[word] in leftover_m:
                na = 'M'
                counter += 1
                break
        if counter == 0:
            members.append('N')
            num_g += 1
            print member
        else:
            members.append(na)
            
print num_g
print len(members)


# In[34]:

with open('scraped_data/metadata/genders', 'w') as gfile:
    json.dump(members, gfile)

