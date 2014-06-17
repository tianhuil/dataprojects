from __future__ import print_function
import gzip
import sys


categories = ("Amazon_Instant_Video",
              "Arts",
              "Automotive",
              "Baby",
              "Beauty",
              "Books",
              "Cell_Phones_&_Accessories",
              "Clothing_&_Accessories",
              "Electronics",
              "finefoods",
              "Furniture",
              "Gift_Cards",
              "Gourmet_Foods",
              "Health",
              "Home_&_Kitchen",
              "Industrial_&_Scientific",
              "Jewelry",
              "Kindle_Store",
              "movies",
              "Musical_Instruments",
              "Music",
              "Office_Products",
              "Patio",
              "Pet_Supplies",
              "Shoes",
              "Software",
              "Sports_&_Outdoors",
              "Tools_&_Home_Improvement",
              "Toys_&_Games",
              "Video_Games",
              "Watches")


def clean(e_name):
    i = e_name.find('/')
    return e_name[i + 1:]


def _set_type(entry):
    tags = ['helpfulness', 'price', 'productId', 'profileName', 'score',
            'summary', 'text', 'time', 'title', 'userId']
    default = {
        'helpfulness': "0/0",
        'price': "unknown",
        'productId': "NA",     #not needed
        'profileName': "NA",   #not needed
        'score': "",
        'summary': "",
        'text': "",
        'time': "",            #not needed
        'title': "",
        'userId': "NA"         #not needed
    }
    for tag in tags:
        if tag not in entry:
            entry[tag] = default[tag]
    if entry['price'] == 'unknown':
        entry['price'] = "NaN"
    else:
        entry['price'] = float(entry['price'])
    entry['score'] = float(entry['score'])


def parse(category, data_dir=""):
    """
    :param category: dataset to open
    :param data_dir: location of 'Data' folder
    :return: iterator over dataset entries
    """
    f = gzip.open('{0}Data/{1}.txt.gz'.format(data_dir, category), 'r')
    entry = {}
    for line in f:
        line = line.strip()
        if not line:
            _set_type(entry)
            yield entry
            entry = {}
            continue
        garb, line = line.split("/", 1)
        desc, content = line.split(":", 1)
        entry[desc] = content.strip()


def parse_old(category, log=False):
    """
    Ex: parse('Electronics')
    if log is True display warning messages.
    """
    f = gzip.open('./Data/{0}.txt.gz'.format(category), 'r')
    entry = {}
    errs = 0
    for l in f:
        try:
            l = l.strip().decode(encoding="utf8")
        except:
            errs += 1
            if log:
                print("Warning %d: Decoding failed - " % errs,
                      l, file=sys.stderr)
            entry = {}
            continue
        colon_pos = l.find(': ')
        if colon_pos == -1:
            try:
                _set_type(entry)
            except KeyError:
                errs += 1
                if log:
                    print("Warning %d: Rating not found - " % errs,
                          entry, file=sys.stderr)
                continue
            yield entry
            entry = {}
            continue
        entry_name = clean(l[:colon_pos])
        rest = l[colon_pos + 2:]
        entry[entry_name] = rest


if __name__ == "__main__":
    for y in categories:
        print(y)
        for x in parse("Beauty", dir="../"):
            assert 'price' in x