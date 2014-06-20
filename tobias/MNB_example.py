# Run sample_data_for_MNB beforehand- this is just an example
# of the implementation of those functions. 

# Drawing training sample
sample = Corpus(10000)

labels = [r'.*?math', r'.*?ph', r'.*?cs', r'.*?nlin', r'.*?cond-mat', r'.*?q-bio', r'.*?stat']


for label in labels:
    Data = GetData(sample.titlecorpus, sample.classes, label)
    Classify = MultiNBClass(Data.X_train, Data.Y_train, 'count')
    DataTest = Classify.vectorizer.transform(Data.X_test)
    y_pred = Classify.classifier.predict(DataTest)
    print label+' predicted: ', sum(y_pred)
    print label+' observed: ', sum(Data.Y_test)
    print label + " Precision:", metrics.precision_score(Data.Y_test, y_pred)
    print label + " Recall:", metrics.recall_score(Data.Y_test, y_pred)
