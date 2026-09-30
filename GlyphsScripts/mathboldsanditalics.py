# MenuTitle: Check or Update Italics, Bold, BoldItalics

import traceback
import io
from contextlib import redirect_stdout
from GlyphsApp import *
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
            targetLayer.shapes.append(newComp)
                
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
        
def decomposedMathWorkaroundLayer(layer, weightAxisId=None, componentWeight=None):
    """Glyphs 4 workaround: resolve smart components into temporary outlines."""
    decomposed = layer.copyDecomposedLayer()
    if (decomposed is None or len(decomposed.components)
            or (len(layer.components) and not len(decomposed.paths))):
        if weightAxisId is not None and componentWeight in (150, 200):
            return interpolateDecomposedMathEndpoints(layer, weightAxisId, componentWeight)
        raise ValueError(
            f"{layer.parent.name}, layer {layer.name}: Glyphs 4 workaround "
            "could not produce decomposed outlines; target glyph was not updated")
    return decomposed


def interpolateDecomposedMathEndpoints(layer, weightAxisId, weight):
    """Glyphs 4 workaround when direct decomposition also returns no outlines.

    This script uses the two Weight endpoints 100 and 900. Resolve the
    same component settings at those endpoints, then blend only outlines,
    anchors and width, bypassing smart-component interpolation at 150/200.
    """
    print(f"{layer.parent.name}, layer {layer.name}: direct decomposition failed; "
          f"using the Glyphs 4 workaround to interpolate decomposed Weight 100/900 outlines to {weight}.")
    endpoints = []
    for masterName, endpointWeight in (("Thin", 100), ("Black", 900)):
        temporary = layer.copy()
        temporary.parent = layer.parent
        master = next(m for m in font.masters if m.name == masterName)
        temporary.associatedMasterId = master.id
        temporary.layerId = master.id
        coords = temporary.attributes.get("coordinates")
        if coords is not None:
            coords = dict(coords)
            coords[weightAxisId] = endpointWeight
            temporary.attributes["coordinates"] = coords
        for component in temporary.components:
            component.smartComponentValues[weightAxisId] = endpointWeight
            preload = getattr(component, "preloadCachedLayers", None)
            if preload is not None:
                preload()
            resolved = component.componentLayer
            if resolved is not None:
                temporary.width = resolved.width
        endpoints.append(decomposedMathWorkaroundLayer(temporary))

    light, heavy = endpoints
    # Refuse incompatible endpoints instead of silently pairing wrong nodes.
    compatible = len(light.paths) == len(heavy.paths)
    if compatible:
        for p, q in zip(light.paths, heavy.paths):
            if (p.closed != q.closed or len(p.nodes) != len(q.nodes)
                    or any(a.type != b.type for a, b in zip(p.nodes, q.nodes))):
                compatible = False
                break
    heavyAnchors = {anchor.name: anchor for anchor in heavy.anchors}
    if not compatible or {a.name for a in light.anchors} != set(heavyAnchors):
        raise ValueError(f"{layer.parent.name}: incompatible decomposed Weight endpoints; "
                         "target glyph was not updated")
    factor = (weight - 100.0) / 800.0
    result = light.copy()
    for p, q in zip(result.paths, heavy.paths):
        for a, b in zip(p.nodes, q.nodes):
            a.position = NSPoint(a.position.x + factor * (b.position.x - a.position.x),
                                 a.position.y + factor * (b.position.y - a.position.y))
    for anchor in result.anchors:
        other = heavyAnchors[anchor.name]
        anchor.position = NSPoint(
            anchor.position.x + factor * (other.position.x - anchor.position.x),
            anchor.position.y + factor * (other.position.y - anchor.position.y))
    result.width = light.width + factor * (heavy.width - light.width)
    return result


SPACING_KEYS = ("leftMetricsKey", "rightMetricsKey", "widthMetricsKey")


def clearSpacingKeys(owner):
    for key in SPACING_KEYS:
        setattr(owner, key, None)


def sstySpacingIssues(glyph):
    if not glyph.name.endswith((".ssty1", ".ssty2")):
        return []
    owners = [(glyph, "glyph")] + [(layer, f"layer {layer.name!r}") for layer in glyph.layers]
    return [f"SSTY spacing on {label}: {key}={getattr(owner, key)!r}; "
            "expected no spacing reference (use interpolated spacing)"
            for owner, label in owners for key in SPACING_KEYS if getattr(owner, key)]


