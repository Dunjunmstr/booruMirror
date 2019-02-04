from flask import Flask, render_template, request, Markup
import DanbooruUtils.DanbooruParser as DanbooruParser
from Utils.TagParser import TagParser, TokenLogicException 
app = Flask(__name__)

# def BooruMirror():


def positiveIntConv(param, defaultValue):
    try:
        param = int(param) if param else defaultValue
        param = param if param > 0 else defaultValue
    except:
        print("Invalid page number of %s, defaulting to %s" % (param, defaultValue))
        param = defaultValue
    return param

@app.route('/')
def hello():
    args = request.args

    page = args.get("page")
    tags = args.get("tags")
    rating = args.get("rating")
    imagesPerPage = args.get("ipp")
    shouldLinkDirectly = args.get("sld")

    if not page and not tags and not rating and not imagesPerPage:
        rating = rating if rating else "s" #TODO: Replace this with an actual method of hiding degenerate images
    elif not rating:
        rating = "sqe"
    tags = tags if tags else ""
    page = positiveIntConv(page, 1)
    imagesPerPage = positiveIntConv(imagesPerPage, 20)

    shouldLinkDirectly = True if (shouldLinkDirectly and shouldLinkDirectly.lower().startswith("on")) else False

    print("Query for Page, Tag, Rating, IPP: %s, %s, %s, %s, %s" % (page, tags, rating, imagesPerPage, shouldLinkDirectly))

    servedImages = DanbooruParser.getImageDFFromArgs(dataBase,  page, tags, rating, imagesPerPage)
    imageString = renderDFAsPage(servedImages, shouldLinkDirectly)
    print("Delivering for Page, Tag, Rating, IPP: %s, %s, %s, %s, %s" % (page, tags, rating, imagesPerPage, shouldLinkDirectly))
    return render_template('pageTemplate.html', images = Markup(imageString), 
                                              page = page, 
                                              tags = tags, 
                                              rating = rating, 
                                              ipp = imagesPerPage,
                                              sld = shouldLinkDirectly)


def renderDFAsPage(df, shouldLinkDirectly):
    if len(df) == 0:
        return ""
    finalStringList = []
    finalStringList.append("<table cellspacing=\"30\"><tr>") #Starts a table
    counter = 0
    reversedDF = df.iloc[::-1]
    for index, row in reversedDF.iterrows():
      finalStringList.append("<td>")
      finalStringList.append(formatDFRow(row, shouldLinkDirectly))
      finalStringList.append("</td>")
      if counter % 5 == 4:
        finalStringList.append("</tr><tr>")
      counter += 1
    finalStringList.append("</tr></table>")
    return "".join(finalStringList)

def formatDFRow(row, shouldLinkDirectly):
    dataId = row["dataId"]
    dataTags = row["dataTags"]
    dataRating = row["dataRating"]
    dataScore = row["dataScore"]
    dataFavcount = row["dataFavcount"]
    dataFileUrl = row["dataFileUrl"]
    dataLargeFileUrl = row["dataLargeFileUrl"]
    dataPreviewFileUrl = row["dataPreviewFileUrl"]
    link = dataLargeFileUrl if shouldLinkDirectly else ("http://danbooru.donmai.us/posts/%s" % dataId)
    return """<a href="%s">  <picture>  <source media="(max-width: 660px)" srcset="%s">      <source media="(min-width: 660px)" srcset="%s">      <img class="has-cropped-true" src="%s" title="%s rating:%s score:%s" alt="%s"></picture></a>""" % (link, dataPreviewFileUrl, dataPreviewFileUrl, dataPreviewFileUrl, dataTags, dataRating, dataScore, dataTags)

if __name__ == '__main__':
    dataBase = DanbooruParser.getDanbooruDF()
    app.run()