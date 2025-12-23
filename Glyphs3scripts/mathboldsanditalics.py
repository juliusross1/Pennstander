# MenuTitle: Update Italics, Bold, BoldItalics

import vanilla
from GlyphsApp import *
from mekkablue import mekkaObject
from Foundation import NSPoint



def copyAnchorsFromLayerToLayer(sourceLayer, targetLayer, keepOriginal=False, verbose=False):
    """Copies all anchors from sourceLayer to targetLayer."""
    numberOfAnchorsInSource = len(sourceLayer.anchors)
    numberOfAnchorsInTarget = len(targetLayer.anchors)

    if numberOfAnchorsInTarget != 0 and not keepOriginal:
        if verbose:
            print("- Deleting %i anchors in target layer" % numberOfAnchorsInTarget)
        targetLayer.setAnchors_(None)

    if numberOfAnchorsInSource > 0:
        if verbose:
            print("- Copying anchors from source layer:")
        for thisAnchor in sourceLayer.anchors:
            newAnchor = thisAnchor.copy()
            targetLayer.anchors.append(newAnchor)
            if verbose:
                print("   %s (%i, %i)" % (thisAnchor.name, thisAnchor.position.x, thisAnchor.position.y))

def copyMetricsFromLayerToLayer(sourceLayer, targetLayer, verbose=False):
    """Copies width of sourceLayer to targetLayer."""
    sourceWidth = sourceLayer.width
    if targetLayer.width != sourceWidth:
        targetLayer.width = sourceWidth
        if verbose:
            print("- Copying width (%.1f)" % sourceWidth)
    else:
        if verbose:
            print("- Width not changed (already was %.1f)" % sourceWidth)

def copyPathsFromLayerToLayer(sourceLayer, targetLayer, keepOriginal=False, verbose=False):
    """Copies all paths from sourceLayer to targetLayer"""
    numberOfPathsInSource = len(sourceLayer.paths)
    numberOfPathsInTarget = len(targetLayer.paths)

    if numberOfPathsInTarget != 0 and not keepOriginal:
        if verbose:
            print("- Deleting %i paths in target layer" % numberOfPathsInTarget)
        try:
            # GLYPHS 3
            for i in reversed(range(len(targetLayer.shapes))):
                if isinstance(targetLayer.shapes[i], GSPath):
                    del targetLayer.shapes[i]
        except:
            # GLYPHS 2
            targetLayer.paths = None

    if numberOfPathsInSource > 0:
        if verbose:
            print("- Copying paths")
        for thisPath in sourceLayer.paths:
            newPath = thisPath.copy()
            try:
                # GLYPHS 3
                targetLayer.shapes.append(newPath)
            except:
                # GLYPHS 2
                targetLayer.paths.append(newPath)

def copyComponentsFromLayerToLayer(sourceLayer, targetLayer, keepOriginal=False, verbose=False):
    """Copies all components from sourceLayer to targetLayer."""
    numberOfComponentsInSource = len(sourceLayer.components)
    numberOfComponentsInTarget = len(targetLayer.components)

    if numberOfComponentsInTarget != 0 and not keepOriginal:
        if verbose:
            print("- Deleting %i components in target layer" % numberOfComponentsInTarget)
        try:
            # GLYPHS 3
            for i in reversed(range(len(targetLayer.shapes))):
                if isinstance(targetLayer.shapes[i], GSComponent):
                    del targetLayer.shapes[i]
        except:
            # GLYPHS 2
            targetLayer.components = []

    if numberOfComponentsInSource > 0:
        if verbose:
            print("- Copying components:")
        for thisComp in sourceLayer.components:
            newComp = thisComp.copy()
            if verbose:
                print("   Component: %s" % (thisComp.componentName))
            targetLayer.components.append(newComp)
                
def addBraceLayersForGlyph(glyph, targetBraceLayers):
    """
    Adds brace layers to a glyph if coordinates are not already present.
    targetBraceLayers: list of tuples (layerName, coordinateDict)
    This should only be needed once, then can be discarded
    """
    for targetName, targetCoords in targetBraceLayers:

        # Check for existing layer with same coordinates
        exists = False
        for layer in glyph.layers:
            if layer.attributes.get("coordinates") == targetCoords:
                exists = True
                break

        if exists:
            print(f"{glyph.name}: Layer with coordinates {targetCoords} already exists")
        else:
            newLayer = GSLayer()
            newLayer.name = targetName
            newLayer.attributes["coordinates"] = targetCoords
            glyph.layers.append(newLayer)
            print(f"Added {targetName} to {glyph.name}")