def populateSstyPaths(glyph):
    """Interpolate decomposed base outlines; never set component weights for ssty."""
    suffix = next((s for s in (".ssty1", ".ssty2") if glyph.name.endswith(s)), None)
    if suffix is None:
        return False
    base = font.glyphs[glyph.name[:-len(suffix)]]
    if base is None:
        raise ValueError(f"{glyph.name}: missing base glyph")
    lightWeight = 150 if suffix == ".ssty1" else 200

    def axisId(axis):
        value = getattr(axis, "axisId", None)
        return value if value is not None else axis.id

    weightIndex = next(i for i, axis in enumerate(font.axes) if axis.name == "Weight")
    weightId = axisId(font.axes[weightIndex])
    interpolationId = weightId
    if "bold-math" in base.name or "bolditalic-math" in base.name:
        interpolationId = axisId(next(axis for axis in font.axes if axis.name == "Math Weight"))
    sourceCopy = base.copy()
    sourceCopy.parent = font
    clearSpacingKeys(sourceCopy)
    # Resolve the original endpoint settings before interpolating paths. This
    # also avoids the Glyphs bug with live components at Weight 150/200.
    for layer in sourceCopy.layers:
        clearSpacingKeys(layer)
        for component in layer.components:
            preload = getattr(component, "preloadCachedLayers", None)
            if preload is not None:
                preload()
        decomposed = decomposedMathWorkaroundLayer(layer)
        layer.shapes = [path.copy() for path in decomposed.paths]
        copyAnchorsFromLayerToLayer(decomposed, layer)
        layer.width = decomposed.width
    repairGlyphCompatibility(sourceCopy)
    baseLayers = [layer for layer in sourceCopy.layers if layer.isMasterLayer
                  or layer.attributes.get("coordinates") is not None]
    jobs = []
    seenCoordinates = set()
    for source in baseLayers:
        coords = source.attributes.get("coordinates")
        if coords is None:
            target = glyph.layers[source.associatedMasterId]
        else:
            seenCoordinates.add(tuple(sorted(dict(coords).items())))
            target = next((layer for layer in glyph.layers
                           if layer.attributes.get("coordinates") == coords), None)
        jobs.append((source, target, dict(coords) if coords is not None else None))
    # Preserve and regenerate additional target intermediate layers as well.
    for target in glyph.layers:
        coords = target.attributes.get("coordinates")
        if coords is not None and tuple(sorted(dict(coords).items())) not in seenCoordinates:
            jobs.append((sourceCopy.layers[target.associatedMasterId], target, dict(coords)))

    prepared = []
    for original, target, coords in jobs:
        if original is None:
            raise ValueError(f"{glyph.name}: missing source master for component interpolation")
        master = font.masters[original.associatedMasterId]
        location = {axisId(axis): master.axes[i] for i, axis in enumerate(font.axes)}
        location.update(coords or {})
        needsInterpolation = location[interpolationId] == 100 or coords is not None
        if location[interpolationId] == 100:
            location[interpolationId] = lightWeight
        source = original
        if needsInterpolation:
            source = GSLayer()
            source.associatedMasterId = master.id
            source.attributes["coordinates"] = location
            sourceCopy.layers.append(source)
            source.reinterpolate()
            temporary = source
            source = temporary.copy()
            source.parent = sourceCopy
            sourceCopy.layers.remove(temporary)
        if len(source.components) or (len(original.paths) and not len(source.paths)):
            raise ValueError(f"{glyph.name}: could not interpolate base outlines at {location}")
        prepared.append((target, source, master, coords))

    clearSpacingKeys(glyph)
    for layer in glyph.layers:
        clearSpacingKeys(layer)
    for target, source, master, coords in prepared:
        if target is None:
            target = GSLayer()
            target.associatedMasterId = master.id
            if coords is None:
                target.layerId = master.id
            else:
                target.attributes["coordinates"] = coords
            glyph.layers.append(target)
        target.shapes = [path.copy() for path in source.paths]
        copyAnchorsFromLayerToLayer(source, target)
        target.width = source.width
    # Backup/special layers must not retain components either.
    for layer in glyph.layers:
        if len(layer.components):
            decomposed = decomposedMathWorkaroundLayer(layer)
            layer.shapes = [path.copy() for path in decomposed.paths]
            copyAnchorsFromLayerToLayer(decomposed, layer)
            layer.width = decomposed.width
        # Refresh cached sidebearings from the final outlines and width.
        # Spacing references have been cleared, so this preserves interpolation.
        layer.updateMetrics()
    print(f"{glyph.name}: populated as paths with light axis value {lightWeight}")
    return True


