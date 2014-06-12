# Data Incubator Projects 
Sam Swift  
samswift@gmail.com  
http://swift.pw  

## Keywords of Influence
Relating donations, lobbying, and influence to word choice by politicians.  Can we measure how influence changes the rhetoric in Congress?

Primary repo at https://github.com/swiftsam/KeywordInfluence

### Data sources

* Senate and House floor transcripts/word-counts http://sunlightlabs.github.io/Capitol-Words/
* Campaign Finance and Lobbying records
  * http://www.opensecrets.org/resources/create/data_doc.php
  * http://www.fec.gov/portal/download.shtml
  * http://sunlightlabs.github.io/datacommons/search.html

### Models

* Relative word frequency by congressman (i.e. what words does each politician say more frequently than his peers)
* Influencer → word use (i.e. what words are used more frequently by the politicians who met with or received contributions from a given influencer)
* Influencer efficiency.  Increase in word use per dollar spent
* Politician responsiveness.  Increase in word use per dollar received
* Politician → chief influencers based on word use, not money

### Audience

Citizens, government transparency & campaign finance reform activists

### Skills
* computational linguistics
* machine learning
* causal and reverse-causal inference

### Reports / Product
* Find out who is influencing your representatives
* Find out which representatives are most influenced

## Predicting Crossfit Performance
Predicting Crossfit Games performance from profile stats and past performance

Primary repo at https://github.com/swiftsam/CrossfitRankings

### Data sources
* 2014 Open and Regional WOD scores
* 2011, 2012, 2013 Open, Regional, and Games scores
* Athlete profile stats

### Models
* Predicting 2014 games rank
* Comparing individual performance to expected performance
* Conditional rank prediction with hypothetical changes to stats (e.g. “If I increase my deadlift by 50lb, what would my chances of making regionals be?”)
* Descriptive Region competitiveness and Profile patterns (e.g. Is it true that it’s easy to get into regionals from the Western Europe region?)

### Audience
Casual and competitive crossfit athletes

### Skills
* scraping public website
* building a predictive model
* interactive public interface

### Reports
* How do you compare to other crossfit athletes
![14.1 histogram by gender](http://swift.pw/wp-content/uploads/2014/05/crossfit_14_1_annotated-1024x614.png)

