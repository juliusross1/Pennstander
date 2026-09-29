# MenuTitle: Copy Assemblies
"""Copy master-layer MATH assemblies between selected glyphs in Glyphs 3/4."""

from copy import deepcopy
import re


DATA_KEY = "com.nagwa.MATHPlugin.variants"
ASSEMBLIES = ("hAssembly", "vAssembly")
BASE_SUFFIX = re.compile(r"\.(ssty\d*|alt\d*|ss\d+)(?=\.|$)")


def source_choices(font, selected_names):
    """Include existing bases, stripping the rightmost recognised suffix first."""
    names = list(dict.fromkeys(selected_names))
    for selected in selected_names:
        name = selected
        while True:
            matches = list(BASE_SUFFIX.finditer(name))
            if not matches:
                break
            suffix = matches[-1]
            name = name[:suffix.start()] + name[suffix.end():]
            if font.glyphs[name] is not None and name not in names:
                names.append(name)
    return names


def default_source(font, selected_names):
    """Prefer the closest shared base, otherwise the first inferred base."""
    if not selected_names:
        return None
    chains = [source_choices(font, [name]) for name in selected_names]
    bases = list(dict.fromkeys(name for chain in chains for name in chain[1:]))
    return next((name for name in bases if all(name in chain for chain in chains)),
                bases[0] if bases else selected_names[0])


def copy_plans(font, source_name, target_names):
    """Validate the complete batch before starting any writes."""
    names = list(dict.fromkeys(target_names))
    if not names:
        raise ValueError("Check at least one target glyph.")
    plans = []
    for name in names:
        try:
            plans.append(copy_plan(font, source_name, name))
        except Exception as error:
            raise ValueError("{}: {}".format(name, error)) from error
    return plans


def copy_parts(parts):
    """Detach arrays and Glyphs references from the source's stored records."""
    if isinstance(parts, (str, bytes)) or hasattr(parts, "keys"):
        raise ValueError("Assembly must be a list of parts.")
    result = []
    for part in parts:
        if isinstance(part, (str, bytes)) or hasattr(part, "keys"):
            raise ValueError("Assembly part must be a record.")
        fields = list(part)
        if len(fields) != 4:
            raise ValueError("Assembly parts must have four fields.")
        reference = getattr(fields[0], "glyph", None)
        if reference is not None:
            fields[0] = reference.name
        result.append(deepcopy(fields))
    return result


def copy_plan(font, source_name, target_name):
    """Preflight every master before any writes; retain originals for rollback."""
    if source_name == target_name:
        raise ValueError("Choose different source and target glyphs.")
    source, target = font.glyphs[source_name], font.glyphs[target_name]
    if source is None or target is None:
        raise ValueError("The source or target glyph no longer exists. Refresh selection.")
    plan = []
    for master in font.masters:
        source_layer = source.layers[master.id]
        target_layer = target.layers[master.id]
        if source_layer is None or target_layer is None:
            raise ValueError("{}: source or target master layer is missing.".format(master.name))
        source_data = source_layer.userData.get(DATA_KEY, {})
        original = target_layer.userData.get(DATA_KEY)
        if not hasattr(source_data, "keys") or (original is not None and not hasattr(original, "keys")):
            raise ValueError("{}: malformed MATH metadata.".format(master.name))
        updated = dict(original) if original is not None else {}
        counts = []
        for key in ASSEMBLIES:
            try:
                if key in source_data:
                    updated[key] = copy_parts(source_data[key])
                else:
                    updated.pop(key, None)
            except Exception as error:
                raise ValueError("{} / {}: {}".format(master.name, key, error))
            counts.append(len(updated.get(key, [])))
        plan.append((master, target_layer, original, updated, counts))
    if not plan:
        raise ValueError("The font has no masters.")
    return target, plan


def apply_plan(target, plan):
    apply_plans([(target, plan)])


def apply_plans(plans):
    """Undo grouping per target; roll back the whole batch on a write failure."""
    written, started = [], []
    try:
        for target, plan in plans:
            target.beginUndo()
            started.append(target)
            for master, layer, original, updated, counts in plan:
                if original is None and not updated:
                    continue
                written.append((layer, original))
                layer.userData[DATA_KEY] = updated
    except Exception:
        for layer, original in reversed(written):
            if original is None:
                if DATA_KEY in layer.userData:
                    del layer.userData[DATA_KEY]
            else:
                layer.userData[DATA_KEY] = original
        raise
    finally:
        for target in reversed(started):
            target.endUndo()


