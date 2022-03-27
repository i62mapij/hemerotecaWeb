import json
import tempfile
import mimetypes
import base64
from base64 import b64encode
import requests
from bs4 import BeautifulSoup
import re
import uuid
import heapq
import nltk
from PIL import Image
import urllib.parse
from urllib.request import urlopen
from htmldate import find_date
nltk.download('punkt')
nltk.download('stopwords')
from datetime import datetime

class ForbidedError(Exception):
    pass

#class to extract elements from a web through its URL and map them to objects
class UrlToObject():

 #get a BeautifulSoup object from an URL
 #url: url to extract from
 def getSoupObjectFromURL(self,url):  
    res = requests.get(url)
    soup=None
    if res.status_code==200:
     htmlPage = res.content
     soup = BeautifulSoup(htmlPage, 'html.parser')
    elif  res.status_code==403:
      raise ForbidedError("El propietario de esta página web impide su descarga") 
    else:
      raise Exception("Error al descargar la página web")  
    return soup

 #get the datetime from the BeautifulSoup object or using de find_date util
 #url: url to extract from
 #soup: BeautifulSoup object
 def getDateWebPage(self,url,soup):
    date=''
    try:
     date=find_date(url)
    
     #if the date was not found try it from the soup object
     if date=='':
      for i in soup.findAll('time'):
       if i.has_attr('datetime'):
        date = i.get('datetime')
        break
    except:
        date=''
    
    #format the date found
    formattedDate = date
   
    if len(date.split("-"))>1:
      if len(date.split("-")[0])==4:
        formattedDate=date.split("-")[2]+'/'+date.split("-")[1]+'/'+date.split("-")[0]
       
    return formattedDate

 #get the title from de BeautifulSoup object
 #soup: BeautifulSoup object
 def getTitleWebPage(self,soup):
    title=''
    try:
     text = soup.find_all(text=True)
     output = ''
     for t in text:      
        output += '{} '.format(t)
        
        if t.parent.name=='title':
         title= '{} '.format(t) 
         break
    except Exception as exc:
        title=''
    
    return title.lstrip().rstrip()

 #get an array of paragraphs from de BeautifulSoup object
 #soup: BeautifulSoup object
 def getArrayParagraphs(self,soup):
    textDiv=[]
    pTags = soup.find_all('p')
    divTags = soup.find_all('div')
    hasDivAndP=False
    for div in divTags:
     pTags = div.find_all('p')
     
     textTags = [tag.get_text().strip() for tag in pTags]
     if not hasDivAndP and len(textTags)>0:
      hasDivAndP=True
     
     sentenceList = [sentence for sentence in textTags if not '\n' in sentence]
     sentenceList = [sentence for sentence in sentenceList if '.' in sentence]
   
     textDiv.append(' '.join(sentenceList))
    
    if not hasDivAndP:
     pTags = soup.find_all('p')
     
     textTags = [tag.get_text().strip() for tag in pTags]
     
     sentenceList = [sentence for sentence in textTags if not '\n' in sentence]
     sentenceList = [sentence for sentence in sentenceList if '.' in sentence]
   
     textDiv.append(' '.join(sentenceList))
    
    return textDiv
 
 #get the title word occurrences in the text score
 # text: article text
 # titleWords: title word
 def getScoreTitleWordsInText(self,text,titleWords):
    score=0
    for titleWord in titleWords:
     if titleWord in text:
      score=score+1
    return score

 # get the main paragraph of the text in the context of the title
 #soup: BeautifulSoup object
 #title: article title
 def getMainParagraphAboutTitle(self, soup, title):
    textDiv=self.getArrayParagraphs(soup)
    
    textArticle=''
    titleWords=[]
    stopWords = nltk.corpus.stopwords.words('spanish')
    
    for word in nltk.word_tokenize(title):
     if word not in stopWords:
      titleWords.append(word)
   
    scoreMax=0
    for text in textDiv:
     score=self.getScoreTitleWordsInText(text,titleWords)
     
     if score>scoreMax:
      scoreMax=score
      textArticle=text
    
    return textArticle

 #get word frequencies from a text
 #text: text 
 def getWordFrequencies(self,text):
    stopWords = nltk.corpus.stopwords.words('spanish')
    frequencies = {}
    maxFreq=0
    for word in nltk.word_tokenize(text):
        if word not in stopWords:
            if word not in frequencies.keys():
                frequencies[word] = 1
            else:
                frequencies[word] += 1
                maxFreq = max(frequencies.values())
                
    for word in frequencies.keys():
        if maxFreq>0:
         frequencies[word] = (frequencies[word]/maxFreq)
        else:
         frequencies[word] = 1
    return frequencies

 #get the summary of the text using word frequency
 #wordFrequencies: word frequency
 #text: text
 def getSummary(self,wordFrequencies,text):
   summary = ''
   try:
    sentenceList = nltk.sent_tokenize(text)
    sentenceScores = {}
    for sent in sentenceList:
        for word in nltk.word_tokenize(sent.lower()):
            if word in wordFrequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentenceScores.keys():
                        sentenceScores[sent] = wordFrequencies[word]
                    else:
                        sentenceScores[sent] += wordFrequencies[word]
        
    summarySentences = heapq.nlargest(7, sentenceScores, key=sentenceScores.get)
    summary = ' '.join(summarySentences)   
   
   except Exception as exc:
        summary = ''
    
   return summary
 
 #get the parts of de web from the URL link
 #url: url link
 def getDataFromSoupObject(self,url):
    try:
     soup = self.getSoupObjectFromURL(url)
     title=self.getTitleWebPage(soup)
     imageSelect = self.getMainImageWebPage(soup,url)
     date=self.getDateWebPage(url,soup)
     text=self.getMainParagraphAboutTitle(soup,title)   
     wordFrequencies = self.getWordFrequencies(text)    
     summary=self.getSummary(wordFrequencies,text)
     return title,imageSelect,date,text,summary
    except Exception as exc:
     raise exc
 
