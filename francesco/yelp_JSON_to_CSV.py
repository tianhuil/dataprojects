__author__ = 'laszlo'
import sys
import json
import pandas as pd

if __name__ == "__main__":
    with open("yelp_training_set/yelp_training_set_reviews.JSON", "r") as revfile:
        reviews = [json.loads(line) for line in revfile]
    df = pd.DataFrame(reviews)
    print df.head(2)