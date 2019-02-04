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