def getlayer_frominfo(layerinfo):
    # Gets the layer from a layerinfo
    # Layerinfo is a list that has the following data:
    # glyph: the glyph of the layer
    # type: can be either "master" or "bracket"
    # for type master the "name" is the name of the master layer
    # for type bracket the coordinates are the coordinates of the bracket layer
    glyph = layerinfo["glyph"]
    returnlayer = None

    if layerinfo["type"] == "master":
        masterName = layerinfo["masterName"]
        chosenmaster = None
        for master in font.masters:
            if master.name == masterName:
                chosenmaster = master
        if chosenmaster==None:
            raise ValueError(f"Master  with name {masterName} not found")

        returnlayer = glyph.layers[chosenmaster.id]
        if returnlayer is None:
            raise ValueError(f"Master layer with name {masterName} not found in glyph {glyph.name}")

    elif layerinfo["type"] == "bracket":
        coords = layerinfo.get("coordinates")
        for layer in glyph.layers:
            if layer.attributes.get("coordinates") == coords:
                returnlayer = layer
                break
        if returnlayer is None:
            raise ValueError(f"Bracket layer with coordinates {coords} not found in glyph '{glyph.name}'")

    else:
        raise ValueError(f"Unsupported layer type: {layerinfo['type']}")

    return returnlayer

def getLayerByCoordinates(glyph,coords):
    print("getting layer by coordinates",coords)
    for layer in glyph.layers:
        print(layer,layer.attributes["coordinates"])
        if layer.attributes.get("coordinates") == coords:
            returnlayer = layer
            break
    return returnlayer

def copyLayers(copyMap,mathic=None):
    # Takes as input a copyMap and copies the layers for each pair in the copyMap
    # Copymap is an array of pairs [p,q] where p,q are both layerInfo
    for pair in copyMap:
        sourceLayerInfo = pair[0]
        targetLayerInfo = pair[1]
        # Find the target brace layer by coordinates
        sourceLayer = getlayer_frominfo(sourceLayerInfo)
        targetLayer = getlayer_frominfo(targetLayerInfo)

        copyPathsFromLayerToLayer(sourceLayer,targetLayer)
        copyAnchorsFromLayerToLayer(sourceLayer,targetLayer)
        copyComponentsFromLayerToLayer(sourceLayer,targetLayer)
        copyMetricsFromLayerToLayer(sourceLayer,targetLayer)
        targetLayer.syncMetrics()

        if mathic=="create":
            anchor_name = "math.ic"
            anchor =  targetLayer.anchors["math.ic"]   # returns GSAnchor or None
            if anchor is not None:                
                newAnchor = GSAnchor(anchor_name)
                newAnchor.position = NSPoint(targetLayer.width, 0)
                targetLayer.addAnchor_(newAnchor)
                print(f"Added {anchor_name} at {newAnchor.position}")
        if mathic=="adjustwidth":
            anchor =  targetLayer.anchors["math.ic"]   # returns GSAnchor or None
            if anchor is not None:
                print('adjusting width using italic correction')
                adjustment=anchor.x- targetLayer.width
                targetLayer.RSB = targetLayer.RSB + adjustment
                anchortr =  targetLayer.anchors["math.tr"] 
                if anchortr is not None:
                    anchortr.x=anchortr.x+adjustment




def populateLayers_initalonly():
    # This creates the necessary brace layers (if they are not already there) and populates the italic-math glyphs
    # This only needs to be done once then this can be discarded
    targetBraceLayersItalic = [
    ("{100,100,100}", {"a01":100, "a02":100, "a03":100}),
    ("{900,100,100}", {"a01":900, "a02":100, "a03":100}),
    ]

    targetBraceLayersBold = [
    ("{100,900,0}", {"a01":100, "a02":900, "a03":0}),
    ("{900,900,0}", {"a01":900, "a02":900, "a03":0}),
    ]

    targetBraceLayersBoldItalic = [
        # Thin: 100, 100,0
        # Black 900,100,0
    ("{100,100,100}", {"a01":100, "a02":100, "a03":100}), 
    ("{900,100,100}", {"a01":900, "a02":100, "a03":100}),
    ("{100,900,100}", {"a01":100, "a02":900, "a03":100}),  
    ("{900,900,100}", {"a01":900, "a02":900, "a03":100}),
    ("{100,900,0}", {"a01":100, "a02":900, "a03":0}),
    ("{900,900,0}", {"a01":900, "a02":900, "a03":0}),
    ]

    for glyph in selectedGlyphs:
        gname = glyph.name
        if "italic-math" in gname and "bolditalic-math" not in gname:
            addBraceLayersForGlyph(glyph, targetBraceLayersItalic)
            copyMap = [
            [{"glyph": glyph, "type": "master", "masterName" : "Thin"}, 
            {"glyph": glyph, "type": "bracket", "coordinates": {"a01":100, "a02":100, "a03":100} }
            ],
            [{"glyph": glyph, "type":"master", "masterName" : "Black"},
            {"glyph": glyph, "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03":100}}
            ]
            ]    
            ## Should throw an error here if the targetLayer is not-empty to avoid running this accidentally
            copyLayers(copyMap,mathic="adjustwidth")
        elif "bold-math" in gname:
            addBraceLayersForGlyph(glyph, targetBraceLayersBold)
        elif "bolditalic-math" in gname:
            addBraceLayersForGlyph(glyph, targetBraceLayersBoldItalic)
        else:
             print(f"{gname}: name not matched — skipped")
        
