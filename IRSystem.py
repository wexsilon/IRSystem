from math import sqrt
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy import array, maximum, linspace
from pandas import DataFrame
from pandas.plotting import table
import dataframe_image as dfi
import os


from util import (
    isSgmFile,
    getSgmFullPath,
    parseSgmFile,
    getWordsTermFrequency,
    getTermFrequencyWeight,
    readLines,
    currentDirectory
)
from preprocess import preProcess
from inverted_index import InvertedIndex
from structures import Document



OUT_DIR = os.path.join(currentDirectory, 'out')
if not os.path.isdir(OUT_DIR):
    os.mkdir(OUT_DIR)

invertedIndex = InvertedIndex()
documents = {}

for sgmFile in os.listdir('reuters21578'):
    if isSgmFile(sgmFile):
        sgmFillePath = getSgmFullPath(sgmFile)
        parsedSgmConent = parseSgmFile(sgmFillePath)
        for reuterDoc in parsedSgmConent.find_all('REUTERS'):
            if reuterDoc.get('TOPICS') == 'YES':
                newId = int(reuterDoc.get('NEWID'))
                topics = [d.text for d in reuterDoc.TOPICS.find_all('D')]
                if reuterDoc.TEXT.BODY:
                    words = preProcess(reuterDoc.TEXT.BODY.text)
                    doc = Document()
                    doc.topics = topics
                    doc.filePath = sgmFillePath
                    doc.docId = newId
                    documents[newId] = doc
                    invertedIndex.append(
                        getWordsTermFrequency(words), 
                        newId,
                        doc
                    )

invertedIndex.calcDocumentFrequencyAndWeight()


topicsStrings = readLines('topics-strings.txt')
topicDocument = []
for i in range(len(topicsStrings)):
    topicString = topicsStrings[i]
    topicDocument.append(
        len(
            dict(
                filter(
                    lambda doc: topicString in doc[1].topics,
                    documents.items()
                )
            )
        )
    )


resSubPlots: tuple[Figure, Axes] = plt.subplots(1, 1)
fig, ax = resSubPlots

queries = readLines('topics-queries.txt')
for i in range(len(queries)):
    query = queries[i]
    qwords = preProcess(query)
    qwordTerm = getWordsTermFrequency(qwords)
    for qword in qwordTerm:
        qwordTerm[qword] = \
            getTermFrequencyWeight(qwordTerm[qword]) * invertedIndex.getWordIDF(qword)
    similarDocuments = []
    for docId in documents:
        doc = documents[docId]
        sumOfQxD = 0
        sumOfQ2 = 0
        sumOfD2 = 0
        for qword in qwordTerm:
            sumOfQxD += qwordTerm[qword] * doc.words.get(qword, { 'weight': 0 })['weight']
            sumOfQ2 += qwordTerm[qword] ** 2
        if sumOfQxD != 0:
            for dword in doc.words:
                sumOfD2 += doc.words[dword]['weight'] ** 2
            divBy = (sqrt(sumOfQ2) * sqrt(sumOfD2))
            if divBy != 0:
                simCos = sumOfQxD / divBy
                similarDocuments.append((docId, simCos))

    similarDocuments.sort(reverse=True, key=lambda x:x[1])
    
    similarDocumentIndexs = []
    
    precisions = []
    recalls = []
    for j in range(len(similarDocuments)):
        topDocument = similarDocuments[j]
        if topicsStrings[i] in documents[topDocument[0]].topics:
            similarDocumentIndexs.append(j)
            p = len(similarDocumentIndexs) / (j + 1)
            r = len(similarDocumentIndexs) / topicDocument[i]
            precisions.append(p)
            recalls.append(r)
    
    nprecall = linspace(0.0, 1.0, num=len(precisions[:20]))
    npprecisions = array(precisions[:20]) * (1.-nprecall)
    decreasing_max_precision = maximum.accumulate(npprecisions[::-1])[::-1]
    ax.plot(nprecall, npprecisions, '--b')
    ax.step(nprecall, decreasing_max_precision, '-r')
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    queryOutDir = os.path.join(OUT_DIR, str(i))
    if not os.path.isdir(queryOutDir):
        os.mkdir(queryOutDir)
    fig.savefig(os.path.join(queryOutDir, f'curve.png'))
    ax.clear()
    fig.clear()
    
    df = DataFrame()
    for j in [100, 50, 10, 5]:
        kprecisions = precisions[:j]
        if len(kprecisions) == j:
            df[str(j)] = [sum(kprecisions) / j]
        else:
            break
    if len(df) > 0:
        df_styled = df.style.background_gradient()
        dfi.export(df_styled, os.path.join(queryOutDir, f'table.png'))
        
plt.close(fig)        
