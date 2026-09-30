# MenuTitle: Create ssty
import vanilla
from GlyphsApp import *
from mathboldsanditalics import *
from mekkablue import mekkaObject
from Foundation import NSPoint


font = Glyphs.font
selectedGlyphs = [l.parent for l in font.selectedLayers]

def insertssty(glyph,sstytype):
    sstyname = glyph.name + sstytype

    # Duplicate a glyph under a different name

    if sstyname not in font.glyphs:
        newsstyglyph = glyph.copy()
        newsstyglyph.name= sstyname
        font.glyphs.append(newsstyglyph)
        newsstyglyph.productionName = sstyname
        newsstyglyph.unicode=None
        newglyphlist.append(newsstyglyph) 
        print(f"added {sstyname}")
    else:
        print(f"skipping {sstyname} as it already exists")


font.disableUpdateInterface()
newglyphlist = []
for glyph in selectedGlyphs:
    if "ssty" in glyph.name:
        print(f"ignoring {glyph.name}")   
    else:
        insertssty(glyph,".ssty1")
        insertssty(glyph,".ssty2")

font.enableUpdateInterface()

for glyph in newglyphlist:  
    populateBoldItalicLayers(glyph)
#    if ".ssty1" in glyph.name:
#        updatevariants(glyph,".ssty1")
#    elif ".ssty2" in glyph.name:
#        updatevariants(glyph,".ssty2")
    print(f"updated {glyph.name}")

count = len(newglyphlist)
Glyphs.showNotification(
    "Adding SSsty Glyphs Finished",
    f"Processed {count} glyphs successfully."
)
