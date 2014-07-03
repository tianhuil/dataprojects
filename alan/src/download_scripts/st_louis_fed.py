import urllib2, json
import sys

sys.path.append('../')
import settings

data_path = settings.project_path + 'data/st_louis_fed'

api_key = settings.fed_api_key
series = settings.fed_series

def fetch_series(series_name, apikey):
    url = "http://api.stlouisfed.org/fred/series/observations?series_id={series}&api_key={api_key}&file_type=json".format(series=series_name, api_key=apikey)
    ret = urllib2.urlopen(url).read()
    return json.loads(ret)

if __name__ == "__main__":
    for fs, outname in series.items():
        data= fetch_series(fs, api_key)
        outfile = open('%s/%s.txt' %(data_path,outname), 'w')
        outfile.write('# series %s\n' %fs)
        outfile.write('# YYYY MM DD Value\n')
        for a in data['observations']:
            try:
                float(a['value'])
                outfile.write('%s %s\n' %(a['date'].replace('-',' '), a['value']))
            except:
                print "Warning line {line} in {series} skipped!!!!!".format(line=' '.join([a['date'].replace('-',' '), a['value']]), series=fs)

        outfile.close()
    
    statusfile = open(settings.fed_downstatus, 'w')
    statusfile.write('Fed data Successfully downloaded!')
    statusfile.close()
