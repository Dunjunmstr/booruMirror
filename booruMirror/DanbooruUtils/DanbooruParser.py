# -*- coding: iso-8859-15 -*-
import urllib2
import re
import cPickle
import time
import os
import random
import logging
import math
import copy
import sys
# from functools import lru_cache

import pandas as pd
import numpy
import os
import time
import cPickle
from DanbooruPic import *
# sys.path.append('../..') 
# from booruMirror.Utils.TagParser import TagParser, TokenLogicException
from Utils.TagParser import TagParser, TokenLogicException 
# from guppy import hpy
import psutil
import datetime
import sqlite3
from mega import Mega

#############################################################################
########################## Front-end functions ##############################
#############################################################################

DEBUG = True

def getDanbooruDF():
  dbName = "danbooru.db"
  if os.path.isfile(dbName):
    print "Found database at %s" % (os.path.join(os.getcwd(), dbName))
  else:
    print "Database not found, downloading a snapshot from the internet...(This may take ~40 mins)"
    downloadDanbooruDB()
  highestIndex = findHighestIndex(dbName) #Gets the highest index in the database
  obtainImagesBetweenIndicesAsSqlite(highestIndex) #Updates the sqlite database
  return extractSqliteAsDF().set_index('dataId', drop=False)

def obtainImagesBetweenIndicesAsDF(startIndex, endIndex = None, arbitrarySizeLimit = 40000):
  if endIndex == None:
    endIndex = getMaximumDanbooruIndex()
  #There may be too many images to load all at once.
  #We'll load them in segments of 500k, and append each result to our DF one by one.
  if (endIndex - startIndex > arbitrarySizeLimit):
    dfAmalgamation = danbooruPicsToPandas([])
    for i in range (endIndex/arbitrarySizeLimit, (startIndex/arbitrarySizeLimit) - 1, -1):
      subStart = max(startIndex, i * arbitrarySizeLimit)
      subEnd = min(endIndex, (i + 1) * arbitrarySizeLimit)
      assert subEnd - subStart <= arbitrarySizeLimit
      subResult = obtainImagesBetweenIndicesAsDF(subStart, subEnd)
      dfAmalgamation = mergeDanbooruDFs(subResult, dfAmalgamation)
      print("Merged range %s to %s!" % (subStart, subEnd))
      process = psutil.Process(os.getpid())
      print(process.memory_info().rss)  # in bytes 
    return dfAmalgamation
  else:
    return danbooruPicsToPandas(list(obtainImagesBetweenIndices(startIndex, endIndex)))

def obtainImagesBetweenIndicesAsSqlite(startIndex, endIndex = None):
  if endIndex == None:
    endIndex = getMaximumDanbooruIndex()
  addToSqliteTable(obtainImagesBetweenIndices(startIndex, endIndex))

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
    print "At upperPoint %s" % upperPoint
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
      newPics = filter(lambda x: int(x.getId()) >= startIndex, newPics)
    results.update(newPics)
  return results

def generateFakeDanbooruPic(ourId, defaultFake = [DanbooruPic("""<article id="post_3341850" class="post-preview blacklisted" data-id="3341850" data-has-sound="false" data-tags="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky" data-pools="" data-approver-id="508240" data-rating="s" data-width="1440" data-height="810" data-flags="" data-has-children="false" data-score="0" data-fav-count="1" data-pixiv-id="71918955" data-file-ext="png" data-source="https://i.pximg.net/img-original/img/2018/12/02/00/27/08/71918955_p0.png" data-top-tagger="533129" data-uploader-id="533129" data-normalized-source="https://www.pixiv.net/member_illust.php?mode=medium&amp;illust_id=71918955" data-is-favorited="false" data-md5="6eecb0f46574adeaafee1782e9e5cbca" data-file-url="https://danbooru.donmai.us/data/6eecb0f46574adeaafee1782e9e5cbca.png" data-large-file-url="https://danbooru.donmai.us/data/sample/sample-6eecb0f46574adeaafee1782e9e5cbca.jpg" data-preview-file-url="https://raikou4.donmai.us/preview/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">  <a href="https://danbooru.donmai.us/posts/3341850?q=rating%3As+scenery+limit%3A200">    <picture>      <source media="(max-width: 660px)" srcset="https://raikou3.donmai.us/crop/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">      <source media="(min-width: 660px)" srcset="https://raikou4.donmai.us/preview/6e/ec/6eecb0f46574adeaafee1782e9e5cbca.jpg">      <img class="has-cropped-true" src="./sampleDanbooruPage_files/6eecb0f46574adeaafee1782e9e5cbca.jpg" title="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky rating:s score:0" alt="alu.m_(alpcmas) cloud falling_star original scenery sky star star_(sky) starry_sky">""")]):
  result = copy.deepcopy(defaultFake[0])
  result.propertyDict['dataId'] = ourId
  return result

