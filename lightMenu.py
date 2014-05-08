import os

class lightMenuElem:
    def __init__(self):
        self.selected = 0


class intElem(lightMenuElem):

    def __init__(self, val, incr = 0.001):
        lightMenuElem.__init__(self)
        self.val = float(val)
        self.incr = incr

    def inc(self):
        self.val +=self.incr

    def dec(self):
        self.val -=self.incr

    def getVal(self):
        return float(self.val)


    def __str__(self):
        return str(float(self.val))

class strElem(lightMenuElem):

    def __init__(self, strList, index=0):
        lightMenuElem.__init__(self)
        self.strIndex= index
        self.strList = strList
        self.strListSize = len(self.strList)

    def inc(self):
        self.strIndex +=1
        self.strIndex %=self.strListSize


    def dec(self):
        self.strIndex -=1
        if (self.strIndex<0): self.strIndex = self.strListSize - 1

    def __str__(self):
        return "%s"%(self.strList[self.strIndex])

    def getVal(self):
        return self.__str__()

class lightMenu:
    """Config handler  for lightPaint"""

    selectCharLeft  = "|>"
    selectCharRight = "|<"

    def changeSelect(self,line,elem,selectedFlag):
        #print "changeSelect(%d,%d)on(%d,%d)"%(line,elem,self.nbElemPerLine[0],self.nbElemPerLine[1])
        self.allParam[line][elem].selected = selectedFlag

    @staticmethod
    def listFileInDir(filedirname):
        dirList=os.listdir(filedirname)
        resultList=[]
        for fname in dirList:
            if(fname[-4:]==".png"):
                resultList.append(fname[:-4])
        return resultList

    def __init__(self, paramList1stLine, paramList2ndLine):
        print "init"

        self.paramList1stLine = paramList1stLine

        self.paramList2ndLine = paramList2ndLine

        self.allParam = [self.paramList1stLine,self.paramList2ndLine]
        self.nbLine = 2
        self.nbElemPerLine=[0,0]
        self.currentParam =[0,0]


        self.nbElemPerLine[0] = len(self.allParam[0])
        self.nbElemPerLine[1] = len(self.allParam[1])
        self.changeSelect(self.currentParam[0],self.currentParam[1],1)

    def nextParam(self):
        #print "nextParamCall"
        # remove selected from the previous one
        self.changeSelect(self.currentParam[0],self.currentParam[1],0)

        self.currentParam[1] += 1

        if(self.currentParam[1] >= self.nbElemPerLine[self.currentParam[0]]):
            # change line
            self.currentParam[1] = 0
            self.currentParam[0] += 1
            self.currentParam[0] %= self.nbLine

        # add selected to the new one
        self.changeSelect(self.currentParam[0],self.currentParam[1],1)

    def prevParam(self):
        #print "prevParam Call "
        # remove selected from the previous one
        self.changeSelect(self.currentParam[0],self.currentParam[1],0)

        self.currentParam[1] -= 1

        if(self.currentParam[1] < 0):
            # change line
            self.currentParam[0] -= 1
            if(self.currentParam[0] < 0): self.currentParam[0] = self.nbLine - 1
            self.currentParam[1] = self.nbElemPerLine[self.currentParam[0]] - 1

        # add selected to the new one
        self.changeSelect(self.currentParam[0],self.currentParam[1],1)

    def incParam(self):
        #print "incParam Call "
        line = self.currentParam[0]
        elem = self.currentParam[1]
        self.allParam[line][elem].inc()

    def decParam(self):
        #print "incParam Call "
        line = self.currentParam[0]
        elem = self.currentParam[1]
        self.allParam[line][elem].dec()

    def __str__(self):
        returnStr = []

        for paramLine in self.allParam:

            for param in paramLine:
                returnStr.append(self.selectCharLeft[param.selected])
                returnStr.append(param.__str__())
                returnStr.append(self.selectCharRight[param.selected])
            returnStr.append("\n")

        return ''.join(returnStr);

    def getParamVal(self,paramIdx):
        return self.allParam[paramIdx[0]][paramIdx[1]].getVal()

if __name__ == "__main__":

    paramList1stLine = [
        strElem(lightMenu.listFileInDir("./png"))
        ];

    paramList2ndLine = [
        strElem(["mode1","mode2","mode3"]),
        intElem(0.001,0.001)
        ];

    c1= lightMenu(paramList1stLine,paramList2ndLine)
    print c1
    c1.incParam()
    print c1
    c1.incParam()
    print c1
    c1.nextParam()
    print c1
