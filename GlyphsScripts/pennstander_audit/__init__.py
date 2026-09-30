"""Source-only Pennstander audit. No entry point here changes a live font."""

import io
import itertools
import math
import re
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path


MATH = "com.nagwa.MATHPlugin.variants"
CONSTANTS = "com.nagwa.MATHPlugin.constants"
EXTENDED = "com.nagwa.MATHPlugin.extendedShape"
GROUPS = ("Structure", "Interpolation", "Assemblies", "MATH data", "Recipes")
SUFFIX = re.compile(r"\.(ssty[12]|alt\d*|ss\d+)(?=\.|$)")
METRICS = ("leftMetricsKey", "rightMetricsKey", "widthMetricsKey")
ANCHORS = ("math.ta", "math.ic", "math.tr", "math.tl", "math.br", "math.bl")


def finite(value):
    return not isinstance(value, (str, bytes)) and isinstance(value, (int, float)) and math.isfinite(value)


def items(value):
    if value is None or isinstance(value, (str, bytes)) or hasattr(value, "keys"):
        raise ValueError("Expected an array, found {!r}".format(value))
    return list(value)


def ref_name(value):
    glyph = getattr(value, "glyph", None)
    if glyph is not None:
        return glyph.name
    if isinstance(value, str) and value:
        return value
    raise ValueError("Invalid glyph reference {!r}".format(value))


def base_of(name):
    matches = list(SUFFIX.finditer(name))
    if not matches:
        return None
    match = matches[-1]
    return name[:match.start()] + name[match.end():], match.group(1).startswith(("ssty", "alt"))


def axis_id(axis):
    value = getattr(axis, "axisId", None)
    value = value if value is not None else axis.id
    return str(value() if callable(value) else value)


def glyph_axes(glyph):
    """Glyphs 4 uses glyph.axes; Glyphs 3 exposes smartComponentAxes."""
    axes = getattr(glyph, "axes", None)
    if axes is None:
        axes = getattr(glyph, "smartComponentAxes", ())
    return list(axes or ())


def master_layer(glyph, master):
    return glyph.layers[master.id]


def active_layers(glyph):
    return [layer for layer in glyph.layers if layer.isMasterLayer or layer.isSpecialLayer]


def metric_is_auto_aligned(layer, key):
    """Ask about this layer's effective alignment, not component checkbox flags."""
    if not len(layer.components):
        return False
    # Newer Glyphs builds distinguish aligned widths from aligned sidebearings.
    specific = "hasAlignedWidth" if key == "widthMetricsKey" else "hasAlignedSideBearings"
    for attribute in (specific, "isAligned"):
        value = getattr(layer, attribute, None)
        if value is not None:
            return bool(value() if callable(value) else value)
    return False


def label(layer):
    return "{} [{}]".format(layer.name, layer.layerId)


def xy(point):
    return float(point.x), float(point.y)


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def flatten_curve(points, tolerance=0.5, depth=0):
    a, b = points[0], points[-1]
    length = math.dist(a, b)
    flatness = max((abs(cross(a, b, p)) / length if length else math.dist(a, p)
                    for p in points[1:-1]), default=0)
    excess = sum(math.dist(p, q) for p, q in zip(points, points[1:])) - length
    if len(points) == 2 or (flatness <= tolerance and excess <= tolerance) or depth >= 14:
        return [a, b]
    rows = [points]
    while len(rows[-1]) > 1:
        rows.append([((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
                     for p, q in zip(rows[-1], rows[-1][1:])])
    left, right = [r[0] for r in rows], [r[-1] for r in reversed(rows)]
    return flatten_curve(left, tolerance, depth + 1)[:-1] + flatten_curve(right, tolerance, depth + 1)


def polygons(layer):
    result = []
    for path in layer.paths:
        nodes = list(path.nodes)
        on = [i for i, n in enumerate(nodes) if str(n.type).lower() != "offcurve"]
        if not on:
            if nodes:
                raise ValueError("Contour contains no on-curve nodes")
            result.append([])
            continue
        points = []
        pairs = list(zip(on, on[1:]))
        if path.closed:
            pairs.append((on[-1], on[0] + len(nodes)))
        for start, end in pairs:
            controls = [xy(nodes[i % len(nodes)].position) for i in range(start, end + 1)]
            if len(controls) not in (2, 3, 4):
                raise ValueError("Unsupported segment with {} control points".format(len(controls)))
            points.extend(flatten_curve(controls)[:-1])
        points.append(xy(nodes[on[0] if path.closed else on[-1]].position))
        result.append(points)
    return result


def signed_area(poly):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:])) / 2


def self_crossings(poly):
    """Proper crossings only; touching/overlapping segments need manual review."""
    segments = list(zip(poly, poly[1:]))
    count = 0
    for i, (a, b) in enumerate(segments):
        for j in range(i + 2, len(segments)):
            if i == 0 and j == len(segments) - 1:
                continue
            c, d = segments[j]
            if max(a[0], b[0]) < min(c[0], d[0]) or max(c[0], d[0]) < min(a[0], b[0]):
                continue
            if max(a[1], b[1]) < min(c[1], d[1]) or max(c[1], d[1]) < min(a[1], b[1]):
                continue
            if cross(a, b, c) * cross(a, b, d) < -1e-8 and cross(c, d, a) * cross(c, d, b) < -1e-8:
                count += 1
    return count


def section(polys, position, vertical):
    """Cross-section intervals after overlap removal; even-odd fill."""
    points = []
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            av, bv = (a[1], b[1]) if vertical else (a[0], b[0])
            if (av <= position < bv) or (bv <= position < av):
                u, v = (a[0], b[0]) if vertical else (a[1], b[1])
                points.append(u + (v - u) * (position - av) / (bv - av))
    points.sort()
    return list(zip(points[::2], points[1::2]))


def repeated_parts(parts, repeats):
    return [part for part in parts for _ in range(repeats if part[1] else 1)]


def dependency_cycles(graph):
    """Iterative DFS avoids recursion limits on broken dependency chains."""
    done, cycles = set(), []
    for root in graph:
        if root in done:
            continue
        stack, path, indices = [(root, iter(graph.get(root, ())))], [root], {root: 0}
        while stack:
            name, children = stack[-1]
            child = next(children, None)
            if child is None:
                done.add(name)
                stack.pop()
                indices.pop(path.pop())
            elif child in indices:
                cycles.append(path[indices[child]:] + [child])
            elif child not in done:
                indices[child] = len(path)
                path.append(child)
                stack.append((child, iter(graph.get(child, ()))))
    return cycles


