# Pennstander
An Opentype mathematics font based on [Grandstander](https://etceteratype.co/grandstander) by Tyler Finck, aimed at LuaLaTeX and ConTeXt.   Beta version, comments/bug reports/advice welcome.

![A sample of the font at each of the different weights](samples/fontweights.png)

## Features
Latin and Greek lower and upper case in upright and oblique/italics

Doublestruck upper case

[Integrals including display and extended](samples/integrals.png)

Mathematical Operators including display

Brackets including multiple sizes and extended

Mathematical accents

Arrows and stackers

Radicals

Mathematical symbols (many available, if you need/want something that is missing report a bug and I will try and create it for you)

## ConTeXt
Sample usage for ConTeXt MKIV
```
\usetypescriptfile[type-imp-pennstander]
\setupmathfractions[symbol="E000]
\setupbodyfont[Pennstander-Thin]
% Replace 'Thin' with 'ExtraLight'/'Light'/'Regular'/'Medium'/'SemiBold'/'Bold'/'ExtraBold'/'Black'
% (some math symbols do not look good at Bold/ExtraBold/Black so use with care)
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
%% 'Light'/'Medium' 
%% 'Regular'/'SemiBold'
%% 'Medium'/'Bold'
%% 'SemiBold'/'ExtraBold'
%% 'Bold'/'Black'  (some math symbols do not look good at Bold/ExtraBold/Black so use with care)
%% 'ExtraBold'/'Black'
%% 'Black'/'Black'

\setmathfont[
script-font  = PennstanderMath-Thin-script.otf,       % optional, acts as cheap optical sizing
sscript-font  = PennstanderMath-Thin-sscript.otf,     % optional, acts as cheap optical sizing
]{PennstanderMath-Thin.otf}
%% Replace 'Thin' with 'ExtraLight'/'Light'/... to match the text font above


\begin{document}
Here is some {\bf bold}, some {\it italics} and some {\bf bolditalics} and an equation

\[ \int_a^b {\bf f}'(x) dx= {\bf f}(b) - {\bf f}(a)\]
\end{document}
```
