def positiveIntConv(param, defaultValue):
    try:
        param = int(param) if param else defaultValue
        param = param if param > 0 else defaultValue
    except:
        print("Invalid page number of %s, defaulting to %s" % (param, defaultValue))
        param = defaultValue
    return param

def renderDFAsPage(df, shouldLinkDirectly, numberOfColumns = 5):
    n = numberOfColumns
    if len(df) == 0:
        return ""
    reversedDF = df.iloc[::-1]
    entries = [formatDFEntry(row, shouldLinkDirectly) 
                  for index, row in reversedDF.iterrows()]
    gridEntries = [entries[i : i + n] for i in range(0, len(entries), n)]
    return formatGridEntriesAsHTML(gridEntries)

def formatGridEntriesAsHTML(entries):
    resultStringAsList = []
    tableStart = "<table><tr><td>"
    tableEnd = "</td></tr></table>"
    rowGap = "</td></tr><tr><td>"
    columnGap = "</td><td>"

    formattedRows = [columnGap.join(row) for row in entries]
    uncappedTable = rowGap.join(formattedRows)

    return tableStart + uncappedTable + tableEnd

def formatDFEntry(row, shouldLinkDirectly):
    dataId = row["dataId"]
    dataTags = row["dataTags"]
    dataRating = row["dataRating"]
    dataScore = row["dataScore"]
    dataFavcount = row["dataFavcount"]
    dataFileUrl = row["dataFileUrl"]
    dataLargeFileUrl = row["dataLargeFileUrl"]
    dataPreviewFileUrl = row["dataPreviewFileUrl"]
    link = (generateDirectLink(dataFileUrl) if shouldLinkDirectly else ("http://danbooru.donmai.us/posts/%s" % dataId)).replace("sample/", "").replace("sample-", "")
    return """<a href="%s">  <picture>  <source media="(max-width: 660px)" srcset="%s">      <source media="(min-width: 660px)" srcset="%s">      <img class="has-cropped-true" src="%s" title="%s rating:%s score:%s" alt="%s"></picture></a>""" % (link, dataPreviewFileUrl, dataPreviewFileUrl, dataPreviewFileUrl, dataTags, dataRating, dataScore, dataTags)

def generateDirectLink(fileURL):
    #Trick the site into thinking we're lost
    newServerURL = "://danbooru.donmai.us/data" #This server the apache error
    if newServerURL in fileURL:
        lastSlash = fileURL.rfind("/") + 1
        header = (fileURL[:lastSlash])
        footer = (fileURL[lastSlash:])
        bogusArtist = "__placeholderTags__"
        return header +  bogusArtist + footer
    return fileURL