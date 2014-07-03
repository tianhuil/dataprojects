# This is the pipeline for installing the commodities predictor

all: .packages src/.paths src/download_scripts/.download_status src/mysql/.mysql_status src/stocks/.gen_dataframe 

# needed packages
.packages:
	pip install prettytable ;
	pip install Quandl ;
	touch .packages ;

# sets up paths
src/.paths:
	cd src;\
	./paths.sh;\
	touch .paths

# downloads all stocks and fed data
src/download_scripts/.download_status:
	cd src/download_scripts;\
	python stock_download.py;\
	python st_louis_fed.py ;\
	touch .download_status ;\

# loads stocks and fed data to mysql
src/mysql/.mysql_status:
	cd src/mysql;\
	python load_fed.py;\
	python load_stock.py;\
	touch .mysql_status;

# this downloads and loads the gdelt data. 
#It is large, so it is left out by default
.gdelt: src/download_scripts/.gdelt_download src/mysql/.gdelt_mysql 
	touch .gdelt

src/download_scripts/.gdelt_download: 
	cd src/download_scripts;\
	python down_gdelt.py;\
	touch .gdelt_download

src/mysql/.gdelt_mysql: 
	cd src/mysql;\
	python build_gdelt_tables.py;\
	touch .gdelt_mysql

src/stocks/.gen_dataframe:
	cd src/mysql
