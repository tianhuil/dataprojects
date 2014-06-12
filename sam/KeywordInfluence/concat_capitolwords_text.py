import os.path
from os import listdir
import json
import pandas as pd

file_path = "data/words/by_bioguide/"
files     = sorted(list(listdir(file_path)))
if "errors.txt" in files:
	files.remove("errors.txt")

print "loading data from " + str(len(files)) + " files"

data = pd.DataFrame()

for file_name in files:
	print file_name
	if os.path.isfile(file_path + file_name) and os.stat(file_path + file_name).st_size:
		df = pd.read_json(file_path + file_name)
		data = pd.concat([data, df])

data.to_csv("data/words.csv")
