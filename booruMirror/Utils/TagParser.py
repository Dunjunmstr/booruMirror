import re
import pandas as pd

class TokenLogicException(Exception):
    pass

def reverseEscapeInputTagLogic(inputTagLogic):
    specialCharacters = ["(", ")", "|", "^", "&", "!"]
    if inputTagLogic in specialCharacters:
        #The intent here is to escape lone special characters.
        #Apparently "!" is a valid edge case tag
        return "`" + inputTagLogic
    for character in specialCharacters:
        inputTagLogic = inputTagLogic.replace("`" + character, character)
    # print inputTagLogic
    return inputTagLogic

class TagParser:
    def __init__(self, tagLogic, freshCall = True):
        #We plan to support !, &^|, (), and tags.
        tokens = filter(lambda x: x != "" and x != " ", re.split("(`[!&^|()]| )", tagLogic))
        if freshCall:
            tokens = map(reverseEscapeInputTagLogic, tokens)
        #Use a backtick to escape logic
        #At this line, the only elements with backticks are parts of strings.
        self.primedObjectToken = None
        self.primedLogicToken = None
        self.falsePrimed = False
        self.constructTokenLogic(tokens)



    def constructTokenLogic(self, tokens):
        i = 0
        while i < len(tokens):
            #We will case on the type:
            token = tokens[i]
            # print "Parsing %s" % token
            if token == "(":
                leftParenIndex = i
                rightParenIndex = self.findMatchingBrace(tokens, i)
                subObjectToken = " ".join(tokens[leftParenIndex + 1 : rightParenIndex]) #Everything between the parentheses, rejoined into a string
                newObjectToken = TagParser("".join(subObjectToken), False).getLogicToken()
                i = rightParenIndex
                self.newObjectTokenHandler(newObjectToken)
            elif token == ")":
                raise TokenLogicException("Unmatched right bracket in logic string. Aborting.")
            elif token in "&^|":
                if self.primedLogicToken != None:
                    raise TokenLogicException("Attempted to add in logic token %s but already found %s. Aborting." % (token, self.primedLogicToken))
                elif self.primedObjectToken == None:
                    raise TokenLogicException("Attempted to add in logic token %s but no object token found. Aborting." % token)
                elif self.falsePrimed:
                    raise TokenLogicException("Attempted to add in logic token %s but found a ! immediately before. Aborting." % token)
                self.primedLogicToken = token
            elif token == "!":
                if self.falsePrimed:
                    raise TokenLogicException("Duplicate ! not expected. Aborting.")
                elif self.primedObjectToken != None and self.primedLogicToken == None:
                    # raise TokenLogicException("Expected a valid logic token before !; found %s instead. Aborting." % self.primedObjectToken)
                    self.primedLogicToken = "&"
                self.falsePrimed = True
            else:
                newObjectToken = BaseToken(token)
                self.newObjectTokenHandler(newObjectToken)
            i += 1
        if self.falsePrimed:
            raise TokenLogicException("Unresolved false operator.")
        if self.primedLogicToken != None:
            raise TokenLogicException("Unresolved binary logic operator %s." % self.primedLogicToken)
        if self.primedObjectToken == None:
            self.primedObjectToken = EmptyToken()
        self.logicToken = self.primedObjectToken

    def findMatchingBrace(self, tokens, i):
        relativeBraceIndex = None
        depth = 1
        # print ("Looking for brace in %s starting from %d" % (tokens, i))
        for i in range (i + 1, len(tokens)):
            if tokens[i] == "(":
                depth += 1
            elif tokens[i] == ")":
                depth -= 1
                if depth == 0:
                    relativeBraceIndex = i
                    break
        if relativeBraceIndex == None:
            raise TokenLogicException("Could not find matching brace from index %d. Aborting." % i)
        return relativeBraceIndex

    def newObjectTokenHandler(self, newObjectToken):
        if self.falsePrimed:
            newObjectToken = NotToken(newObjectToken)
            self.falsePrimed = False
        if self.primedObjectToken == None:
            self.primedObjectToken = newObjectToken
        else:
            if self.primedLogicToken == None and self.primedObjectToken != None:
                self.primedLogicToken = "&" #Default logic token is and
            #At this point, we should have both a logic and object token.
            if self.primedLogicToken == "|":
                self.primedObjectToken = OrToken(self.primedObjectToken, newObjectToken)
            elif self.primedLogicToken == "&":
                self.primedObjectToken = AndToken(self.primedObjectToken, newObjectToken)
            elif self.primedLogicToken == "^":
                self.primedObjectToken = XorToken(self.primedObjectToken, newObjectToken)
            else:
                raise TokenLogicException("Unrecognized logic token %s. Aborting." % self.primedLogicToken)
            self.primedLogicToken = None
        self.primedLogicToken = None #Resets the token

    def getLogicToken(self):
        return self.logicToken

    def evaluate(self, tags):
        return self.logicToken.evaluate(tags)

    def evaluateDF(self, df):
        return self.logicToken.evaluateDF(df)

    def generateSQLQuery(self):
        return "select * from images where" + self.logicToken.generateSQLQueryFragment()

    def __str__(self):
        return str(self.logicToken)

