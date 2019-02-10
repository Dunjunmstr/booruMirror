from flask import Flask, render_template, request, Markup
import DanbooruUtils.DanbooruParser as DanbooruParser
import Utils.HTMLFormatting as HTMLFormatting
from Utils.TagParser import TagParser, TokenLogicException

app = Flask(__name__)

@app.route('/')
def displayMainPage():
    args = request.args

    page = args.get("page")
    tags = args.get("tags")
    rating = args.get("rating")
    imagesPerPage = args.get("ipp")
    shouldLinkDirectly = args.get("sld")

    if not page and not tags and not rating and not imagesPerPage:
        rating = rating if rating else "s" 
        #TODO: Replace this with an actual method of hiding degenerate images
    elif not rating:
        rating = "sqe"
        
    page               = HTMLFormatting.positiveIntConv(page, 1)
    tags               = tags if tags else ""
    imagesPerPage      = HTMLFormatting.positiveIntConv(imagesPerPage, 20)

    shouldLinkDirectly = (True if (shouldLinkDirectly and 
                              shouldLinkDirectly.lower().startswith("on")) else False)
    print("Query for Page, Tag, Rating, IPP: %s, %s, %s, %s, %s" % 
                (page, tags, rating, imagesPerPage, shouldLinkDirectly))

    servedImages = DanbooruParser.getImageDFFromArgs(dataBase, 
                                                     page, 
                                                     tags, 
                                                     rating, 
                                                     imagesPerPage)
    imageString = HTMLFormatting.renderDFAsPage(servedImages, shouldLinkDirectly)
    print("Delivering for Page, Tag, Rating, IPP: %s, %s, %s, %s, %s" % 
                (page, tags, rating, imagesPerPage, shouldLinkDirectly))
    return render_template('pageTemplate.html', images = Markup(imageString), 
                                                page = page, 
                                                tags = tags, 
                                                rating = rating, 
                                                ipp = imagesPerPage,
                                                sld = shouldLinkDirectly)




if __name__ == '__main__':
    dataBase = DanbooruParser.getDanbooruDF()
    app.run()