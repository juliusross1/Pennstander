# MenuTitle: Creates axis for math italics and math bold

# Creates a copy of the existing font with 6 new masters at corners for 3-axis Weight, MathWeight, MathSlant as per GrandstanderMath project
# Assumes the first two Masters exist (Thin and Black) and have the correct axes
# FIXME?: For consistency the master called "Black" should be renamed to "Weight" (and maybe "Thin" to origin)
from populatemasters import *
from GlyphsApp import *


font_original = Glyphs.font
font = font_original.copy()
font.familyName = font_original.familyName



def copy_masters(original_master,data):
    # Create a new master by copying properties from the original
    new_master = original_master.copy()
    new_master.name = data['name']
    new_master.internalAxesValues[font.axes[0].id] = data['a01']*800+100
    new_master.internalAxesValues[font.axes[1].id] = data['a03']*800+100
    new_master.internalAxesValues[font.axes[2].id] = data['a04']*100
    new_master.customParameters['Master Icon Glyph Name'] = data['icon']
    font.masters.append(new_master)


data = [
    {'name': 'Mathweight', 'a01': 0, 'a02': 0, 'a03': 1, 'a04': 0,'icon': 'Adotbelow', 'source':0},
    {'name': 'Mathslant', 'a01': 0, 'a02': 0, 'a03': 0, 'a04': 1,'icon': 'Acircumflex','source':0},
    {'name': 'WeightMathslant', 'a01': 1, 'a02': 0, 'a03': 0, 'a04': 1,'icon': 'Acircumflex','source':1},
    {'name': 'WeightMathweight', 'a01': 1, 'a02': 0, 'a03': 1, 'a04': 0,'icon': 'Adotbelow','source':1},
    {'name': 'MathweightMathSlant', 'a01': 0, 'a02': 0, 'a03': 1, 'a04': 1,'icon': 'Acircumflexdotbelow','source':0},
    {'name': 'WeightMathweightMathslant', 'a01': 1, 'a02': 0, 'a03': 1, 'a04': 1,'icon': 'Acircumflexdotbelow','source':1},
]
for dataelement in data:
	copy_masters(font.masters[dataelement['source']],dataelement)

# Change icon for the Thin and Black Masters
font.masters[0].customParameters['Master Icon Glyph Name'] = 'A'
font.masters[1].customParameters['Master Icon Glyph Name'] = 'A'


## Populate all the layers for the different kinds of glyphs
populate_all_layers3(font,font.glyphs,font_original)


## Create all the instances
#weights = ['Thin','ExtraLight','Light','Regular','Medium','SemiBold','Bold','ExtraBold','Black']

for i in range (len(font.instances)):
	font.instances[i].active = True

#for i in range(len(weights)):
#	for j in range(i,len(weights)):
#		instance = font.instances[i+1].copy()
#		instance.name = weights[i]+'-bf'+weights[j]
#		font.instances.append(instance)
#		instance.axes = [100.0+ i*100, 0.0,100.0+j*100,100.0]

font.show()
