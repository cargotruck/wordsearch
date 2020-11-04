#!/usr/bin/env python3

#--------------------------------------------------------------------------

# make_wordsearch.py written by nicholas.flesch@outlook.com
# last modified: 21 October 2020
# Takes a list of words from a test document and builts a
# wordsearch puzzle from them. The user can  set
# optional parameters of number of columns, number of rows,
# output destination, and puzzle title.
#
# Workflow:
# get user options >> read words into list (trims leading/trailing
# spaces and special characters, also replaces spaces
# in words with a special marker) >> check words meet 
# requirements (checks for special characters, word length, 
# and total number of words does not exceed puzzle maximum) >>
# randomly assign direction of word >> randomly assign 
# possition of word (also checks for error correction) >>
# write word into a dictionary with its coordinates >>
# fill grid with words and random letters >>
# write puzzle to html document
#


#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

import argparse
import sys
import os
import random
from datetime import datetime
from enum import Enum

#--------------------------------------------------------------------------

errorFlag = False;

#--------------------------------------------------------------------------

class Write_Direction(Enum):
    Horizontal = 1
    Vertical = 2
    Dexter = 3
    Sinister = 4

#--------------------------------------------------------------------------

def errorMsg(msg):
    print("ERROR: " + msg)
    global errorFlag 
    errorFlag = True

#--------------------------------------------------------------------------

def getUserOptions():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--source",help = "sets the source file")
    parser.add_argument("-d","--dest",help = "sets the destination directory")
    parser.add_argument("-r","--rows",help = "sets the maximum number of rows")
    parser.add_argument("-c","--columns",help = "sets the maximum number of columns")
    parser.add_argument("-t","--title",help = "sets the title of the document")
    args = parser.parse_args()

    if args.source:
        sourceFile = args.source
    else:
        errorMsg("No source file.\n\nSpecify a source file: -s")
    if args.dest:
        destDir = args.dest
    else:
        destDir = os.getcwd()
    if args.columns:
        totalColumns = int(args.columns)
        if(totalColumns > 25):
            errorMsg("Total number of columns must be less than 25.")
    else:
        totalColumns = 25
    if args.rows:
        totalRows = int(args.rows)
        if(totalRows > 15):
            errorMsg("Total number of rows must be less than 15.")
    else:
        totalRows = 15
    if args.title:
        title = args.title
    else:
        title = "WORD SEARCH"
   
    if(errorFlag == True):
        sys.exit()

    return sourceFile,destDir,totalColumns,totalRows,title

#--------------------------------------------------------------------------

def cleanWord(word):
    word = word.strip()
    word = word.strip(",")
    word = word.strip(";") 
    word = word.replace(" ","`")

    return word

#--------------------------------------------------------------------------

def getWordList(sf):

    fp = open(sf,"r")
    wordList = []

    while True:
        buffer = fp.readline()
        if buffer == "":
            break
        else:
            wordList.append(cleanWord(buffer))
    fp.close
    
    return wordList

#--------------------------------------------------------------------------

def yesNo(msg):

    while True:
        answer = str(input(msg))
        if answer[0].lower() == 'y':
            return True
        elif answer[0].lower() == 'n':
            return False
        else:
            continue 

#--------------------------------------------------------------------------

def wordIsShortEnough(word,columns,rows):
    maxSize = 0
    if columns <= rows:
        maxSize = columns
    else:
        maxSize = rows

    maxSize -= 3

    if len(word) > maxSize:
        if yesNo("\'" + word.replace("`"," ") + "\' is too long. Remove word and continue? [Y]es/[N]o\n"):
            return ""
        else:
            print("Exiting...")
            sys.exit()

    return word

#--------------------------------------------------------------------------

def noSpecialCharacters(word):
    if word == "":
        return word

    if not word.replace("`","").isalpha():
        if yesNo("\'" + word.replace("`", " ") + "\' contains illegal characters. Only letters are allowed.\n" \
            + "Remove word and continue? [Y]es/[N]o\n"):
            return ""
        else:
            print("Exiting...")
            sys.exit()

    return word

#--------------------------------------------------------------------------

def checkWords(words,columns,rows):
    wordsDraft = []
    for word in words:
        word = wordIsShortEnough(word,columns,rows)
        word = noSpecialCharacters(word)
        if len(word) > 0:
            wordsDraft.append(word)

    maxNumWords = ((columns * rows) / 8 ) * 3
    if len(wordsDraft) > maxNumWords:
        print("The number of words in the list exceeds the number allowed (" + maxNumWords + ")")
        print("Exiting...")
        sys.exit()

    return wordsDraft

#--------------------------------------------------------------------------
   
def makeGrid(columnLength,rowLength):
    
    grid = []
    
    for row in range(rowLength):
        r = []
        for c in range(columnLength):
                r.append("*")
        grid.append(r)

    return grid

def genStartCoords(writeDirection,columnLength,rowLength,wordLength):
    minX = 0
    minY = 0
    maxX = 0
    maxY = 0

    if writeDirection == Write_Direction.Horizontal:
        maxX = columnLength - wordLength
        maxY = rowLength

    elif writeDirection == Write_Direction.Vertical:
        maxX = columnLength
        maxY = rowLength - wordLength

    elif writeDirection == Write_Direction.Dexter:
        maxX = columnLength - wordLength
        maxY = rowLength - wordLength

    elif writeDirection == Write_Direction.Sinister:
        minY = wordLength
        maxX = columnLength - wordLength
        maxY = rowLength

    xCoord = random.randint(minX,maxX - 1)
    yCoord = random.randint(minY,maxY - 1)

    return xCoord,yCoord

