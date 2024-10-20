#MenuTitle: Populate Masters

import time
from GlyphsApp import *
from Foundation import NSPoint


def copy_master_content2(source_layer,glyph_target,target_layer_id):
	#Copies layer
	newlayer = source_layer.copy()
	glyph_target.layers[target_layer_id]=newlayer


action= dict()

action['letter']= 	[
					['Thin','Thin'],
					['Black','Black'],
					["Mathweight", "Thin"],
					["Mathslant", "Thin"],
					["WeightMathslant", "Black"],
					["WeightMathweight", "Black"],
					["MathweightMathSlant", "Thin"],
					["WeightMathweightMathslant", "Black"],
				]

action['symbol'] = 	[
					['Thin','Thin'],
					['Black','Black'],
					["Mathweight", "Thin"],
					["Mathslant", "Thin"],
					["WeightMathslant", "Black"],
					["WeightMathweight", "Black"],
					["MathweightMathSlant", "Thin"],
					["WeightMathweightMathslant", "Black"],
				]
				
				
action['bold-math'] = [
				["Thin","Thin"],
				["Black","Thin"],
				["Mathweight", "Black"],
				["Mathslant", "Thin"],
			    ["WeightMathslant", "Thin"],
			    ["WeightMathweight", "Black"],
			    ["MathweightMathSlant", "Black"],
			    ["WeightMathweightMathslant", "Black"],
			]

action['italic-math'] = [
				["Thin","Thin"],
				["Black","Black"],
				["Mathweight", "Thin"],
				["Mathslant", "Slant"],
			    ["WeightMathslant", "WeightSlant"],
			    ["WeightMathweight", "Black"],
			    ["MathweightMathSlant", "Slant"],
			    ["WeightMathweightMathslant", "WeightSlant"],
			]


action['bolditalic-math'] = [
				["Thin","Thin"],
				["Black","Thin"],
				["Mathweight", "Black"],
				["Mathslant", "Slant"],
			    ["WeightMathslant", "Slant"],
			    ["WeightMathweight", "Black"],
			    ["MathweightMathSlant", "WeightSlant"],
			    ["WeightMathweightMathslant", "WeightSlant"],

			]
			



def populate_all_layers3(font,glyphlist,font_original):
	masternames = {'Thin','Black',"Mathweight","Mathslant","WeightMathslant","WeightMathweight","MathweightMathSlant","WeightMathweightMathslant"}
