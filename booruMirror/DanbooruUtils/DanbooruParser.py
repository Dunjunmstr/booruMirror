# -*- coding: iso-8859-15 -*-
import urllib.request, urllib.error, urllib.parse
import re
import time
import os
import copy
import pandas as pd
import numpy
import sys
sys.path.append('..')
from DanbooruUtils.DanbooruPic import *
from Utils.TagParser import TagParser, TokenLogicException
import Utils.ListUtils as ListUtils
import sqlite3
from mega import Mega

#############################################################################
########################## Front-end functions ##############################
#############################################################################
DEBUG = True

class DanbooruParser:
  #Should extend BooruScraper
  #Public API: getImageRange, refreshTag

  def __init__(self, dbName = "danbooru.db"):
    self.dbName = dbName
    self.database = None
    self.database = self.getDanbooruDF()
    self.knownTagRating = dict()
    self.knownTagDict = dict()
    self.lambdaGen = self.lambdaGenerator(self.database)

  def getImageDFFromArgs(self, page, tags, rating, imagesPerPage):
    #First we filter by tags, then by rating, then grab the appropriate pages
    ratingFilteredDatabase = None
    results = None
    self.timestamp("Beginning retrieval of the tags %s on page %s with ratings %s, with %s images per page..." % (tags, page, rating, imagesPerPage))
    if (tags, rating) not in self.knownTagRating:
      if tags in self.knownTagDict:
        tagFilteredDatabase = self.getIndexElementsFromDatabase(self.knownTagDict[tags])
      else:
        self.knownTagDict[tags] = self.retrieveTagFilteredDFWithLambdas(tags)
        tagFilteredDatabase = self.getIndexElementsFromDatabase(self.knownTagDict[tags])
      self.timestamp("Retrieved tag-filtered entries for %s..." % (tags))
      ratingFilteredDatabase = self.retrieveRatingFilteredDF(tagFilteredDatabase, rating)
      self.knownTagRating[(tags, rating)] = self.getIndicesFromDF(ratingFilteredDatabase)
      self.timestamp("Retrieved rating-filtered entries for %s and added to cache..." % (tags))
    else:
      self.timestamp("Retrieved rating-filtered via cache...")
    knownTagRatingElement = self.knownTagRating[(tags, rating)]
    start = (page - 1) * imagesPerPage
    end = page * imagesPerPage
    filteredDatabaseElements = reversed(ListUtils.getElementsFromReversedList(knownTagRatingElement, start, end))
    results = self.getIndexElementsFromDatabase(filteredDatabaseElements)
    self.timestamp("Retrieved page-filtered entries for query %s, returning..." % (tags))
    return results

  def refreshImages(self, tag = None):
    self.initializeSqliteTable()
    highestIndex = self.findHighestIndexFromDB() #Gets the highest index in the database
    newImages = self.obtainImagesBetweenIndices(tag, highestIndex)
    self.addToSqliteTable(newImages)
    if self.database:
      self.mergeDanbooruDFs(self.database, newImages)

  #############################################################################
  ########################## Instantiation code ###############################
  #############################################################################

  def getDanbooruDF(self):
    if os.path.isfile(self.dbName):
      print("Found database at %s" % (os.path.join(os.getcwd(), self.dbName)))
    else:
      print("Database not found, downloading a snapshot from the internet...(This may take ~40 mins)")
      self.downloadDanbooruDB()
    self.refreshImages()
    return self.extractSqliteAsDF()

  #############################################################################
  ############################# Helper functions ##############################
  #############################################################################

  def obtainImagesBetweenIndices(self, tag, startIndex, endIndex = None):
    #Indexing is python list syntax
    if endIndex == None:
      endIndex = self.getMaximumDanbooruIndex()
    upperPoint = endIndex
    results = set()
    newPics = True
    while upperPoint > max(startIndex, 1) and newPics:
      #There are two checks.
      #The first one is to cap the search if there are extra images involved.
      #The second is to cap the search if it doesn't necessarily reach the start index.
      print("At upperPoint %s" % upperPoint)
      # print upperPoint
      newPics = None
      while newPics == None:
        try:
          newPics = self.obtainImagesAtIndex(upperPoint, tag)
        except Exception as e:
          print("Couldn't get pictures due to %s, trying again in 10s" % str(e))
          time.sleep(10)
      if newPics: #Checks for emptiness
        upperPoint = min(newPics).getId()
        if upperPoint <= max(startIndex, 1):
          newPics = [x for x in newPics if int(x.getId()) >= startIndex]
        results.update(newPics)
    return results

  #############################################################################
  ########################## Artifactory functions ############################
  #############################################################################

  def downloadDanbooruDB(self):
    m = Mega.from_ephemeral()
    print ("Initiated Mega instance, downloading danbooru snapshot from 2/19/19...")
    artifactLink = "https://mega.nz/#!SzYSRaxR!-w3vMfOwH4PJqRjUfE7hijEEvTtlIx-TgQ3AFSSFdUI"
    m.download_from_url(artifactLink)
    print ("Download complete.")

  #############################################################################
  ########################## Basic helper functions ###########################
  #############################################################################

  """Functions easy to write unit tests for."""

  def getMaximumDanbooruIndex(self):
    return self.obtainImagesAtURL("http://danbooru.donmai.us/")[-1].getId()

  def mergeDanbooruDFs(self, old, new): #Use later
    #Merging:
    mergedDFs = pd.concat([old, new], ignore_index=False)
    return mergedDFs[~mergedDFs.index.duplicated(keep='last')]

  def obtainImagesAtIndex(self, index, extraTag = None):
    URL = self.getDanbooruURLAtIndex(index, extraTag)
    return self.obtainImagesAtURL(URL)

  def getDanbooruURLAtIndex(self, currentId, extraTag = None):
    result = "http://danbooru.donmai.us/posts?page=1&tags=id%%3A<%s+limit%%3A200" % (str(currentId))
    if extraTag:
      result += "+%s" % extraTag
    return result

  def parsePage(self, pageString):
    ourRegex = re.compile("(<article id=.*?</article>)")
    result = ourRegex.findall(pageString)
    return result

  def obtainImagesAtURL(self, URL):
    pageSource = str(self.readWebpage(URL))
    booruPicsString = self.parsePage(pageSource)
    booruPics = [DanbooruPic(picString) for picString in booruPicsString]
    return sorted(booruPics)

  #############################################################################
  ######################## Untestable helper functions ########################
  #############################################################################

  def readWebpage(self, URL):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'}
    req = urllib.request.Request(URL, headers=hdr)
    return urllib.request.urlopen(req, timeout=100).read()

  def timestamp(self, printString = None, lastTime = [None]):
    if DEBUG:
      timeString = None
      if not lastTime[0]:
        lastTime[0] = time.time()
        timeString = "Initialized timestamps"
        return
      else:
        newLastTime = time.time() 
        timeString = newLastTime - lastTime[0]
        lastTime[0] = newLastTime
      if printString:
        timeString = printString + ": " + str(timeString)
      print(timeString)

  def getIndexElementsFromDatabase(self, indices):
    return self.database.loc[indices, :]

  def getIndicesFromDF(self, dataframe):
    return [i for i in dataframe["dataId"]]

  def lambdaGenerator(self, df):
    memoizationDict = dict()
    def internalLambda(searchTerm):
      if searchTerm in memoizationDict:
        return set(memoizationDict[searchTerm])
      else:
        spacedTokenString = " " + searchTerm.strip() + " "
        if searchTerm == "":
          spacedTokenString = " "
        allEntries = df[df['dataTags'].str.contains(spacedTokenString, regex=False)]
        result = self.getIndicesFromDF(allEntries)
        memoizationDict[searchTerm] = result
        print ("Got %s entries" % len(result))
        return set(result)
    return internalLambda

  #############################################################################
  ############################# SQLite functions ##############################
  #############################################################################

  def extractSqliteAsDF(self):
    """Extracts all entries from the Sqlite table"""
    conn = sqlite3.connect(self.dbName)
    cur = conn.cursor()
    result = None
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
      result = pd.read_sql_query("select * from images", conn)
    result.set_index('dataId', drop=False, inplace = True)
    return result


  def findHighestIndexFromDB(self):
    """Finds the most recent entry of a database by index."""
    conn = sqlite3.connect(self.dbName)
    cur = conn.cursor()
    cur.execute("SELECT MAX(dataId) FROM images;")
    rows = cur.fetchall()
    result = rows[0][0]
    if result == None:
      result = 1
    return result

  def addToSqliteTable(self, danbooruPics):
    """Adds a set of pictures to the sqlite table"""
    conn = sqlite3.connect(self.dbName)
    cur = conn.cursor()
    counter = 0
    print ("Adding dataframe to database!")
    for danbooruPic in danbooruPics:
      keyList = list(danbooruPic.propertyDict.keys())
      valueList = [str(danbooruPic.propertyDict[x]) for x in keyList]
      keyString = ",".join(keyList)
      valueString = ",".join(["?"] * len(valueList))
      command = """REPLACE INTO images (%s) VALUES (%s)""" % (keyString, valueString)
      cur.execute(command, tuple(valueList))
      counter += 1
      if counter % 1000 == 0:
        print("Counter: %s" % counter)
    print ("Done adding dataframe!")
    conn.commit()

  def initializeSqliteTable(self):
    conn = sqlite3.connect(self.dbName)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS images (
    dataId integer PRIMARY KEY,
    dataTags text,
    dataRating text,
    dataScore integer,
    dataFavcount integer,
    dataFileUrl text,
    dataLargeFileUrl text,
    dataPreviewFileUrl text
    );""")
    conn.commit()

  def retrieveTagFilteredDFWithLambdas(self, tags):
    ourParser = TagParser(tags)
    return sorted(list(ourParser.lambdaHandler(self.lambdaGen)))

  def retrieveRatingFilteredDF(self, database, rating):
    """Retrieves all posts from a dataframe of a certain rating."""
    if (rating == "sqe"):
      return database
    ratingRegex = "[%s]" % rating #Should be a string of sqe
    result = database[database['dataRating'].str.contains(ratingRegex, regex=True)]
    return result