def obtainImagesBetweenIndicesMock(startIndex, endIndex = None):
  print ("Getting mock indices:")
  results = [generateFakeDanbooruPic(i) for i in range (startIndex, endIndex)]
  print ("Done getting mock indices:")
  return results

  # #Indexing is python list syntax
  # if endIndex == None:
  #   endIndex = getMaximumDanbooruIndex()
  # upperPoint = endIndex
  # results = set()
  # while upperPoint > max(startIndex, 1):
  #   print "At upperPoint %s" % upperPoint
  #   # print upperPoint
  #   newPics = None
  #   while not newPics:
  #     try:
  #       newPics = obtainImagesAtIndex(upperPoint)
  #     except Exception as e:
  #       print("Couldn't get pictures due to %s, trying again in 10s" % str(e))
  #       time.sleep(10)
  #   upperPoint = min(newPics).getId()
  #   if upperPoint <= max(startIndex, 1):
  #     newPics = filter(lambda x: int(x.getId()) >= startIndex, newPics)
  #   results.update(newPics)
  # return results

def danbooruPicsToPandas(danbooruPics):
  columns = ["dataId", "dataTags", "dataRating", "dataScore", "dataFavcount", "dataFileUrl", "dataLargeFileUrl", "dataPreviewFileUrl", "originalString"]
  dtype = str
  pandasData = []
  for danbooruPic in danbooruPics:
    subResult = [(danbooruPic.originalString if (columns[i] == "originalString") else danbooruPic.propertyDict[columns[i]]) for i in range (0, len(columns))]
    pandasData.append(subResult)

  #Data populated. 
  result = pd.DataFrame(data = pandasData, columns = columns, dtype = dtype)
  result.set_index('dataId', inplace=True)
  return result

  
# def pandasToSqlite(pandasDF):


#############################################################################
########################## Basic helper functions ###########################
#############################################################################

"""Functions easy to write unit tests for."""

def parsePage(pageString):
  ourRegex = re.compile("(<article id=.*</article>)")
  result = ourRegex.findall(pageString)
  return result

def getMaximumDanbooruIndex():
  return obtainImagesAtURL("http://danbooru.donmai.us/")[-1].getId()

def mergeDanbooruDFs(old, new):
  #Merging:
  mergedDFs = pd.concat([old, new], ignore_index=False)
  return mergedDFs[~mergedDFs.index.duplicated(keep='last')]

def getURLAtIndex(currentId):
  return "http://danbooru.donmai.us/posts?page=1&tags=id%%3A<%s+limit%%3A200" % (str(currentId))

def obtainImagesAtIndex(index):
  URL = getURLAtIndex(index)
  return obtainImagesAtURL(URL)

def obtainImagesAtURL(URL):
  pageSource = readWebpage(URL)
  booruPicsString = parsePage(pageSource)
  booruPics = [DanbooruPic(picString) for picString in booruPicsString]
  return sorted(booruPics)

#############################################################################
######################## Untestable helper functions ########################
#############################################################################

def readWebpage(URL):
  hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'}
  req = urllib2.Request(URL, headers=hdr)
  return urllib2.urlopen(req, timeout=100).read()

# def 


# h = hpy()
# print h.heap()
# a = pd.HDFStore('junk.h5')
# imageDF = obtainImagesBetweenIndicesAsDF(1, 2500000)
# # a["booruDF4"] = imageDF
# print(datetime.datetime.now())
# print("Writing...")

def initializeSqliteTable():
  conn = sqlite3.connect("danbooru.db")
  cur = conn.cursor()
  cur.execute("""CREATE TABLE IF NOT EXISTS guru99 (
  Id integer PRIMARY KEY,
  dataTags text,
  dataRating text,
  dataScore integer,
  dataFavcount integer,
  dataFileUrl text,
  dataLargeFileUrl text,
  dataPreviewFileUrl text
  );""")
  conn.commit()

def extractSqliteAsDF(dbName = 'danbooru.db'):
  conn = sqlite3.connect(dbName)
  cur = conn.cursor()
  result = None
  with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    result = pd.read_sql_query("select * from images", conn)
  return result

def dfToSqlite(df, dbName = 'danbooru.db'):
  conn = sqlite3.connect(dbName)
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
  counter = 0
  print ("Adding dataframe to database!")
  keyList = "dataId","dataTags","dataRating","dataScore","dataFavcount","dataFileUrl","dataLargeFileUrl","dataPreviewFileUrl"
  for index, row in df.iterrows():
    valueList = map(lambda x: str(row[x]), keyList)
    keyString = ",".join(keyList)
    valueString = ",".join(["?"] * len(valueList))
    command = """REPLACE INTO images (%s) VALUES (%s)""" % (keyString, valueString)
    cur.execute(command, tuple(valueList))
    counter += 1
    if counter % 1000 == 0:
      print "Counter: %s" % counter
      print valueString
  print ("Done adding dataframe!")
  conn.commit()

