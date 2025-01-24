# Pennstander
A text and mathematics font based on [Grandstander](https://etceteratype.co/grandstander), aimed at LuaLaTeX and ConTeXt.   Beta version, comments/bug reports/advice welcome.

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/fontweights.png" width="650">

## Features
[Latin and Greek lower and upper case in upright and oblique/italics](samples/letters.png)

[Doublestruck upper case](samples/doublestruck.png)

[Script upper case](samples/script.png)

[Fraktur-like lower case] (samples/fraktur.png)

[Integrals](samples/integrals.png)

[Brackets](samples/fences.png)

[Accents and stackers](samples/accents.png)

[Arrows](samples/arrows.png)

Radicals

[Mathematical symbols](samples/symbols.png) (attempted to cover all the most used ones; if you need/want something that is missing report a bug and I will see if I can create it for you)

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
Here is some {\bf bold}, some {\it italics} and some {\bfit bolditalics} and an equation

\[ \int_a^b {\bf f}'(x) dx= {\bf f}(b) - {\bf f}(a)\]
\end{document}
```
## Sample

I am not sure how useful this font will be for long documents/papers, perhaps it is more suitable for posters or presentations.    Here is a sample of what motivated its creation (joint with Andrea Tomatis)

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/CAsample.png" width="600">

## Acknowledgements

Thanks to Tyler Fink for creating and sharing Grandstander (for the new name think NYC train stations).  Thanks to Andrea Tomatis, Khaled Hosny, and to Hans Hagan and Mikael P. Sundqvist for help/comments and for the "Mathematics in ConTeXt" work, from which some tests have been taken.
