#!/usr/bin/python

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import RPi.GPIO as GPIO, Image, time
from subprocess import call
import lightMenu
import lightImage as lightImage

button1_GPIO = 27
button2_GPIO = 22
button3_GPIO = 17

pngDirName = "./png"

# lightImages assigned to each button
Button1Image = None
Button2Image = None
Button3Image = None



def piPaint(filename):
	# Configurable values
	dev       = "/dev/spidev0.0"
	
	# Open SPI device, load image in RGB format and get dimensions:
	spidev    = file(dev, "wb")
	print "Loading..."
	img       = Image.open(filename).convert("RGB")
	pixels    = img.load()
	width     = img.size[0]
	height    = img.size[1]
	print "%dx%d pixels" % img.size
	# To do: add resize here if image is not desired height
	
	# Calculate gamma correction table.  This includes
	# LPD8806-specific conversion (7-bit color w/high bit set).
	gamma = bytearray(256)
	for i in range(256):
		gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)
	
	# Create list of bytearrays, one for each column of image.
	# R, G, B byte per pixel, plus extra '0' byte at end for latch.
	print "Allocating..."
	column = [0 for x in range(width)]
	for x in range(width):
		column[x] = bytearray(height * 3 + 1)
	
	# Convert 8-bit RGB image into column-wise GRB bytearray list.
	print "Converting..."
	for x in range(width):
		for y in range(height):
			value = pixels[x, y]
			y3 = y * 3
			column[x][y3]     = gamma[value[1]]
			column[x][y3 + 1] = gamma[value[0]]
			column[x][y3 + 2] = gamma[value[2]]
	
	
	# Then it's a trivial matter of writing each column to the SPI port.
	print "Displaying..."
	for x in range(width):
	        spidev.write(column[x])
	        spidev.flush()
		time.sleep(0.001)
	time.sleep(0.5)




# Initialize the LCD plate.  Should auto-detect correct I2C bus.  If not,
# pass '0' for early 256 MB Model B boards or '1' for all later versions
lcd = Adafruit_CharLCDPlate()
lcd.begin( 16, 2)
lcd.blink()

# Clear display and show greeting, pause 1 sec
lcd.clear()
lcd.message("lightPaint menu!")
sleep(1)

#############
# prepare Main Menu
mainMenu1stLine = [
    lightMenu.strElem(["PiPaint !!"])
    ];

mainMenu2ndLine = [
    lightMenu.strElem(["configure","stop","halt"])];

mainMenu = lightMenu.lightMenu(mainMenu1stLine,mainMenu2ndLine)

#############
# prepare config Menu
paramList1stLine = [
    lightMenu.strElem(lightMenu.lightMenu.listFileInDir(pngDirName))
    ];

paramList2ndLine = [
        lightMenu.strElem(lightImage.lightImage.listSupportedModes()),
    lightMenu.intElem(0.001,0.001)
    ];

FILENAME_IDX = (0,0)
MODE_IDX     = (1,0)
DELAY_IDX    = (1,1)

configMenu = lightMenu.lightMenu(paramList1stLine,paramList2ndLine)

#############
# screen State

currentMenu = mainMenu



# Cycle through backlight colors
col = (lcd.ON, lcd.OFF, lcd.ON)
for c in col:
    lcd.backlight(c)
    sleep(.5)

getout = 0

lcd.clear()
lcd.message(currentMenu.__str__())


def onSelect():
    global currentMenu
    global getout
    print "select"
    if(currentMenu is configMenu):
        print "select CONFIG"
        # CONFIG Screen
        # come back to  Main Screen
        currentMenu = mainMenu
        lcd.message(mainMenu.__str__())
    else :
        # MAIN screen
        print "select MAIN"

        mainChoice = mainMenu2ndLine[0].__str__()

        if (mainChoice == "configure"):
            # go to configure menu
            currentMenu = configMenu
            lcd.message(currentMenu.__str__())
        elif(mainChoice == "stop"):
            # quit script without halting
            # turn off bar
            filename = "%s/off.png"%(pngDirName)
            offImg = lightImage.lightImage(filename,32)
            offImg.paint_step()

            lcd.clear()
            lcd.backlight(lcd.OFF)
            getout=1
            print "sortie"
        elif(mainChoice == "halt"):
            call(["halt", "-p"])
            # turn off bar
            filename = "%s/off.png"%(pngDirName)
            offImg = lightImage.lightImage(filename,32)
            offImg.paint_step()
            lcd.clear()
            lcd.backlight(lcd.OFF)
            getout=1
            print "sortie"
        else:
            print "select ERROR"

def onLeft():
    print "left"
    currentMenu.prevParam()

def onRight():
    print "right"
    currentMenu.nextParam()

def onUp():
    print "up"
    currentMenu.incParam()

def onDown():
    print "down"
    currentMenu.decParam()

def buttonProcess(button):
    if(currentMenu is mainMenu):
        # play button 1
        if button is None:
           print "button1 not assigned"
        else:
           button.paint_step()
    else :
        # assign to button 1
        filename = "%s/%s.png"%(pngDirName,
                            configMenu.getParamVal(FILENAME_IDX))
        button = lightImage.lightImage(filename,32,configMenu.getParamVal(MODE_IDX),configMenu.getParamVal(DELAY_IDX))
    return button

def onButton1():
    print "button1"
    global Button1Image
    Button1Image = buttonProcess(Button1Image)

def onButton2():
    print "button2"
    global Button2Image
    Button2Image = buttonProcess(Button2Image)

def onButton3():
    print "button3"
    global Button3Image
    Button3Image = buttonProcess(Button3Image)

# Poll buttons, display message & set backlight accordingly
btn = ((lcd.LEFT   , onLeft   ),
       (lcd.UP     , onUp     ),
       (lcd.DOWN   , onDown   ),
       (lcd.RIGHT  , onRight  ),
       (lcd.SELECT , onSelect ))

GPIOButtons = ((button1_GPIO,onButton1),
               (button2_GPIO,onButton2),
               (button3_GPIO,onButton3))

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIOButtons[0][0],GPIO.IN)
GPIO.setup(GPIOButtons[1][0],GPIO.IN)
GPIO.setup(GPIOButtons[2][0],GPIO.IN)

prev = -1
prevIO = -1
refreshCounter = 30
while getout != 1 :
    #check LCD Plate button
    for b in btn:
        if lcd.buttonPressed(b[0]):
            if b is not prev:
                refreshCounter = 30
                time.sleep(0.3)
                prev = b
            else:
                refreshCounter -= 1
                print refreshCounter
                if (refreshCounter > 25):
                    time.sleep(0.3)
                elif (refreshCounter > 10):
                    time.sleep(0.2)
                else:
                    time.sleep(0.1)
            lcd.clear()
            b[1]()
            lcd.message(currentMenu.__str__())
            break
    #check GPIO button
    for b in GPIOButtons:
        input = GPIO.input(b[0])
        #if the last reading was low and this one high, print
        if ((b[0] is not prevIO) and input):
                print("Button %d pressed"%(b[0]))
                prevIO = b[0]
                b[1]()
        if ((b[0] is prevIO) and not input):
                print("Button %d released"%(b[0]))
                prevIO = -1

    #slight pause to debounce
    time.sleep(0.05)

