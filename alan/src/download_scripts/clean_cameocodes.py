import sys
import os
from bs4 import BeautifulSoup
import pickle 

infiles = ['actor3codes','actorfullcodes','countrybycode','countrybyname', 
           'ethnicitycodes','igocodes','ngocodes',
           'religioncodes','rolecodes']

sys.path.append('../')
import settings

data_path = settings.project_path + 'data/gdelt_files/'

for filename in infiles:
    print 'Cleaning '+ filename
    raw_page = open(data_path+filename).read()

    for char in ['\n', r'<br/>', r'</tr>',r'</td>', '"', ',',r"u'\n'",
                 r"]",r"[" ]:
        raw_page= raw_page.replace(char, '')
    
    raw_page = raw_page.split('<tr>')
    
    codes = [line.split('<td>')[1:3] for line in raw_page]
    
    outpage = open(data_path+filename+'.clean', 'w')
    for code in codes:
        try:
            if code[0].isupper():
                outpage.write(';'.join(code)+'\n')
        except IndexError:
            pass

    outpage.close()
        
        
# The eventcodes are different...
print 'Cleaning EventCodes'    
raw_page = open(data_path+'EventCodes').read()
for char in ['\n', r'</li>', r'<ul>', r'</ul>', r'</tr>',
             r'</td>', '"', ',',r"u'\n'",
             r"]",r"[", r" u'\n", r"'" ]:
    raw_page= raw_page.replace(char, '')

raw_page = raw_page.replace('</h2>', '<br/>')
raw_page = raw_page.replace('<li>', '<br/>')
raw_page = raw_page.split('<br/>')

outpage = open(data_path+'EventCodes.clean', 'w')
for line in raw_page:
    line = line.strip()
    try:
        codes = line.split(':')
        if len(codes)==2:
            if codes[0][0]=='0':
                codes[0]=codes[0][1:]
            outpage.write(';'.join(codes)+'\n')
    except:
        pass

outpage.close()
