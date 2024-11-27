# Pennstander
An opentype mathematics font based on Grandstander by Tyler Finck, aimed at LuaLaTeX and ConTeXt

![A sample of the font at each of the different weights](samples/fontweights.png)

## Features
Latin and Greek lower and upper case in upright and oblique/italics
Doublestruck upper case
Integrals including display and extended
Mathematical Operators including display
Mathematics Accents
Arrows and stackers
Radicals
Mathematical symbols

## ConTeXt
Sample usage for ConTeXt MKIV

\usetypescriptfile[type-imp-pennstander]
\setupmathfractions[symbol="E000] %recommended but optional
\setupalign[profile] %recommended but optional
\setupinterlinespace[14pt] %recommended but optional
\setupbodyfont[Pennstander-Thin] %replace 'Thin' with 'ExtraLight','Light',...
\starttext
\startformula
\int_a^b \frac{df}{dx} dx = f(b) - f(a)
\stopformula
\stoptext

## LuaLaTeX
