import xml.etree.ElementTree as ET
import sys
import copy
from xml.dom import minidom
from PIL import Image
from collections import namedtuple


schematicfilename = sys.argv[1]
boardFilename = sys.argv[2]
outFile = "leds.sch"
brdOutfile = "leds.brd"

schematicVerticalSpacing = 15.24
schematicHorizontalSpacing = 25.4

schematicIndividualVerticalSpacing = 2.54

boardVerticalSpacing = 5
boardHorizontalSpacing = 5

boardXoffset = 5
boardYoffsetBottom = 7
boardYoffsetTop = 5

wireWidth = 1

ledAxPos = -5.08
ledCxPos = 2.54

netList = {}

vccSignal = None
gndSignal = None

Point = namedtuple('Point', 'x y')

def buildSchematicGrid(grid):

	createNets(["VCCR", "VCCG", "VCCB", "VCCW"])

	for x in range(0, grid[0]):
		schematicPlaceAndWireColumn(x, grid[1])

	# schematicPlaceAndWireHeader()

def wire(segment, startPos, endPos, layer = 91, width = 0.1524):
	ET.SubElement(segment, 'wire', {'x1': str(startPos.x), 'y1': str(startPos.y), 'x2': str(endPos.x), 'y2': str(endPos.y), 'width': str(width), 'layer': str(layer)})

def pinRef(segment, partName, pin):
	ET.SubElement(segment, 'pinref', {'part': partName, 'gate': 'G$1', 'pin': str(pin)})

def label(segment, pos, rotation, size = "1.4224", layer="95"):
	ET.SubElement(segment, 'label', {'x': str(pos.x), 'y': str(pos.y), 'size': size, 'layer': layer, 'rot': rotation, 'xref': "yes"})

def dropLED(ledName, pos, anode = None, cathode = None, rotation = "R90"):
	ET.SubElement(instances, 'instance', {'part': ledName, 'gate': "G$1", 'x': str(pos.x), 'y': str(pos.y), 'rot': rotation})
	ET.SubElement(parts, 'part', {'device': "0603", 'deviceset': "LED", 'library': "grid", 'name': ledName})

	# if anode is not None:
	# 	anodeSegment = ET.SubElement(netList[anode], 'segment')
	# 	pinRef(anodeSegment, ledName, "A")

	# 	wireStart = Point(pos.x - 5.08, pos.y)
	# 	wireEnd = Point(pos.x - 7.62, pos.y)
	# 	wire(anodeSegment, wireStart, wireEnd)
	# 	label(anodeSegment, wireEnd, "R180")

	# if cathode is not None:
	# 	anodeSegment = ET.SubElement(netList[cathode], 'segment')
	# 	pinRef(anodeSegment, ledName, "C")

	# 	wireStart = Point(pos.x + 5.08, pos.y)
	# 	wireEnd = Point(pos.x + 7.62, pos.y)
	# 	wire(cathodeSegment, wireStart, wireEnd)
	# 	label(cathodeSegment, wireEnd, "R0")

def dropResistor(name, pos, anode = None, cathode = None, rotation = "R0"):
	ET.SubElement(instances, 'instance', {'part': name, 'gate': "G$1", 'x': str(pos.x), 'y': str(pos.y), 'rot': rotation})
	ET.SubElement(parts, 'part', {'device': "0402", 'deviceset': "RESISTOR", 'library': "grid", 'name': name})

def createNets(netNames):
	global netList

	for name in netNames:
		netList[name] = ET.SubElement(nets, 'net', {'name': name, 'class': "0"})

def getSegment(netName):
	return ET.SubElement(getNet(netName), 'segment')

def getNet(netName):
	if netName not in netList:
		netList[netName] = ET.SubElement(nets, 'net', {'name': netName, 'class': "0"})
	return netList[netName]

