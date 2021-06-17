#----------------------------------------------------------
# flashcards.py
# takes an html link and makes flashcards for the site
#----------------------------------------------------------

from bs4 import BeautifulSoup
import re
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#from latex import build_pdf
from pdflatex import PDFLaTeX
import os

# globalvariables------------------------------------------
dictionary = {}
additionalmath = {}

# main()---------------------------------------------------
def main():
    global dictionary
    htmlcode = requests.get("https://scioly.org/wiki/index.php/Crave_the_Wave")
    tree = BeautifulSoup(htmlcode.text, "html.parser")
    readhtml(tree)
    dictionary = notags(dictionary)
    dictionary = mathmode(dictionary)
    dictionary = dupli(dictionary)
    latexgen(dictionary, tree)

# helper functions-----------------------------------------
def readhtml(tree):
    global dictionary
    #prettyfile = str(tree.prettify)
    with open("log.txt", "w", encoding="utf-8") as file:
        prevterm = ""
        previtem = ""
        for tag in tree.find_all(["p", "b", "h4", "li","dd","div"]):
            term = ""
            definition = ""
            for i in tag.children:
                if str(i).find("href") == -1:

                    if str(i).find("<b>") != -1:
                        term = i.get_text()
                        definition += ("-")*(len(i.get_text()))
                    if str(i).find("<b>") == -1:
                        definition += str(i)
                if prevterm != "" and str(i).find("[/math]") != -1:
                    dictionary[prevterm] += str(i)
                    prevterm = ""
                if term != "":
                    if "\n\n" not in definition and "\n\n" not in term:
                        if (len(term)+0.01)/(len(definition)+0.01) < 0.75 and len(term)<300:
                            buffer = (term, definition)
                            dictionary.update([buffer])
                            prevterm = term
                        elif tag.get_text().find("[/math]") != -1:
                            buffer = (previtem, str(tag))
                            dictionary.update([buffer])
            previtem = tag.get_text()
        for key,value in dictionary.items():
            file.write(key+";; "+value+"\n\n")



def mathmode(dictionary):
    buffer = {}
    for key,definition in dictionary.items():
        mathdef = definition.find("[math]")
        mathenddef = definition.find("[/math]")
        while mathdef != -1 and mathenddef != -1:
            definition = definition[:mathdef] + "$" + definition[mathdef + 6:mathenddef] + "$" + definition[mathenddef + 7:]
            mathdef = definition.find("[math]")
            mathenddef = definition.find("[/math]")


        mathdef = key.find("[math]")
        mathenddef = key.find("[/math]")
        while mathdef != -1 and mathenddef != -1:
            key = key[:mathdef] + "$" + key[mathdef + 6:mathenddef] + "$" + key[mathenddef + 7:]
            mathdef = key.find("[math]")
            mathenddef = key.find("[/math]")
        buffer.update([(key, definition)])
    return(buffer)

#todo find out why "missing $ inserted" error happens. fix mathmode problem with key item. dupli function not pairing keys properly.

def notags(dictionary):
    for key,value in dictionary.items():
        update = ""
        brackets = False
        mathmode = False
        for i in value:
            if i == "$":
                mathmode = not mathmode
            if not mathmode:
                if i == "<":
                    brackets = not brackets
                if brackets == False:
                    update += i
                if i == ">":
                    brackets = not brackets
            else:
                update += i

        dictionary[key] = update
    return dictionary
        #go through the characters in the value checking for the mathmode ($) and stop when you get to a tag. dont remove it if it is within a mathmode, and remove it if it is (to check use the mathmode variable))
def countdash(definition):
    dashcount = 0
    maxdash = 0
    for i in definition:
        if i == "-":
            dashcount += 1
        else:
            if dashcount > maxdash:
                maxdash = dashcount
            dashcount = 0
    return maxdash

def dupli(dictionary):
    newdict = {}
    lastset = ("","")
    addvar = True
    for key,value in dictionary.items():
        if str(key) != "":
            if str(value).find(str(lastset[1])) != -1:
                addvar = True
            else:
                addvar = False
            if addvar:
                if lastset[0] != "":
                    lastset = ((lastset[0]+";;;; "+str(key)), (str(value)))
                else:
                    lastset = ((lastset[0]+str(key)), (str(value)))
                print(lastset)
            else:
                newdict.update([lastset])
                lastset = ("","")
    return newdict


def latexgen(dictionary, tree):
    with open("output.tex", "w", encoding="utf-8")as file:
        file.write("\\documentclass{beamer}\n")
        file.write("\\usepackage{tabularx}\n")
        file.write("\\usepackage{colortbl}\n")
        file.write("\\usepackage{amsmath}\n")
        file.write("\\usetheme{Copenhagen}\n")  # theme
        file.write("\\title{" + tree.find("title").get_text() + "}\n\n")
        file.write("\\begin{document}\n")
        file.write("\\begin{frame}\n")
        file.write("\\titlepage\n")
        file.write("\\end{frame}\n")
        for key,value in dictionary.items():
            if (countdash(value) != len(key) or len(key) > 2) and key != "" and value != "" :
                file.write("\\begin{frame}\n")
                file.write("\\begin{center}\n")
                file.write(value + "\n")
                file.write("\\end{center}\n")
                file.write("\\end{frame}\n")
                file.write("\\begin{frame}\n")
                file.write("\\begin{center}\n")
                file.write(f"\\bf{{{key}}}\n")
                file.write("\\end{center}\n")
                file.write("\\end{frame}\n")
        file.write("\\end{document}\n")
    os.system("pdflatex output.tex")

# callmain-------------------------------------------------
if __name__ == "__main__":
    main()