#get the text from the url link
#url: url link
 def getTextFromSoupObject(self,url):
    text=''

    try:
     soup = self.getSoupObjectFromURL(url)
     title=self.getTitleWebPage(soup)
     text=self.getMainParagraphAboutTitle(soup,title)   
    except Exception as exc:
      text=''
    
    return text

#get the parts of the web page and return them as an json object
#url: url link
#screen_name: Twitter user screen name
#type: catch source
 def getDataFromWebPage(self,url,screen_name,type):  
     try:
      title,image,date,text,summary=self.getDataFromSoupObject(url)

      return {
                'title': title,
                'webDate':date,
                'url':url,
                'type': type,
                'text': text,
                'summary':summary,
                'image': image,
                'screen_name':screen_name
           }
     
     except Exception as exc:
      raise exc
 
 #get the main image from of the web page from the url
 #soup: BeautifulSoup object
 #url:url link
 def getMainImageWebPage(self,soup,url):
   imageSelect=''
   try:
    images = soup.findAll('img')
    widthAnt=0
    heightAnt=0
    width=0 
    height=0
    parsedURL=urllib.parse.urlparse(url)
    
    isImage=False
    imgWithDomain = ''
    for im in images:  
      width=0 
      height=0    
      if not im.has_attr('src') or im['src']=='': 
       continue
      try:  
       #try images with src attribute 
       if im['src'].startswith("/"):   
        imgWithDomain= parsedURL.scheme+"://"+parsedURL.netloc+im['src']
       else:
        imgWithDomain=im['src']
          
       image = Image.open(requests.get(imgWithDomain, stream=True).raw)
       isImage=True
       width, height = image.size
       
       #returns the highest image
       if height>heightAnt:
        imageSelect=imgWithDomain
        heightAnt=height
      except:
       isImage=False
       #try images with source attribute
       children = im.findChildren("source" , recursive=False)
       for imgAlt in children:
        width=0 
        height=0       
        if not imgAlt.has_attr('srcset') or imgAlt['srcset']=='': 
         continue
        try:  
         if im['src'].startswith("/"):
          imgWithDomain= parsedURL.scheme+"://"+parsedURL.netloc+imgAlt['srcset']
         else:
          imgWithDomain=imgAlt['srcset']
        
         image = Image.open(requests.get(imgWithDomain, stream=True).raw)
         isImage=True
         if isImage:           
          width, height = image.size
      
         if height>heightAnt:
          imageSelect=imgWithDomain
          heightAnt=height
        except:
         isImage=False
   except Exception as excGen:
       imageSelect=''
    
   return imageSelect
    