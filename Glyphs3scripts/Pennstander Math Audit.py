# MenuTitle: Pennstander Math Audit
"""Read-only source audit for Glyphs 3/4. Keep pennstander_audit alongside this script."""

import importlib.util
import time
import traceback
from collections import Counter
from pathlib import Path


# Reload the helper when the script is rerun after an edit.
helper_path = Path(__file__).resolve().parent / "pennstander_audit" / "__init__.py"
spec = importlib.util.spec_from_file_location("pennstander_source_audit", helper_path)
audit_module = importlib.util.module_from_spec(spec)
exec(compile(helper_path.read_text(), str(helper_path), "exec"), audit_module.__dict__)
Audit, GROUPS = audit_module.Audit, audit_module.GROUPS


class PennstanderAuditWindow:
    def __init__(self):
        import vanilla
        self.steps = None
        self.audit = None
        self.source_font = None
        self.visible = []
        self.last_refresh = 0
        self.finished_state = "Ready"
        self.w = vanilla.FloatingWindow((1000, 780), "Pennstander Math Audit", minSize=(850, 700))
        self.w.introLabel = vanilla.TextBox((15, 12, -15, 34),
            "Choose source checks. The audit uses a private font snapshot; it never edits or exports the open font. "
            "Warnings and review items may describe intentional design choices.")
        descriptions = [
            "1. Structure — layers, references, components, Unicode, production names, feature source",
            "2. Deep interpolation — compatibility, kinks, crossings, counters and geometry outliers",
            "3. Assemblies — master/base consistency, references, overlap, growth and join geometry",
            "4. MATH data — variants, anchors, kerning heights, flags and constants",
            "5. Generated glyphs — family completeness and comparison with the existing recipes",
        ]
        self.check_controls = []
        for index, description in enumerate(descriptions):
            control = vanilla.CheckBox((15, 53 + index * 25, -15, 22), description, value=True)
            setattr(self.w, "groupCheck{}".format(index), control)
            self.check_controls.append(control)
        self.w.scopeLabel = vanilla.TextBox((15, 186, 48, 20), "Scope")
        self.w.scopePopup = vanilla.PopUpButton((65, 182, 235, 25), ["All glyphs (including nonexporting)", "Selected glyphs"])
        self.w.gridLabel = vanilla.TextBox((320, 186, 80, 20), "Axis samples")
        self.w.gridPopup = vanilla.PopUpButton((405, 182, 200, 25), ["3 per axis (up to 27)", "5 per axis (up to 125)", "7 per axis (up to 343)"])
        self.w.toleranceLabel = vanilla.TextBox((630, 186, 150, 20), "Geometry tolerance")
        self.w.toleranceEdit = vanilla.EditText((780, 182, 65, 24), "2")
        self.w.unitLabel = vanilla.TextBox((854, 186, 65, 20), "units")
        self.w.scopeNoteLabel = vanilla.TextBox((15, 214, -15, 34),
            "Font-wide checks run with Structure/MATH. Assembly bases are checked too. Interpolation also samples named instances "
            "and intermediate-layer neighbours. Recipe comparisons use a fixed 1-unit tolerance.", sizeStyle="small")
        self.w.runAuditButton = vanilla.Button((15, 256, 170, 30), "Run Selected Tests", callback=self.start)
        self.w.cancelAuditButton = vanilla.Button((195, 256, 110, 30), "Cancel", callback=self.cancel)
        self.w.cancelAuditButton.enable(False)
        self.w.progressIndicator = vanilla.ProgressBar((325, 266, -15, 12), isIndeterminate=True)
        self.w.statusLabel = vanilla.TextBox((15, 298, -15, 35), "Ready")
        self.w.filterLabel = vanilla.TextBox((15, 340, 45, 20), "Show")
        self.w.severityPopup = vanilla.PopUpButton((60, 336, 145, 25), ["All findings", "Error", "Warning", "Review", "Skipped"], callback=self.filter_results)
        self.w.groupPopup = vanilla.PopUpButton((215, 336, 150, 25), ["All groups"] + list(GROUPS), callback=self.filter_results)
        self.w.searchEdit = vanilla.EditText((375, 336, -15, 24), "", placeholder="Filter glyph, check or details", callback=self.filter_results)
        self.w.resultsList = vanilla.List((15, 373, -15, -202), [], columnDescriptions=[
            {"title": "Severity", "key": "severity", "width": 70},
            {"title": "Group", "key": "group", "width": 90},
            {"title": "Glyph", "key": "glyph", "width": 220},
            {"title": "Layer / position", "key": "location", "width": 220},
            {"title": "Finding", "key": "check", "width": 320},
        ], selectionCallback=self.show_details, doubleClickCallback=self.open_selected)
        self.w.detailEditor = vanilla.TextEditor((15, -192, -15, 132), "Select a finding to read its details.", readOnly=True)
        self.w.openSelectedButton = vanilla.Button((15, -45, 175, 28), "Open Selected Findings", callback=self.open_selected)
        self.w.openFilteredButton = vanilla.Button((200, -45, 175, 28), "Open Filtered Glyphs", callback=self.open_filtered)
        self.w.printReportButton = vanilla.Button((385, -45, 175, 28), "Report to Macro Panel", callback=self.print_report)
        self.w.saveReportButton = vanilla.Button((570, -45, 150, 28), "Save Text Report…", callback=self.save_report)
        self.w.bind("close", self.cancel)
        self.w.open()

    def start(self, sender):
        from GlyphsApp import Glyphs
        from PyObjCTools.AppHelper import callLater
        font = Glyphs.font
        groups = [name for name, control in zip(GROUPS, self.check_controls) if control.get()]
        if font is None or not groups:
            self.w.statusLabel.set("Open a font and choose at least one test group.")
            return
        try:
            tolerance = float(self.w.toleranceEdit.get())
            if not audit_module.finite(tolerance) or tolerance <= 0:
                raise ValueError()
        except ValueError:
            self.w.statusLabel.set("Geometry tolerance must be a finite positive number.")
            return
        names = [g.name for g in font.glyphs] if self.w.scopePopup.get() == 0 else list(dict.fromkeys(l.parent.name for l in font.selectedLayers))
        if not names:
            self.w.statusLabel.set("Select at least one glyph or choose All glyphs.")
            return
        self.source_font = font
        self.audit = None
        self.visible = []
        self.w.resultsList.set([])
        self.w.detailEditor.set("Preparing a source snapshot. A large font may take a while to copy.")
        self.w.statusLabel.set("Preparing a private source snapshot…")
        self.finished_state = "Running"
        self.steps = self.run_steps(font, names, groups, (3, 5, 7)[self.w.gridPopup.get()], tolerance)
        self.set_running(True)
        callLater(.05, self.advance, self.steps)

    def run_steps(self, font, names, groups, density, tolerance):
        yield "Copying font; cancellation resumes after the snapshot is ready…"
        working = font.copy()
        self.audit = Audit(working, names, groups, density, tolerance)
        yield from self.audit.run()

    def set_running(self, running):
        self.w.runAuditButton.enable(not running)
        self.w.cancelAuditButton.enable(running)
        for control in self.check_controls + [self.w.scopePopup, self.w.gridPopup, self.w.toleranceEdit]:
            control.enable(not running)
        if running:
            self.w.progressIndicator.start()
        else:
            self.w.progressIndicator.stop()

    def advance(self, steps):
        from PyObjCTools.AppHelper import callLater
        if self.steps is not steps:
            return
        try:
            status = next(steps)
            self.w.statusLabel.set(status)
            if time.monotonic() - self.last_refresh > 1:
                self.filter_results(None)
                self.last_refresh = time.monotonic()
        except StopIteration:
            self.finish("Complete")
        except Exception:
            error = traceback.format_exc()
            if self.audit:
                self.audit.failed("Structure", "", "Audit interrupted", error)
            print(error)
            self.w.detailEditor.set(error)
            self.finish("Failed; partial results")
        else:
            callLater(.01, self.advance, steps)

    def finish(self, state):
        if self.steps:
            self.steps.close()
        self.steps = None
        self.finished_state = state
        self.set_running(False)
        self.filter_results(None)
        counts = Counter(row["severity"] for row in self.audit.issues) if self.audit else Counter()
        self.w.statusLabel.set("{} · {} errors, {} warnings, {} review, {} skipped. Font unchanged.".format(
            state, counts["Error"], counts["Warning"], counts["Review"], counts["Skipped"]))

    def cancel(self, sender):
        if self.steps is not None:
            self.finish("Cancelled; partial results")

    def filter_results(self, sender):
        severity = self.w.severityPopup.get()
        group = self.w.groupPopup.get()
        query = self.w.searchEdit.get().strip().lower()
        self.visible = [row for row in self.audit.issues if
                        (not severity or row["severity"] == ("", "Error", "Warning", "Review", "Skipped")[severity]) and
                        (not group or row["group"] == GROUPS[group - 1]) and
                        (not query or query in " ".join(map(str, row.values())).lower())] if self.audit else []
        self.w.resultsList.set(self.visible)

    def selected_rows(self):
        # Read list order so clicking a column header cannot desynchronise rows.
        rows = self.w.resultsList.get()
        return [rows[i] for i in self.w.resultsList.getSelection() if i < len(rows)]

    def show_details(self, sender):
        rows = self.selected_rows()
        self.w.detailEditor.set("\n\n".join("[{severity}] {group}: {check}\n/{glyph} — {location}\n{detail}".format(**r) for r in rows))

    def open_rows(self, rows):
        from GlyphsApp import Glyphs
        if self.source_font is None or not any(f == self.source_font for f in Glyphs.fonts):
            self.w.detailEditor.set("The source font is no longer open.")
            return
        names = list(dict.fromkeys(r["glyph"] for r in rows if r["glyph"] and self.source_font.glyphs[r["glyph"]] is not None))
        if names:
            self.source_font.newTab("".join("/" + name for name in names))
        else:
            self.w.detailEditor.set("These findings are font-wide or refer only to missing glyphs.")

    def open_selected(self, sender):
        self.open_rows(self.selected_rows())

    def open_filtered(self, sender):
        self.open_rows(self.visible)

    def report_text(self):
        return "Status: {}\n\n{}".format(self.finished_state, self.audit.report())

    def print_report(self, sender):
        if self.audit:
            from GlyphsApp import Glyphs
            Glyphs.showMacroWindow()
            print(self.report_text())

    def save_report(self, sender):
        if self.audit:
            from GlyphsApp import GetSaveFile
            destination = GetSaveFile("Save audit report", "Pennstander-source-audit.txt", filetypes=["txt"])
            if destination:
                Path(destination).write_text(self.report_text(), encoding="utf-8")


if __name__ == "__main__":
    pennstanderAuditWindow = PennstanderAuditWindow()
