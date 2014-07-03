import xlrd
import csv

zones = ['RTO','MIDATL','APS','COMED','DAY','DUQ','DOM']
yrs    = [ 2011,2012] #lots of data, can take awhile.

def csv_from_excel(zone,yr):
	raw_file = 'raw_lf_data/%i-rto-forecasts.xls' %yr
        wb = xlrd.open_workbook(raw_file)
        sh = wb.sheet_by_name(zone)
	outfile = 'raw_lf_csv/%s%i.csv' %(zone,yr)  
        your_csv_file = open( outfile, 'wb')
        wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
        for rownum in xrange(sh.nrows):
                wr.writerow(sh.row_values(rownum))
        your_csv_file.close()


for yr in yrs:
	for zone_ind in range(len(zones)): 
		x = csv_from_excel(zones[zone_ind],yr)

print "success"
