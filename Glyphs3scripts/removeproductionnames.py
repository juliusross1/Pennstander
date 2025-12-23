# MenuTitle: Remove Production Names from Selected Glyphs
# -*- coding: utf-8 -*-
from GlyphsApp import *

Glyphs.showMacroWindow()
Glyphs.clearLog()
font = Glyphs.font
selectedGlyphs = [l.parent for l in font.selectedLayers]


font = Glyphs.font

for glyph in selectedGlyphs:
    glyph.productionName = glyph.name
    print(f"Removed production name from: {glyph.name}")

Glyphs.showNotification(
    "Production Names Removed",
    f"Done. Removed production names from {len(selectedGlyphs)} glyphs."
)