def addToSqliteTable(danbooruPics):
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
  counter = 0
  print ("Adding dataframe to database!")
  for danbooruPic in danbooruPics:
    keyList = list(danbooruPic.propertyDict.keys())
    valueList = map(lambda x: str(danbooruPic.propertyDict[x]), keyList)
    keyString = ",".join(keyList)
    valueString = ",".join(["?"] * len(valueList))
    command = """REPLACE INTO images (%s) VALUES (%s)""" % (keyString, valueString)
    cur.execute(command, tuple(valueList))
    counter += 1
    if counter % 1000 == 0:
      print "Counter: %s" % counter
  print ("Done adding dataframe!")
  conn.commit()

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
  timestamp("Beginning retrieval...")
  if (tags, rating) in knownTagRating:
    ratingFilteredDatabase = getIndexElementsFromDatabase(database, knownTagRating[(tags, rating)])
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
  pageFilteredDatabase = getPageOfDatabase(ratingFilteredDatabase, page, imagesPerPage)
  timestamp("Retrieved page-filtered, returning...")
  return pageFilteredDatabase

def getPageOfDatabase(database, page, pageSize):
  offset = pageSize * (page)
  return database.nlargest(offset, "dataId").nsmallest(pageSize, "dataId")


# @lru_cache(maxsize=64)
def retrieveTagFilteredDF(database, tags, knownTagList=[dict()]):
  knownTags = knownTagList[0]
  if tags in knownTags:
    print "Using cache!!!"
    return knownTags[tags]

  ourParser = TagParser(tags)
  result = ourParser.evaluateDF(database)
  knownTags[tags] = result
  return result

def downloadDanbooruDB():
  m = Mega.from_ephemeral()
  print ("Initiated Mega instance, downloading danbooru snapshot from 2/2/19...")
  m.download_from_url('https://mega.nz/#!72ARxaSQ!-iOqAlYH6Rr7tbxFBiw3hnykIMiz0gcNgeEJMXLScQk')
  print ("Download complete.")

def retrieveRatingFilteredDF(database, rating):
  if (rating == "sqe"):
    return database
  ratingRegex = "[%s]" % rating #Should be a string of sqe
  result = database[database['dataRating'].str.contains(ratingRegex, regex=True)]
  return result

# def updateDatabase(dbName):
#   if dbName
#   conn = sqlite3.connect(dbName)
#   cur = conn.cursor()
#   with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     result = pd.read_sql_query("select * from images", conn)
#   return result

def findHighestIndex(dbName):
  conn = sqlite3.connect(dbName)
  cur = conn.cursor()
  cur.execute("SELECT MAX(dataId) FROM images;")
  rows = cur.fetchall()
  return rows[0][0]



# a = extractSqliteAsDF()
# b = retrieveTagFilteredDF(a, "shangguan_feiying")
# print b
# print "~~~~"
# print getPageOfDatabase(b, 2, 20)

# nanRow = pd.Series([numpy.NaN] * 8, index = ["dataId", "dataTags", "dataRating", "dataScore", "dataFavcount", "dataFileUrl", "dataLargeFileUrl", "dataPreviewFileUrl"])
# y = "1girl 2016 artist_name bare_shoulders black_border border dated fujiwara_no_mokou hair_ribbon highres long_hair looking_back nail_polish off_shoulder realistic red_eyes red_nails ribbon shangguan_feiying silver_hair smile solo touhou tress_ribbon upper_body watermark web_address"
# b = TagParser("shangguan_feiying")
# timestamp("Initializing DB!")
# print a.where(b.evaluate(a["dataTags"])).dropna()


# counter = 0
# for index, row in a.iterrows():
#   counter += 1
#   print row['dataTags']
#   if counter > 100:
#     break
# counter = 0

# b = TagParser("hi")
# print b.evaluate(["hi", "lo"])
# x = a.where(a['dataId'] > 3396800).dropna()

# 

# c = 
# dataBase[dataBase['dataTags'].str.contains("scenery", regex=False)]


# def xprint(row):
#   x = row['dataTags']
#   if "shangguan_feiying" in x:
#     print row
#     print type(row)
#     print len(row)
#     return b.evaluate(x)
#   return False
#   # print x

# obtainImagesBetweenIndicesAsSqlite(1)
# df = extractSqliteAsDF()
# for index, row in df.iterrows():
#   print row['dataTags']
#   if index > 10:
#     break

# timestamp("Finished initializing DB, about to evaluate")
# d = a.apply(lambda row: row if (xprint(row)) else nanRow, axis=1)
# timestamp("Done evaluating!")

# # print a.where("shangguan_feiying" in a['dataTags']).dropna()
# # print a['dataTags'].apply(lambda x: x if xprint(x) else numpy.NaN).dropna()

# # print a['dataTags'].apply(lambda x: " ".join(sorted(list(eval(x)))))


# # print a['dataTags'].apply(lambda x: xprint(x))

# print ("Taking orders!")
# while True:
#   try:
#     print eval(raw_input())
#   except Exception as e:
#     print "Failed from %s. Try again?" % e

# testingStuff()