# This script reads a file, list.txt, that lists all the files in a directory. It then opens each file with BeautifulSoup and saves them in a 
# list, PaperList. THis is useful for me right now because I'm working with a small directory. I need a different solution when I work with 
# actual directory of xml files; I don't want to put all 10^6 in a single list. 
temp = open("/home/tobias/Harvests/list.txt","r")
directory = temp.read().splitlines()
PaperList=[]
for line in directory:
    a = open("/home/tobias/Harvests/"+line,"r")
    PaperList.append(BeautifulSoup(a))
PaperList.pop(0) # at least in this example, the list file is the first file in Harvests, but I don't want it in the PaperList

