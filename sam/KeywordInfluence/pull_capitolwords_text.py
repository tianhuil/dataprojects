import urllib3 as url
import json
import os.path
import datetime
import time
import math

import api_keys as key
import pull_congresspeople as pullc

# SunlightFoundation Congress API
api_text = 'http://capitolwords.org/api/1/text.json?'

def pull_bioguide_text(bioguide_id):
  http = url.PoolManager(timeout = 1)
  # check to see if we already have it
  file_path = 'data/words/by_bioguide/bgid_' + str(bioguide_id) + '.txt'
  if not os.path.isfile(file_path):
    # query parameters
    query_params = {'apikey': key.sunlight,
                    'sort': 'id asc',
                    'bioguide_id': bioguide_id}
    # call API
    try:
      response = http.request('GET', api_text + url.request.urlencode(query_params))
      num_found = json.loads(response.data)['num_found']
      print str(datetime.datetime.now().time()) + ' getting ' + str(bioguide_id) + ' ['+ str(num_found) +']'
    except:
      return None

    # check if there were any results
    if num_found:
      results  = json.loads(response.data)['results']
      # check if there were more than 1 page of results, iterate as necessary
      if num_found > 50:
        for page in range(1,int(math.floor(num_found/50))+1):
          print str(datetime.datetime.now().time()) + ' getting ' + str(bioguide_id) + ', page '+ str(page)
          page_params = query_params
          page_params['page'] = page
          try:
            response = http.request('GET', api_text + url.request.urlencode(page_params))
            results += json.loads(response.data)['results']
          except:
            print "timeout on " + str(bioguide_id) + ', page '+ str(page)
      # write file with results
      with open(file_path, 'w') as outfile:
        json.dump(results, outfile)
    # if not, write an empty file
    else:
      open(file_path, 'a') 

def log_error(bioguide_id):
  print str(datetime.datetime.now().time()) + ' time out on ' + str(bioguide_id)
  with open("data/words/errors.txt", "a") as error_log:
    error_log.write('bgid_' + str(bioguide_id) +',')


for bgid in pullc.pull_congress_ids(538):
  pull_bioguide_text(bgid)




