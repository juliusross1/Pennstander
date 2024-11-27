# Pennstander
An opentype mathematics font based on Grandstander by Tyler Finck, aimed at LuaLaTeX and ConTeXt.   Beta version, comments/bugs/advice welcome.

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
```
\usetypescriptfile[type-imp-pennstander]
\setupmathfractions[symbol="E000]
\setupbodyfont[Pennstander-Thin]
\setupalign[profile]
\setupinterlinespace[14pt]
\starttext
Here is some {\bf bold} and some {\it italics} and an equation
\startformula
\int_a^b \frac{d{\bf f}}{dx} dx = {\bf f}(b) - {\bf f}(a)
\stopformula
\stoptext
```

## LuaLaTeX
Sample usage
```
\documentclass[12pt]{article}

\usepackage{unicode-math}

\setmainfont[
BoldFont =Pennstander-Light.otf,   
ItalicFont = Pennstander-ItalicThin.otf, 
BoldItalicFont = Pennstander-ItalicLight.otf
]
{Pennstander-Thin.otf}
%% Replace 'Thin'/'Light' in the above with one of the following to match the 
%% mathematics font below
%% 'ExtraLight'/'Regular' 
%%'Light'/'Medium' 
%% 'Regular'/'Bold'
%% 'SemiBold'/'ExtraBold'
%% 'Bold'/'Black'
%% 'ExtraBold'/'Black'
%% 'Black'/'Black'

\setmathfont[
script-font  = PennstanderMath-Thin-script.otf,
sscript-font  = PennstanderMath-Thin-sscript.otf,
]{PennstanderMath-Thin.otf}
%% Replace 'Thin' with 'ExtraLight'/'Light'/... to match the text font above


\begin{document}
Here is some {\bf bold}, some {\it italics} and some {\bf bolditalics} and an equation

\[ \int_a^b {\bf f}'(x) dx= {\bf f}(b) - {\bf f}(a)\]
\end{document}
```
