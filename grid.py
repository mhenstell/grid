import xml.etree.ElementTree as ET
import sys
import copy
from xml.dom import minidom
from PIL import Image


schematicfilename = sys.argv[1]
boardFilename = sys.argv[2]
outFile = "leds.sch"
brdOutfile = "leds.brd"

schematicVerticalSpacing = 12.7
schematicHorizontalSpacing = 20

boardVerticalSpacing = 5
boardHorizontalSpacing = 5

boardXoffset = 5
boardYoffsetBottom = 7
boardYoffsetTop = 5

wireWidth = 1

ledAxPos = -5.08
ledCxPos = 2.54

vccNet = None
gndNet = None

vccSignal = None
gndSignal = None

def buildSchematicGrid(grid):
	for x in range(0, grid[0]):
		schematicPlaceAndWireColumn(x, grid[1])

	schematicPlaceAndWireHeader()

def schematicPlaceAndWireColumn(columnNumber, numHigh):
	global vccNet, gndNet

	columnCenter = columnNumber * schematicHorizontalSpacing

	for y in range(0, numHigh):
		yPos = str((numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
		ET.SubElement(instances, 'instance', {'part': "LED-%s-%s" % (columnNumber, y), 'gate': "G$1", 'x': str(columnCenter), 'y': yPos, 'rot': "R90"})
		ET.SubElement(parts, 'part', {'device': "", 'deviceset': "LED", 'library': "grid", 'name': "LED-%s-%s" % (columnNumber, y)})

	# Wire up anodes
	if vccNet is None:
		vccNet = ET.SubElement(nets, 'net', {'name': 'VCC', 'class': "0"})
	aSegment = ET.SubElement(vccNet, 'segment')
	
	ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, 0), 'gate': 'G$1', 'pin': 'A'})
	for y in range(1, numHigh):
		ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, y), 'gate': 'G$1', 'pin': 'A'})
		y1 = str((numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
		y2 = str((numHigh * schematicVerticalSpacing) - ((y-1) * schematicVerticalSpacing))
		ET.SubElement(aSegment, 'wire', {'x1': str(columnCenter + ledAxPos), 'y1': y1, 'x2': str(columnCenter + ledAxPos), 'y2': y2, 'width': "0.1524", 'layer': "91"})
		ET.SubElement(aSegment, 'junction', {'x': str(columnCenter + ledAxPos), 'y': y1})
	ET.SubElement(aSegment, 'junction', {'x': str(columnCenter + ledAxPos), 'y': str(numHigh * schematicVerticalSpacing)})

	# # Wire up cathodes
	cNet = ET.SubElement(nets, 'net', {'name': 'C%sC' % columnNumber, 'class': "0"})
	cSegment = ET.SubElement(cNet, 'segment')

	ET.SubElement(cSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, 0), 'gate': 'G$1', 'pin': 'C'})
	for y in range(1, numHigh):
		ET.SubElement(cSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, y), 'gate': 'G$1', 'pin': 'C'})
		y1 = str((numHigh * schematicVerticalSpacing) - (y * schematicVerticalSpacing))
		y2 = str((numHigh * schematicVerticalSpacing) - ((y-1) * schematicVerticalSpacing))
		ET.SubElement(cSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': y1, 'x2': str(columnCenter + ledCxPos), 'y2': y2, 'width': "0.1524", 'layer': "91"})
		ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': y1})
	ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': str(numHigh * schematicVerticalSpacing)})

	# Add resistor
	ET.SubElement(instances, 'instance', {'part': "R%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledCxPos), 'y': "0", 'rot': "R90"})
	ET.SubElement(parts, 'part', {'device': "0805", 'deviceset': "RESISTOR", 'library': "grid", 'name': "R%s" % columnNumber, 'value': "Ohms"})
	ET.SubElement(cSegment, 'pinref', {'part': 'R%s' % columnNumber, 'gate': 'G$1', 'pin': '2'})
	ET.SubElement(cSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': str(schematicVerticalSpacing), 'x2': str(columnCenter + ledCxPos), 'y2': "5.08", 'width': "0.1524", 'layer': "91"})
	ET.SubElement(cSegment, 'junction', {'x': str(columnCenter + ledCxPos), 'y': "5.08"})

	# Add VCC
	ET.SubElement(instances, 'instance', {'part': "VCC-%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledAxPos), 'y': str((numHigh + 1) * schematicVerticalSpacing) , 'rot': "R0"})
	ET.SubElement(parts, 'part', {'device': "", 'deviceset': "VCC", 'library': "grid", 'name': "VCC-%s" % columnNumber})
	ET.SubElement(aSegment, 'pinref', {'part': 'LED-%s-%s' % (columnNumber, numHigh - 1), 'gate': 'G$1', 'pin': 'A'})
	ET.SubElement(aSegment, 'pinref', {'part': 'VCC-%s' % columnNumber, 'gate': 'G$1', 'pin': 'VCC'})
	ET.SubElement(aSegment, 'wire', {'x1': str(columnCenter + ledAxPos), 'y1': str((numHigh * schematicVerticalSpacing)), 'x2': str(columnCenter + ledAxPos), 'y2': str(((numHigh + 1) * schematicVerticalSpacing)), 'width': "0.1524", 'layer': "91"})

	# Add GND
	if gndNet is None:
		gndNet = ET.SubElement(nets, 'net', {'name': 'GND', 'class': "0"})
	rSegment = ET.SubElement(gndNet, 'segment')
	ET.SubElement(instances, 'instance', {'part': "GND-%s" % columnNumber, 'gate': "G$1", 'x': str(columnCenter + ledCxPos), 'y': str(-schematicVerticalSpacing) , 'rot': "R0"})
	ET.SubElement(parts, 'part', {'device': "", 'deviceset': "GND", 'library': "grid", 'name': "GND-%s" % columnNumber})
	ET.SubElement(rSegment, 'pinref', {'part': 'R%s' % columnNumber, 'gate': 'G$1', 'pin': '1'})
	ET.SubElement(rSegment, 'pinref', {'part': 'GND-%s' % columnNumber, 'gate': 'G$1', 'pin': 'GND'})
	ET.SubElement(rSegment, 'wire', {'x1': str(columnCenter + ledCxPos), 'y1': str(2 * -ledCxPos), 'x2': str(columnCenter + ledCxPos), 'y2': str(-schematicVerticalSpacing), 'width': "0.1524", 'layer': "91"})

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

	gridWidth = 25
	gridHeight = 25

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


	with open(boardFilename, 'r') as boardFile:
		tree = ET.parse(boardFile)
		root = tree.getroot()

		elements = root.find('drawing').find('board').find('elements')
		signals = root.find('drawing').find('board').find('signals')
		for layer in root.find('drawing').find('layers'):
			if layer.attrib['number'] == "25" or layer.attrib['number'] == "27":
				layer.set('visible', 'no')
		
		buildBoardGrid((gridWidth, gridHeight))

		with open(brdOutfile, 'w') as outBrd:
			outBrd.write(prettify(root).encode('utf-8'))