#--------------------------------------------------------------------------

def mapWord(word,writeDirection,wordDirection,columnLength,rowLength):

    wordCoords = {word:{}}
    xCoord,yCoord = genStartCoords(writeDirection,columnLength,rowLength,len(word))

    if writeDirection == Write_Direction.Horizontal:
        for letter in word[::wordDirection]:
            coords = xCoord,yCoord
            wordCoords[word][coords] = letter
            xCoord += 1

    if writeDirection == Write_Direction.Vertical:
        for letter in word[::wordDirection]:
            coords = xCoord,yCoord
            wordCoords[word][coords] = letter
            yCoord += 1

    if writeDirection == Write_Direction.Dexter:
        for letter in word[::wordDirection]:
            coords = xCoord,yCoord
            wordCoords[word][coords] = letter
            xCoord += 1
            yCoord += 1     

    if writeDirection == Write_Direction.Sinister:
        for letter in word[::wordDirection]:
            coords = xCoord,yCoord
            wordCoords[word][coords] = letter
            xCoord += 1
            yCoord -= 1

    return wordCoords 

#--------------------------------------------------------------------------

def setCoordinates(word,columnLength,rowLength):

    wordLength = len(word)
    writeDirection = Write_Direction(random.randint(1,4))
    wordDirection = random.randint(0,1)
    
    if wordDirection == 0:
        wordDirection = -1

    if writeDirection == Write_Direction.Horizontal:
        return mapWord(word,writeDirection,wordDirection,columnLength,rowLength)

    elif writeDirection == Write_Direction.Vertical:
        return mapWord(word,writeDirection,wordDirection,columnLength,rowLength)

    elif writeDirection == Write_Direction.Dexter:
        return mapWord(word,writeDirection,wordDirection,columnLength,rowLength)

    elif writeDirection == Write_Direction.Sinister:
        return mapWord(word,writeDirection,wordDirection,columnLength,rowLength)

#--------------------------------------------------------------------------

def collisionDetection(masterDict,subDict):
    
    for masterEntry in masterDict:
        for subEntry in subDict:
            for letter in subDict[subEntry]:
                if masterDict[masterEntry].get(letter):
                    match = masterDict[masterEntry].get(letter)
                    if masterDict[masterEntry][letter] == subDict[subEntry][letter]:
                        return False
                    else:
                        return True

#--------------------------------------------------------------------------

def fillGrid(grid,wordsAndCoords):
 
    for masterEntry in wordsAndCoords:
        for coords in wordsAndCoords[masterEntry]:
            x = coords[0]
            y = coords[1]          
            grid[y][x] = wordsAndCoords[masterEntry][coords].upper()

    for row in grid:
        for column in row:
            if column == "*":
                newLetter = chr(random.randint(ord("A"),ord("Z")))
                row[row.index(column)] = newLetter

    return grid

#--------------------------------------------------------------------------

def writeHTML(destDir,finalGrid,wordList,title):

    HEADER = "<html>\n<body>\n<font face = \"Courier New\">\n<center>\n"
    FOOTER = "</body>\n</html>"
    TABLE_HEADER = "<table cellspacing = \"40\">\n"
    TABLE_FOOTER = "</table>"
    ROW_HEADER = "<tr align = \"center\", valign = \"middle\">\n"
    fileName = os.path.join(destDir,"WORD_SEARCH-"\
                + str(datetime.now().strftime("%Y%m%d%H%M%S%f"))\
                + ".html")
    title = "<h1>" + title + "</h1>\n"
    lSpace = " "
    divider = "-"

    fp = open(fileName, "w")

    fp.write(HEADER)
    fp.write(title)
    for row in finalGrid:
        fp.write("<p>")
        for letter in row:
            fp.write(letter + lSpace * 3)
        fp.write("</p>\n")
    fp.write("<p>" + divider * 74 + "</p>\n")
    fp.write(TABLE_HEADER)
    n = 0
    for word in wordList:
        word = word.replace("`"," ")
        if n == 0:
            fp.write(ROW_HEADER)
        fp.write("<td>" + word.upper() + "</td>\n")
        n += 1
        if n == 3:
            n = 0
    fp.write(TABLE_FOOTER)    
    fp.write(FOOTER)

    fp.close()
    print("Word search created at: file://" + fileName)

#--------------------------------------------------------------------------

def main():

    sourceFile,destDir,columns,rows,title = getUserOptions()
    wordList = checkWords(getWordList(sourceFile),columns,rows)
    masterDict = {}
    masterGrid = makeGrid(columns,rows)

    for word in wordList:
        word = word.replace("`","")
        while True:
            subDict = setCoordinates(word,columns,rows)
            if collisionDetection(masterDict,subDict) == True:
                continue
            else:
                masterDict[word] = subDict[word]
                break

    finalGrid = fillGrid(masterGrid,masterDict)
    writeHTML(destDir,finalGrid,wordList,title)

#--------------------------------------------------------------------------

if __name__ == "__main__":

    main()  
