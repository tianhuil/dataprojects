prec_scores = pd.read_csv('precision_scores.csv')
rec_scores = pd.read_csv('recall_scores.csv')
prec_scores = prec_scores.drop(u'Unnamed: 0',1)
rec_scores = rec_scores.drop(u'Unnamed: 0',1)
prec_avs = prec_scores.mean(1)
rec_avs = rec_scores.mean(1)

Math_recall = {}
Math_prec = {}
Phys_recall = {}
Phys_prec = {}
for item in math_labels:
    Math_recall[item] = rec_avs[all_labels.index(item)]
    Math_prec[item] = prec_avs[all_labels.index(item)]
for item in physics_labels:
    Phys_recall[item] = rec_avs[all_labels.index(item)]
    Phys_prec[item] = prec_avs[all_labels.index(item)]


plt.bar(range(len(Math_recall)), Math_recall.values(), align='center', alpha = 0.5, color = 'green')
plt.xticks(range(len(Math_recall)), Math_recall.keys(), rotation = 90)
plt.margins(0.02)
plt.title( 'Recall Averages for Math Subfields' )
plt.ylabel('Recall')
plt.show()

plt.bar(range(len(Math_prec)), Math_prec.values(), align='center', alpha = 0.5, color = 'green')
plt.xticks(range(len(Math_prec)), Math_prec.keys(), rotation = 90)
plt.margins(0.02)
plt.title( 'Precision Averages for Math Subfields' )
plt.ylabel('Precision')
plt.show()

plt.bar(range(len(Phys_recall)), Phys_recall.values(), align='center', alpha = 0.5, color = 'green')
plt.xticks(range(len(Phys_recall)), Phys_recall.keys(), rotation = 90)
plt.margins(0.02)
plt.title( 'Recall Averages for Physics Subfields' )
plt.ylabel('Recall')
plt.show()

plt.bar(range(len(Phys_prec)), Phys_prec.values(), align='center', alpha = 0.5, color = 'green')
plt.xticks(range(len(Phys_prec)), Phys_prec.keys(), rotation = 90)
plt.margins(0.02)
plt.title( 'Precision Averages for Physics Subfields' )
plt.ylabel('Precision')
plt.show()

