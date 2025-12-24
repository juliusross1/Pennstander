# Virtual Masters

PennstanderMath is a variable font.  In addition to the "weight" axis there are two more axes "mwgt" that controls the weight of the bold-math glyphs and boltitalic-math glyphs and a "mslt" axis that controls the "italic-math" and "bolditalic-math" glyphs.  PennstanderMath.glyphs uses virtual masters so these masters only appear for the relevant glyphs.  That is 

Regular (upright and symbols): Have Thin and Black Master
Italic: Have Thin, Black and a master for "Italic" and "ItalicBlack"
Bold: Have Thin, Black and a master for "MathBoldThin" and "MathBoldBlack"
BoldItalic: Have Thin, Black, "Italic", "ItalicBlack", "MathBoldThin" and "MathBoldBlack", ""MathBoldItalicThin" and "MathBoldItalicBlack"

Note that the Thin and Black laters in the "Italic" should be taken from the corresponding upright ones; only the other two axes should be edited.  This is indicated in the Glyphs file by having those glyphs in blue.  You can update the automatic layers using mathboldsanditalics.py.

Further the none of the layers in the Bold-math and BoldItalic-math glyphs are edited themselves and instead are created from the other glyphs using the script mathboldsanditalics.py.   The glyphs are in grey to indicate this.

# Cheap Optical Sizing

Many of the glyphs have an ssty and ssty.  This is a cheap solution made with the weight axis.  These are automatically made so also in gray.  For ssty1 the weight of Thin or ItalicThin is replaced to be 150.  For ssty2 the weight of Thin or ItalicThin is replaced to be 200.  The Black masters are unchanged.   These ssty glyphs can be created using createssty.py and then (re)populated at any point with mathboldsanditalics.py.  Sometimes you need to change the shape order afterwards if you get incompatible masters.  And if you want to make sure the math variants work you can use extendedmathflag.py.

# Bug in Opentype Math Table Plugin

There is some kind of bug at export that occurs with the Opentype Math Table plugin to do with production names.  If that occurs it can be fixed by running removeproductionnames.py on the offending glyphs (often these are the ssty ones)


# Old version

This section refers to version 0.2 and earlier, and does not apply to versions after that

To build the mathematics fonts: run createmasters.py script on PennstanderMath.glyphs Glyphs 3 and then export from Glyphs3.

Notes:

1. PennstanderMath is a variable font, but since the mathematics table does not recognize this we instead use instances.  

2. The script creates a new font with an additional axes that is used for the Bold and Italics mathematics letters.

3. The bold-math and boliditalic-math letters in PennstanderMath are written over by the script (using the upright and italics version of the letters), and thus editing them within PennstanderMath.glyphs has no effect.

4. The exports for PennstanderText/PennstanderMath have the italics axes at 50/100 which is different from the instances used in Grandstander.
