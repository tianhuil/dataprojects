import urllib3 as url
import json
import pandas as pd

import api_keys as key

# SunlightFoundation Congress API
api_congress = 'https://congress.api.sunlightfoundation.com/legislators/?'

# Pull all legislators
def pull_congress_ids(n_ids):
	http = url.PoolManager()
	params   = {'apikey'          : key.sunlight,
	            'all_legislators' : 'false',
	            'per_page'        : 'all'}
	response = http.request('GET', api_congress + url.request.urlencode(params))
	results  = json.loads(response.data)['results']
	if n_ids:
		results = results[:n_ids]

	return [person['bioguide_id'] for person in results]

