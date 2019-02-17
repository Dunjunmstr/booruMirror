# -*- coding: iso-8859-15 -*-
import urllib.request, urllib.error, urllib.parse
import re
import time
import os
import copy
import pandas as pd
import numpy
from .DanbooruPic import *
import sys
sys.path.append('..') 
from Utils.TagParser import TagParser, TokenLogicException
import Utils.ListUtils as ListUtils
import sqlite3
from mega import Mega

#############################################################################
########################## Front-end functions ##############################
#############################################################################

DEBUG = True

def getDanbooruDF():
  dbName = "danbooru.db"
  if os.path.isfile(dbName):
    print("Found database at %s" % (os.path.join(os.getcwd(), dbName)))
  else:
    print("Database not found, downloading a snapshot from the internet...(This may take ~40 mins)")
    downloadDanbooruDB()
  initializeSqliteTable()
  highestIndex = findHighestIndexFromDB(dbName) #Gets the highest index in the database
  obtainImagesBetweenIndicesAsSqlite(highestIndex) #Updates the sqlite database up to the highest index
  return extractSqliteAsDF()

def obtainImagesBetweenIndicesAsSqlite(startIndex, endIndex = None):
  initializeSqliteTable()
  addToSqliteTable(obtainImagesBetweenIndices(startIndex, endIndex))

#############################################################################
############################# Helper functions ##############################
#############################################################################

def obtainImagesBetweenIndices(startIndex, endIndex = None):
  #Indexing is python list syntax
  if endIndex == None:
    endIndex = getMaximumDanbooruIndex()
  upperPoint = endIndex
  results = set()
  while upperPoint > max(startIndex, 1):
    print("At upperPoint %s" % upperPoint)
    # print upperPoint
    newPics = None
    while not newPics:
      try:
        newPics = obtainImagesAtIndex(upperPoint)
      except Exception as e:
        print("Couldn't get pictures due to %s, trying again in 10s" % str(e))
        time.sleep(10)
    upperPoint = min(newPics).getId()
    if upperPoint <= max(startIndex, 1):
      newPics = [x for x in newPics if int(x.getId()) >= startIndex]
    results.update(newPics)
  return results

# TODO: Move this to testing
# def obtainImagesBetweenIndicesMock(startIndex, endIndex = None):
#   print ("Getting mock indices:")
#   results = [generateFakeDanbooruPic(i) for i in range (startIndex, endIndex)]
#   print ("Done getting mock indices:")
#   return results
#
# def generateFakeDanbooruPic(ourId, defaultFake = [DanbooruPic("""<article id="post_3341850" class="post-preview blacklisted" data-id="3341850" data-has-sound="false" data-tags="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky" data-pools="" data-approver-id="508240" data-rating="s" data-width="1440" data-height="810" data-flags="" data-has-children="false" data-score="0" data-fav-count="1" data-pixiv-id="71918955" data-file-ext="png" data-source="https://i.pximg.net/img-original/img/2018/12/02/00/27/08/71918955_p0.png" data-top-tagger="533129" data-uploader-id="533129" data-normalized-source="https://www.pixiv.net/member_illust.php?mode=medium&amp;illust_id=71918955" data-is-favorited="false" data-md5="6eecb0f46574adeaafee1782e9e5cbca" data-file-url="https://danbooru.donmai.us/data/6eecb0f46574adeaafee1782e9e5cbca.png" data-large-file-url="https://danbooru.donmai.us/data/sample/sample-6eecb0f46574adeaafee1782e9e5cbca.jpg" data-preview-file-url="https://raikou4.donmai.us/preview/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">  <a href="https://danbooru.donmai.us/posts/3341850?q=rating%3As+scenery+limit%3A200">    <picture>      <source media="(max-width: 660px)" srcset="https://raikou3.donmai.us/crop/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">      <source media="(min-width: 660px)" srcset="https://raikou4.donmai.us/preview/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">      <img class="has-cropped-true" src="./sampleDanbooruPage_files/6eecb0f46574adeaafee1782e9e5cbca.jpg" title="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky rating:s score:0" alt="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky">""")]):
#   result = copy.deepcopy(defaultFake[0])
#   result.propertyDict['dataId'] = ourId
#   return result

#############################################################################
########################## Artifactory functions ############################
#############################################################################

def downloadDanbooruDB():
  m = Mega.from_ephemeral()
  print ("Initiated Mega instance, downloading danbooru snapshot from 2/2/19...")
  m.download_from_url('https://mega.nz/#!72ARxaSQ!-iOqAlYH6Rr7tbxFBiw3hnykIMiz0gcNgeEJMXLScQk')
  print ("Download complete.")

#############################################################################
########################## Basic helper functions ###########################
#############################################################################

"""Functions easy to write unit tests for."""

def getMaximumDanbooruIndex():
  return obtainImagesAtURL("http://danbooru.donmai.us/")[-1].getId()

def mergeDanbooruDFs(old, new):
  #Merging:
  mergedDFs = pd.concat([old, new], ignore_index=False)
  return mergedDFs[~mergedDFs.index.duplicated(keep='last')]

