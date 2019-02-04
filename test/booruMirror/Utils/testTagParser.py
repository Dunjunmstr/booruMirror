import unittest
import sys
from mock import MagicMock
sys.path.append('../../..') 
from booruMirror.Utils.TagParser import TagParser, TokenLogicException
class TestTagParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        # """
        # For now, just sets up a sample danbooru page for usage.
        # """
        # samplePage = open("sampleDanbooruPage.html", "r").read()
        # cls.samplePage = samplePage
        # sampleArticle = open("sampleDanbooruArticle.txt", "r").read()
        # cls.sampleArticle = sampleArticle
        # DanbooruParser.readWebpage = MagicMock(return_value=samplePage)

    def _escapeInputTagLogic(self, inputTagLogic):
        specialCharacters = ["(", ")", "|", "^", "&", "!"]
        for character in specialCharacters:
            inputTagLogic = inputTagLogic.replace(character, "`" + character)
        return inputTagLogic

    def _tagParserRepresentationTest(self, inputTagLogic, expectedRepresentation, addEscape = True):
        escapedInputTagLogic = inputTagLogic
        if addEscape:
            escapedInputTagLogic = self._escapeInputTagLogic(inputTagLogic)
        tagParserObject = TagParser(escapedInputTagLogic)
        self.assertEqual(str(tagParserObject), expectedRepresentation)

    def testRepresentationBasic1(self):
        self._tagParserRepresentationTest("(a | b)", "(a | b)")
        self._tagParserRepresentationTest("(a & b)", "(a & b)")
        self._tagParserRepresentationTest("(a ^ b)", "(a ^ b)")
        self._tagParserRepresentationTest("!a", "!a")

    def testRepresentationBasic2(self):
        self._tagParserRepresentationTest("a | b", "(a | b)")
        self._tagParserRepresentationTest("a & b", "(a & b)")
        self._tagParserRepresentationTest("a ^ b", "(a ^ b)")
        self._tagParserRepresentationTest("(!a)", "!a")

    def testRepresentationAndDefault(self):
        self._tagParserRepresentationTest("a b", "(a & b)")
        self._tagParserRepresentationTest("(a b)", "(a & b)")

    def testRepresentationAdvanced1(self):
        self._tagParserRepresentationTest("a & b (c d)", "((a & b) & (c & d))")
        self._tagParserRepresentationTest("a & (b (c) | d)", "(a & ((b & c) | d))")

    def testRepresentationAdvancedNot(self):
        self._tagParserRepresentationTest("!a !(b & c) d", "((!a & !(b & c)) & d)")
        self._tagParserRepresentationTest("(!a | !b) & !c ^ !d", "(((!a | !b) & !c) ^ !d)")

    def testRepresentationSymbols(self):
        self._tagParserRepresentationTest("`!!", "!`!", False)
        self._tagParserRepresentationTest("`!asdf!", "!asdf!", False)
        self._tagParserRepresentationTest("`!`(asdf(!)`)", "!asdf(!)", False)
        self._tagParserRepresentationTest("`!`(asdf( !`)", "!(asdf( & `!)", False)

    def testRepresentationEmptyToken(self):
        self._tagParserRepresentationTest("", "<No tags>")

    def _tagParserRaiseTest(self, tagLogic, addEscape = True):
        if addEscape:
            tagLogic = self._escapeInputTagLogic(tagLogic)
        with self.assertRaises(TokenLogicException):
            TagParser(tagLogic)

    def testInvalidRepresentationBasic1(self):
        tagLogicList = ["!", "(", ")", "|", "&"]
        for tagLogic in tagLogicList:
            self._tagParserRaiseTest(tagLogic)

    def testInvalidRepresentationBasic2(self):
        self._tagParserRaiseTest(")(")
        self._tagParserRaiseTest("())(()")
        self._tagParserRaiseTest("(()")

    def testInvalidRepresentationBasic3(self):
        self._tagParserRaiseTest("!!")
        self._tagParserRaiseTest("&!")
        self._tagParserRaiseTest("&|")
        self._tagParserRaiseTest("&&")
        self._tagParserRaiseTest("!&")

    def testInvalidRepresentationBasic3(self):
        self._tagParserRaiseTest("a !")
        self._tagParserRaiseTest("a!")
        self._tagParserRaiseTest("!!")
        self._tagParserRaiseTest("a&!")
        self._tagParserRaiseTest("&a")
        self._tagParserRaiseTest("& &")

    def testInvalidRepresentationSingletons(self):
        pass

    def testInvalidRepresentationAdvanced1(self):
        self._tagParserRaiseTest("`(a_()", False)
        self._tagParserRaiseTest(":)`)", False)
        self._tagParserRaiseTest(":(`):)", False)




    
    # def 

    # def testEvaluationBasic1(self):
    #     orString = TagParser("(a | b)")
    #     self.assertEqual(str(orString), "(a | b)")
    #     xorString = TagParser("(a ^ b)")
    #     self.assertEqual(str(xorString), "(a ^ b)")
    #     andString = TagParser("(a & b)")
    #     self.assertEqual(str(andString), "(a & b)")
    #     notString = TagParser("!a")
    #     self.assertEqual(str(notString), "!a")

if __name__ == '__main__':
    unittest.main()



# a = TagParser("obama (!did | 7/11) or ")
# print a
# print a.evaluate("obama did 7/11 or")