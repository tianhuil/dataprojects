[ImThirsty](http://107.170.156.226:5000/index.html): Find your new favorite beer.
========================================

This is Rob Howley's project for the Summer 2014 [Data Incubator](http://www.thedataincubator.com/) program. The goal was to create a beer recommendation engine using written and numeric beer review data from [BeerAdvocate.com](http://www.beeradvocate.com). The project directory has three primary components:

1. Data Gathering and Organization
  * web scrapers for beer, brewer and user information (stored in JSON)
  * MySQL database design
  * database filler that uploaded scraped JSON data into MySQL
2. Analysis
  * Python based NLP
  * Extract beer style vocabulary from written reviews
  * Compute and upload similarities to database
  * MySQL implementation of item based filtering
3. ImThirsty Website
  * Python Restful Flask Server
  * Bootstrap and AngularJS dynamically loaded UI components

Please contact Rob at (howley dot robert at gmail dot com) for any questions/comments/concerns.