## Get a dictionary of the masterids by name for font
## Fixme: Fail nicely here if masters are not available
	masterids = dict()
	for mastername in masternames:
		for master in font.masters:
			if master.name == mastername:
				masterids[mastername] = master.id

	def insert_mathic(populatinglayers):			
			print('checking for math.ic')
			mathic_anchor = populatinglayers['Slant'].anchors['math.ic']
			if mathic_anchor:
				print('found math.ic in Slant')
				new_anchor = GSAnchor()
				new_anchor.name = "math.ic"
				new_anchor.position = NSPoint(populatinglayers['Slant'].width, 0)
				
				#print('Thin anchors before',populatinglayers['Thin'].anchors)
				populatinglayers['Thin'].anchors.append(new_anchor)
				#print('Thin anchors afer',populatinglayers['Thin'].anchors)
				
				new_anchor2 = GSAnchor()
				new_anchor2.name = "math.ic"
				new_anchor2.position = NSPoint(populatinglayers['Slant'].width, 0)
				
				new_anchor2.position = NSPoint(populatinglayers['WeightSlant'].width, 0)
				populatinglayers['Black'].anchors.append(new_anchor2)
				#print('Black anchors',glyph.layers[masterids['Black']].anchors)


	populatinglayers = dict()
	
	
	for glyph in glyphlist:
		if 'bold-math' in glyph.name:
			print('Processing ', glyph.name,' as bold-math letter')
			print('italic-name of this glyph is',glyph.name.replace('bold-math','italic-math'))
			print('italic glyph of this is',font.glyphs[glyph.name.replace('bold-math','italic-math')])
			sourceglyphname = glyph.name.replace('bold-math','')
			print('sourceglyphname',sourceglyphname)
			populatinglayers['Thin']=font_original.glyphs[sourceglyphname].layers[masterids['Thin']].copy()
			populatinglayers['Black']=font_original.glyphs[sourceglyphname].layers[masterids['Black']].copy()
			if glyph.name.replace('bold-math','italic-math') in font.glyphs:
				populatinglayers['Slant']=font_original.glyphs[glyph.name.replace('bold-math','italic-math')].layers[masterids['Thin']].copy()
				populatinglayers['WeightSlant']=font_original.glyphs[glyph.name.replace('bold-math','italic-math')].layers[masterids['Black']].copy()
			else:
				populatinglayers['Slant']=font_original.glyphs[sourceglyphname].layers[masterids['Thin']].copy()
				populatinglayers['WeightSlant']=font_original.glyphs[sourceglyphname].layers[masterids['Black']].copy()
			
			insert_mathic(populatinglayers)

					
			for element in action['bold-math']:
				copy_master_content2(populatinglayers[element[1]],glyph,masterids[element[0]])

		if 'italic-math' in glyph.name and 'bolditalic-math' not in glyph.name:
			print('Processing ', glyph.name,' as italic-math letter')
			sourceglyphname = glyph.name.replace('italic-math','')
			print('source: ',sourceglyphname)
			populatinglayers['Thin']=font_original.glyphs[sourceglyphname].layers[masterids['Thin']].copy()
			populatinglayers['Black']=font_original.glyphs[sourceglyphname].layers[masterids['Black']].copy()
			populatinglayers['Slant']=font_original.glyphs[glyph.name].layers[masterids['Thin']].copy()
			populatinglayers['WeightSlant']=font_original.glyphs[glyph.name].layers[masterids['Black']].copy()
			insert_mathic(populatinglayers)
				
			for element in action['italic-math']:
				copy_master_content2(populatinglayers[element[1]],glyph,masterids[element[0]])
		
		if 'bolditalic-math' in glyph.name:
			print('Processing ', glyph.name,' as bolditalic-math letter')
			sourceglyphname = glyph.name.replace('bolditalic-math','')
			populatinglayers['Thin']=font_original.glyphs[sourceglyphname].layers[masterids['Thin']].copy()
			populatinglayers['Black']=font_original.glyphs[sourceglyphname].layers[masterids['Black']].copy()
			populatinglayers['Slant']=font_original.glyphs[glyph.name.replace('bolditalic-math','italic-math')].layers[masterids['Thin']].copy()
			populatinglayers['WeightSlant']=font_original.glyphs[glyph.name.replace('bolditalic-math','italic-math')].layers[masterids['Black']].copy()
			insert_mathic(populatinglayers)
				
			for element in action['bolditalic-math']:
				copy_master_content2(populatinglayers[element[1]],glyph,masterids[element[0]])
					
		if ('bold-math' not in glyph.name) and ('italic-math' not in glyph.name) and ('bolditalic-math' not in glyph.name):	
			if glyph.name+'italic-math' in font.glyphs:
				# This will not work for things like A.ss02 so need to think about this
				print('Processing ', glyph.name,' as upright letter')
				populatinglayers['Thin']=glyph.layers[masterids['Thin']].copy()
				populatinglayers['Black']=glyph.layers[masterids['Black']].copy()
				populatinglayers['Slant']=font_original.glyphs[glyph.name+'italic-math'].layers[masterids['Thin']].copy()
				populatinglayers['WeightSlant']=font_original.glyphs[glyph.name+'italic-math'].layers[masterids['Black']].copy()
			
			
				# If an anchor called math.ic exists in the italic Thin layer then create one in the Thin and Black layer
				insert_mathic(populatinglayers)

				for element in action['letter']:
					copy_master_content2(populatinglayers[element[1]],glyph,masterids[element[0]])

			else: #Else we are a Symbol not a letter and we do not have an italics version
				print('Processing ', glyph.name,' as symbol')
				populatinglayers['Thin']=glyph.layers[masterids['Thin']].copy()
				populatinglayers['Black']=glyph.layers[masterids['Black']].copy()
				populatinglayers['Slant']=glyph.layers[masterids['Thin']].copy()
				populatinglayers['WeightSlant']=glyph.layers[masterids['Black']].copy()

				for element in action['symbol']:
					copy_master_content2(populatinglayers[element[1]],glyph,masterids[element[0]])


#populatelayers(font.selection)