def populateSmartMathLayers(glyph):
    """Populate smart components with explicit source weight and italic values.

    Bold styles map Math Weight to the component's Weight font axis.
    Smart ssty glyphs copy their non-ssty counterpart and raise its light endpoint.
    Path-based glyphs still use the existing interpolation/decomposition code.
    """
    baseName = glyph.name
    thinWeight = 100
    for suffix, value in ((".ssty1", 150), (".ssty2", 200)):
        if baseName.endswith(suffix):
            baseName = baseName[:-len(suffix)]
            thinWeight = value
            break
    isSsty = thinWeight != 100
    style = next((s for s in ("bolditalic-math", "italic-math", "bold-math")
                  if s in baseName), None)
    if style is None and not isSsty:
        return False
    # Glyphs 4 workaround: live smart components fail at Weight 150/200
    # with Italic 100. Decompose ALL layers of both italic ssty styles so
    # their masters and intermediate layers retain the same shape type.
    decomposeForGlyphs4 = isSsty and style in ("italic-math", "bolditalic-math")
    base = font.glyphs[baseName if isSsty else baseName.replace(style, "")]
    if base is None:
        return False

    masters = {master.name: master for master in font.masters}
    sources = {}
    for name in ("Thin", "Black"):
        master = masters.get(name)
        if master is None:
            return False
        layer = base.layers[master.id]
        if (layer is None or len(layer.shapes) != 1
                or len(layer.components) != 1
                or not layer.components[0].componentName.startswith("_smart")):
            return False
        component = layer.components[0]
        smartGlyph = component.component
        smartAxes = getattr(smartGlyph, "axes", None)
        if smartAxes is None:
            smartAxes = smartGlyph.smartComponentAxes  # Glyphs 3
        italicAxis = next((axis for axis in smartAxes
                           if axis.name == "Italic"), None)
        if italicAxis is None and style in ("italic-math", "bolditalic-math"):
            raise ValueError(f"{glyph.name}: {component.componentName} has no Italic smart axis")
        sources[name] = (layer, italicAxis)

    weightAxis = next((axis for axis in font.axes if axis.name == "Weight"), None)
    if weightAxis is None:
        raise ValueError(f"{glyph.name}: font has no Weight axis")
    weightAxisId = getattr(weightAxis, "axisId", None)
    if weightAxisId is None:
        weightAxisId = weightAxis.id

    # Coordinates are {Weight, Math Weight, Math Slant}, as in the existing script.
    corners = [(100, 0)]
    if style in ("italic-math", "bolditalic-math"):
        corners.append((100, 100))
    if style in ("bold-math", "bolditalic-math"):
        corners.append((900, 0))
    if style == "bolditalic-math":
        corners.append((900, 100))

    # Validate source layers before modifying any target layers.
    copies = []
    for name, weight in (("Thin", 100), ("Black", 900)):
        master = masters[name]
        for mathWeight, slant in corners:
            componentWeight = mathWeight if style in ("bold-math", "bolditalic-math") else weight
            coords = None if (mathWeight, slant) == (100, 0) else {
                "a01": weight, "a02": mathWeight, "a03": slant}
            if isSsty:
                source, italicAxis = sources[name]
                if coords is not None:
                    source = next((layer for layer in base.layers
                                   if layer.attributes.get("coordinates") == coords), None)
                    if source is None:
                        raise ValueError(f"{glyph.name}: source {base.name} has no layer at {coords}")
                    if (len(source.shapes) != 1 or len(source.components) != 1
                            or source.components[0].componentName != sources[name][0].components[0].componentName):
                        return False
                if componentWeight == 100:
                    componentWeight = thinWeight
            else:
                source, italicAxis = sources["Thin" if componentWeight == 100 else "Black"]
            copies.append((master, coords, source, italicAxis, componentWeight, slant))

    if decomposeForGlyphs4:
        print(
            f"{glyph.name}: using a workaround due to a bug in Glyphs 4 "
            "with smart components at Weight 150/200 and Italic 100; "
            "decomposing all layers into outlines.")

    preparedLayers = []
    for master, coords, source, italicAxis, componentWeight, slant in copies:
        if coords is None:
            target = glyph.layers[master.id]
        else:
            target = next((layer for layer in glyph.layers
                           if layer.attributes.get("coordinates") == coords), None)
        existingTarget = target
        if decomposeForGlyphs4:
            # Keep the temporary layer connected to the font for component
            # resolution, without inserting it into the glyph's layer list.
            target = target.copy() if target is not None else GSLayer()
            target.parent = glyph
            target.associatedMasterId = master.id
            if coords is not None:
                target.attributes["coordinates"] = coords
                target.name = "{%s,%s,%s}" % (coords["a01"], coords["a02"], coords["a03"])
        elif coords is not None:
            if target is None:
                target = GSLayer()
                target.associatedMasterId = master.id
                target.name = "{%s,%s,%s}" % (coords["a01"], coords["a02"], coords["a03"])
                target.attributes["coordinates"] = coords
                glyph.layers.append(target)
            else:
                target.associatedMasterId = master.id

        # Copying preserves alternate values, transforms and alignment settings.
        copyPathsFromLayerToLayer(source, target)
        copyComponentsFromLayerToLayer(source, target)
        copyAnchorsFromLayerToLayer(source, target)
        component = target.components[0]
        if italicAxis is not None:
            axisId = getattr(italicAxis, "axisId", None)
            if axisId is None:
                axisId = italicAxis.id  # Glyphs 3
            component.smartComponentValues[axisId] = slant
        # A copied reference otherwise resolves at the target layer's Weight.
        # Override the FONT axis, which is not in smartGlyph.axes.
        component.smartComponentValues[weightAxisId] = componentWeight
        # Glyphs 4 may return None (or a stale layer) until the smart
        # interpolation cache is prepared after changing the axis values.
        preload = getattr(component, "preloadCachedLayers", None)
        if preload is not None:
            preload()
        resolvedLayer = component.componentLayer
        if decomposeForGlyphs4:
            # Try native decomposition first. If it also hits the Glyphs 4
            # bug, fall back to interpolating decomposed endpoint outlines.
            if resolvedLayer is not None:
                target.width = resolvedLayer.width
            decomposed = decomposedMathWorkaroundLayer(target, weightAxisId, componentWeight)
            preparedLayers.append((existingTarget, target, decomposed))
            continue
        if resolvedLayer is None:
            raise ValueError(
                f"{glyph.name}, layer {target.name}: cannot resolve "
                f"{component.componentName} at Weight={componentWeight}, Italic={slant}")
        target.width = resolvedLayer.width
        target.syncMetrics()

    if decomposeForGlyphs4:
        # Include any additional layers too, to avoid leaving a mixture of
        # components and paths. Prepare every copy before changing the glyph.
        updatedIds = {existing.layerId for existing, _, _ in preparedLayers
                      if existing is not None}
        for layer in glyph.layers:
            if layer.layerId not in updatedIds:
                temporary = layer.copy()
                temporary.parent = glyph
                preparedLayers.append((layer, temporary,
                                       decomposedMathWorkaroundLayer(temporary)))
        for existing, temporary, decomposed in preparedLayers:
            target = existing if existing is not None else temporary
            copyPathsFromLayerToLayer(decomposed, target)
            copyComponentsFromLayerToLayer(decomposed, target)
            copyAnchorsFromLayerToLayer(decomposed, target)
            copyMetricsFromLayerToLayer(decomposed, target)
            target.associatedMasterId = temporary.associatedMasterId
            if existing is None:
                glyph.layers.append(target)
        print(f"{glyph.name}: populated as outlines (Glyphs 4 smart-component workaround)")
        return True

    print(f"{glyph.name}: populated from smart components")
    return True


