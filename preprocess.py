from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re

stemmer = PorterStemmer()

stopwords = []
with open('stopwords.txt', 'r') as f:
    stopwords.extend([w.strip() for w in f.readlines()])

def tokenizeWords(content):
    words = word_tokenize(content)
    return list(filter(lambda x: bool(re.match(r'^([A-Za-z\-])+$', x)), words))

def remStopWords(words):
    for stopword in stopwords:
        while stopword in words:
            words.remove(stopword)

def stemWords(words):
    return list(map(lambda x: stemmer.stem(x), words))


def preProcess(content):
    words = tokenizeWords(content)
    remStopWords(words)
    return stemWords(words)