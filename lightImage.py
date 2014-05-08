#import RPi.GPIO as GPIO\
import Image, time

class spidev:
    @staticmethod
    def write(col):
        print col
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
        return ["1passeOn","1passeOff","allerRetour"]

    def __init__(self, filename, lightBarLength, paintMethod = "1Passe"):
        self.filename = filename
        # Calculate gamma correction table.  This includes
        # LPD8806-specific conversion (7-bit color w/high bit set).
        for i in range(256):
            self.gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)
        self.lightBarLength = lightBarLength
        self.paintMethod = paintMethod
        self.load()

    def convert(self):
        # Convert 8-bit RGB image into column-wise GRB byteArray list.
        print "Converting..."

        for x in range(self.width):
            for y in range(self.height):
                value = self.pixels[x, y]
                y3 = y * 3
                self.column[x][y3] = self.gamma[value[1]]
                self.column[x][y3 + 1] = self.gamma[value[0]]
                self.column[x][y3 + 2] = self.gamma[value[2]]


    def unePasse(self):
        print "une Passe\n"
        for x in range(self.width):
            spidev.write(self.column[x])
            spidev.flush()
            time.sleep(0.001)

    def allerRetour():
        print "allerRetour\n"
    
    paintingMethod = unePasse

    def load(self):
        print "Loading..."
        img       = Image.open(self.filename).convert("RGB")
        self.pixels    = img.load()
        self.width     = img.size[0]
        self.height    = img.size[1]

        print "%dx%d pixels" % img.size
        print "Allocating..."

        self.column = [0 for x in range(self.width)]
        for x in range(self.width):
            self.column[x] = bytearray(self.height * 3 + 1)
        self.convert()

    def paint_step(self):
        print "painting"
        self.paintingMethod()

if __name__ == "__main__":
    i1= lightImage("hello.png",32)
    i1.load("1Passe")
    i1.paint_step()