MATH_VARIANTS_KEY = "com.nagwa.MATHPlugin.variants"
MATH_VARIANT_LISTS = ("hVariants", "vVariants")
MATH_ASSEMBLIES = ("hAssembly", "vAssembly")


def mathReferenceName(value):
    referenced = getattr(value, "glyph", None)
    return referenced.name if referenced is not None else str(value)


def mathAssemblyParts(data, key):
    return [(mathReferenceName(part[0]), *part[1:]) for part in data.get(key, [])]


def sstyComponentIssues(glyph):
    """All ssty layers must contain outlines, never live components."""
    if not glyph.name.endswith((".ssty1", ".ssty2")):
        return []
    return [f"SSTY paths in layer {layer.name!r}: current components="
            f"{[c.componentName for c in layer.components]!r}; expected paths only"
            for layer in glyph.layers if len(layer.components)]


def sstyAssemblySources(glyph, base):
    """Pair each ssty owner with its base owner, retaining unsuffixed parts."""
    yield glyph, base, "glyph"
    for layer in glyph.layers:
        source = None
        coords = layer.attributes.get("coordinates")
        if coords is not None:
            source = next((candidate for candidate in base.layers
                           if candidate.attributes.get("coordinates") == coords), None)
        elif layer.isMasterLayer:
            source = base.layers[layer.associatedMasterId]
        else:
            source = base.layers[layer.layerId]
        if source is None:
            source = base.layers[layer.associatedMasterId]
        yield layer, source, f"layer {layer.name!r}"


def sstyMathPlan(glyph):
    """Plan metadata corrections from the original glyph without changing it."""
    suffix = next((s for s in (".ssty1", ".ssty2") if glyph.name.endswith(s)), None)
    if suffix is None:
        return None
    plan = {"expected": {}, "issues": [], "missing": [], "base": None}
    baseName = glyph.name[:-len(suffix)]
    base = font.glyphs[baseName]
    plan["base"] = base
    if base is None:
        plan["missing"].append(f"original glyph {baseName!r}")
    else:
        baseData = base.userData.get(MATH_VARIANTS_KEY, {})
        actualData = glyph.userData.get(MATH_VARIANTS_KEY, {})
        for key in MATH_VARIANT_LISTS:
            expected = []
            for reference in baseData.get(key, []):
                name = mathReferenceName(reference)
                # Do not append a second script-size suffix to an existing one.
                for scriptSuffix in (".ssty1", ".ssty2"):
                    if name.endswith(scriptSuffix):
                        name = name[:-len(scriptSuffix)]
                        break
                target = name + suffix
                expected.append(target)
                if font.glyphs[target] is None:
                    message = f"{key} target {target!r}"
                    if message not in plan["missing"]:
                        plan["missing"].append(message)
            plan["expected"][key] = expected
            actual = [mathReferenceName(ref) for ref in actualData.get(key, [])]
            if actual != expected:
                plan["issues"].append(f"MATH {key}: current={actual!r}, expected={expected!r}")

    if base is not None:
        for owner, source, label in sstyAssemblySources(glyph, base):
            if source is None:
                plan["missing"].append(f"base assembly source for {label}")
                continue
            actualData = owner.userData.get(MATH_VARIANTS_KEY, {})
            sourceData = source.userData.get(MATH_VARIANTS_KEY, {})
            for key in MATH_ASSEMBLIES:
                actual = mathAssemblyParts(actualData, key)
                expected = mathAssemblyParts(sourceData, key)
                if actual != expected:
                    plan["issues"].append(
                        f"MATH {key} on {label}: current={actual!r}, expected={expected!r}")
    plan["issues"].extend(f"MATH missing {item}; cannot update this glyph" for item in plan["missing"])
    return plan


def applySstyMathPlan(glyph, plan):
    if plan is None:
        return
    data = dict(glyph.userData.get(MATH_VARIANTS_KEY, {}))
    for key, names in plan["expected"].items():
        if names:
            data[key] = list(names)
        else:
            data.pop(key, None)
    glyph.userData[MATH_VARIANTS_KEY] = data
    for owner, source, label in sstyAssemblySources(glyph, plan["base"]):
        if source is None:
            raise ValueError(f"{glyph.name}: missing base assembly source for {label}")
        data = dict(owner.userData.get(MATH_VARIANTS_KEY, {}))
        sourceData = source.userData.get(MATH_VARIANTS_KEY, {})
        for key in MATH_ASSEMBLIES:
            parts = mathAssemblyParts(sourceData, key)
            if parts:
                data[key] = parts
            else:
                data.pop(key, None)
        if data or owner.userData.get(MATH_VARIANTS_KEY) is not None:
            owner.userData[MATH_VARIANTS_KEY] = data


