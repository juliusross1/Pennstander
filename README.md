# Pennstander
A text and mathematics font based on [Grandstander](https://etceteratype.co/grandstander), aimed at LuaLaTeX and ConTeXt.   Beta version, comments/bug reports/advice welcome.

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/fontweights.png" width="650">

## Characters
Latin and Greek lower and upper case in upright and oblique/italics

Doublestruck upper case and numerals

Script upper case

Fraktur-like upper and lower case (with simplified styleset)

Integrals

Brackets

Accents and stackers

Arrows

Radicals

Mathematical symbols (attempted to cover all the most used ones; if you need/want something that is missing report a bug and I will see if I can create it for you)

Here is the [Pennstander Math Characters document](docs/pennstandercharacters.pdf)

## CTAN

This is available as [Pennstander-otf on CTAN](https://www.ctan.org/pkg/pennstander-otf) (thanks to Cédric Pierquet)

## ConTeXt
Sample usage for ConTeXt MKXL (the required typescript and goodies files are included in the latest ConTeXt, or can be found above and placed in your working directory)
```
\usetypescriptfile[type-imp-pennstander]
\setupbodyfont[pennstander]
% Replace 'pennstander' with 'pennstander-thin', 'pennstander-extralight', 'pennstander-light' etc. as desired
% (some math symbols do not look good at bold/extrabold/black so use with care)
\setupalign[profile]
\setupinterlinespace[14pt]
\starttext
Here is some {\bf bold} and some {\it italics} some {\bi bolditalics} and an equation
\startformula
\int_a^b \frac{d{\bf f}}{dx} dx = {\bf f}(b) - {\bf f}(a)
\stopformula
\stoptext
```

## LuaLaTeX
Sample usage
```
\documentclass[12pt]{article}

\usepackage[math-style=upright]{unicode-math} %The upright option is recommended for this font, but not necessary

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

\setmathfont{PennstanderMath-Thin.otf}
%% Replace 'Thin' with 'ExtraLight'/'Light'/... to match the text font above


\begin{document}
Here is some {\bf bold}, some {\it italics} and some {\bf\it bolditalics} and an equation

\[ \int_a^b {\bf f}'(x) dx= {\bf f}(b) - {\bf f}(a)\]
\end{document}
```

## Cheap Optical Sizing
The latest (not released) version of PennstanderMath has cheap optical sizing using the weight axis.   Fussy users may want the text font to match this so that operators in superscripts and subscripts do not look too Thin; [here is an example of how to achieve this in luaLaTeX](/docs/cheapopticalsizing.pdf) (this appears to me not necessary in ConTeXt)

## Sample

I am not sure how useful this font will be for long documents/papers, perhaps it is more suitable for posters or presentations.  I have been using it for writing solutions for students.  Here is a sample of what motivated its creation (joint with Andrea Tomatis)

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/CAsample.png" width="600">

## Acknowledgements

Thanks to Tyler Fink for creating and sharing Grandstander (for the new name think NYC train stations).  Thanks to those who submitted issues, as well as Andrea Tomatis, David Carlisle, Khaled Hosny, and to Hans Hagan and Mikael P. Sundqvist for help/comments and for the "Mathematics in ConTeXt" work, from which some tests have been taken.  Thanks to Cédric Pierquet for the CTAN package.
