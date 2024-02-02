from bs4 import BeautifulSoup
import os
from math import log

currentDirectory = os.getcwd()

def isSgmFile(sgmFile):
    return os.path.splitext(sgmFile)[1].lower() == '.sgm'

def getSgmFullPath(sgmFile):
    return os.path.join(currentDirectory, 'reuters21578', sgmFile)

def parseSgmFile(sgmFilePath):
    with open(sgmFilePath, 'r') as sgmFileHandle:
        sgmContent = '<XML>' + sgmFileHandle.read().replace('<!DOCTYPE lewis SYSTEM "lewis.dtd">', '') + '</XML>'
    return BeautifulSoup(sgmContent, 'xml')

def getWordsTermFrequency(words):
    wordTerm = {}
    for w in set(words):
        wordTerm[w] = words.count(w)
    return wordTerm

def getTermFrequencyWeight(termFrequency):
    return 1.0 + log(termFrequency)

def readLines(filePath):
    lines = []
    with open(filePath, 'r') as fileHandle:
        lines.extend([line.strip() for line in fileHandle.readlines()])
    return lines