def load_neighbor(filename):
    path = Path(__file__).resolve().parent.parent / filename
    # exec avoids writing bytecode and always reads the current recipe script.
    import types
    module = types.ModuleType("pennstander_audit_" + path.stem.replace(" ", "_"))
    module.__file__ = str(path)
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


class Audit:
    def __init__(self, font, names, groups, density=3, tolerance=2.0):
        # Caller supplies a detached font snapshot, never the open document.
        self.font = font
        self.names = list(dict.fromkeys(names))
        self.scope = set(self.names)
        self.groups = set(groups)
        self.density = density
        self.tolerance = tolerance
        self.issues = []
        self.seen = set()
        self.stats = Counter()
        self.axis_ids = [axis_id(a) for a in font.axes]
        self.masters = list(font.masters)
        self.master_ids = {str(m.id) for m in self.masters}
        self.glyphs = {g.name: g for g in font.glyphs}
        self.component_graph = {}
        self.unsafe = set()
        self.geometry_cache = {}
        self.recipe = None
        self.assembly_checked = set()
        self.bounds = self.axis_bounds()

    def add(self, group, check, glyph, location, detail, severity="Warning"):
        name = glyph if isinstance(glyph, str) else getattr(glyph, "name", "")
        key = (group, check, name, location, detail, severity)
        if key not in self.seen:
            self.seen.add(key)
            self.issues.append(dict(group=group, check=check, glyph=name, location=location,
                                    detail=detail, severity=severity))

    def failed(self, group, glyph, location, error):
        self.add(group, "Check incomplete", glyph, location, str(error), "Skipped")

    def guard(self, group, glyph, location, callback):
        try:
            callback()
            self.stats[group + " checks"] += 1
        except Exception as error:
            self.failed(group, glyph, location, "{}: {}".format(type(error).__name__, error))

    def axis_bounds(self):
        points = [tuple(m.axes) for m in self.masters]
        for parameter in self.font.customParameters:
            if parameter.name == "Virtual Master" and not getattr(parameter, "disabled", False):
                try:
                    values = {v["Axis"]: float(v["Location"]) for v in parameter.value}
                    points.append(tuple(values.get(a.name, points[0][i]) for i, a in enumerate(self.font.axes)))
                except Exception as error:
                    self.failed("Structure", "", "Virtual Master", error)
        return [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(len(self.axis_ids))] if points else []

    def location(self, layer, ignored_axis_ids=()):
        master = next((m for m in self.masters if str(m.id) == str(layer.associatedMasterId)), None)
        if master is None:
            raise ValueError("Associated master is missing")
        values = dict(zip(self.axis_ids, map(float, master.axes)))
        coords = layer.attributes.get("coordinates")
        if coords is not None:
            values.update({str(k): float(v) for k, v in coords.items()
                           if str(k) in self.axis_ids and str(k) not in ignored_axis_ids})
        return tuple(values[k] for k in self.axis_ids)

    def data(self, owner, group, glyph, where):
        value = owner.userData.get(MATH, {})
        if not hasattr(value, "get"):
            self.add(group, "Malformed MATH metadata", glyph, where, repr(value), "Error")
            return {}
        return value

    def prepare_dependencies(self):
        for glyph in self.font.glyphs:
            refs = set()
            for layer in active_layers(glyph):
                refs.update(c.componentName for c in layer.components)
            self.component_graph[glyph.name] = refs
            if refs - self.glyphs.keys():
                self.unsafe.add(glyph.name)
        for cycle in dependency_cycles(self.component_graph):
            self.unsafe.update(cycle)
            if "Structure" in self.groups:
                for name in set(cycle) & self.scope:
                    self.add("Structure", "Component cycle", name, "", " → ".join(cycle), "Error")
        while True:
            more = {name for name, refs in self.component_graph.items() if refs & self.unsafe}
            if more <= self.unsafe:
                break
            self.unsafe.update(more)

    def resolved(self, layer):
        if layer.parent.name in self.unsafe:
            raise ValueError("Unresolved or cyclic component dependency; geometry was not attempted")
        result = layer.copyDecomposedLayer()
        if result is None or len(result.components) or (len(layer.components) and not len(result.paths)):
            raise ValueError("Glyphs could not decompose the components")
        return result

    def geometry(self, layer):
        key = (layer.parent.name, str(layer.layerId))
        if key not in self.geometry_cache:
            resolved = self.resolved(layer)
            resolved.removeOverlap()
            bounds = resolved.bounds
            self.geometry_cache[key] = (polygons(resolved), (bounds.origin.x, bounds.origin.y,
                                                           bounds.size.width, bounds.size.height))
        return self.geometry_cache[key]

    def run(self):
        yield "Indexing component dependencies…"
        self.prepare_dependencies()
        if "Structure" in self.groups:
            yield "Checking font structure and feature references…"
            self.guard("Structure", "", "Font", self.font_structure)
        if "MATH data" in self.groups:
            self.guard("MATH data", "", "Constants", self.constants)
        for group in GROUPS:
            if group not in self.groups:
                continue
            for index, name in enumerate(self.names, 1):
                glyph = self.glyphs.get(name)
                if glyph is None:
                    self.add(group, "Missing glyph", name, "", "Glyph does not exist", "Error")
                    continue
                yield "{} · {}/{} · {}".format(group, index, len(self.names), name)
                if group == "Interpolation":
                    try:
                        yield from self.interpolation(glyph)
                        self.stats[group + " checks"] += 1
                    except Exception as error:
                        self.failed(group, glyph, "", error)
                else:
                    callback = {"Structure": self.structure, "Assemblies": self.assemblies,
                                "MATH data": self.math_data, "Recipes": self.recipes}[group]
                    self.guard(group, glyph, "", lambda: callback(glyph))
        self.geometry_cache.clear()

    def font_structure(self):
        if not self.masters:
            self.add("Structure", "No masters", "", "", "Font has no masters", "Error")
        for what, values in (("master ID", [str(m.id) for m in self.masters]),
                             ("axis ID", self.axis_ids), ("axis tag", [a.axisTag for a in self.font.axes])):
            for value, count in Counter(values).items():
                if count > 1:
                    self.add("Structure", "Duplicate " + what, "", "", str(value), "Error")
        for attr, title in (("unicodes", "Unicode collision"), ("productionName", "Production name collision")):
            owners = defaultdict(list)
            for g in self.font.glyphs:
                if not g.export:
                    continue
                value = getattr(g, attr, None)
                for v in (value or []) if attr == "unicodes" else [value or g.name]:
                    owners[str(v)].append(g.name)
            for value, names in owners.items():
                if len(names) > 1:
                    for name in self.scope.intersection(names):
                        self.add("Structure", title, name, "", "{}: {}".format(value, ", ".join(names)), "Error")
        graph = defaultdict(set)
        for glyph in self.font.glyphs:
            for owner in [glyph] + active_layers(glyph):
                for key in METRICS:
                    value = getattr(owner, key, None)
                    if value:
                        # Numeric keys and self-relative forms contain no glyph reference.
                        match = re.match(r"^=+\|?([A-Za-z_.][A-Za-z0-9_.-]*?)(?=[+*/]|[+-]\d|$)", str(value))
                        if match and match.group(1) != glyph.name:
                            graph[glyph.name].add(match.group(1))
        for cycle in dependency_cycles(graph):
            for name in self.scope.intersection(cycle):
                self.add("Structure", "Possible metrics cycle", name, "", " → ".join(cycle))
        self.feature_references()

    def feature_references(self):
        chunks = []
        for prefix in self.font.featurePrefixes:
            if not getattr(prefix, "disabled", False):
                chunks.append(prefix.code or "")
        for cls in self.font.classes:
            if not getattr(cls, "disabled", False):
                chunks.append("@{} = [{}];".format(cls.name, cls.code or ""))
        for feature in self.font.features:
            if not getattr(feature, "disabled", False):
                chunks.append("feature {0} {{\n{1}\n}} {0};".format(feature.name, feature.code or ""))
        code = "\n".join(chunks)
        if re.search(r"\binclude\s*\(", code):
            self.failed("Structure", "", "Features", "External include files are not read; feature-reference parsing skipped")
            return
        try:
            from fontTools.feaLib.parser import Parser
            Parser(io.StringIO(code), glyphNames=set(self.glyphs), followIncludes=False).parse()
        except ImportError:
            self.failed("Structure", "", "Features", "fontTools.feaLib is unavailable")
        except Exception as error:
            self.add("Structure", "Feature source needs review", "", "Features/classes/prefixes",
                     "Stored feature code could not be parsed: {}. Automatic code and Glyphs-specific syntax may need regeneration; no code was changed.".format(error))

    def coordinate_structure(self, glyph, layer, local_axes, locations):
        coords = layer.attributes.get("coordinates")
        if coords is None:
            return
        where = label(layer)
        if not hasattr(coords, "items"):
            self.add("Structure", "Malformed coordinates", glyph, where, repr(coords), "Error")
            return
        coords = {str(key): value for key, value in coords.items()}
        unknown = set(coords) - set(self.axis_ids) - set(local_axes)
        if unknown:
            self.add("Structure", "Unknown coordinate axes", glyph, where,
                     "{} are absent from both font.axes and this glyph's own axes".format(sorted(unknown)), "Error")
        invalid = {key: value for key, value in coords.items() if not finite(value)}
        if invalid:
            self.add("Structure", "Invalid coordinate value", glyph, where, repr(invalid), "Error")
        if unknown or invalid:
            return
        # Font bounds apply only to font axes. Local smart-axis coordinates must
        # remain part of the duplicate key, or different smart layers collapse
        # onto the same font-master location and produce another false positive.
        loc = self.location(layer, ignored_axis_ids=local_axes)
        local_values = tuple(sorted((key, float(value)) for key, value in coords.items() if key in local_axes))
        location_key = (loc, local_values) if local_axes else loc
        locations[location_key].append(where)
        for axis, value, bounds in zip(self.font.axes, loc, self.bounds):
            if axis_id(axis) not in local_axes and (not finite(value) or not bounds[0] <= value <= bounds[1]):
                self.add("Structure", "Coordinate outside master/virtual-master range", glyph, where,
                         "{}={} outside {}".format(axis.name, value, bounds))

    def structure(self, glyph):
        layers = active_layers(glyph)
        local_axes = {axis_id(axis): axis for axis in glyph_axes(glyph)}
        production = getattr(glyph, "productionName", None) or glyph.name
        if glyph.export and (not re.fullmatch(r"[A-Za-z0-9_.-]+", production) or len(production) > 63):
            self.add("Structure", "Suspicious production name", glyph, "", repr(production), "Review")
        for value in getattr(glyph, "unicodes", []) or []:
            try:
                scalar = int(value, 16)
                if not 0 <= scalar <= 0x10FFFF or 0xD800 <= scalar <= 0xDFFF:
                    raise ValueError()
            except (TypeError, ValueError):
                self.add("Structure", "Invalid Unicode scalar", glyph, "", repr(value), "Error")
        ids, locations = Counter(str(l.layerId) for l in glyph.layers), defaultdict(list)
        for value, count in ids.items():
            if count > 1:
                self.add("Structure", "Duplicate layer ID", glyph, value, str(count), "Error")
        for master in self.masters:
            if master_layer(glyph, master) is None:
                self.add("Structure", "Missing master layer", glyph, master.name, str(master.id), "Error")
        for layer in layers:
            where = label(layer)
            if str(layer.associatedMasterId) not in self.master_ids:
                self.add("Structure", "Unknown master", glyph, where, str(layer.associatedMasterId), "Error")
            self.coordinate_structure(glyph, layer, local_axes, locations)
            for component in layer.components:
                if component.componentName not in self.glyphs:
                    self.add("Structure", "Missing component", glyph, where, component.componentName, "Error")
                transform = tuple(component.transform)
                if not all(finite(v) for v in transform):
                    self.add("Structure", "Invalid component transform", glyph, where, repr(transform), "Error")
                elif abs(transform[0] * transform[3] - transform[1] * transform[2]) < 1e-8:
                    self.add("Structure", "Collapsed component transform", glyph, where, component.componentName, "Error")
            for owner in (glyph, layer):
                for key in METRICS:
                    value = getattr(owner, key, None)
                    if value:
                        match = re.match(r"^=+\|?([A-Za-z_.][A-Za-z0-9_.-]*?)(?=[+*/]|[+-]\d|$)", str(value))
                        if match and match.group(1) not in self.glyphs:
                            owner_label = "glyph" if owner is glyph else "layer"
                            detail = "Stored {} {}: {}; referenced glyph {!r} does not exist.".format(owner_label, key, value, match.group(1))
                            if metric_is_auto_aligned(layer, key):
                                self.add("Structure", "Unused/stale metrics reference", glyph, where,
                                         detail + " Automatic alignment controls this metric on this layer; this leftover key does not establish broken spacing.", "Review")
                            else:
                                self.add("Structure", "Missing metrics reference", glyph, where, detail, "Error")
            if not finite(layer.width) or layer.width < 0:
                self.add("Structure", "Invalid advance width", glyph, where, repr(layer.width), "Error")
            if glyph.export and not len(layer.shapes) and getattr(glyph, "category", "") not in ("Separator", "Other"):
                self.add("Structure", "Empty exported glyph", glyph, where, "No paths or components")
            if glyph.name not in self.unsafe and len(layer.components):
                self.guard("Structure", glyph, where, lambda: self.resolved(layer))
            if glyph.name not in self.unsafe and any(getattr(owner, key, None) and not metric_is_auto_aligned(layer, key)
                                                    for owner in (glyph, layer) for key in METRICS):
                def check_metrics():
                    temporary = layer.copy()
                    temporary.parent = glyph
                    temporary.syncMetrics()
                    for key, metrics_key in (("width", "widthMetricsKey"), ("LSB", "leftMetricsKey"), ("RSB", "rightMetricsKey")):
                        if metric_is_auto_aligned(layer, metrics_key):
                            continue
                        actual, expected = float(getattr(layer, key)), float(getattr(temporary, key))
                        if abs(actual - expected) > self.tolerance:
                            self.add("Structure", "Stale metrics", glyph, where,
                                     "{}: stored {:g}, recalculated {:g}, delta {:+g}".format(key, actual, expected, expected - actual))
                self.guard("Structure", glyph, where + " / metrics", check_metrics)
        for loc, owners in locations.items():
            if len(owners) > 1:
                self.add("Structure", "Duplicate intermediate location", glyph, repr(loc), "; ".join(owners), "Error")

    def sample_locations(self, glyph):
        points = set(itertools.product(*[
            [lo + (hi - lo) * i / (self.density - 1) for i in range(self.density)] if hi != lo else [lo]
            for lo, hi in self.bounds]))
        for instance in self.font.instances:
            if getattr(instance, "type", 0) == 0:
                coords = tuple(map(float, instance.axes))
                if len(coords) == len(self.axis_ids):
                    points.add(coords)
        for layer in active_layers(glyph):
            coords = layer.attributes.get("coordinates")
            if coords is None:
                continue
            loc = self.location(layer)
            points.add(loc)
            for i, (lo, hi) in enumerate(self.bounds):
                for sign in (-1, 1):
                    near = list(loc)
                    near[i] += sign * max((hi - lo) * 0.001, 0.01)
                    if lo <= near[i] <= hi:
                        points.add(tuple(near))
        return sorted(points)

    def sample(self, glyph, coords):
        from GlyphsApp import GSLayer
        layer = GSLayer()
        layer.associatedMasterId = self.masters[0].id
        layer.attributes["coordinates"] = dict(zip(self.axis_ids, coords))
        glyph.layers.append(layer)
        try:
            layer.reinterpolate()
            if not len(layer.shapes) and any(len(l.shapes) for l in active_layers(glyph) if l is not layer):
                raise ValueError("Interpolation returned an empty layer for a nonempty glyph")
            resolved = self.resolved(layer)
            return resolved
        finally:
            glyph.layers.remove(layer)

    def shape_stats(self, layer):
        polys = polygons(layer)
        areas = [signed_area(p) for p in polys]
        crossings = sum(self_crossings(p) for p in polys)
        kinks = 0
        short = 0
        for path in layer.paths:
            nodes = list(path.nodes)
            for i, node in enumerate(nodes):
                if not finite(node.position.x) or not finite(node.position.y):
                    raise ValueError("Non-finite node coordinates")
                if not node.smooth or len(nodes) < 3 or (not path.closed and i in (0, len(nodes) - 1)):
                    continue
                a, b, c = xy(nodes[i - 1].position), xy(node.position), xy(nodes[(i + 1) % len(nodes)].position)
                u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
                denom = math.hypot(*u) * math.hypot(*v)
                if denom and math.degrees(math.acos(max(-1., min(1., (u[0] * v[0] + u[1] * v[1]) / denom)))) > 5:
                    kinks += 1
            on = [xy(n.position) for n in nodes if str(n.type).lower() != "offcurve"]
            pairs = list(zip(on, on[1:] + on[:1])) if path.closed else list(zip(on, on[1:]))
            short += sum(math.dist(a, b) < self.tolerance for a, b in pairs)
        union = layer.copy()
        union.removeOverlap()
        topology = tuple(sorted(int(p.direction) for p in union.paths if p.closed))
        bounds = layer.bounds
        return dict(area=sum(abs(a) for a in areas), crossings=crossings, kinks=kinks, short=short,
                    topology=topology, width=float(layer.width), bboxWidth=float(bounds.size.width),
                    bboxHeight=float(bounds.size.height), tiny=sum(abs(a) < self.tolerance ** 2 for a in areas))

    def interpolation_structure(self, glyph, layers):
        if not layers:
            return
        reference = layers[0]
        def signature(layer):
            return [("component", s.componentName) if hasattr(s, "componentName") else
                    ("path", bool(s.closed), tuple(str(n.type) for n in s.nodes)) for s in layer.shapes]
        for layer in layers[1:]:
            if signature(reference) != signature(layer):
                self.add("Interpolation", "Incompatible source layers", glyph, label(layer),
                         "Path/component order, counts, node types or closure differ from {}".format(label(reference)), "Error")
                continue
            if len(reference.paths) > 1:
                def centre(path, box):
                    return ((path.bounds.origin.x + path.bounds.size.width / 2 - box.origin.x) / max(box.size.width, 1),
                            (path.bounds.origin.y + path.bounds.size.height / 2 - box.origin.y) / max(box.size.height, 1))
                if all(hasattr(p, "bounds") for p in list(reference.paths) + list(layer.paths)):
                    p = [centre(path, reference.bounds) for path in reference.paths]
                    q = [centre(path, layer.bounds) for path in layer.paths]
                    candidates = []
                    for i, path in enumerate(reference.paths):
                        choices = [(math.dist(p[i], q[j]) ** 2, j) for j, other in enumerate(layer.paths)
                                   if path.closed == other.closed and tuple(n.type for n in path.nodes) == tuple(n.type for n in other.nodes)]
                        candidates.append(min(choices) if choices else (float("inf"), i))
                    pairing = [j for cost, j in candidates]
                    current = sum(math.dist(a, b) ** 2 for a, b in zip(p, q))
                    if len(set(pairing)) == len(pairing) and pairing != list(range(len(pairing))) and current > .01 and sum(cost for cost, j in candidates) < current * .25:
                        self.add("Interpolation", "Suspicious contour pairing", glyph, label(layer),
                                 "Nearest compatible contours suggest order {}; current order moves much farther. Review correspondence.".format([j + 1 for j in pairing]), "Review")
            for index, (a, b) in enumerate(zip(reference.paths, layer.paths), 1):
                if a.closed and a.direction != b.direction:
                    self.add("Interpolation", "Reversed contour", glyph, label(layer), "Path {} differs in winding".format(index), "Error")
                # Pure diagnostic: normalize by whole-layer bounds and compare
                # cyclic starts. Slanted designs can legitimately trigger this.
                if not a.closed or len(a.nodes) < 3:
                    continue
                def normalized(path, box):
                    return [((n.position.x - box.origin.x) / max(box.size.width, 1),
                             (n.position.y - box.origin.y) / max(box.size.height, 1)) for n in path.nodes]
                p, q = normalized(a, reference.bounds), normalized(b, layer.bounds)
                score = lambda points: sum(math.dist(u, v) ** 2 for u, v in zip(p, points)) / len(p)
                current = score(q)
                choices = [(score(q[k:] + q[:k]), k) for k in range(1, len(q))
                           if all(n.type == b.nodes[(j + k) % len(q)].type for j, n in enumerate(a.nodes))]
                if choices and current > .005 and min(choices)[0] < current * .25:
                    self.add("Interpolation", "Suspicious contour start", glyph, label(layer),
                             "Path {}: rotation {} fits geometry much better than current correspondence; review, especially for slanted forms.".format(index, min(choices)[1]), "Review")

    def interpolation(self, glyph):
        if glyph.name in self.unsafe:
            self.failed("Interpolation", glyph, "", "Broken component dependency; sampling skipped")
            return
        if glyph.name.startswith("_smart.") or glyph_axes(glyph):
            self.failed("Interpolation", glyph, "", "Smart-source internal axes are not font axes; test their consuming glyphs")
            return
        layers = [l for l in active_layers(glyph) if l.isMasterLayer or l.attributes.get("coordinates") is not None]
        self.interpolation_structure(glyph, layers)
        if any(l.isSpecialLayer and l.attributes.get("coordinates") is None for l in active_layers(glyph)):
            self.failed("Interpolation", glyph, "Alternate layers", "Bracket/other special layers are not paired with default outlines; their conditional transitions are not sampled")
        baseline = []
        for layer in layers:
            try:
                stats = self.shape_stats(self.resolved(layer))
                baseline.append(stats)
                for key in ("crossings", "kinks", "tiny", "short"):
                    if stats[key]:
                        self.add("Interpolation", "Source geometry: " + key, glyph, label(layer),
                                 "{} occurrences (approximate geometry; review intentional details)".format(stats[key]), "Review")
            except Exception as error:
                self.failed("Interpolation", glyph, label(layer), error)
        if not baseline:
            return
        points = self.sample_locations(glyph)
        initial_count = len(points)
        scheduled = set(points)
        originals = {self.location(l) for l in layers}
        for index, coords in enumerate(points, 1):
            if coords in originals:
                continue
            where = ", ".join("{}={:g}".format(a.name, v) for a, v in zip(self.font.axes, coords))
            yield "Interpolation · {} · sample {}/{} · {}".format(glyph.name, index, len(points), where)
            try:
                before_findings = len(self.issues)
                current = self.shape_stats(self.sample(glyph, coords))
                self.stats["Interpolated locations"] += 1
                if current["topology"] not in [s["topology"] for s in baseline]:
                    self.add("Interpolation", "Changed visible contour structure", glyph, where,
                             "After overlap removal: {}; source structures: {}".format(current["topology"], sorted(set(s["topology"] for s in baseline))))
                for key in ("crossings", "kinks", "tiny", "short"):
                    maximum = max(s[key] for s in baseline)
                    if current[key] > maximum:
                        self.add("Interpolation", "New " + key, glyph, where,
                                 "{} versus source maximum {}".format(current[key], maximum))
                for key in ("area", "bboxWidth", "bboxHeight", "width"):
                    low, high = min(s[key] for s in baseline), max(s[key] for s in baseline)
                    if current[key] < low * .5 - self.tolerance or current[key] > high * 1.5 + self.tolerance:
                        self.add("Interpolation", "Geometry outlier", glyph, where,
                                 "{}={:g}; source range {:g}–{:g}".format(key, current[key], low, high))
                # One refinement level near suspicious initial samples. Bound
                # the work explicitly; this is still a sampled source check.
                if len(self.issues) > before_findings and index <= initial_count:
                    for axis, (lo, hi) in enumerate(self.bounds):
                        if hi == lo:
                            continue
                        for sign in (-1, 1):
                            near = list(coords)
                            near[axis] += sign * (hi - lo) / (4 * (self.density - 1))
                            point = tuple(near)
                            if lo <= near[axis] <= hi and point not in scheduled and point not in originals:
                                points.append(point)
                                scheduled.add(point)
                                self.stats["Refinement locations scheduled"] += 1
            except Exception as error:
                self.failed("Interpolation", glyph, where, error)

    def assembly_records(self, glyph, master, key):
        layer = master_layer(glyph, master)
        if layer is None:
            raise ValueError("Missing master layer {}".format(master.name))
        data = self.data(layer, "Assemblies", glyph, master.name)
        raw = items(data.get(key, []))
        normalized = []
        for index, record in enumerate(raw, 1):
            record = items(record)
            if len(record) != 4:
                raise ValueError("{} part {} has {} fields; expected glyph, extender, start, end".format(key, index, len(record)))
            name = ref_name(record[0])
            flags, start, end = record[1:]
            if not finite(flags) or flags not in (0, 1):
                raise ValueError("{} part {} has invalid extender flag {!r}".format(key, index, flags))
            if any(not finite(v) or not 0 <= v <= 65535 or int(v) != v for v in (start, end)):
                raise ValueError("{} part {} has invalid connector lengths {!r}".format(key, index, record[2:]))
            normalized.append((name, flags, start, end))
        return normalized

    def assemblies(self, glyph):
        if glyph.name in self.assembly_checked:
            return
        self.assembly_checked.add(glyph.name)
        relationship = base_of(glyph.name)
        if relationship and relationship[0] not in self.glyphs:
            self.add("Assemblies", "Missing base", glyph, "", relationship[0], "Error")
        elif relationship:
            self.assemblies(self.glyphs[relationship[0]])
        for key, vertical in (("hAssembly", False), ("vAssembly", True)):
            reference = None
            for master in self.masters:
                where = "{} / {}".format(master.name, key)
                try:
                    parts = self.assembly_records(glyph, master, key)
                    if reference is None:
                        reference = (master.name, parts)
                    elif parts != reference[1]:
                        self.add("Assemblies", "Master assemblies differ", glyph, where,
                                 "Current={!r}; {}={!r}".format(parts, *reference), "Error")
                    if relationship and relationship[1] and relationship[0] in self.glyphs:
                        expected = self.assembly_records(self.glyphs[relationship[0]], master, key)
                        if parts != expected:
                            self.add("Assemblies", "Base assembly differs", glyph, where,
                                     "Current={!r}; base {}={!r}".format(parts, relationship[0], expected), "Error")
                    if parts:
                        self.assembly_geometry(glyph, master, key, parts, vertical)
                except Exception as error:
                    self.add("Assemblies", "Assembly check failed", glyph, where, str(error), "Error")

    def assembly_geometry(self, glyph, master, key, parts, vertical):
        where = "{} / {}".format(master.name, key)
        geometries = {}
        for name, flag, start, end in parts:
            target = self.glyphs.get(name)
            if target is None:
                self.add("Assemblies", "Missing part", glyph, where, name, "Error")
                continue
            if not target.export:
                self.add("Assemblies", "Part does not export", glyph, where, name, "Error")
            layer = master_layer(target, master)
            if layer is None:
                self.add("Assemblies", "Part master missing", glyph, where, name, "Error")
                continue
            try:
                polys, box = self.geometry(layer)
                advance = box[3 if vertical else 2]
                geometries[name] = (polys, box, advance)
                if advance <= 0:
                    self.add("Assemblies", "Empty assembly part", glyph, where, name, "Error")
                if max(start, end) > advance + self.tolerance:
                    self.add("Assemblies", "Connector exceeds part advance", glyph, where,
                             "{}: connectors {}, {}; bbox advance {}".format(name, start, end, advance), "Error")
            except Exception as error:
                self.failed("Assemblies", glyph, where + " / " + name, error)
        if len(geometries) != len({p[0] for p in parts}):
            return
        constants = master.userData.get(CONSTANTS, {})
        overlap = constants.get("MinConnectorOverlap")
        if not finite(overlap) or overlap < 0:
            self.failed("Assemblies", glyph, where, "Missing/invalid MinConnectorOverlap; join checks skipped")
            return
        has_extender = any(p[1] for p in parts)
        if not has_extender:
            self.add("Assemblies", "No extender", glyph, where, "Assembly cannot grow by repeating a part", "Review")
        checked = set()
        previous = None
        for repeats in range(5) if has_extender else (0,):
            expanded = repeated_parts(parts, repeats)
            if not expanded:
                continue
            joins = list(zip(expanded, expanded[1:]))
            maxima = [min(a[3], b[2]) for a, b in joins]
            total = sum(geometries[p[0]][2] for p in expanded)
            smallest, largest = total - sum(maxima), total - len(joins) * overlap
            if previous is not None and smallest > previous + self.tolerance and all(v >= overlap for v in maxima):
                self.add("Assemblies", "Gap in achievable assembly sizes", glyph, where,
                         "{} repeats start at {:g}; previous count reaches {:g}".format(repeats, smallest, previous), "Review")
            if previous is not None and largest <= previous:
                self.add("Assemblies", "Extenders do not increase length", glyph, where,
                         "{} repeats: maximum size {}; previous {}".format(repeats, largest, previous), "Error")
            previous = largest
            for a, b in joins:
                pair = (a, b)
                if pair in checked:
                    continue
                checked.add(pair)
                maximum = min(a[3], b[2])
                join_name = "{} → {}".format(a[0], b[0])
                if maximum < overlap:
                    self.add("Assemblies", "Insufficient connector overlap", glyph, where,
                             "{}: available {}, required {} ({} extender repeats)".format(join_name, maximum, overlap, repeats), "Error")
                    continue
                for amount in sorted({overlap, (overlap + maximum) / 2, maximum}):
                    if amount <= 0:
                        continue
                    pa, ba, aa = geometries[a[0]]
                    pb, bb, ab = geometries[b[0]]
                    origin = 1 if vertical else 0
                    offset = aa - amount
                    start = max(ba[origin], offset + bb[origin])
                    end = min(ba[origin] + aa, offset + bb[origin] + ab)
                    if end <= start:
                        self.add("Assemblies", "No geometric overlap at join", glyph, where,
                                 "{}: requested overlap {:g}, but positioned part bounds do not overlap".format(join_name, amount), "Review")
                        break
                    if abs((end - start) - amount) > self.tolerance:
                        self.add("Assemblies", "Part origins change geometric overlap", glyph, where,
                                 "{}: requested overlap {:g}, bbox overlap {:g}".format(join_name, amount, end - start), "Review")
                    seam = (start + end) / 2
                    sa = section(pa, seam, vertical)
                    sb = section(pb, seam - offset, vertical)
                    delta = max((abs(u - v) for first, second in zip(sa, sb) for u, v in zip(first, second)), default=0)
                    if not sa or not sb or len(sa) != len(sb) or delta > self.tolerance:
                        self.add("Assemblies", "Join cross-sections differ", glyph, where,
                                 "{} at overlap {:g}: end {} / start {}; verify seam and alignment".format(join_name, amount, sa, sb), "Review")
                        break
            self.stats["Assembly constructions"] += 1

    def constants(self):
        known = set("""ScriptPercentScaleDown ScriptScriptPercentScaleDown DelimitedSubFormulaMinHeight
            DisplayOperatorMinHeight MathLeading AxisHeight AccentBaseHeight FlattenedAccentBaseHeight
            MinConnectorOverlap SubscriptShiftDown SubscriptTopMax SubscriptBaselineDropMin
            SuperscriptShiftUp SuperscriptShiftUpCramped SuperscriptBottomMin SuperscriptBaselineDropMax
            SubSuperscriptGapMin SuperscriptBottomMaxWithSubscript SpaceAfterScript UpperLimitGapMin
            UpperLimitBaselineRiseMin LowerLimitGapMin LowerLimitBaselineDropMin StackTopShiftUp
            StackTopDisplayStyleShiftUp StackBottomShiftDown StackBottomDisplayStyleShiftDown StackGapMin
            StackDisplayStyleGapMin StretchStackTopShiftUp StretchStackBottomShiftDown StretchStackGapAboveMin
            StretchStackGapBelowMin FractionNumeratorShiftUp FractionNumeratorDisplayStyleShiftUp
            FractionDenominatorShiftDown FractionDenominatorDisplayStyleShiftDown FractionNumeratorGapMin
            FractionNumDisplayStyleGapMin FractionRuleThickness FractionDenominatorGapMin
            FractionDenomDisplayStyleGapMin SkewedFractionHorizontalGap SkewedFractionVerticalGap
            OverbarVerticalGap OverbarRuleThickness OverbarExtraAscender UnderbarVerticalGap
            UnderbarRuleThickness UnderbarExtraDescender RadicalVerticalGap RadicalDisplayStyleVerticalGap
            RadicalRuleThickness RadicalExtraAscender RadicalKernBeforeDegree RadicalKernAfterDegree
            RadicalDegreeBottomRaisePercent""".split())
        unsigned = {"DelimitedSubFormulaMinHeight", "DisplayOperatorMinHeight", "MinConnectorOverlap", "RadicalDegreeBottomRaisePercent"}
        for master in self.masters:
            data = master.userData.get(CONSTANTS, {})
            if not hasattr(data, "items"):
                self.add("MATH data", "Malformed constants", "", master.name, repr(data), "Error")
                continue
            missing = known - set(data)
            if missing:
                self.add("MATH data", "Constants not explicitly stored", "", master.name,
                         ", ".join(sorted(missing)) + ". Plugin defaults may apply; verify intended values.", "Review")
            for name, value in data.items():
                if name not in known:
                    self.add("MATH data", "Unknown constant", "", master.name, str(name), "Review")
                low, high = (0, 65535) if name in unsigned else (-32768, 32767)
                if not finite(value) or not low <= value <= high:
                    self.add("MATH data", "Invalid constant", "", master.name, "{}={!r}; expected {}…{}".format(name, value, low, high), "Error")
                elif ("Percent" in name and not 0 < value <= 100) or ("RuleThickness" in name and value <= 0):
                    self.add("MATH data", "Suspicious constant", "", master.name, "{}={}".format(name, value))
            script, scriptscript = data.get("ScriptPercentScaleDown"), data.get("ScriptScriptPercentScaleDown")
            if finite(script) and finite(scriptscript) and scriptscript > script:
                self.add("MATH data", "Script scaling order", "", master.name,
                         "Scriptscript {}% exceeds script {}%".format(scriptscript, script))
            minus = self.glyphs.get("minus")
            if minus and master_layer(minus, master) is not None:
                try:
                    _, box = self.geometry(master_layer(minus, master))
                    for key in ("FractionRuleThickness", "RadicalRuleThickness", "OverbarRuleThickness", "UnderbarRuleThickness"):
                        value = data.get(key)
                        if finite(value) and box[3] > 0 and abs(value - box[3]) > max(self.tolerance, box[3] * .5):
                            self.add("MATH data", "Rule thickness differs from minus", "minus", master.name,
                                     "{}={}; minus thickness={:g}".format(key, value, box[3]), "Review")
                except Exception as error:
                    self.failed("MATH data", "minus", master.name, error)

    def math_data(self, glyph):
        data = self.data(glyph, "MATH data", glyph, "Glyph")
        for key, vertical in (("hVariants", False), ("vVariants", True)):
            try:
                names = [ref_name(v) for v in items(data.get(key, []))]
            except Exception as error:
                self.add("MATH data", "Malformed variant list", glyph, key, str(error), "Error")
                continue
            for name, count in Counter(names).items():
                if count > 1:
                    self.add("MATH data", "Duplicate variant", glyph, key, "{} appears {} times".format(name, count))
                target = self.glyphs.get(name)
                if target is None or not target.export:
                    self.add("MATH data", "Missing/nonexporting variant", glyph, key, name, "Error")
            for master in self.masters:
                previous = None
                for name in names:
                    target = self.glyphs.get(name)
                    if target is None:
                        previous = None
                        continue
                    try:
                        layer = master_layer(target, master)
                        if layer is None:
                            raise ValueError("Missing master layer")
                        _, box = self.geometry(layer)
                        size = box[3 if vertical else 2]
                        if previous and size < previous[1] - self.tolerance:
                            self.add("MATH data", "Variant sizes decrease", glyph, master.name + " / " + key,
                                     "{}={:g} follows {}={:g}".format(name, size, *previous), "Error")
                        elif previous and abs(size - previous[1]) <= self.tolerance:
                            self.add("MATH data", "Nearly equal variant sizes", glyph, master.name + " / " + key,
                                     "{} and {}: {:g}, {:g}".format(previous[0], name, previous[1], size), "Review")
                        previous = (name, size)
                    except Exception as error:
                        self.failed("MATH data", glyph, master.name + " / " + key + " / " + name, error)
                        previous = None
        reference = None
        for layer in active_layers(glyph):
            where = label(layer)
            anchors = [a for a in layer.anchors if a.name.startswith("math.")]
            names = Counter(a.name for a in anchors)
            for name, count in names.items():
                if count > 1:
                    self.add("MATH data", "Duplicate anchor name", glyph, where, name, "Error")
                if not any(name == a or (a in ANCHORS[2:] and name.startswith(a)) for a in ANCHORS):
                    self.add("MATH data", "Unknown MATH anchor", glyph, where, name, "Review")
            if layer.isMasterLayer:
                signature = (frozenset(names), tuple(sum(n.startswith(prefix) for n in names.elements()) for prefix in ANCHORS[2:]))
                if reference is None:
                    reference = (where, signature)
                elif signature != reference[1]:
                    self.add("MATH data", "Anchor structure differs between masters", glyph, where,
                             "Current names {}; reference {}: {}".format(sorted(names), reference[0], sorted(reference[1][0])))
            for anchor in anchors:
                x, y = xy(anchor.position)
                if not finite(x) or not finite(y):
                    self.add("MATH data", "Non-finite anchor", glyph, where, anchor.name, "Error")
                elif max(abs(x), abs(y)) > max(1, self.font.upm) * 10:
                    self.add("MATH data", "Extreme anchor position", glyph, where, "{}: ({}, {})".format(anchor.name, x, y), "Review")
            for prefix in ANCHORS[2:]:
                heights = [float(a.position.y) for a in anchors if a.name.startswith(prefix)]
                if len(heights) != len(set(heights)):
                    self.add("MATH data", "Duplicate MATH kern heights", glyph, where,
                             "{}: {}. Plugin sorts these by height; equal heights need review.".format(prefix, heights), "Error")
        relation = base_of(glyph.name)
        if relation:
            base = self.glyphs.get(relation[0])
            if base is None:
                self.add("MATH data", "Missing base", glyph, "", relation[0], "Error")
            elif ".ssty" in glyph.name and bool(glyph.userData.get(EXTENDED, False)) != bool(base.userData.get(EXTENDED, False)):
                self.add("MATH data", "Extended-shape flag differs", glyph, "", "Base: " + base.name)
            if base is not None and glyph.name.endswith((".ssty1", ".ssty2")):
                suffix = glyph.name[-6:]
                source_data = self.data(base, "MATH data", glyph, "Base " + base.name)
                for key in ("hVariants", "vVariants"):
                    try:
                        expected = [re.sub(r"\.ssty[12]$", "", ref_name(v)) + suffix for v in items(source_data.get(key, []))]
                        actual = [ref_name(v) for v in items(data.get(key, []))]
                        if actual != expected:
                            self.add("MATH data", "Ssty variants differ from recipe", glyph, key,
                                     "Current={!r}; expected={!r}".format(actual, expected))
                        for name in expected:
                            if name not in self.glyphs:
                                self.add("MATH data", "Missing expected ssty variant", glyph, key, name, "Error")
                    except Exception as error:
                        self.failed("MATH data", glyph, key, error)
        for key in ("hAssembly", "vAssembly"):
            if data.get(key):
                self.add("MATH data", "Legacy glyph-level assembly", glyph, key,
                         "Assembly is stored on the glyph; the current source convention is master-layer assemblies", "Review")

    def recipes(self, glyph):
        relation = base_of(glyph.name)
        if relation and relation[0] not in self.glyphs:
            self.add("Recipes", "Missing base", glyph, "", relation[0], "Error")
        root = re.sub(r"\.ssty[12]$", "", glyph.name)
        siblings = [root + ".ssty1", root + ".ssty2"]
        if any(n in self.glyphs for n in siblings):
            for name in siblings:
                if name not in self.glyphs:
                    self.add("Recipes", "Missing script-size sibling", glyph, "", name, "Error")
        upright = re.sub(r"bolditalic-math|italic-math|bold-math", "", glyph.name)
        if upright != glyph.name and upright not in self.glyphs:
            self.add("Recipes", "Missing upright counterpart", glyph, "", upright, "Error")
        if "bolditalic-math" in glyph.name:
            italic = glyph.name.replace("bolditalic-math", "italic-math")
            if italic not in self.glyphs:
                self.add("Recipes", "Missing italic counterpart", glyph, "", italic, "Error")
        if upright == glyph.name and glyph.category == "Letter":
            stem, dot, suffix = glyph.name.partition(".")
            styles = [stem + style + (dot + suffix if dot else "") for style in ("italic-math", "bold-math", "bolditalic-math")]
            if any(name in self.glyphs for name in styles):
                for name in styles:
                    if name not in self.glyphs:
                        self.add("Recipes", "Incomplete style family", glyph, "", name + " is absent; confirm it is intended", "Review")
        if not any(s in glyph.name for s in ("italic-math", "bold-math", ".ssty")):
            return
        if ".ssty" in glyph.name and not glyph.name.endswith((".ssty1", ".ssty2")):
            self.failed("Recipes", glyph, "", "Existing generator expects a terminal .ssty1/.ssty2 suffix")
            return
        if glyph.name in self.unsafe:
            self.failed("Recipes", glyph, "", "Broken component dependencies; regeneration skipped")
            return
        if self.recipe is None:
            self.recipe = load_neighbor("mathboldsanditalics.py")
        module = self.recipe
        previous_font = module.font
        originals = {}
        details = io.StringIO()
        related = {glyph.name, glyph.name.replace(".ssty1", "").replace(".ssty2", "")}
        for name in list(related):
            related.update(name.replace(s, "") for s in ("bolditalic-math", "italic-math", "bold-math"))
            related.add(name.replace("bolditalic-math", "italic-math"))
        try:
            module.font = self.font
            for name in sorted(related):
                source = self.font.glyphs[name]
                if source is not None:
                    originals[name] = source
                    self.font.glyphs[name] = source.copy()
            target = self.font.glyphs[glyph.name]
            plan = module.sstyMathPlan(target)
            for problem in ((plan["issues"] if plan else []) + module.sstyComponentIssues(target) + module.sstySpacingIssues(target)):
                self.add("Recipes", "Recipe metadata differs", glyph, "", problem)
            before = module.checkedGlyphSnapshot(target)
            with redirect_stdout(io.StringIO()):
                module._populateBoldItalicLayers(target)
                module.repairGlyphCompatibility(target)
            after = module.checkedGlyphSnapshot(target)
            with redirect_stdout(details):
                changes = module.reportMathDifferences(before, after)
            if changes:
                self.add("Recipes", "Generated glyph differs", glyph, "All relevant layers",
                         "{} differences; recipe tolerance is 1 unit.\n{}".format(changes, details.getvalue()))
            self.stats["Regenerated glyphs"] += 1
        finally:
            for name, original in originals.items():
                self.font.glyphs[name] = original
            module.font = previous_font

    def report(self):
        lines = ["PENNSTANDER MATH SOURCE AUDIT", "Font: " + str(self.font.familyName),
                 "Groups: " + ", ".join(g for g in GROUPS if g in self.groups),
                 "Scope: {} glyphs; grid: {} positions per varying axis; geometry tolerance: {:g} units".format(len(self.names), self.density, self.tolerance),
                 "All checks used a detached source snapshot. No export or live-font changes.",
                 "Geometry is approximate. Bracket transitions and smart-source internal axes are not sampled.",
                 "Failed/skipped checks do not count as passes.", ""]
        counts = Counter(row["severity"] for row in self.issues)
        lines.append("Results: " + ", ".join("{} {}".format(counts[s], s) for s in ("Error", "Warning", "Review", "Skipped")))
        lines.extend("{}: {}".format(key, value) for key, value in sorted(self.stats.items()))
        for issue in self.issues:
            lines.append("\n[{severity}] {group} / {check}\n/{glyph} — {location}\n{detail}".format(**issue))
        return "\n".join(lines)
