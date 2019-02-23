import unittest
import sys
import urllib2
from mock import MagicMock
sys.path.append('../../..') 
import booruMirror.DanbooruUtils.DanbooruParser as DanbooruParser
class TestDanbooruParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        For now, just sets up a sample danbooru page for usage.
        """
        samplePage = open("sampleDanbooruPage.html", "r").read()
        cls.samplePage = samplePage
        sampleArticle = open("sampleDanbooruArticle.txt", "r").read()
        cls.sampleArticle = sampleArticle
        DanbooruParser.readWebpage = MagicMock(return_value=samplePage)


    # TODO: Implement usage of this
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


    # def testGetMaximumDanbooruIndex1(self):
    #     """
    #     Checks to see if there doesn't exist a danbooru page with an index one greater than what is given.
    #     Has one edge case in which the next image is actually deleted, though I believe that usually,
    #     there is a placeholder page to indicated deleted pages.

    #     (THIS IS AN INTEGRATION TEST.)
    #     """
    #     currentMax = DanbooruParser.getMaximumDanbooruIndex()
    #     urlGenerator = (lambda x : "https://danbooru.donmai.us/posts/" + str(x))
    #     while urlExists(urlGenerator(currentMax + 1)):
    #         newMax = DanbooruParser.getMaximumDanbooruIndex()
    #         self.assertEqual(newMax, currentMax + 1)
    #         currentMax = newMax

    def testGetMaximumDanbooruIndex1(self):
        #Difficult to test this one due to the amount of data required, but this should probably suffice.
        self.assertEqual(3341850, DanbooruParser.getMaximumDanbooruIndex())
    
    def testParsePage1(self):
        self.assertEqual(200, len(DanbooruParser.parsePage(self.samplePage)))

    def testParsePage2(self):
        parsedPage = DanbooruParser.parsePage(self.samplePage)
        stringsOfInterest = ['data-id="', 'data-tags="', 'data-rating="', 'data-score="', 'data-fav-count="', 'data-file-url="', 'data-large-file-url="', 'data-preview-file-url']
        for article in parsedPage:
            for interestString in stringsOfInterest:
                self.assertIn(interestString, stringsOfInterest)

    # def testDanbooruPicsToPandas(danbooruPics):


    # def testMergeDanbooruDFs1(self):
    #     emptyDF = danbooruPicsToPandas([])
    #     populatedDF = 

    # def testMergeDanbooruDFs1(self):


    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


def urlExists(URL):
    try:
        hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'}
        req = urllib2.Request(URL, headers=hdr)
        pageSource = urllib2.urlopen(req, timeout=100).read()
        return True
    except urllib2.HTTPError as e:
        return False

if __name__ == '__main__':
    unittest.main()