class CopyAssembliesWindow:
    def __init__(self):
        import vanilla
        self.font = None
        self.names = []
        self.source_names = []
        self.w = vanilla.FloatingWindow((620, 620), "Copy Assemblies")
        self.w.info = vanilla.TextBox((15, 12, -15, 38),
            "The inferred base is the default source. Check the selected glyphs you want to copy to. "
            "Both assembly directions are copied across every font master.")
        self.w.sourceLabel = vanilla.TextBox((15, 64, 65, 20), "Source")
        self.w.source = vanilla.PopUpButton((85, 60, -110, 25), [], callback=self.targets_changed)
        self.w.refresh = vanilla.Button((-95, 60, 80, 25), "Refresh", callback=self.refresh)
        self.w.targetLabel = vanilla.TextBox((15, 105, 300, 20), "Targets — source is always excluded")
        self.w.allTargetsButton = vanilla.Button((-185, 100, 80, 25), "All", callback=self.select_all)
        self.w.noTargetsButton = vanilla.Button((-95, 100, 80, 25), "None", callback=self.select_none)
        self.w.targetsList = vanilla.List((15, 135, -15, 175), [], columnDescriptions=[
            {"title": "Copy", "key": "checked", "width": 45, "editable": True,
             "cell": vanilla.CheckBoxListCell()},
            {"title": "Glyph", "key": "name", "width": 520, "editable": False},
        ], editCallback=self.targets_changed)
        self.w.previewLabel = vanilla.TextBox((15, 327, -15, 20), "Result on each checked target (part counts)")
        self.w.masters = vanilla.List((15, 352, -15, 125), [], columnDescriptions=[
            {"title": "Master", "key": "master", "width": 340},
            {"title": "Horizontal", "key": "horizontal", "width": 110},
            {"title": "Vertical", "key": "vertical", "width": 110},
        ])
        self.w.warning = vanilla.TextBox((15, 489, -15, 38),
            "Replaces every checked target’s assemblies. A missing source assembly clears the target’s. "
            "Outlines, variants and other MATH settings stay unchanged.")
        self.w.copyAssembliesButton = vanilla.Button((15, 534, -15, 32), "Copy to Checked Targets", callback=self.copy)
        self.w.status = vanilla.TextBox((15, 577, -15, 35), "")
        self.refresh(None)
        self.w.open()

    def refresh(self, sender):
        from GlyphsApp import Glyphs
        self.font = Glyphs.font
        self.names = list(dict.fromkeys(layer.parent.name for layer in self.font.selectedLayers)) if self.font else []
        self.source_names = source_choices(self.font, self.names) if self.font else []
        self.w.source.setItems(self.source_names)
        source = default_source(self.font, self.names) if self.font else None
        if source is not None:
            self.w.source.set(self.source_names.index(source))
        self.w.targetsList.set([{"name": name, "checked": name != source} for name in self.names])
        self.preview(None)

    def choices(self):
        if not self.names or not self.source_names:
            return None, []
        source = self.source_names[self.w.source.get()]
        return source, [row["name"] for row in self.w.targetsList.get()
                        if row["checked"] and row["name"] != source]

    def current_plan(self):
        from GlyphsApp import Glyphs
        if self.font is None:
            raise ValueError("Open a font and select a target glyph, then Refresh.")
        if Glyphs.font != self.font:
            raise ValueError("The active font changed. Refresh to use its selection.")
        if not self.names:
            raise ValueError("Select a target glyph, then click Refresh.")
        if len(self.source_names) < 2:
            raise ValueError("No existing base found. Select another source glyph and Refresh.")
        return copy_plans(self.font, *self.choices())

    def targets_changed(self, sender):
        source, targets = self.choices()
        rows = self.w.targetsList.get()
        if any(row["name"] == source and row["checked"] for row in rows):
            for row in rows:
                if row["name"] == source:
                    row["checked"] = False
            self.w.targetsList.set(rows)
        self.preview(None)

    def select_all(self, sender):
        source, targets = self.choices()
        self.w.targetsList.set([{"name": name, "checked": name != source} for name in self.names])
        self.preview(None)

    def select_none(self, sender):
        self.w.targetsList.set([{"name": name, "checked": False} for name in self.names])
        self.preview(None)

    def preview(self, sender):
        self.w.copyAssembliesButton.enable(False)
        self.w.masters.set([])
        try:
            plans = self.current_plan()
            target, plan = plans[0]
            self.w.masters.set([
                {"master": master.name, "horizontal": counts[0], "vertical": counts[1]}
                for master, layer, original, updated, counts in plan
            ])
            source, destinations = self.choices()
            self.w.status.set("{} → {} targets · {} masters".format(source, len(destinations), len(plan)))
            self.w.copyAssembliesButton.enable(True)
        except Exception as error:
            self.w.status.set(str(error))

    def copy(self, sender):
        from GlyphsApp import Glyphs
        self.w.copyAssembliesButton.enable(False)
        try:
            # Rebuild on click: neither edits nor font switches can stale the plan.
            plans = self.current_plan()
            apply_plans(plans)
            source, destinations = self.choices()
            print("\nCOPY ASSEMBLIES: {} → {}".format(source, ", ".join(destinations)))
            for target, plan in plans:
                print("  /" + target.name)
                for master, layer, original, updated, counts in plan:
                    print("    {} [{}]: horizontal {} parts; vertical {} parts".format(master.name, master.id, *counts))
            self.preview(None)
            self.w.status.set("Copied {} → {} targets across {} masters.".format(source, len(destinations), len(plans[0][1])))
        except Exception as error:
            import traceback
            Glyphs.showMacroWindow()
            traceback.print_exc()
            self.w.status.set("Copy failed: {}".format(error))
            # Refresh or change a picker to revalidate before retrying.


if __name__ == "__main__":
    copyAssembliesWindow = CopyAssembliesWindow()
