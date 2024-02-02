from collections import deque, OrderedDict
from util import getTermFrequencyWeight
from structures import Document
from math import log


class InvertedIndex:
    def __init__(self) -> None:
        self.inverted_index = OrderedDict()
        self.countOfDocument = 0
    
    def append(self, wordTerm, newId, doc: Document):
        self.countOfDocument += 1
        for w in wordTerm:
            if w not in self.inverted_index:
                self.inverted_index[w] = {
                    'documentFrequency': 0,
                    'postingList': deque(),
                    'totalTermFrequency': 0
                }
            cellInvertedIndex = { 
                'termFrequency' : wordTerm[w],
                'document': doc,
                'weight': getTermFrequencyWeight(wordTerm[w])
            }
            self.inverted_index[w]['postingList'].append(
                cellInvertedIndex
            )
            doc.words[w] = cellInvertedIndex
            self.inverted_index[w]['totalTermFrequency'] += wordTerm[w]
    
    def calcDocumentFrequencyAndWeight(self):
        for word in self.inverted_index:
            self.inverted_index[word]['documentFrequency'] = len(
                self.inverted_index[word]['postingList']
            )
            inverseDocumentFrequency = log(
                self.countOfDocument / self.inverted_index[word]['documentFrequency']
            )
            self.inverted_index[word]['inverseDocumentFrequency'] = inverseDocumentFrequency
            for cellInvertedIndex in self.inverted_index[word]['postingList']:
                cellInvertedIndex['weight'] *= inverseDocumentFrequency
    
    def getWordIDF(self, word):
        return self.inverted_index.get(word, { 'inverseDocumentFrequency': 0 })['inverseDocumentFrequency']

    