def _minimumPathAssignment(costs):
    """Minimum-cost one-to-one assignment (Hungarian algorithm)."""
    n = len(costs)
    u, v, p, way = [0.] * (n + 1), [0.] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minimum, used = [float("inf")] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float("inf"), 0
            for j in range(1, n + 1):
                if not used[j]:
                    value = costs[i0 - 1][j - 1] - u[i0] - v[j]
                    if value < minimum[j]:
                        minimum[j], way[j] = value, j0
                    if minimum[j] < delta:
                        delta, j1 = minimum[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minimum[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    assignment = [0] * n
    for j in range(1, n + 1):
        assignment[p[j] - 1] = j - 1
    return sum(costs[i][j] for i, j in enumerate(assignment)), assignment


def _pathAlignments(reference, target, referenceBounds, targetBounds):
    """Preserve compatible node order; score repairs only when it is incompatible."""
    if reference.closed != target.closed or len(reference.nodes) != len(target.nodes):
        return []
    if not len(reference.nodes):
        return [(0., target.copy(), False, 0)]
    # Geometry is not evidence that an existing correspondence is wrong:
    # slant and weight can make a different cyclic start look closer. Changing
    # just one endpoint then corrupts interpolation between valid source layers.
    if _pathsHaveMatchingNodeOrder(reference, target):
        return [(0., target.copy(), False, 0)]
    def points(nodes, bounds):
        return [((node.position.x - bounds.origin.x) / max(bounds.size.width, 1.),
                 (node.position.y - bounds.origin.y) / max(bounds.size.height, 1.)) for node in nodes]
    referenceTypes = tuple(node.type for node in reference.nodes)
    referencePoints = points(reference.nodes, referenceBounds)
    candidates = []
    for reverse in (False, True):
        path = target.copy()
        if reverse:
            path.reverse()
        # Closed contours must have the reference winding, including holes.
        if path.closed and path.direction != reference.direction:
            continue
        nodes = list(path.nodes)
        for shift in range(len(nodes) if path.closed else 1):
            rotated = nodes[shift:] + nodes[:shift]
            if tuple(node.type for node in rotated) != referenceTypes:
                continue
            score = sum((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
                        for a, b in zip(referencePoints, points(rotated, targetBounds))) / len(nodes)
            aligned = path.copy()
            copied = list(aligned.nodes)
            aligned.nodes = copied[shift:] + copied[:shift]
            candidates.append((score, aligned, reverse, shift))
    return sorted(candidates, key=lambda candidate: candidate[0])


def _pathsHaveMatchingNodeOrder(reference, target):
    return (reference.closed == target.closed
            and len(reference.nodes) == len(target.nodes)
            and (not reference.closed or reference.direction == target.direction)
            and all(a.type == b.type for a, b in zip(reference.nodes, target.nodes)))


def glyphCompatibilityPlan(glyph):
    """Plan repairs without mutation. Refuse missing or ambiguous correspondences."""
    layers = [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]
    if len(layers) < 2:
        return []
    reference = next((layer for layer in layers if layer.layerId == font.masters[0].id), layers[0])
    referencePaths = list(reference.paths)
    referenceComponents = [(i, shape.componentName) for i, shape in enumerate(reference.shapes)
                           if isinstance(shape, GSComponent)]
    repairs = []
    impossible = 1e12
    for layer in layers:
        if layer is reference or layer.layerId == reference.layerId:
            continue
        label = f"Compatibility in {glyph.name}, layer {layer.name!r}"
        components = [(i, shape.componentName) for i, shape in enumerate(layer.shapes)
                      if isinstance(shape, GSComponent)]
        paths = list(layer.paths)
        if components != referenceComponents or len(paths) != len(referencePaths):
            raise ValueError(f"{label}: different path counts or component layout; cannot fix by reordering")
        if not paths:
            continue
        # Preserve the source's path order and node correspondence whenever
        # already compatible. In particular, never rematch italic layers to
        # upright layers solely because another order scores better spatially.
        if all(_pathsHaveMatchingNodeOrder(a, b) for a, b in zip(referencePaths, paths)):
            continue
        options = [[_pathAlignments(a, b, reference.bounds, layer.bounds) for b in paths]
                   for a in referencePaths]
        costs = [[choices[0][0] if choices else impossible for choices in row] for row in options]
        score, assignment = _minimumPathAssignment(costs)
        if score >= impossible:
            raise ValueError(f"{label}: incompatible node counts/types; cannot fix by reordering")
        if (assignment == list(range(len(paths)))
                and all(not options[i][j][0][2] and options[i][j][0][3] == 0
                        for i, j in enumerate(assignment))):
            continue
        # Reject a nearly equal alternative assignment rather than guessing.
        for i, j in enumerate(assignment):
            alternate = [row[:] for row in costs]
            alternate[i][j] = impossible
            alternativeScore, _ = _minimumPathAssignment(alternate)
            if alternativeScore < impossible and alternativeScore - score <= max(1e-8, abs(score) * .05):
                raise ValueError(f"{label}: ambiguous path correspondence; needs manual matching")
        messages, alignedPaths = [], []
        if assignment != list(range(len(paths))):
            messages.append(f"path order: use current paths {[j + 1 for j in assignment]} "
                            f"to match {reference.name!r}")
        for i, j in enumerate(assignment):
            choices = options[i][j]
            best, aligned, reverse, shift = choices[0]
            if len(choices) > 1 and choices[1][0] - best <= max(1e-8, abs(best) * .05):
                raise ValueError(f"{label}: ambiguous start point for path {j + 1}; needs manual matching")
            alignedPaths.append(aligned)
            if reverse or shift:
                messages.append(f"path {j + 1}: reverse={reverse}, start-point rotation={shift}")
        if messages:
            repairs.append((layer, alignedPaths, [f"{label}: {message}" for message in messages]))
    return repairs


def repairGlyphCompatibility(glyph):
    repairs = glyphCompatibilityPlan(glyph)
    # All layers have been validated before applying any repair.
    for layer, paths, messages in repairs:
        slots = [i for i, shape in enumerate(layer.shapes) if isinstance(shape, GSPath)]
        for i, path in zip(slots, paths):
            layer.shapes[i] = path
        for message in messages:
            print(message)


def populateBoldItalicLayers(glyph):
    """Update outlines and script-size MATH metadata after validating targets."""
    plan = sstyMathPlan(glyph)
    if plan is not None and plan["missing"]:
        raise ValueError(f"{glyph.name}: missing " + "; ".join(plan["missing"]) + "; glyph was not updated")
    originalLayers = [layer.copy() for layer in glyph.layers]
    originalSpacing = {key: getattr(glyph, key) for key in SPACING_KEYS}
    try:
        _populateBoldItalicLayers(glyph)
        repairGlyphCompatibility(glyph)
        applySstyMathPlan(glyph, plan)
    except Exception:
        glyph.layers = originalLayers
        for key, value in originalSpacing.items():
            setattr(glyph, key, value)
        raise
    if plan is not None and plan["issues"]:
        print(f"{glyph.name}: corrected MATH variants and copied base assemblies")


def _populateBoldItalicLayers(glyph):
    """
    Copies content into relevant italic-math bold-math or italic-math glyphs from the right places
    for italic-math glyphs this import Thin and Black from the corresponding upright glyph
    for bold-math  glyphs thisimports layers from the corresponding upright glyph
    for bolditalic-math glyphs this imports layers from the corresponding italic glyph
    """
    if populateSstyPaths(glyph):
        return
    if populateSmartMathLayers(glyph):
        return

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

font = Glyphs.font


def isMathUpdateGlyph(glyph):
    return any(style in glyph.name for style in ("italic-math", "bold-math")) or "ssty" in glyph.name


def canonicalOutline(path):
    """Ignore contour order/start points, but preserve winding and node geometry."""
    nodes = tuple((str(n.type), float(n.position.x), float(n.position.y)) for n in path.nodes)
    if path.closed and nodes:
        nodes = min(nodes[i:] + nodes[:i] for i in range(len(nodes)))
    return bool(path.closed), nodes


def checkedLayerSnapshot(layer):
    # This runs only on the detached font. Components must resolve there too.
    for component in layer.components:
        preload = getattr(component, "preloadCachedLayers", None)
        if preload is not None:
            preload()
    decomposed = layer.copyDecomposedLayer()
    if (decomposed is None or len(decomposed.components)
            or (len(layer.components) and not len(decomposed.paths))):
        raise ValueError(f"Cannot resolve components in layer {layer.name!r}; comparison is incomplete")
    # Component-layer LSB/RSB can still be cached as zero before regeneration.
    # Derive both from the same resolved geometry used for the outline check.
    width = float(layer.width)
    bounds = decomposed.bounds
    left = float(bounds.origin.x) if len(decomposed.paths) else 0.0
    right = width - float(bounds.origin.x + bounds.size.width) if len(decomposed.paths) else width
    return {
        "outlines": sorted(canonicalOutline(path) for path in decomposed.paths),
        "anchors": {a.name: (float(a.position.x), float(a.position.y)) for a in decomposed.anchors},
        "width": width,
        "LSB": left,
        "RSB": right,
    }


def checkedGlyphSnapshot(glyph):
    result = {}
    for layer in glyph.layers:
        coords = layer.attributes.get("coordinates")
        if coords is not None:
            key = ("coordinates", tuple(sorted((str(k), float(v)) for k, v in coords.items())))
        elif layer.isMasterLayer:
            key = ("master", str(layer.associatedMasterId))
        else:
            key = ("layer", str(layer.layerId))
        # Keep duplicate coordinate layers distinct rather than hiding one.
        ordinal = sum(1 for existing in result if existing[0] == key)
        result[(key, ordinal)] = (str(layer.name), checkedLayerSnapshot(layer))
    return result


CHECK_TOLERANCE = 1.0  # Ignore numeric differences strictly smaller than one unit.


def outlinesWithinTolerance(actual, expected):
    if actual[0] != expected[0] or len(actual[1]) != len(expected[1]):
        return False
    a, b = actual[1], expected[1]
    # Small coordinate changes can change the canonical start of a closed path.
    for offset in range(len(b) if actual[0] and b else 1):
        rotated = b[offset:] + b[:offset]
        if all(p[0] == q[0]
               and abs(p[1] - q[1]) < CHECK_TOLERANCE
               and abs(p[2] - q[2]) < CHECK_TOLERANCE
               for p, q in zip(a, rotated)):
            return True
    return False


def reportMathDifferences(before, after):
    """Report differences of at least one unit, retaining exact values and deltas."""
    differences = 0

    def report(message):
        nonlocal differences
        differences += 1
        print("    " + message)

    def number(label, actual, expected):
        if abs(expected - actual) >= CHECK_TOLERANCE:
            report(f"{label}: current={actual!r}, expected={expected!r}, delta={expected - actual!r}")

    for key in sorted(before.keys() | after.keys(), key=repr):
        if key not in before:
            report(f"Missing layer: script would add {after[key][0]!r} ({key[0]!r})")
            continue
        if key not in after:
            report(f"Extra layer: script would remove {before[key][0]!r} ({key[0]!r})")
            continue
        name, actual = before[key]
        _, expected = after[key]
        if actual == expected:
            continue
        print(f"  Layer {name!r} ({key[0]!r})")
        for metric in ("width", "LSB", "RSB"):
            number(metric, actual[metric], expected[metric])
        for anchor in sorted(actual["anchors"].keys() | expected["anchors"].keys()):
            a, b = actual["anchors"].get(anchor), expected["anchors"].get(anchor)
            if a is None or b is None:
                report(f"Anchor {anchor!r}: current={a!r}, expected={b!r}")
            else:
                number(f"Anchor {anchor!r} x", a[0], b[0])
                number(f"Anchor {anchor!r} y", a[1], b[1])
        # Remove exact matches before pairing changed contours for diagnostics.
        remaining = list(expected["outlines"])
        changed = []
        for outline in actual["outlines"]:
            if outline in remaining:
                remaining.remove(outline)
            else:
                changed.append(outline)
        # Also remove contours whose coordinates differ only within tolerance.
        unmatched = []
        for outline in changed:
            match = next((i for i, candidate in enumerate(remaining)
                          if outlinesWithinTolerance(outline, candidate)), None)
            if match is None:
                unmatched.append(outline)
            else:
                remaining.pop(match)
        changed = unmatched
        for index in range(max(len(changed), len(remaining))):
            label = f"Changed contour {index + 1}"
            if index >= len(changed):
                report(f"{label}: missing; expected={remaining[index]!r}")
                continue
            if index >= len(remaining):
                report(f"{label}: extra; current={changed[index]!r}")
                continue
            a, b = changed[index], remaining[index]
            if a[0] != b[0]:
                report(f"{label} closed: current={a[0]}, expected={b[0]}")
            if len(a[1]) != len(b[1]):
                report(f"{label} node count: current={len(a[1])}, expected={len(b[1])}")
                report(f"{label} nodes: current={a[1]!r}, expected={b[1]!r}")
                continue
            for nodeIndex, (p, q) in enumerate(zip(a[1], b[1]), 1):
                if p[0] != q[0]:
                    report(f"{label} node {nodeIndex} type: current={p[0]!r}, expected={q[0]!r}")
                number(f"{label} node {nodeIndex} x", p[1], q[1])
                number(f"{label} node {nodeIndex} y", p[2], q[2])
    return differences


def checkMathGlyphSteps(sourceFont, glyphNames=None, openTab=False):
    """Run the real updater in a detached font; never update the live document.

    Each target and every possible source the updater modifies are replaced by
    disposable copies, then restored. Checks do not cascade updates to later
    glyphs. glyphNames is an optional subset for scripted verification.
    """
    global font
    previousFont = font
    names = [name for name in dict.fromkeys(glyphNames)
             if sourceFont.glyphs[name] is not None and isMathUpdateGlyph(sourceFont.glyphs[name])] if glyphNames is not None else [
        g.name for g in sourceFont.glyphs if isMathUpdateGlyph(g)]
    counts = {"match": 0, "different": 0, "error": 0}
    differentNames = []
    print(f"CHECK: {len(names)} glyphs; ignoring numeric differences smaller than {CHECK_TOLERANCE:g} unit.")
    print("Components are compared as decomposed outlines. Deltas are expected minus current.")
    print("SSTY glyphs require paths only; light outlines are interpolated at 150/200.")
    print("Each glyph is checked independently against the current font. No changes are saved.")
    print("Preparing an in-memory font copy…", flush=True)
    yield "Preparing an in-memory font copy…"
    try:
        workingFont = sourceFont.copy()
        for index, name in enumerate(names, 1):
            # Return to the app between glyphs, with the live font context restored.
            yield (f"Checking {index}/{len(names)}: {name} "
                   f"({counts['different']} different)")
            font = workingFont
            originals = {}
            mathIssues = []
            try:
                # Legacy ssty branches add/remove layers on their source glyph.
                # Copy all potential direct sources as well as the target.
                related = {name, name.replace(".ssty1", "").replace(".ssty2", "")}
                for candidate in list(related):
                    related.update(candidate.replace(style, "") for style in (
                        "italic-math", "bold-math", "bolditalic-math"))
                    related.add(candidate.replace("bolditalic-math", "italic-math"))
                for candidate in sorted(related):
                    original = font.glyphs[candidate]
                    if original is not None:
                        originals[candidate] = original
                        font.glyphs[candidate] = original.copy()
                glyph = font.glyphs[name]
                plan = sstyMathPlan(glyph)
                mathIssues = plan["issues"] if plan is not None else []
                mathIssues = list(mathIssues) + sstyComponentIssues(glyph) + sstySpacingIssues(glyph)
                try:
                    compatibility = glyphCompatibilityPlan(glyph)
                    mathIssues.extend(message for _, _, messages in compatibility for message in messages)
                except ValueError as error:
                    mathIssues.append(str(error))
                before = checkedGlyphSnapshot(glyph)
                # Suppress updater chatter during checks; Update Selected keeps
                # its normal output. Never hold redirected stdout across a yield.
                with redirect_stdout(io.StringIO()):
                    # Check geometry even if a required MATH target is missing.
                    _populateBoldItalicLayers(glyph)
                    repairGlyphCompatibility(glyph)
                after = checkedGlyphSnapshot(glyph)
                details = io.StringIO()
                with redirect_stdout(details):
                    changes = reportMathDifferences(before, after)
                    for issue in mathIssues:
                        print("    " + issue)
                    changes += len(mathIssues)
                status = "different" if changes else "match"
                counts[status] += 1
                if changes:
                    differentNames.append(name)
                if changes:
                    print(f"\n[{index}/{len(names)}] {name}")
                    print(details.getvalue(), end="")
                    print(f"  DIFFERENT: {changes} reported differences")
            except Exception:
                counts["error"] += 1
                print(f"\n[{index}/{len(names)}] {name}")
                for issue in mathIssues:
                    print("    " + issue)
                print("  ERROR: could not complete this glyph's check")
                print(traceback.format_exc())
            finally:
                try:
                    for candidate, original in originals.items():
                        workingFont.glyphs[candidate] = original
                finally:
                    font = previousFont
        print(f"\nCHECK COMPLETE: {counts['match']} matching, {counts['different']} different, "
              f"{counts['error']} errors. The open font was not modified.")
        if openTab:
            if differentNames:
                sourceFont.newTab("".join("/" + name for name in differentNames))
                print(f"Opened a tab with all {len(differentNames)} differing glyphs "
                      "in scan order. Failed checks are not included.")
            else:
                print("No differing glyphs to open in a tab. Failed checks are not included.")
        return counts
    finally:
        font = previousFont


def checkMathGlyphs(sourceFont, glyphNames=None, openTab=False):
    """Synchronous entry point for scripted checks; the UI advances one step at a time."""
    steps = checkMathGlyphSteps(sourceFont, glyphNames, openTab)
    while True:
        try:
            next(steps)
        except StopIteration as finished:
            return finished.value


class MathUpdateWindow:
    def __init__(self):
        import vanilla
        self.steps = None
        self.w = vanilla.FloatingWindow((410, 235), "Check / Update Maths")
        self.w.explanation = vanilla.TextBox(
            (15, 12, -15, 55), "Check selected glyphs without changing the font, "
            "or update selected glyphs. "
            "Details appear in the Macro Panel.")
        self.w.openTab = vanilla.CheckBox(
            (15, 77, -15, 20), "Open tab with all differing glyphs", value=False)
        self.w.check = vanilla.Button((15, 115, 180, 30), "Check Selected", callback=self.check)
        self.w.update = vanilla.Button((210, 115, 185, 30), "Update Selected", callback=self.update)
        self.w.status = vanilla.TextBox((15, 153, -15, 35), "Ready")
        self.w.cancel = vanilla.Button((15, 195, -15, 25), "Cancel Check", callback=self.cancel)
        self.w.cancel.enable(False)
        self.w.bind("close", self.cancel)
        self.w.open()

    def run(self, checking):
        global font
        font = Glyphs.font
        Glyphs.clearLog()
        if font is None:
            print("Open a font first.")
            self.notifyResult("Maths: nothing to process", "Open a font first.")
            return
        self.w.check.enable(False)
        self.w.update.enable(False)
        try:
            if checking:
                from PyObjCTools.AppHelper import callLater
                selectedNames = list(dict.fromkeys(
                    layer.parent.name for layer in font.selectedLayers
                    if isMathUpdateGlyph(layer.parent)))
                if not selectedNames:
                    print("Select italic-math, bold-math, bolditalic-math or ssty glyphs to check.")
                    self.notifyResult("Maths: nothing to check", "No applicable glyphs selected")
                    return
                self.steps = checkMathGlyphSteps(
                    font, glyphNames=selectedNames, openTab=self.w.openTab.get())
                self.w.openTab.enable(False)
                self.w.cancel.enable(True)
                self.w.status.set("Starting check…")
                callLater(0.05, self.advanceCheck, self.steps)
            else:
                selected = list({layer.parent.name: layer.parent for layer in font.selectedLayers}.values())
                print(f"UPDATE: {len(selected)} selected glyphs")
                failed = 0
                for glyph in selected:
                    try:
                        populateBoldItalicLayers(glyph)
                    except Exception:
                        failed += 1
                        print(f"UPDATE ERROR: {glyph.name}")
                        print(traceback.format_exc())
                summary = f"{len(selected) - failed} updated, {failed} errors"
                print(f"UPDATE COMPLETE: {summary}")
                self.notifyResult("Maths update complete", summary)
        except Exception:
            print(traceback.format_exc())
            self.notifyResult("Maths operation failed", "See the Macro Panel for details.")
            if self.steps is not None:
                self.steps.close()
                self.steps = None
        finally:
            if self.steps is None:
                self.finishCheck()

    def notifyResult(self, title, summary):
        self.w.status.set(summary)
        try:
            Glyphs.showNotification(title, summary)
        except Exception:
            # The dialog still shows the result if notifications are unavailable.
            print(f"{title}: {summary}")

    def finishCheck(self):
        self.w.check.enable(True)
        self.w.update.enable(True)
        self.w.openTab.enable(True)
        self.w.cancel.enable(False)

    def advanceCheck(self, steps):
        if self.steps is not steps:
            return
        from PyObjCTools.AppHelper import callLater
        try:
            self.w.status.set(next(self.steps))
        except StopIteration as finished:
            self.steps = None
            counts = finished.value
            self.notifyResult(
                "Maths check complete",
                f"{counts['different']} different, {counts['match']} matching, "
                f"{counts['error']} errors. Font unchanged.")
            self.finishCheck()
        except Exception:
            self.steps.close()
            self.steps = None
            print(traceback.format_exc(), flush=True)
            self.notifyResult("Maths check failed", "See the Macro Panel for details.")
            self.finishCheck()
        else:
            # Glyphs objects stay on the main thread. Scheduling another callback
            # lets the Macro Panel repaint and handles Cancel between glyphs.
            callLater(0.01, self.advanceCheck, steps)

    def cancel(self, sender):
        if self.steps is not None:
            self.steps.close()
            self.steps = None
            print("CHECK CANCELLED. The open font was not modified.", flush=True)
            self.w.status.set("Cancelled")
            self.finishCheck()

    def check(self, sender):
        self.run(True)

    def update(self, sender):
        self.run(False)


if __name__ == "__main__":
    mathUpdateWindow = MathUpdateWindow()
