# Pennstander Math Audit

Run **Pennstander Math Audit** in Glyphs 3/4. Keep the `pennstander_audit`
folder beside `Pennstander Math Audit.py`. Group 5 also needs the existing
`mathboldsanditalics.py` beside the script. FontTools, when installed in Glyphs,
provides parsing of stored feature source; its absence is reported as Skipped.

Choose any combination of five groups, All glyphs or Selected glyphs, a sampling
density, and a geometry tolerance. The default 3 samples per varying font axis
gives 27 combinations for this font; 5 and 7 give 125 and 343. Named static
instance coordinates and intermediate-layer locations/neighbours are added.
Suspicious samples trigger one extra level of nearby samples along each axis.
Master/virtual-master coordinates define the sampled axis bounds.

The audit copies the font once. All decomposition, overlap removal,
interpolation, metrics synchronization and recipe regeneration use that private
snapshot. It neither exports nor changes the open source font. The sole optional
document action is opening tabs with glyphs from the results. Saving a report
writes only the text file chosen in the save dialog.

## Checks

1. **Structure:** master layers/IDs, coordinate axes and duplicate locations,
   component references/cycles/transforms/decomposition, metrics references,
   possible metrics cycles and stale calculated metrics, exported empty glyphs,
   invalid/duplicate Unicode, production-name collisions and suspicious names,
   stored feature/class/prefix parsing. Font-wide checks run even in selection
   mode; collisions are reported against selected glyphs.
2. **Interpolation:** path/component structure, winding, suspicious contour
   pairing and cyclic starts, source geometry, and a cross product of sampled
   axis positions. Measures visible contour structure after overlap removal,
   proper self-crossings, smooth-node kinks over 5 degrees, tiny contours, short
   segments and substantial area/bounds/width outliers. All source master and
   intermediate layers establish the comparison baseline.
3. **Assemblies:** horizontal/vertical records on every master, master
   consistency, recursive base consistency (.ssty/.alt; .ssXX may differ),
   missing/nonexporting parts, part advance versus connector lengths,
   MinConnectorOverlap, extender growth and achievable-size gaps. Examines
   constructions with 0–4 repeats of each extender, including newly adjacent
   parts when extenders are omitted and self-joins when repeated. Compares join
   cross-sections at minimum, midpoint and maximum permitted overlaps. Required
   bases are checked even outside the selection. Part geometry uses each master.
4. **MATH data:** variant references, duplicates and size ordering on each
   master; ssty variant recipes and expected targets; duplicate/unknown/non-finite
   MATH anchors; master anchor structure; duplicate MATH kern heights; extended
   shape flags; legacy glyph-level assemblies; constant types/ranges and likely
   outliers; script scaling order; rule thickness compared with the minus glyph.
   Missing stored constants are Review items because plugin defaults may apply.
5. **Recipes:** missing bases, incomplete ssty pairs/style families, missing
   upright/italic counterparts, then the existing Pennstander generator on
   disposable glyph copies. Compares outlines, anchors, spacing and layers with
   the existing 1-unit tolerance, and reports ssty component/metrics/MATH issues.
   Copies are restored after every glyph, including when a recipe fails, so
   previous checks do not change later checks' inputs.

## Results and limitations

Filter by severity, group or search text; select a row to see full details.
Double-click or use **Open Selected Findings** to inspect glyphs; **Open Filtered
Glyphs** opens every glyph in the current filter. Font-wide findings have no
glyph to open. Reports include settings, counts and completed sample totals.

**Error** denotes invalid source data or a violated consistency rule.
**Warning** denotes likely trouble. **Review** denotes a heuristic/design choice.
**Skipped** means a check could not complete, including unavailable APIs or
dependencies; it is never counted as a pass. Cancellation keeps partial results.
The UI yields between glyphs and interpolation samples. Copying a large font,
processing an individual complicated shape, or regenerating one glyph can still
take time before cancellation is handled.

This is a source audit, not proof of export or rendering correctness. In
particular:

- Samples do not cover every point in the continuous designspace. Bracket-layer
  transitions and smart-source internal axes are explicitly skipped; font-axis
  samples still exercise smart components through their consuming glyphs.
  Structural coordinate checks recognise both font axes and the glyph's own
  axes (`glyph.axes` in Glyphs 4, `smartComponentAxes` in Glyphs 3). Smart-axis
  coordinates are checked for finite values and retained when identifying
  duplicate locations; font-axis bounds are not applied to smart axes.
- Curves are flattened to approximately 0.5 units (with a recursion limit).
  Proper self-crossings are tested within individual contours. Collinear
  overlaps/tangencies and arbitrary mathematical collisions are not certified.
- Join cross-sections diagnose likely seams; they are not pixel-rendered proofs.
  Bbox advances follow the current MATH plugin's source convention. Actual
  compiled glyph IDs, flags, advances and layout-engine behavior are not tested.
- Metrics dependency cycles are conservative glyph-level warnings; separate
  left/right/width dependencies can make some of them harmless.
- A missing stored metrics reference is **Review** (unused/stale) where Glyphs
  reports that automatic alignment controls that metric on the layer. It remains
  **Error** on unaligned layers. Width and sidebearing alignment are distinguished
  when the API supports it; a component's alignment checkbox alone is not enough.
  Auto-controlled metrics are excluded from stale-key synchronization comparisons.
- Feature parsing uses stored source and does not regenerate automatic features,
  resolve external includes, compile features or run substitutions. Parse
  failures can reflect Glyphs-specific syntax. Production-name checks use source
  names/settings, not final export overrides.
- MATH kern checks follow the installed plugin convention of sorting corner
  anchor heights numerically. No arbitrary anchor is required on every glyph.
  Italic correction magnitude is not checked.
- Family inventory only infers expectations from existing members and the
  established Pennstander recipes. It does not require all mathematical styles
  for every symbol or validate the design correctness of a shared recipe.

Headless regression checks: `python3 -B -m unittest discover -s tests -p test_source_audit.py`.
Native Glyphs interpolation, Cocoa controls and plugin behavior require an
in-app run; the headless tests use stand-ins for these objects.
