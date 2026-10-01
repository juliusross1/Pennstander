# Pennstander
A text and mathematics font based on [Grandstander](https://etceteratype.co/grandstander), aimed at LuaLaTeX and ConTeXt.   Beta version, comments/bug reports/advice welcome.

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/fontweights.png" width="650">

## Characters and Features
### Text
Characters in upright and oblique/italics with support for over 500 languages

Stylistic and other alternates Letters

Some Emjois

Here is the [Pennstander Text guide](docs/pennstandertext_guide.pdf) [(download)](https://raw.githubusercontent.com/juliusross1/Pennstander/main/docs/pennstandertext_guide.pdf)

### Math
Math Latin and Greek lower and upper case in upright and oblique/italics

Doublestruck upper case and numerals

Script upper case

Fraktur-like upper and lower case (with simplified styleset)

Integrals

Brackets

Accents and stackers

Arrows

Radicals

Mathematical symbols (attempted to cover all the most used ones; if you need/want something that is missing report a bug and I will see if I can create it for you)

Here is the [Pennstander Math guide](docs/pennstandermath_guide.pdf) [(download)](https://raw.githubusercontent.com/juliusross1/Pennstander/main/docs/pennstandermath_guide.pdf)

## CTAN

This is available as [Pennstander-otf on CTAN](https://www.ctan.org/pkg/pennstander-otf) (thanks to Cédric Pierquet)

## ConTeXt
Sample usage for ConTeXt MKXL:
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
PennstanderMath has cheap optical sizing using the weight axis.   Fussy users may want the text font to match this so that operators in superscripts and subscripts do not look too Thin; [here is an example of how to achieve this in luaLaTeX](/docs/cheapopticalsizing.pdf) (I am not sure what is the best way to do this in ConTeXt)


## Randoms (Experimental)

Pennstander and PennstanderMath have random alternates for some glyphs, which can be used in ConTeXt to get randomness in mathematics.  Sample usage:

```
\usetypescriptfile[type-imp-pennstander]
\setupbodyfont[pennstander]
\setupmathematics[stylealternative=random]
\starttext
\startformula
  \startalign[n=1,align=middle]
    \NC \{a,b,c\} \quad \{a,b,c\} \quad \{a,b,c\} \NR
    \NC (x+y) \quad (x+y) \quad [x-y] \quad [x-y] \NR
    \NC \int f(x)\,dx \quad \int f(x)\,dx \quad \int f(x)\,dx \NR
  \stopalign
\stopformula
\stoptext
```

Setting ``stylealternative=random`` gives the most randomness.  Other options are randomletters, randomnumerals, randomfences, randomsansintegrals, randomserifintegrals,randomintegrals (with multiple options allowed as a list).


<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/pennstander-randoms.png" width="650">


## Variable Mathematics Font (Experimental)

PennstanderMathVF.ttf is a variable font with an experimental variable MATH table. This is not an Opentype specification, but is supported in ConTeXt.  

The math weight number controls the weight of the math-bold letters (0=default, 100=maximum weight) and the
math slant number controls the slant of the math-italic letters (0=no slant, 50=default, 100=maximum slant)

Use a recent ConTeXt MKXL, with `PennstanderMathVF.ttf` installed or in the same directory as the document.  

```tex
\usetypescriptfile[type-imp-pennstander]
\definefontfeature[pennstander-math-vf]
  [axis={weight=400,math weight=80,math slant=100}]
% Adjust weight from 100 to 900; math weight and math slant from 0 to 100.
\starttypescript[math][pennstander-math-vf]
  \definefontsynonym[MathRoman][file:PennstanderMathVF.ttf]
    [features={math\mathsizesuffix,pennstander-math-vf},goodies=pennstander-math]
\stoptypescript
\definetypeface[pennstander-vf][rm][serif][pennstander]
\definetypeface[pennstander-vf][mm][math][pennstander-math-vf]
\setupbodyfont[pennstander-vf,12pt]

\starttext
\startformula
  \startalign[n=2,align={right,left}]
    \NC \nabla \cdot {\bf E}  \NC = \frac{\rho}{\varepsilon_0} \NR
    \NC \nabla \cdot {\bf B}  \NC = 0 \NR
    \NC \nabla \times {\bf E} \NC = -\frac{\partial {\bf B}}{\partial t} \NR
    \NC \nabla \times {\bf B} \NC = \mu_0 {\bf J}
      + \mu_0 \varepsilon_0 \frac{\partial {\bf E}}{\partial t} \NR
  \stopalign
\stopformula
\stoptext
```

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/pennstander-variable.png" width="650">

e In case anybody wants to use this but does not want to use variable math, there is a script that will create a static font from this variable font.  Sample usage:

```
python3 pythonScripts/instantiate_pennstander.py \
  -i fonts/opentype/PennstanderMathVF.ttf \
  wght=400 MWGT=80 MLNT=100 \
  -o PennstanderMath-Custom.ttf
```

## Sample

I am not sure how useful this font will be for long documents/papers, perhaps it is more suitable for posters or presentations.  I have been using it for writing solutions for students.  Here is a sample of what motivated its creation (joint with Andrea Tomatis)

<img src="https://github.com/juliusross1/Pennstander/blob/main/samples/CAsample.png" width="600">

## Acknowledgements

Thanks to Tyler Fink for creating and sharing Grandstander (for the new name think NYC train stations).  Thanks to those who submitted issues, as well as Andrea Tomatis, David Carlisle, Khaled Hosny, and to Hans Hagan and Mikael P. Sundqvist for help/comments/collaboration and for the "Mathematics in ConTeXt" work, from which some tests have been taken.  Thanks to Cédric Pierquet for the CTAN package.
