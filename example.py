from EagleLayout import Layout
from EagleSchematic import Schematic
import xml.etree.ElementTree as ET
import sys
import copy

sfilename = sys.argv[1]
outfile = "leds"

if __name__ == "__main__":

	with open(sfilename, 'rw') as sfile:
		schematic = Schematic(sfile)

		ledPart = None

		for part in schematic.drawing.schematic.partsList:
			if part.xml.attrib['name'] == 'LED':
				# print part
				pass

		for part in schematic.drawing.schematic.instanceList:
			if part.xml.attrib['part'] == 'LED':
				ledPart = part
				del schematic.drawing.schematic.instanceList[schematic.drawing.schematic.instanceList.index(part)]

		print len(schematic.drawing.schematic.instanceList)

		for x in xrange(10, 0, -1):
			newPart = copy.deepcopy(ledPart)
			newPart.xml.attrib['part'] = "LED%s" % x
			newPart.xml.attrib
			schematic.xml._children[0]._children[-1]._children[5]._children[0]._children[1]._children.append(newPart)

		print len(schematic.drawing.schematic.instanceList)


		with open("%s.sch" % outfile, 'w') as outSch:

			schematic.getXMLElement().write(outSch) 