def obtainImagesAtIndex(index):
  URL = getDanbooruURLAtIndex(index)
  return obtainImagesAtURL(URL)

def getDanbooruURLAtIndex(currentId):
  return "http://danbooru.donmai.us/posts?page=1&tags=id%%3A<%s+limit%%3A200" % (str(currentId))

def parsePage(pageString):
  ourRegex = re.compile("(<article id=.*?</article>)")
  result = ourRegex.findall(pageString)
  return result

def obtainImagesAtURL(URL):
  pageSource = str(readWebpage(URL))
  booruPicsString = parsePage(pageSource)
  booruPics = [DanbooruPic(picString) for picString in booruPicsString]
  return sorted(booruPics)

#############################################################################
######################## Untestable helper functions ########################
#############################################################################

def readWebpage(URL):
  hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'}
  req = urllib.request.Request(URL, headers=hdr)
  return urllib.request.urlopen(req, timeout=100).read()




def extractSqliteAsDF(dbName = 'danbooru.db'):
  conn = sqlite3.connect(dbName)
  cur = conn.cursor()
  result = None
  with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    result = pd.read_sql_query("select * from images", conn)
  result.set_index('dataId', drop=False, inplace = True)
  return result

def timestamp(printString = None, lastTime = [None]):
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

def getIndexElementsFromDatabase(database, indices):
  return database.loc[indices, :]

def getIndicesFromDF(dataframe):
  return [i for i in dataframe["dataId"]]


def getImageDFFromArgs(database, page, tags, rating, imagesPerPage, knownTagRatingList=[dict()], knownTagDict=[dict()]):
  #First we filter by tags, then by rating, then grab the appropriate pages
  knownTagRating = knownTagRatingList[0]
  ratingFilteredDatabase = None
  results = None
  timestamp("Beginning retrieval...")
  if (tags, rating) in knownTagRating:
    knownTagRatingElement = knownTagRating[(tags, rating)]
    start = (page - 1) * imagesPerPage
    end = page * imagesPerPage
    filteredDatabaseElements = ListUtils.getElementsFromReversedList(knownTagRatingElement, start, end)
    results = getIndexElementsFromDatabase(database, filteredDatabaseElements)
    timestamp("Retrieved rating-filtered via cache...")
  else:
    if tags in knownTagDict[0]:
      tagFilteredDatabase = getIndexElementsFromDatabase(database, knownTagDict[0][tags])
    elif " " in tags:
      tagFilteredDatabase = extractDFFromQuery(tags)
      knownTagDict[0][tags] = getIndicesFromDF(tagFilteredDatabase)
    else:
      tagFilteredDatabase = retrieveTagFilteredDF(database, tags)
      knownTagDict[0][tags] = getIndicesFromDF(tagFilteredDatabase)

    timestamp("Retrieved tag-filtered...")
    ratingFilteredDatabase = retrieveRatingFilteredDF(tagFilteredDatabase, rating)
    knownTagRating[(tags, rating)] = getIndicesFromDF(ratingFilteredDatabase)
    timestamp("Retrieved rating-filtered and added to cache...")
    if len(ratingFilteredDatabase) == 0:
      return ratingFilteredDatabase #Arbitrarily
    results = getPageOfDatabase(ratingFilteredDatabase, page, imagesPerPage)
  timestamp("Retrieved page-filtered, returning...")
  return results

def getPageOfDatabase(database, page, pageSize):
  offset = pageSize * (page)
  return database.nlargest(offset, "dataId").nsmallest(pageSize, "dataId")


#############################################################################
############################# SQLite functions ##############################
#############################################################################

def addToSqliteTable(danbooruPics):
  conn = sqlite3.connect("danbooru.db")
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

def initializeSqliteTable():
  conn = sqlite3.connect("danbooru.db")
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

def extractDFFromQuery(tags):
  conn = sqlite3.connect("danbooru.db")
  cur = conn.cursor()
  result = None
  timestamp("Resetting timestamp")
  timestamp("Connected, generating query for %s..." % tags)
  a = TagParser(tags)
  with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    result = pd.read_sql_query(a.generateSQLQuery(), conn)
  timestamp("Query complete, time taken:")
  return result

# @lru_cache(maxsize=None)
def retrieveTagFilteredDF(database, tags, knownTagList=[dict()]):
  knownTags = knownTagList[0]
  if tags in knownTags:
    print("Using cache!!!")
    return knownTags[tags]

  ourParser = TagParser(tags)
  result = ourParser.evaluateDF(database)
  knownTags[tags] = result
  return result

def retrieveRatingFilteredDF(database, rating):
  if (rating == "sqe"):
    return database
  ratingRegex = "[%s]" % rating #Should be a string of sqe
  result = database[database['dataRating'].str.contains(ratingRegex, regex=True)]
  return result

def findHighestIndexFromDB(dbName):
  conn = sqlite3.connect(dbName)
  cur = conn.cursor()
  cur.execute("SELECT MAX(dataId) FROM images;")
  rows = cur.fetchall()
  result = rows[0][0]
  if result == None:
    result = 1
  return result