# This is the pipeline for installing the commodities predictor


#mkdir data
#mkdir data/crop_data
#mkdir data/gdelt_files
#mkdir data/quandl

#sudo pip install prettytable

all: data/.make_data_summary


packages:
	pip install prettytable
	pip install Quandl
	touch .packages


data/.make_data_summary:
	touch $@

learn: 
	touch .learn

clean:
	rm -r data/*
	rm -f data/.make_*