def schematicPlaceAndWireColumn(columnNumber, numHigh):
	global netList

	columnCenter = columnNumber * schematicHorizontalSpacing

	for y in range(0, numHigh):
		ledPos1 = Point(columnCenter, (numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
		ledPos2 = Point(columnCenter, (numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing) - schematicIndividualVerticalSpacing)
		ledPos3 = Point(columnCenter, (numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing) - (schematicIndividualVerticalSpacing * 2))
		ledPos4 = Point(columnCenter, (numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing) - (schematicIndividualVerticalSpacing * 3))

		resistorPos1 = Point(ledPos1.x + 7.62, ledPos1.y)
		resistorPos2 = Point(ledPos2.x + 7.62, ledPos2.y)
		resistorPos3 = Point(ledPos3.x + 7.62, ledPos3.y)
		resistorPos4 = Point(ledPos4.x + 7.62, ledPos4.y)

		vccrSegment = getSegment("VCCR")
		vccgSegment = getSegment("VCCG")
		vccbSegment = getSegment("VCCB")
		vccwSegment = getSegment("VCCW")

		rResistorSegment = getSegment("LED_RES-%s-R" % columnNumber)
		gResistorSegment = getSegment("LED_RES-%s-G" % columnNumber)
		bResistorSegment = getSegment("LED_RES-%s-B" % columnNumber)
		wResistorSegment = getSegment("LED_RES-%s-W" % columnNumber)

		gndSegment = getSegment("GND")

		dropLED("LED-%s-%s-R" % (columnNumber, y), ledPos1)		
		pinRef(vccrSegment, "LED-%s-%s-R" % (columnNumber, y), "A")
		pinRef(rResistorSegment, "LED-%s-%s-R" % (columnNumber, y), "C")
		pinRef(rResistorSegment, "R-%s-%s-R" % (columnNumber, y), "1")
		dropResistor("R-%s-%s-R" % (columnNumber, y), resistorPos1)
		pinRef(gndSegment, "R-%s-%s-R" % (columnNumber, y), "2")

		dropLED("LED-%s-%s-G" % (columnNumber, y), ledPos2)
		pinRef(vccgSegment, "LED-%s-%s-G" % (columnNumber, y), "A")
		pinRef(gResistorSegment, "LED-%s-%s-G" % (columnNumber, y), "C")
		pinRef(gResistorSegment, "R-%s-%s-G" % (columnNumber, y), "1")
		dropResistor("R-%s-%s-G" % (columnNumber, y), resistorPos2)
		pinRef(gndSegment, "R-%s-%s-G" % (columnNumber, y), "2")

		dropLED("LED-%s-%s-B" % (columnNumber, y), ledPos3)
		pinRef(vccbSegment, "LED-%s-%s-B" % (columnNumber, y), "A")
		pinRef(bResistorSegment, "LED-%s-%s-B" % (columnNumber, y), "C")
		pinRef(bResistorSegment, "R-%s-%s-B" % (columnNumber, y), "1")
		dropResistor("R-%s-%s-B" % (columnNumber, y), resistorPos3)
		pinRef(gndSegment, "R-%s-%s-B" % (columnNumber, y), "2")

		dropLED("LED-%s-%s-W" % (columnNumber, y), ledPos4)
		pinRef(vccwSegment, "LED-%s-%s-W" % (columnNumber, y), "A")
		pinRef(wResistorSegment, "LED-%s-%s-W" % (columnNumber, y), "C")
		pinRef(wResistorSegment, "R-%s-%s-W" % (columnNumber, y), "1")
		dropResistor("R-%s-%s-W" % (columnNumber, y), resistorPos4)
		pinRef(gndSegment, "R-%s-%s-W" % (columnNumber, y), "2")




	
	
	# ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, 0), 'gate': 'G$1', 'pin': 'A'})
	# for y in range(1, numHigh):
	# 	ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, y), 'gate': 'G$1', 'pin': 'A'})
	# 	y1 = str((numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
	# 	y2 = str((numHigh * schematicVerticalSpacing) - ((y-1) * schematicVerticalSpacing))
	# 	ET.SubElement(aSegment, 'wire', {'x1': str(columnCenter + ledAxPos), 'y1': y1, 'x2': str(columnCenter + ledAxPos), 'y2': y2, 'width': "0.1524", 'layer': "91"})
	# 	ET.SubElement(aSegment, 'junction', {'x': str(columnCenter + ledAxPos), 'y': y1})
	# ET.SubElement(aSegment, 'junction', {'x': str(columnCenter + ledAxPos), 'y': str(numHigh * schematicVerticalSpacing)})

	# # # Wire up cathodes
	# cNet = ET.SubElement(nets, 'net', {'name': 'C%sC' % columnNumber, 'class': "0"})
	# cSegment = ET.SubElement(cNet, 'segment')

	# ET.SubElement(cSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, 0), 'gate': 'G$1', 'pin': 'C'})
	# for y in range(1, numHigh):
	# 	ET.SubElement(cSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, y), 'gate': 'G$1', 'pin': 'C'})
	# 	y1 = str((numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
	# 	y2 = str((numHigh * schematicVerticalSpacing) - ((y-1) * schematicVerticalSpacing))
	# 	ET.SubElement(cSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': y1, 'x2': str(columnCenter + ledCxPos), 'y2': y2, 'width': "0.1524", 'layer': "91"})
	# 	ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': y1})
	# ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': str(numHigh * schematicVerticalSpacing)})

	# # Add resistor
	# ET.SubElement(instances, 'instance', {'part': "R%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledCxPos), 'y': "0", 'rot': "R90"})
	# ET.SubElement(parts, 'part', {'device': "0805", 'deviceset': "RESISTOR", 'library': "grid", 'name': "R%s" % columnNumber, 'value': "Ohms"})
	# ET.SubElement(cSegment, 'pinref', {'part': 'R%s' % columnNumber, 'gate': 'G$1', 'pin': '2'})
	# ET.SubElement(cSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': str(schematicVerticalSpacing), 'x2': str(columnCenter + ledCxPos), 'y2': "5.08", 'width': "0.1524", 'layer': "91"})
	# ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': "5.08"})

	# # Add VCC
	# ET.SubElement(instances, 'instance', {'part': "VCC-%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledAxPos), 'y': str((numHigh + 1) * schematicVerticalSpacing) , 'rot': "R0"})
	# ET.SubElement(parts, 'part', {'device': "", 'deviceset': "VCC", 'library': "grid", 'name': "VCC-%s" % columnNumber})
	# ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, numHigh - 1), 'gate': 'G$1', 'pin': 'A'})
	# ET.SubElement(aSegment, 'pinref', {'part': 'VCC-%s' % columnNumber, 'gate': 'G$1', 'pin': 'VCC'})
	# ET.SubElement(aSegment, 'wire', {'x1': str(columnCenter + ledAxPos), 'y1': str((numHigh * schematicVerticalSpacing)), 'x2': str(columnCenter + ledAxPos), 'y2': str(((numHigh + 1) * schematicVerticalSpacing)), 'width': "0.1524", 'layer': "91"})

	# # Add GND
	# if gndNet is None:
	# 	gndNet = ET.SubElement(nets, 'net', {'name': 'GND', 'class': "0"})
	# rSegment = ET.SubElement(gndNet, 'segment')
	# ET.SubElement(instances, 'instance', {'part': "GND-%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledCxPos), 'y': str(-schematicVerticalSpacing) , 'rot': "R0"})
	# ET.SubElement(parts, 'part', {'device': "", 'deviceset': "GND", 'library': "grid", 'name': "GND-%s" % columnNumber})
	# ET.SubElement(rSegment, 'pinref', {'part': 'R%s' % columnNumber, 'gate': 'G$1', 'pin': '1'})
	# ET.SubElement(rSegment, 'pinref', {'part': 'GND-%s' % columnNumber, 'gate': 'G$1', 'pin': 'GND'})
	# ET.SubElement(rSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': str(2 * -ledCxPos), 'x2': str(columnCenter + ledCxPos), 'y2': str(-schematicVerticalSpacing), 'width': "0.1524", 'layer': "91"})

def schematicPlaceAndWireHeader():
	headerXpos = -22
	headerYpos = 0
	# Drop header
	ET.SubElement(parts, 'part', {'device': "", 'deviceset': "HEADER", 'library': "grid", 'name': "J1", 'value': "POWER"})
	ET.SubElement(instances, 'instance', {'part': "J1", 'gate': "G$1", 'x': str(headerXpos), 'y': str(headerYpos)})

	# Drop VCC
	ET.SubElement(instances, 'instance', {'part': "VCC-IN", 'gate': "G$1", 'x': str(headerXpos + 10.16), 'y': str(headerYpos + 5.08), 'rot': "R0"})
	ET.SubElement(parts, 'part', {'device': "", 'deviceset': "VCC", 'library': "grid", 'name': "VCC-IN"})
	# Wire VCC
	headerVccSegment = ET.SubElement(vccNet, 'segment')
	ET.SubElement(headerVccSegment, 'pinref', {'part': "VCC-IN", 'gate': "G$1", 'pin': "VCC"})
	ET.SubElement(headerVccSegment, 'pinref', {'part': "J1", 'gate': "G$1", 'pin': "1"})
	ET.SubElement(headerVccSegment, 'wire', {'x1': str(headerXpos + 7.62), 'y1': str(headerYpos + 2.54), 'x2': str(headerXpos + 10.16), 'y2': str(headerYpos + 5.08), 'width': "0.1524", 'layer': "91"})

	# Drop GND
	ET.SubElement(instances, 'instance', {'part': "GND-IN", 'gate': "G$1", 'x': str(headerXpos + 10.16), 'y': str(headerYpos - 2.54), 'rot': "R0"})
	ET.SubElement(parts, 'part', {'device': "", 'deviceset': "GND", 'library': "grid", 'name': "GND-IN"})
	# Wire GND
	headerGndSegment = ET.SubElement(gndNet, 'segment')
	ET.SubElement(headerGndSegment, 'pinref', {'part': "GND-IN", 'gate': "G$1", 'pin': "GND"})
	ET.SubElement(headerGndSegment, 'pinref', {'part': "J1", 'gate': "G$1", 'pin': "2"})
	ET.SubElement(headerGndSegment, 'wire', {'x1': str(headerXpos + 7.62), 'y1': str(headerYpos), 'x2': str(headerXpos + 10.16), 'y2': str(headerYpos - 2.54), 'width': "0.1524", 'layer': "91"})


def buildBoardGrid(grid):

	for x in range(0, grid[0]):
		boardPlaceAndWireColumn(x, grid[1])

	addPowerRails(grid[0], grid[1])
	updateDimensions(grid[0], grid[1])

def boardPlaceAndWireColumn(columnNumber, numHigh):
	# <element name="LED-10" library="grid" package="CHIPLED_0805" value="LED" x="-16.51" y="3.81"/>
	global vccSignal, gndSignal
	columnCenter = (columnNumber * boardHorizontalSpacing) + boardXoffset

	if vccSignal is None:
		vccSignal = ET.SubElement(signals, 'signal', {'name': "VCC"})
	if gndSignal is None:
		gndSignal = ET.SubElement(signals, 'signal', {'name': "GND"})

	cSignal = ET.SubElement(signals, 'signal', {'name': "C%sC" % columnNumber})

	for y in range(0, numHigh):
		# if columnPixels[y] == 0: continue
		yPos = str((numHigh * boardVerticalSpacing) - (y * boardVerticalSpacing) + boardYoffsetBottom)
		ET.SubElement(elements, 'element', {'name': "LED-%s-%s" % (columnNumber, y), 'library': "grid", 'package': "CHIPLED_0805", 'value': "LED", 'x': str(columnCenter), 'y': yPos, 'rot': "R270"})
		ET.SubElement(vccSignal, 'contactref', {'element': "LED-%s-%s" % (columnNumber, y), 'pad': 'A'})
		ET.SubElement(cSignal, 'contactref', {'element': "LED-%s-%s" % (columnNumber, y), 'pad': 'C'})

	# Wire up VCC
	for y in range(1, numHigh):
		x = columnCenter - 1
		y1 = str((numHigh * boardVerticalSpacing) - (y * boardVerticalSpacing) + boardYoffsetBottom)
		y2 = str((numHigh * boardVerticalSpacing) - ((y-1) * boardVerticalSpacing) + boardYoffsetBottom)
		ET.SubElement(vccSignal, 'wire', {'x1': str(x), 'y1': y1, 'x2': str(x), 'y2': y2, 'width': str(wireWidth), 'layer': "1"})
	# VCC rail stubs
	ET.SubElement(vccSignal, 'wire', {'x1': str(columnCenter - 1), 'y1': str((numHigh * boardVerticalSpacing) + boardYoffsetBottom), 'x2': str(columnCenter - 1), 'y2': str((numHigh * boardVerticalSpacing) + (boardVerticalSpacing / 2) + boardYoffsetBottom), 'width': str(wireWidth), 'layer': "1"})
	
	# Wire up Cathodes
	for y in range(1, numHigh):
		x = columnCenter + 1
		y1 = str((numHigh * boardVerticalSpacing) - (y * boardVerticalSpacing) + boardYoffsetBottom)
		y2 = str((numHigh * boardVerticalSpacing) - ((y-1) * boardVerticalSpacing) + boardYoffsetBottom)
		ET.SubElement(cSignal, 'wire', {'x1': str(x), 'y1': y1, 'x2': str(x), 'y2': y2, 'width': str(wireWidth), 'layer': "1"})
	
	# Add Resistor and wire it up
	resistorYpos = boardYoffsetBottom + (boardVerticalSpacing / 2)
	ET.SubElement(elements, 'element', {'name': "R%s" % columnNumber, 'library': "grid", 'package': "RESISTOR_0805", 'value': "Ohms", 'x': str(columnCenter), 'y': str(resistorYpos), 'rot': "R0"})
	ET.SubElement(cSignal, 'contactref', {'element': "R%s" % columnNumber, 'pad': '2'})
	ET.SubElement(gndSignal, 'contactref', {'element': "R%s" % columnNumber, 'pad': '1'})
	
	y1 = str(boardYoffsetBottom + boardVerticalSpacing)
	y2 = str(resistorYpos)
	# Cathode stubs
	ET.SubElement(cSignal, 'wire', {'x1': str(columnCenter + 1), 'y1': y1, 'x2': str(columnCenter + 1), 'y2': y2, 'width': str(wireWidth), 'layer': "1"})
	# GND rail stubs
	ET.SubElement(gndSignal, 'wire', {'x1': str(columnCenter - 1), 'y1': str(boardYoffsetBottom), 'x2': str(columnCenter - 1), 'y2': y2, 'width': str(wireWidth), 'layer': "1"})

def addPowerRails(numColumns, numHigh):
	global gndSignal, vccSignal
	
	# Add GND wire
	xPos1 = str(boardXoffset - 1)
	xPos2 = str(int(xPos1) + ((numColumns - 1) * boardHorizontalSpacing))
	ET.SubElement(gndSignal, 'wire', {'x1': xPos1, 'y1': str(boardYoffsetBottom), 'x2': xPos2, 'y2': str(boardYoffsetBottom), 'width': str(wireWidth), 'layer': "1"})

	# Add VCC wire
	yPos = (numHigh * boardVerticalSpacing) + (boardVerticalSpacing / 2) + boardYoffsetBottom
	ET.SubElement(vccSignal, 'wire', {'x1': xPos1, 'y1': str(yPos), 'x2': xPos2, 'y2': str(yPos), 'width': str(wireWidth), 'layer': "1"})

	headerXpos = boardXoffset * 1.5
	headerYpos = boardYoffsetBottom / 3
	ET.SubElement(elements, 'element', {'name': "J1", 'library': "grid", 'package': "SCREWTERM-0.2", 'value': "POWER", 'x': str(headerXpos), 'y': str(headerYpos), 'rot': "R0"})
	
	# Wire up VCC
	ledYpos = str(boardVerticalSpacing + boardYoffsetBottom)

	ET.SubElement(vccSignal, 'contactref', {'element': "J1", 'pad': 'P1'})
	ET.SubElement(vccSignal, 'wire', {'x1': str(boardXoffset - 3), 'y1': str(headerYpos + 2.54), 'x2': str(boardXoffset - 3), 'y2': str(ledYpos), 'layer': "1", 'width': str(wireWidth)})
	ET.SubElement(vccSignal, 'wire', {'x1': str(headerXpos - 2.54), 'y1': str(headerYpos), 'x2': str(boardXoffset - 3), 'y2': str(headerYpos + 2.54), 'layer': "1", 'width': str(wireWidth)})
	ET.SubElement(vccSignal, 'wire', {'x1': str(boardXoffset - 3), 'y1': str(ledYpos), 'x2': str(boardXoffset - 1), 'y2': str(ledYpos), 'layer': "1", 'width': str(wireWidth)})

	# Wire up GND
	ET.SubElement(gndSignal, 'contactref', {'element': "J1", 'pad': 'P2'})
	ET.SubElement(gndSignal, 'wire', {'x1': str(headerXpos + 2.54), 'y1': str(headerYpos), 'x2': str(headerXpos + 2.54), 'y2': str(boardYoffsetBottom), 'layer': "1", 'width': str(wireWidth)})

def updateDimensions(numColumns, numHigh):
	
	maxX = str(((numColumns - 1) * boardHorizontalSpacing) + (2 * boardXoffset))
	maxY = str((numHigh * boardVerticalSpacing) + (boardYoffsetBottom + boardYoffsetTop))

	plain = root.find('drawing').find('board').find('plain')
	plain._children = []
	ET.SubElement(plain, 'wire', {'x1': "0", 'y1': "0", 'x2': maxX, 'y2': "0", 'width': "0", 'layer': "20"})
	ET.SubElement(plain, 'wire', {'x1': maxX, 'y1': "0", 'x2': maxX, 'y2': maxY, 'width': "0", 'layer': "20"})
	ET.SubElement(plain, 'wire', {'x1': maxX, 'y1': maxY, 'x2': "0", 'y2': maxY, 'width': "0", 'layer': "20"})
	ET.SubElement(plain, 'wire', {'x1': "0", 'y1': maxY, 'x2': "0", 'y2': "0", 'width': "0", 'layer': "20"})

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

if __name__ == "__main__":

	gridWidth = 5
	gridHeight = 5

	# myImage = Image.open(sys.argv[3])
	# myImage = myImage.convert("1")
	# myImage.save("out.bmp")
	# myImage.thumbnail((gridWidth, gridHeight), Image.BILINEAR)
	# myImage.show()

	with open(schematicfilename, 'r') as schematicfile:
		tree = ET.parse(schematicfile)
		root = tree.getroot()
		
		instances = root.find('drawing').find('schematic').find('sheets').find('sheet').find('instances')
		parts = root.find('drawing').find('schematic').find('parts')
		nets = root.find('drawing').find('schematic').find('sheets').find('sheet').find('nets')

		buildSchematicGrid((gridWidth, gridHeight))
		
		with open(outFile, 'w') as outSch:
			outSch.write(prettify(root))


	# with open(boardFilename, 'r') as boardFile:
	# 	tree = ET.parse(boardFile)
	# 	root = tree.getroot()

	# 	elements = root.find('drawing').find('board').find('elements')
	# 	signals = root.find('drawing').find('board').find('signals')
	# 	for layer in root.find('drawing').find('layers'):
	# 		if layer.attrib['number'] == "25" or layer.attrib['number'] == "27":
	# 			layer.set('visible', 'no')
		
	# 	buildBoardGrid((gridWidth, gridHeight))

	# 	with open(brdOutfile, 'w') as outBrd:
	# 		outBrd.write(prettify(root).encode('utf-8'))




