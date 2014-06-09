import numpy as np
from lxml.html import fromstring
from urllib2 import urlopen
import sys

#Gets pertinent info based on a plane's tail number:
def scrape_tail(tailnum,urlprefix = "http://planefinder.net/data/aircraft/"):
    url = urlprefix+tailnum
    stringpage = (urlopen(url)).read()
    tree = fromstring(stringpage)

    datasections = tree.xpath('//td[@class = "stacked-stat"]')
    outdict = {}
    for section in datasections:
        name,value = woo.getchildren()
        outdict[name.strip()] = value.strip()

    return outdict


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Syntax: [Tail #]")

    print scrape_tail(sys.argv[1])
