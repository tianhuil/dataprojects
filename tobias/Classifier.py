# Set up the main classifiers
MainClassify = MultiNBClass(train.title,'count', 5, (1,1))
RareClassify = MultiNBClass(rare.title,'count', 5, (1,1))
PhysicsClassify = MultiNBClass(physics.title, 'count', 5, (1,1))
MathClassify = MultiNBClass(math.title,'count', 5, (1,1))
MainClasses = Classifier(labels, test.title, train.categories, test.categories, MainClassify, 0.5)

# Separate papers that are math, physics, or rare (neither math nor physics) 
rare_titles = [test.title[i] for i in range(len(MainClasses.predicted)) if (MainClasses.predicted[i,0] + MainClasses.predicted[i,5]) == 0]
rare_cats = [test.categories[i] for i in range(len(MainClasses.predicted)) if (MainClasses.predicted[i,0] + MainClasses.predicted[i,5]) == 0]
rare_index = [i for i in range(len(MainClasses.predicted)) if (MainClasses.predicted[i,0] + MainClasses.predicted[i,5]) == 0]

math_titles = [test.title[i] for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,0] == 1]
math_cats = [test.categories[i] for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,0] == 1]
math_index = [i for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,0] == 1]

physics_titles = [test.title[i] for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,5] == 1]
physics_cats = [test.categories[i] for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,5] == 1]
physics_index = [i for i in range(len(MainClasses.predicted)) if MainClasses.predicted[i,5] == 1]

#Build math, physics, and rare classifiers
MathClasses = Classifier(math_labels, math_titles, math.categories, math_cats, MathClassify, 0.5)
PhysicsClasses = Classifier(physics_labels, physics_titles, physics.categories, physics_cats, PhysicsClassify, 0.5)
RareClasses = Classifier(rare_labels, rare_titles, rare.categories, rare_cats, RareClassify, 0.5)
