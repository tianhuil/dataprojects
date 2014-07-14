with open('labelcounts.csv', 'r') as labcounts:
    for row in csv.DictReader(labcounts):
        count_dict = row
physics_counts = {item: int(count_dict[item]) for item in physics_labels}
math_counts = {item: int(count_dict[item]) for item in math_labels}   
titles = ['Physics Subfields','Math Subfields']
countlist = [physics_counts, math_counts]
for item in countlist:
    plt.bar(range(len(item)), item.values(), align='center', alpha = 0.5, color = 'green')
    plt.xticks(range(len(item)), item.keys(), rotation = 90)
    plt.margins(0.02)
    plt.title( 'Distribution of ' + titles[countlist.index(item)] )
    plt.ylabel('Number of Papers')
    plt.show()