def populateBoldItalicLayers(glyph):
    """
    Copies content into relevant italic-math bold-math or italic-math glyphs from the right places
    for italic-math glyphs this import Thin and Black from the corresponding upright glyph
    for bold-math  glyphs thisimports layers from the corresponding upright glyph
    for bolditalic-math glyphs this imports layers from the corresponding italic glyph
    """
    ssty1boldness = 150
    ssty2boldness = 200
    gname = glyph.name

    if "italic-math" in gname and "bolditalic-math" not in gname:
        if "ssty" not in gname:  
            print(f"{gname}: processing as italic not ssty")
            glyph_upright=font.glyphs[glyph.name.replace("italic-math","")]
            if not glyph_upright:
                raise ValueError(f"{glyph.name}: Upright Glyph not found")
            copyMap = [
                [{"glyph": glyph_upright, "type": "master", "masterName" : "Thin"}, 
                {"glyph": glyph, "type": "master", "masterName" : "Thin"}, 
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Black"},
                {"glyph": glyph, "type":"master", "masterName" : "Black"},
                ]
            ]
            copyLayers(copyMap)


        elif "ssty" in gname:  
            print(f"{gname}: processing as italic ssty")
            if ".ssty1" in gname:
                glyph_original=font.glyphs[glyph.name.replace(".ssty1","")]
                sstyboldness=ssty1boldness
                sstycoordinatesupright = {"a01":ssty1boldness, "a02":100, "a03":0}
                sstycoordinatesitalic = {"a01":ssty1boldness, "a02":100, "a03":100}
            elif ".ssty2" in gname:
                sstyboldness=ssty2boldness
                glyph_original=font.glyphs[glyph.name.replace(".ssty2","")]
                sstycoordinatesupright = {"a01":ssty2boldness, "a02":100, "a03":0}
                sstycoordinatesitalic = {"a01":ssty2boldness, "a02":100, "a03":100}
            else:
                raise ValueError(f"Unsupported ssty type")
            
            if not glyph_original:
                raise ValueError(f"Original Italic Glyph not found")

            addBraceLayersForGlyph(glyph_original,[(f"{{{sstyboldness},100,0}}", sstycoordinatesupright)]) 
            addBraceLayersForGlyph(glyph_original,[(f"{{{sstyboldness},100,0}}", sstycoordinatesitalic)])
            temporaryLayerupright = getLayerByCoordinates(glyph_original,sstycoordinatesupright)
            temporaryLayeritalic = getLayerByCoordinates(glyph_original,sstycoordinatesitalic)
            temporaryLayerupright.decomposeComponents()
            temporaryLayeritalic.decomposeComponents()
            temporaryLayerupright.reinterpolate()
            temporaryLayeritalic.reinterpolate()




            copyMap = [
            [{"glyph": glyph_original, "type": "bracket", "coordinates": sstycoordinatesupright},
            {"glyph": glyph, "type": "master", "masterName" : "Thin"},  
            ],
            [{"glyph": glyph_original, "type": "bracket", "coordinates": sstycoordinatesitalic},  
            {"glyph": glyph, "type": "bracket", "coordinates": {"a01": 100, "a02":100, "a03":100}},  
            ],
            [{"glyph": glyph_original, "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03":100}},  
            {"glyph": glyph, "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03":100}},  
            ],
            [{"glyph": glyph_original, "type": "master", "masterName" : "Black"},
            {"glyph": glyph, "type": "master", "masterName" : "Black"},
            ]
            ]
            copyLayers(copyMap)
            glyph_original.layers.remove(temporaryLayerupright)
            glyph_original.layers.remove(temporaryLayeritalic)


    elif "ssty" in gname and not "bold-math" in gname and not "italic-math" in gname:
            print(f"{gname}: processing as upright ssty")
            if ".ssty1" in gname:
                glyph_original=font.glyphs[glyph.name.replace(".ssty1","")]
                sstyboldness=ssty1boldness
                sstycoordinates = {"a01":sstyboldness, "a02":100, "a03":0}
            elif ".ssty2" in gname:
                sstyboldness=ssty2boldness
                glyph_original=font.glyphs[glyph.name.replace(".ssty2","")]
                sstycoordinates = {"a01":ssty2boldness, "a02":100, "a03":0}
            else:
                raise ValueError(f"Unsupported ssty type")
            if not glyph_original:
                raise ValueError(f"Original Glyph not found (ssty1)")
            
            addBraceLayersForGlyph(glyph_original,[(f"{{{sstyboldness},100,0}}", sstycoordinates)])
            temporaryLayer = getLayerByCoordinates(glyph_original,sstycoordinates)





            temporaryLayer.reinterpolate()
            layercontainscomponents= False
            if len(temporaryLayer.components)>0:
                layercontainscomponents= True
                glyph_original.layers[temporaryLayer.layerId].decomposeComponents()

            copyMap = [
            [{"glyph": glyph_original, "type": "bracket", "coordinates": sstycoordinates},
            {"glyph": glyph, "type": "master", "masterName" : "Thin"},  
            ],
            [{"glyph": glyph_original, "type": "master", "masterName" : "Black"},
            {"glyph": glyph, "type": "master", "masterName" : "Black"},
            ]
            ]
            copyLayers(copyMap)

            # If there was one layer that needed decomposing we should do that to all of them
            if layercontainscomponents== True:
                for layer in glyph.layers:
                    layer.decomposeComponents()

            glyph_original.layers.remove(temporaryLayer)


    elif "bold-math" in gname:
            print(f"{gname}: processing as bold")
            glyph_upright=font.glyphs[glyph.name.replace("bold-math","")]
            if not glyph_upright:
                raise ValueError(f"{glyph.name}: Upright Glyph not found")
            copyMap = [
                [{"glyph": glyph_upright, "type": "master", "masterName" : "Thin"}, 
                {"glyph": glyph, "type": "master", "masterName" : "Thin"}, 
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Thin"},
                {"glyph": glyph, "type":"master", "masterName" : "Black"},
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Black"},
                {"glyph": glyph, "type": "bracket", "coordinates": {"a01":100, "a02":900, "a03":0} }
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Black"},
                {"glyph": glyph, "type": "bracket", "coordinates": {"a01":900, "a02":900, "a03":0} }
                ]
            ]
            copyLayers(copyMap)


    elif "bolditalic-math" in gname: 
            print(f"{gname}: processing as bolditalic")
            glyph_upright=font.glyphs[glyph.name.replace("bolditalic-math","")]
            if not glyph_upright:
                raise ValueError(f"Upright Glyph not found")
            copyMap = [
                [{"glyph": glyph_upright, "type": "master", "masterName" : "Thin"}, 
                {"glyph": glyph, "type": "master", "masterName" : "Thin"}, ## Thin is 100,100,0
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Thin"},
                {"glyph": glyph, "type":"master", "masterName" : "Black"},   ## Black is 900,100,0
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Black"},
                {"glyph": glyph,  "type": "bracket", "coordinates": {"a01":100, "a02":900, "a03":0} }   
                ],
                [{"glyph": glyph_upright, "type":"master", "masterName" : "Black"},
                {"glyph": glyph,  "type": "bracket", "coordinates": {"a01":900, "a02":900, "a03":0} }   
                ],
            ]
            copyLayers(copyMap)

            glyph_italic=font.glyphs[glyph.name.replace("bolditalic-math","italic-math")]
            if not glyph_italic:
                raise ValueError(f"Italic Glyph not found")
            copyMap = [
                [{"glyph": glyph_italic,  "type": "bracket", "coordinates": {"a01":100, "a02":100, "a03":100} },    #Thin Italic
                {"glyph": glyph,  "type": "bracket", "coordinates": {"a01":100, "a02":100, "a03":100} }   
                ],
                [{"glyph": glyph_italic, "type": "bracket", "coordinates": {"a01":100, "a02":100, "a03":100} },     #Thin Italic
                {"glyph": glyph, "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03": 100} }
                ],
            [{"glyph": glyph_italic,  "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03":100} },     #Bold Italic
                {"glyph": glyph,  "type": "bracket", "coordinates": {"a01":100, "a02":900, "a03":100} } 
            ],
            [{"glyph": glyph_italic, "type": "bracket", "coordinates": {"a01":900, "a02":100, "a03":100} },      #Bold Italic
                {"glyph": glyph, "type": "bracket", "coordinates": {"a01":900, "a02":900, "a03":100} }
                ]
            ]
            copyLayers(copyMap)
    else:
        print(f"{gname}: name not matched to anything I need to process -- skipped")

Glyphs.showMacroWindow()
Glyphs.clearLog()

selectedGlyphs = [l.parent for l in font.selectedLayers]


for glyph in selectedGlyphs:
   populateBoldItalicLayers(glyph)




#populateLayers_initalonly()