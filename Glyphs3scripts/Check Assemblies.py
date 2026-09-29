# MenuTitle: Check Assemblies
"""Report MATH assembly issues without editing the font.

Only selected glyphs and their required bases are visited. Assemblies live on
font master layers. .ssty/.alt use their immediate base; .ssXX may differ.
"""

import math
import re


DATA_KEY = "com.nagwa.MATHPlugin.variants"
DIRECTIONS = (("hAssembly", "horizontal"), ("vAssembly", "vertical"))
SUFFIX = re.compile(r"\.(ssty\d*|alt\d*|ss\d+)(?=\.|$)")
MISSING = ("missing",)


def base_relationship(name):
    matches = list(SUFFIX.finditer(name))
    if not matches:
        return None
    match = matches[-1]
    base = name[:match.start()] + name[match.end():]
    return base, not match.group(1).startswith("ss") or match.group(1).startswith("ssty")


def sequence(value):
    # Also accepts the NSArray proxies returned by Glyphs/PyObjC.
    if isinstance(value, (str, bytes)) or hasattr(value, "keys"):
        return None
    try:
        return list(value)
    except TypeError:
        return None


def snapshot(value):
    """Immutable comparison value, including malformed and extra fields."""
    if hasattr(value, "keys"):
        return ("mapping", tuple(sorted((str(k), snapshot(value[k])) for k in value.keys())))
    items = sequence(value)
    if items is not None:
        return tuple(snapshot(item) for item in items)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def reference_name(value):
    reference = getattr(value, "glyph", None)
    if reference is not None:
        return reference.name
    return value if isinstance(value, str) and value else None


def valid_number(value):
    if isinstance(value, (str, bytes, bool)):
        return False
    try:
        return math.isfinite(value) and 0 <= value <= 65535
    except (TypeError, ValueError, OverflowError):
        return False


def check_assemblies(font, selected_names):
    """Return (issues by glyph name, visited names); never assign font data."""
    issues, visited, cache = {}, [], {}

    def report(name, message):
        messages = issues.setdefault(name, [])
        if message not in messages:
            messages.append(message)

    def read_assembly(glyph, master, key, direction):
        label = "{} [{}], {} assembly".format(master.name, master.id, direction)
        layer = glyph.layers[master.id]
        if layer is None:
            report(glyph.name, "{}: master layer is missing".format(label))
            return ("missing layer",)
        data = layer.userData.get(DATA_KEY, {})
        if not hasattr(data, "get"):
            report(glyph.name, "{}: malformed MATH data {!r}".format(label, data))
            return ("malformed data", snapshot(data))
        if key not in data:
            return MISSING
        raw = data[key]
        parts = sequence(raw)
        if parts is None:
            report(glyph.name, "{}: expected a list of parts, found {!r}".format(label, raw))
            return ("malformed assembly", snapshot(raw))
        # An empty list and an absent assembly both mean no assembly.
        if not parts:
            return MISSING
        normalized = []
        for index, part in enumerate(parts, 1):
            location = "{}, part {}".format(label, index)
            fields = sequence(part)
            if fields is None:
                report(glyph.name, "{}: malformed record {!r}".format(location, part))
                normalized.append(snapshot(part))
                continue
            if len(fields) != 4:
                report(glyph.name, "{}: expected 4 fields (glyph, extender, start, end), found {}: {!r}".format(location, len(fields), fields))
            if fields:
                name = reference_name(fields[0])
                if name is None:
                    report(glyph.name, "{}: invalid glyph reference {!r}".format(location, fields[0]))
                else:
                    fields[0] = name
                    target = font.glyphs[name]
                    if target is None:
                        report(glyph.name, "{}: referenced glyph {!r} does not exist".format(location, name))
                    elif not target.export:
                        report(glyph.name, "{}: referenced glyph {!r} has export disabled".format(location, name))
            if len(fields) > 1 and (not isinstance(fields[1], (int, float)) or fields[1] not in (0, 1)):
                report(glyph.name, "{}: extender flag must be 0 or 1, found {!r}".format(location, fields[1]))
            for offset, title in ((2, "start connector"), (3, "end connector")):
                if len(fields) > offset and not valid_number(fields[offset]):
                    report(glyph.name, "{}: {} must be a finite number from 0 to 65535, found {!r}".format(location, title, fields[offset]))
            normalized.append(snapshot(fields))
        return ("parts", tuple(normalized))

    def differences(name, context, actual, expected):
        if actual == expected:
            return
        if actual[0] != "parts" or expected[0] != "parts":
            report(name, "{}: current={!r}; expected={!r}".format(context, actual, expected))
            return
        left, right = actual[1], expected[1]
        if len(left) != len(right):
            report(name, "{}: part count {}; expected {}".format(context, len(left), len(right)))
        for index in range(max(len(left), len(right))):
            a = left[index] if index < len(left) else MISSING
            b = right[index] if index < len(right) else MISSING
            if a != b:
                report(name, "{}, part {}: current={!r}; expected={!r} (glyph, extender, start, end)".format(context, index + 1, a, b))

    def visit(name):
        if name in cache:
            return
        glyph = font.glyphs[name]
        if glyph is None:
            return
        relationship = base_relationship(name)
        base = None
        if relationship:
            base_name, compare = relationship
            base = font.glyphs[base_name]
            if base is None:
                report(name, "Base glyph {!r} is missing".format(base_name))
            else:
                visit(base_name)
        visited.append(name)
        values = {}
        cache[name] = values
        for master in font.masters:
            for key, direction in DIRECTIONS:
                values[(master.id, key)] = read_assembly(glyph, master, key, direction)
        masters = list(font.masters)
        if masters:
            first = masters[0]
            for master in masters[1:]:
                for key, direction in DIRECTIONS:
                    differences(name, "{} assembly: master {} [{}] versus {} [{}]".format(direction, master.name, master.id, first.name, first.id),
                                values[(master.id, key)], values[(first.id, key)])
        if base is not None and compare:
            for master in masters:
                for key, direction in DIRECTIONS:
                    differences(name, "{} assembly on {} [{}], versus base {}".format(direction, master.name, master.id, base.name),
                                values[(master.id, key)], cache[base.name][(master.id, key)])

    for name in dict.fromkeys(selected_names):
        visit(name)
    # Keep report and tab in base-first check order.
    return {name: issues[name] for name in visited if name in issues}, visited


