# Virtual Masters

PennstanderMath is a variable font. In addition to the "weight" axis there are two more axes "mwgt" that controls the weight of the bold-math glyphs and boltitalic-math glyphs and a "mslt" axis that controls the "italic-math" and "bolditalic-math" glyphs. PennstanderMath.glyphs uses virtual masters so these masters only appear for the relevant glyphs. That is

Regular (upright and symbols): Have Thin and Black Master

Italic: Have Thin, Black and a master for "Italic" and "ItalicBlack"

Bold: Have Thin, Black and a master for "MathBoldThin" and "MathBoldBlack"

BoldItalic: Have Thin, Black, "Italic", "ItalicBlack", "MathBoldThin" and "MathBoldBlack", ""MathBoldItalicThin" and "MathBoldItalicBlack"

Note that the Thin and Black laters in the "Italic" should be taken from the corresponding upright ones; only the other two axes should be edited. This is indicated in the Glyphs file by having those glyphs in blue. You can update the automatic layers using mathboldsanditalics.py.

Further the none of the layers in the Bold-math and BoldItalic-math glyphs are edited themselves and instead are created from the other glyphs using the script mathboldsanditalics.py. The glyphs are in grey to indicate this.

# Cheap Optical Sizing

`mathboldsanditalics.py` opens a combined **Check Selected / Update Selected** dialog.
**Update Selected** retains the existing update behavior. **Check Selected** scans
only selected italic-math, bold-math, bolditalic-math and ssty glyphs, once each,
using an isolated in-memory font copy. Unrelated glyphs are skipped.
With no applicable selection it prompts you to select glyphs. Each glyph is
checked independently against the current sources; earlier checks do not update
the inputs for later ones. No check result is applied or saved to the open font.

The Macro Panel reports only differing glyphs/layers and errors, comparing decomposed
outlines, anchors, width, and left/right sidebearings, ignoring numeric differences
smaller than 1 unit (differences of exactly 1 unit are still reported).
Equivalent components and paths count as matching; contour order and closed
contour starting points are ignored. Reports include current and expected
values and exact numeric deltas, plus missing/extra layers, contours, and anchors.
Unresolvable components and other failures are reported as errors, not matches,
and checking continues with the next glyph. The final summary counts matching,
different, and failed checks.
Enable **Open tab with all differing glyphs** to show every confirmed
difference in scan order after checking. Matching glyphs and failed checks are
excluded; no tab is opened when there are no confirmed differences.
Checking processes every selected applicable glyph, regardless of the number of
differences found. The optional results tab includes all differing glyphs.
The Macro Panel is not opened automatically. Completion notifications summarise
check or update totals, and the dialog also displays the result. Detailed reports
remain in the Macro Panel for manual inspection.
The dialog shows progress and runs one glyph per UI callback so the Macro Panel
can repaint between glyphs. **Cancel Check** (or closing the dialog) stops the
scan between glyphs without applying changes. Preparing the initial in-memory
font copy and processing an individual complex glyph can still take a moment.

Generation now finishes with a compatibility pass across master and special
layers, using the first font master as the reference. Existing path and node
order is preserved when node counts/types, closure and winding already match.
Only incompatible layouts are candidates for repair using normalized node
positions. Compatible path pairs retain their original start points even when
other paths need repair. This prevents slant or weight differences from causing
false start-point rotations and corrupting ssty interpolation. Components stay
in place. Ambiguous matches, different path counts, or incompatible component
layouts are reported for manual correction; the target's original layers are
restored if an update fails. All repair plans are validated before application.
Check reports existing compatibility problems separately from visual differences,
while regenerated outlines reveal previously distorted ssty glyphs. Structurally
compatible but semantically incorrect node orders still need manual matching;
the script does not infer those from geometry alone.

All `.ssty1` and `.ssty2` glyphs are generated as paths, including upright,
bold, italic and bolditalic styles. The script decomposes a private copy of the
base at its existing axis settings, repairs contour compatibility, then
interpolates outlines, anchors and widths. The light endpoint is 150 for
`.ssty1` and 200 for `.ssty2`; bold styles interpolate along Math Weight.
It does not set component weights to generate ssty glyphs. Existing left, right
and width spacing keys are removed from the ssty glyph and every layer; spacing
comes solely from interpolated outline positions and advance width. The check
reports any remaining spacing keys. Master and
intermediate layers are supported, and remaining components in additional
layers are decomposed. Source glyphs are not modified.

The ssty recipe check reports any remaining components, even when their rendered
outlines match. All outlines, anchors, metrics and MATH metadata still undergo
the usual checks. Results can differ from the earlier live-component workflow.

For `.ssty1` and `.ssty2`, checking also compares horizontal and vertical MATH
variant lists against the original glyph's lists, with every target changed to
the matching script-size suffix. Missing targets are problems; the checker does
not fall back to the original size. Assemblies are retained and must match the
base glyph, including the original part names, extender flags, and connector
lengths. No `.ssty` assembly parts are created or required. Layer assemblies use
the matching base master/coordinate layer, falling back to the associated base
master for extra layers; legacy glyph-level assemblies are also copied.
**Update Selected** applies these metadata corrections along with the outlines.
If required variant targets or base sources are missing, that glyph is left
unchanged and reported; other selected glyphs continue updating.

Many of the glyphs have an ssty and ssty. This is a cheap solution made with the weight axis. These are automatically made so also in gray. For ssty1 the weight of Thin or ItalicThin is replaced to be 150. For ssty2 the weight of Thin or ItalicThin is replaced to be 200. The Black masters are unchanged. These ssty glyphs can be created using createssty.py and then (re)populated at any point with mathboldsanditalics.py. Sometimes you need to change the shape order afterwards if you get incompatible masters. And if you want to make sure the math variants work you can use extendedmathflag.py.

Decomposing the source before interpolation also avoids the Glyphs 4 problem
with smart components at Weight 150/200 and Italic 100. This path-based workflow
now applies to every ssty style. Failed decomposition or ambiguous contour
compatibility is reported, and the target's original layers are restored.

# Bug in Opentype Math Table Plugin

There is some kind of bug at export that occurs with the Opentype Math Table plugin to do with production names. If that occurs it can be fixed by running removeproductionnames.py on the offending glyphs (often these are the ssty ones)

# Old version

This section refers to version 0.2 and earlier, and does not apply to versions after that

To build the mathematics fonts: run createmasters.py script on PennstanderMath.glyphs Glyphs 3 and then export from Glyphs3.

Notes:

1.  PennstanderMath is a variable font, but since the mathematics table does not recognize this we instead use instances.
    
2.  The script creates a new font with an additional axes that is used for the Bold and Italics mathematics letters.
    
3.  The bold-math and boliditalic-math letters in PennstanderMath are written over by the script (using the upright and italics version of the letters), and thus editing them within PennstanderMath.glyphs has no effect.
    
4.  The exports for PennstanderText/PennstanderMath have the italics axes at 50/100 which is different from the instances used in Grandstander.
