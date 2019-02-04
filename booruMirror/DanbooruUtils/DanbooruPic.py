import re

class DanbooruPic:

  def __init__(self, articleString):
    self.propertyDict = dict()
    self.originalString = articleString
    self.propertyDict['dataId'] = "data-id"
    self.propertyDict['dataTags'] = "data-tags"
    self.propertyDict['dataRating'] = "data-rating"
    self.propertyDict['dataScore'] = "data-score"
    self.propertyDict['dataFavcount'] = "data-fav-count"
    self.propertyDict['dataFileUrl'] = "data-file-url"
    self.propertyDict['dataLargeFileUrl'] = "data-large-file-url" #We kinda don't need this
    self.propertyDict['dataPreviewFileUrl'] = "data-preview-file-url"
    for propKey in self.propertyDict.keys():
      tagToSearchFor = self.propertyDict[propKey]
      ourRegex = re.compile(tagToSearchFor + "=\"([^\"]*)\"")
      result = ourRegex.findall(articleString)
      if len(result) != 1:
        print ("For some reason, we have duplicate results for %s.")
      if self.propertyDict[propKey]:
        self.propertyDict[propKey] = result[0]
      else:
        self.propertyDict[propKey] = None
    #Special processing
    self.propertyDict['dataId'] = int(self.propertyDict['dataId'])
    self.propertyDict['dataTags'] = " " + self.propertyDict['dataTags'].strip() + " "
    self.propertyDict['dataScore'] = int(self.propertyDict['dataScore'])
    self.propertyDict['dataFavcount'] = int(self.propertyDict['dataFavcount'])

  def __eq__(self, other):
    return self.getId() == other.getId()

  def __ne__(self, other):
    return not self.__eq__(other)

  def __lt__(self, other):
    return int(self.propertyDict['dataId']) < int(other.propertyDict['dataId']) #CustomLt returns true iff self < other

  def __le__(self, other):
    return self.__lt__(other) or self.__eq__(other)
  
  def __gt__(self, other):
    return not self.__le__(other)

  def __ge__(self, other):
    return self.__gt__(other) or self.__eq__(other)

  def __repr__(self):
    sb = []
    sb.append("~~~~~~~~~")
    for propKey in self.propertyDict.keys():
      sb.append("%s: %s" % (propKey, self.propertyDict[propKey]))
    sb.append("~~~~~~~~~")
    return "\n".join(sb)

  def getId(self):
    return self.propertyDict['dataId']

  def getWebString(self):
    return self.originalString

  def getTags(self):
    return self.propertyDict['dataTags']

  def getFavCount(self):
    return self.propertyDict['dataFavcount']
    
  def getScore(self):
    return self.propertyDict['dataScore']

  def getRating(self):
    return self.propertyDict['dataRating']

  def __hash__(self):
    return self.getId()