class CheckAssembliesWindow:
    def __init__(self):
        import vanilla
        self.w = vanilla.FloatingWindow((460, 205), "Check Assemblies")
        self.w.info = vanilla.TextBox((15, 12, -15, 55),
            "Check selected glyphs and their bases. Detailed results appear in the Macro Panel. The font is not modified.")
        self.w.openTab = vanilla.CheckBox((15, 77, -15, 22),
            "Open a tab with all glyphs that have issues", value=True)
        self.w.check = vanilla.Button((15, 112, -15, 30), "Check Selected", callback=self.run)
        self.w.status = vanilla.TextBox((15, 154, -15, 40), "Ready")
        self.w.open()

    def run(self, sender):
        from GlyphsApp import Glyphs
        font = Glyphs.font
        if font is None:
            self.w.status.set("Open a font first.")
            return
        names = list(dict.fromkeys(layer.parent.name for layer in font.selectedLayers))
        if not names:
            self.w.status.set("Select glyphs first.")
            return
        self.w.check.enable(False)
        try:
            Glyphs.showMacroWindow()
            print("\nCHECK ASSEMBLIES — {}".format(font.familyName))
            print("{} selected glyphs; required bases are checked first.".format(len(names)))
            print("Master layers only. .ssXX may differ from their base. Empty/absent assemblies are equivalent.")
            issues, visited = check_assemblies(font, names)
            for name, messages in issues.items():
                print("\n/{}".format(name))
                for message in messages:
                    print("  - " + message)
            summary = "{} glyphs checked; {} glyphs with issues.".format(len(visited), len(issues))
            print("\n" + summary + " Font unchanged.")
            self.w.status.set(summary)
            if self.w.openTab.get() and issues:
                font.newTab("".join("/" + name for name in issues))
        except Exception:
            import traceback
            traceback.print_exc()
            self.w.status.set("Check failed; see the Macro Panel for details.")
        finally:
            self.w.check.enable(True)


if __name__ == "__main__":
    checkAssembliesWindow = CheckAssembliesWindow()