#Initializer

class EmptyToken:
    def __init__(self):
        pass

    def evaluate(self, tags):
        return True

    def evaluateDF(self, df):
        return df

    def generateSQLQueryFragment(self):
        return "(dataId > 0)" #Always true

    def __str__(self):
        return "<No tags>"

class BaseToken:
    def __init__(self, tokenString):
        self.tokenString = reverseEscapeInputTagLogic(tokenString.lower())
        self.cleanedRepresentation = reverseEscapeInputTagLogic(self.tokenString)
        #cleanedRepresentation only prints escape backticks with lone symbols, like `!.
        #Things like ":)" should be safe from backticking.

    def evaluate(self, tags):
        lowerTags = None
        try:
            if type(tags) == str or type(tags) == unicode:
                lowerTags = tags.lower().split(" ")
            elif type(tags) == list or type(tags) == set:
                lowerTags = map(lambda x: x.lower(), tags)
            return self.tokenString in lowerTags
        except Exception as e:
            print "Failed at %s evaluating %s, getting %s" % (self.tokenString, tags, lowerTags)
            print "Type of tags: %s" % type(tags)
            raise Exception("Found exception %s" % e)

    def evaluateDF(self, df):
        spacedTokenString = " " + self.tokenString.strip() + " "
        return df[df['dataTags'].str.contains(self.tokenString, regex=False)]

    def generateSQLQueryFragment(self):
        return "(instr(dataTags, '%s') > 0)" % self.tokenString

    def __str__(self):
        return self.cleanedRepresentation

#Unary token

class NotToken:
    def __init__(self, token):
        self.token = token

    def evaluate(self, tags):
        return not self.token.evaluate(tags)

    def __str__(self):
        return "!%s" % self.token

    def evaluateDF(self, df):
        normalEvalDF = self.token.evaluateDF(df)
        doubleDF = pd.concat([df, normalEvalDF])
        complementDF = doubleDF.drop_duplicates(keep=False)
        return complementDF

    def generateSQLQueryFragment(self):
        return "(not(%s))" % self.token.generateSQLQueryFragment()


class AndToken:
    def __init__(self, firstToken, secondToken):
        self.firstToken = firstToken
        self.secondToken = secondToken

    def evaluate(self, tags):
        return self.firstToken.evaluate(tags) and self.secondToken.evaluate(tags)

    def evaluateDF(self, df):
        firstFilter = self.firstToken.evaluateDF(df)
        bothFilter = self.secondToken.evaluateDF(firstFilter)
        return bothFilter

    def generateSQLQueryFragment(self):
        return "(%s and %s)" % (self.firstToken.generateSQLQueryFragment(), self.secondToken.generateSQLQueryFragment())


    def __str__(self):
        return "(%s & %s)" % (str(self.firstToken), str(self.secondToken))


class OrToken:
    def __init__(self, firstToken, secondToken):
        self.firstToken = firstToken
        self.secondToken = secondToken

    def evaluate(self, tags):
        return self.firstToken.evaluate(tags) or self.secondToken.evaluate(tags)

    def evaluateDF(self, df):
        firstDF = self.firstToken.evaluateDF(df)
        secondDF = self.secondToken.evaluateDF(df)
        doubleDF = pd.concat([firstDF, secondDF])
        orDF = doubleDF.drop_duplicates(keep="first")
        return orDF

    def generateSQLQueryFragment(self):
        return "(%s or %s)" % (self.firstToken.generateSQLQueryFragment(), self.secondToken.generateSQLQueryFragment())

    def __str__(self):
        return "(%s | %s)" % (str(self.firstToken), str(self.secondToken))


class XorToken:
    def __init__(self, firstToken, secondToken):
        self.firstToken = firstToken
        self.secondToken = secondToken

    def evaluate(self, tags):
        return self.firstToken.evaluate(tags) ^ self.secondToken.evaluate(tags)


    def generateSQLQueryFragment(self): #I don't think xor exists naturally
        firstQuery = self.firstToken.generateSQLQueryFragment()
        secondQuery = self.secondToken.generateSQLQueryFragment()
        return " ((%s and not(%s)) or (not(%s) and %s)) " % (firstQuery, secondQuery, firstQuery, secondQuery)

    def evaluateDF(self, df):
        firstDF = self.firstToken.evaluateDF(df)
        secondDF = self.secondToken.evaluateDF(df)
        doubleDF = pd.concat([firstDF, secondDF])
        orDF = doubleDF.drop_duplicates(keep=False)
        return orDF

    def __str__(self):
        return "(%s ^ %s)" % (str(self.firstToken), str(self.secondToken))