from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
#from helper.text_preprocessing import add_negation
from helper.text_preprocessing import stem
import pickle
import string


# Create your views here.
with open("classifier.p") as class_source:
    classifier = pickle.load(class_source)
with open("vectorizer.p") as vect_source:
    vectorizer = pickle.load(vect_source)


def index(request):
    template = loader.get_template('rate/index.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


@csrf_exempt
def predict(request):
    message = {}
    if request.method == 'POST':
        text = request.POST['text']
        exclude = set(string.punctuation)
        text = ''.join(ch for ch in text if ch not in exclude)
        data = stem(text)
        vectdata = vectorizer.transform(data)
        if not vectdata.getnnz() and len(data) < 5:
            value = 0
        else:
            value = classifier.predict(vectdata)[0]
        message['value'] = value
    json = simplejson.dumps(message)
    return HttpResponse(json, mimetype='application/json')
