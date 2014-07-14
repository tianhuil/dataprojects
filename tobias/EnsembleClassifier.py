class EnsembleClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self):
        pass
    
    def fit(self, train_corpus, train_categories):
       #vectorizing 
        self.vectorizer = CountVectorizer(min_df=5, ngram_range=(1,1), stop_words=nltk.corpus.stopwords.words('english'))
        self.X = self.vectorizer.fit_transform(train_corpus)
        self.words = self.vectorizer.get_feature_names()
        self.word_vect = self.vectorizer.transform(self.words)
        
        
        # create Y for each category, save in dictionaries
        observed_labels = {}
        for item in all_labels:
            observed_labels[item]= class_vector(item, train_categories)
                
        classifiers = {}
        predicted_train_probs = {}
        predicted_train_labels = {}
               
       # major classifying and then predicting training categories
        for item in major_labels:
            classifier = MultinomialNB()
            classifiers[item]=classifier.fit(self.X, observed_labels[item])
            predicted_train_probs[item]= classifiers[item].predict_proba(self.X)
            predicted_train_labels[item] = thresh_predict(predicted_train_probs[item][:,1], 0.5)
            
        train_subvectors = {}
        train_subcategories = {}
       # To change between training with predicted labels and training with known labels, switch from 
       # predicted_train_labels to observed_labels in conditions 
        m = np.array(observed_labels[r'math'])
        p = np.array(observed_labels[phys_short])
        conditions={'math': m ==1, 'physics': p ==1, 'rare': m + p == 0, 'mathph': m + p >= 1}

        for item in conditions:
            train_subvectors[item] = train_corpus[conditions[item]]
            train_subcategories[item] = train_categories[conditions[item]]
        
        subclass_obs_labels = {}
        mathph_classifiers = {} 
        secondary_labels = {'math': math_labels, 'physics': physics_labels, 'rare': rare_labels}
        # Create the classifiers for each of the subcategories
        for item in secondary_labels:
            X_sub = self.vectorizer.transform(train_subvectors[item])
            for label in secondary_labels[item]:
                classifier = MultinomialNB()
                subclass_obs_labels[label]=class_vector(label, train_subcategories[item])
                classifiers[label] = classifier.fit(X_sub, subclass_obs_labels[label])
        # Also want to run the math/physics papers through the rare categories, but
        # need to save separately to avoid overwriting the rare classifiers        
        X_sub=self.vectorizer.transform(train_subvectors['mathph'])
        for item in rare_labels:
            classifier = MultinomialNB()
            subclass_obs_labels[item] = class_vector(item, train_subcategories['mathph'])
            mathph_classifiers[item] = classifier.fit(X_sub, subclass_obs_labels[item])
            

       
        self.classifiers = classifiers
        self.mathph_classifiers = mathph_classifiers
        self.observed_labels = observed_labels
        self.predicted_train_labels = predicted_train_labels
        self.predicted_train_probs = predicted_train_probs
       
        return self
    
    def predict(self, test_corpus):
       # Vectorize the test data
       self.X_test = self.vectorizer.transform(test_corpus)
       # Classify the test data as math/physics/neither
       predicted_probs = {} 
       predicted_labels = {}

       for item in major_labels:
            predicted_probs[item] = self.classifiers[item].predict_proba(self.X_test)
            predicted_labels[item] = thresh_predict(predicted_probs[item][:,1], 0.5)
       # Separate the test data for the subclassifiers     
       subvectors = {}
       m = np.array(predicted_labels[r'math'])
       p = np.array(predicted_labels[phys_short])
       conditions={'math': m ==1, 'physics': p ==1, 'rare': m + p == 0, 'mathph': m + p >= 1}

       for item in conditions:
            subvectors[item] = test_corpus[conditions[item]]
       # Apply subclassifiers to test data   
       secondary_labels = {'math': math_labels, 'physics': physics_labels, 'rare': rare_labels}
       for item in secondary_labels:
            X_sub = self.vectorizer.transform(subvectors[item])
            for label in secondary_labels[item]:
                predicted_probs[label] = np.zeros(len(test_corpus))
                predicted_probs[label][conditions[item]] = self.classifiers[label].predict_proba(X_sub)[:,1]
                predicted_labels[label]= thresh_predict(predicted_probs[label], 0.5)
       # Again, run math/physics test data through the rare classifier separately          
       X_sub = self.vectorizer.transform(subvectors['mathph'])                
       for item in rare_labels:
            predicted_probs[item][m + p >= 1] = self.classifiers[item].predict_proba(X_sub)[:,1]
            predicted_labels[item]= thresh_predict(predicted_probs[item], 0.5)
    
       # return the predicted probabilities and labels  
       self.predicted_labels = predicted_labels
       self.predicted_probs = predicted_probs
       
            
       return self

