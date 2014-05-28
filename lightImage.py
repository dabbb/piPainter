import Image, time

class spidev_stub:
    @staticmethod
    def write(col):
        strToDisplay =[]
        for x in col:
            strToDisplay.append(":%s"%x)

        print ''.join(strToDisplay)

    @staticmethod
    def flush():
        print "flush"


class lightImage:
    """Image pour lightPaint"""
    filename = "toto.png"
    gamma = bytearray(256)
    width = 0
    height = 0
    lightBarLength = 0

    @staticmethod
    def listSupportedModes():
        return ["1passeOn","1passeOff","flipflap","rouleau"]

    def allocate_1step_on(self):

        print "Allocating..."
        self.currentStep = 0
        self.nbStep = 1
        self.step = []
        column = [0 for x in range(self.width)]
        self.step.append(column)
        for x in range(self.width):
            self.step[0][x] = bytearray(self.height * 3 + 1)

        print "Converting..."

        for x in range(self.width):
            for y in range(self.height):
                value = self.pixels[x, self.height - 1 - y]
                y3 = y * 3
                self.step[0][x][y3] = self.gamma[value[1]]
                self.step[0][x][y3 + 1] = self.gamma[value[0]]
                self.step[0][x][y3 + 2] = self.gamma[value[2]]

    def allocate_1step_off(self):

        print "Allocating..."
        self.currentStep = 0
        self.nbStep = 1
        self.step = []
        column = [0 for x in range(self.width + 1 )]
        self.step.append(column)
        for x in range(self.width + 1):
            self.step[0][x] = bytearray(self.height * 3 + 1)

        print "Converting..."

        for x in range(self.width):
            for y in range(self.height):
                value = self.pixels[x, self.height - 1 - y]
                y3 = y * 3
                self.step[0][x][y3] = self.gamma[value[1]]
                self.step[0][x][y3 + 1] = self.gamma[value[0]]
                self.step[0][x][y3 + 2] = self.gamma[value[2]]

        # off FOR THE LAST LINE
        for y in range(self.height):
            y3 = y * 3
            self.step[0][self.width][y3] = 128
            self.step[0][self.width][y3 + 1] = 128
            self.step[0][self.width][y3 + 2] = 128
        # to print the off column
        self.width = self.width + 1


    def allocate_rouleau(self):
        # step of 32 pix (self.lightBarLength) each "nbstep" line

        print "Allocating..."
        self.currentStep = 0
        self.nbStep = self.height // self.lightBarLength
        self.step = []
        # fill each step
        for s in range(0,self.nbStep):

            column = [0 for x in range(self.width + 1)]
            self.step.append(column)
            for x in range(self.width + 1):
                self.step[s][x] = bytearray(self.lightBarLength * 3 + 1)

            print "Converting..."

            for x in range(self.width):
                for y in range(self.lightBarLength):
                    #print "%d,%d -> %d"%(x,y,self.height - (y + s*self.lightBarLength))
                    if(s%2 is 0):
#                        print "normal print"
                        value = self.pixels[x, self.height - 1 - (y + s*self.lightBarLength)]
                    else:
#                        print "reverse print"
                        value = self.pixels[self.width - x - 1, self.height - 1 - (y + s*self.lightBarLength)]
                    y3 = (y)* 3
                    #print "%d,%d,%d"%(x,y,y3)
                    self.step[s][x][y3] = self.gamma[value[1]]
                    self.step[s][x][y3 + 1] = self.gamma[value[0]]
                    self.step[s][x][y3 + 2] = self.gamma[value[2]]

            # off FOR THE LAST LINE
            for y in range(self.lightBarLength):
                y3 = y * 3
                self.step[0][self.width][y3] = 128
                self.step[s][self.width][y3 + 1] = 128
                self.step[s][self.width][y3 + 2] = 128

        # to print the off column
        self.width = self.width + 1

    def allocate_flipflap(self):
        # step of 32 pix (self.lightBarLength) each "nbstep" line

        print "Allocating..."
        self.currentStep = 0
        self.nbStep = self.height // self.lightBarLength
        self.step = []
        # fill each step
        for s in range(0,self.nbStep):

            column = [0 for x in range(self.width + 1)]
            self.step.append(column)
            for x in range(self.width + 1):
                self.step[s][x] = bytearray(self.lightBarLength * 3 + 1)

            print "Converting..."

            for x in range(self.width):
                for y in range(self.lightBarLength):
                    #print "%d,%d "%(x,y)
                    if(s%2 is 0):
#                        print "normal print"
                        value = self.pixels[x, self.height - 1 - (self.nbStep*y)]
                    else:
#                        print "reverse print"
                        value = self.pixels[self.width - x - 1, self.height - 1 - (self.nbStep*y + s)]
                    y3 = (y)* 3
                    #print "%d,%d,%d"%(x,y,y3)
                    self.step[s][x][y3] = self.gamma[value[1]]
                    self.step[s][x][y3 + 1] = self.gamma[value[0]]
                    self.step[s][x][y3 + 2] = self.gamma[value[2]]

            # off FOR THE LAST LINE
            for y in range(self.lightBarLength):
                y3 = y * 3
                self.step[0][self.width][y3] = 128
                self.step[s][self.width][y3 + 1] = 128
                self.step[s][self.width][y3 + 2] = 128

        # to print the off column
        self.width = self.width + 1


    alocateMethodDico = {"1passeOn" :allocate_1step_on,
                         "1passeOff":allocate_1step_off,
                         "rouleau"  :allocate_rouleau,
                         "flipflap" :allocate_flipflap}

    def __init__(self, filename, lightBarLength, paintMethod = "1passeOn", delay = 0.001):
        self.filename = filename
        self.delay = delay
        # Calculate gamma correction table.  This includes
        # LPD8806-specific conversion (7-bit color w/high bit set).
        for i in range(256):
            self.gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)
        self.lightBarLength = lightBarLength
        self.paintMethod = paintMethod
        self.load()

        self.alocateMethodDico[paintMethod](self)

        

    def load(self):
        print "Loading..."
        img       = Image.open(self.filename).convert("RGB")
        self.pixels    = img.load()
        self.width     = img.size[0]
        self.height    = img.size[1]

        print "%dx%d pixels" % img.size



    def paint_step(self):
        print "painting"
        spidev    = file("/dev/spidev0.0", "wb")

        # print each collumn
        for x in range(self.width):
            spidev.write(self.step[self.currentStep][x])
            spidev.flush()
            time.sleep(self.delay)

        # switch to next pattern
        self.currentStep += 1
        self.currentStep %= self.nbStep

if __name__ == "__main__":
    i1= lightImage("png/joconde64.png",32,"flipflap")
#    i1= lightImage("png/joconde.png",32,"1passeOn")
    i1.paint_step()
    i1.paint_step()
