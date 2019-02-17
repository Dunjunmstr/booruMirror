def getElementsFromReversedList(targetList, start, end):
	resultLength = len(targetList)
	firstBound = resultLength - start - 1
	secondBound = max(0, resultLength - end - 1)
	return [targetList[i] for i in range (firstBound, secondBound, -1)]