temp = open("/home/tobias/Harvests/list.txt","r")
directory = temp.read().splitlines()
PaperList=[]
for line in directory:
    a = open("/home/tobias/Harvests/"+line,"r")
    PaperList.append(BeautifulSoup(a))
PaperList.pop(0) # at least in this example, the list file is the first file in Harvests, but I don't want it in the PaperList

