-- Combine two lists
 function combine_lists(t1, t2)
    local result = {}
    for _, v in ipairs(t1) do
        table.insert(result, v)
    end
    for _, v in ipairs(t2) do
        table.insert(result, v)
    end
    return result
end

-- Hardcode useful axes
 allfonts = {"Pennstander-Thin",    "Pennstander-ExtraLight",    "Pennstander-Light",    "Pennstander-Medium",    "Pennstander-Regular",
    "Pennstander-SemiBold",    "Pennstander-Bold",    "Pennstander-ExtraBold",    "Pennstander-Black"
}
 samplefonts = {"Pennstander-Thin", "Pennstander-Regular", "Pennstander-Bold"}
 extremefonts = {"Pennstander-Thin", "Pennstander-Bold"}


 latinlower = {
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z"
}

 latinupper = {
    "A","B","C","D","E","F","G","H","I","J","K","L","M",
    "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"
}

alllatin = combine_lists(latinlower,latinupper)

 greeklower = {
    "𝛼","𝛽","𝛾","𝛿","𝜀","𝜁","𝜂","𝜃","𝜄","𝜅","𝜆","𝜇",
    "𝜈","𝜉","𝜊","𝜋","𝜌","𝜎","𝜏","𝜐","𝜑","𝜒","𝜓","𝜔"
}

greeklower = {
    "\\alpha", "\\beta", "\\gamma", "\\delta", "\\epsilon", "\\zeta", "\\eta", "\\theta", "\\iota", "\\kappa", "\\lambda", "\\mu",
    "\\nu", "\\xi", "\\omicron", "\\pi", "\\rho", "\\sigma", "\\tau", "\\upsilon", "\\phi", "\\chi", "\\psi", "\\omega"
}

greekupper = {
    "\\Alpha", "\\Beta", "\\Gamma", "\\Delta", "\\Epsilon", "\\Zeta", "\\Eta", "\\Theta", "\\Iota", "\\Kappa", "\\Lambda", "\\Mu",
    "\\Nu", "\\Xi", "\\Omicron", "\\Pi", "\\Rho", "\\Sigma", "\\Tau", "\\Upsilon", "\\Phi", "\\Chi", "\\Psi", "\\Omega"
}

frakturupper = {
    "\\mathfrak{A}", "\\mathfrak{B}", "\\mathfrak{C}", "\\mathfrak{D}", "\\mathfrak{E}", "\\mathfrak{F}", "\\mathfrak{G}", "\\mathfrak{H}", "\\mathfrak{I}", "\\mathfrak{J}", "\\mathfrak{K}", "\\mathfrak{L}", "\\mathfrak{M}",
    "\\mathfrak{N}", "\\mathfrak{O}", "\\mathfrak{P}", "\\mathfrak{Q}", "\\mathfrak{R}", "\\mathfrak{S}", "\\mathfrak{T}", "\\mathfrak{U}", "\\mathfrak{V}", "\\mathfrak{W}", "\\mathfrak{X}", "\\mathfrak{Y}", "\\mathfrak{Z}"
}


frakturlower = {
    "\\mathfrak{a}", "\\mathfrak{b}", "\\mathfrak{c}", "\\mathfrak{d}", "\\mathfrak{e}", "\\mathfrak{f}", "\\mathfrak{g}", "\\mathfrak{h}", "\\mathfrak{i}", "\\mathfrak{j}", "\\mathfrak{k}", "\\mathfrak{l}", "\\mathfrak{m}",
    "\\mathfrak{n}", "\\mathfrak{o}", "\\mathfrak{p}", "\\mathfrak{q}", "\\mathfrak{r}", "\\mathfrak{s}", "\\mathfrak{t}", "\\mathfrak{u}", "\\mathfrak{v}", "\\mathfrak{w}", "\\mathfrak{x}", "\\mathfrak{y}", "\\mathfrak{z}"
}


 doublestruckupper = {
    "𝔸","𝔹","ℂ","𝔻","𝔼","𝔽","𝔾","ℍ","𝕀","𝕁","𝕂","𝕃","𝕄",
    "ℕ","𝕆","ℙ","ℚ","ℝ","𝕊","𝕋","𝕌","𝕍","𝕎","𝕏","𝕐","ℤ"
}

doublestrucknumerals = {"𝟘","𝟙","𝟚","𝟛","𝟜","𝟝","𝟞","𝟟","𝟠","𝟡"
}


 numerals = {
    "0","1","2","3","4","5","6","7","8","9"
}

scriptlower = {
    "\\mathscr{a}", "\\mathscr{b}", "\\mathscr{c}", "\\mathscr{d}", "\\mathscr{e}", "\\mathscr{f}", "\\mathscr{g}", "\\mathscr{h}", "\\mathscr{i}", "\\mathscr{j}", "\\mathscr{k}", "\\mathscr{l}", "\\mathscr{m}",
    "\\mathscr{n}", "\\mathscr{o}", "\\mathscr{p}", "\\mathscr{q}", "\\mathscr{r}", "\\mathscr{s}", "\\mathscr{t}", "\\mathscr{u}", "\\mathscr{v}", "\\mathscr{w}", "\\mathscr{x}", "\\mathscr{y}", "\\mathscr{z}"
}

scriptupper = {
    "\\mathscr{A}", "\\mathscr{B}", "\\mathscr{C}", "\\mathscr{D}", "\\mathscr{E}", "\\mathscr{F}", "\\mathscr{G}", "\\mathscr{H}", "\\mathscr{I}", "\\mathscr{J}", "\\mathscr{K}", "\\mathscr{L}", "\\mathscr{M}",
    "\\mathscr{N}", "\\mathscr{O}", "\\mathscr{P}", "\\mathscr{Q}", "\\mathscr{R}", "\\mathscr{S}", "\\mathscr{T}", "\\mathscr{U}", "\\mathscr{V}", "\\mathscr{W}", "\\mathscr{X}", "\\mathscr{Y}", "\\mathscr{Z}"
}


overbraces={
"\\overparent",
"\\overbrace",
"\\overbar",
"\\overbracket"
}

 underbraces={
"\\underparent",
 "\\underbrace",
 "\\underbar",
 "\\underbracket"
 }

  doublebraces={
"\\doubleparent",
 "\\doublebrace",
 "\\doublebar",
 "\\doublebracket"
 }

 allunderandoverbraces = combine_lists(combine_lists(overbraces,underbraces),doublebraces)
 
 overarrows = {
    "\\overleftrightarrow",
    "\\overleftarrow",
    "\\overtwoheadleftarrow",
    "\\overlefttailarrow",
    "\\overleftbararrow",
    "\\overlefthookarrow",
    "\\overleftharpoondown",
    "\\overleftharpoonup",
    "\\overLeftarrow",
    "\\overLeftbararrow",
    "\\overLeftrightarrow",
    "\\overrightarrow",
    "\\overtwoheadrightarrow",
    "\\overrighttailarrow",
    "\\overrightbararrow",
    "\\overrighthookarrow",
    "\\overrightharpoondown",
    "\\overrightharpoonup",
    "\\overRightarrow",
    "\\overRightbararrow"
}


 underarrows = {
    "\\underleftrightarrow",
    "\\underleftarrow",
    "\\undertwoheadleftarrow",
    "\\underlefttailarrow",
    "\\underlefttailarrow",
    "\\underlefthookarrow",
    "\\underleftharpoondown",
    "\\underleftharpoonup",
    "\\underLeftarrow",
    "\\underLeftbararrow",
    "\\underLeftrightarrow",
    "\\underrightarrow",
    "\\undertwoheadrightarrow",
    "\\underrighttailarrow",
    "\\underrighttailarrow",
    "\\underrighthookarrow",
    "\\underrightharpoondown",
    "\\underrightharpoonup",
    "\\underRightarrow",
    "\\underRightbararrow"
}




allarrows = combine_lists(overarrows,underarrows)

accents = {"\\grave", "\\acute", "\\hat",
 "\\tilde", "\\bar", "\\breve",
 "\\dot", "\\ddot", "\\ring",
 "\\check", "\\overleftharpoon", "\\overrightharpoon",
 "\\dddot", "\\ddddot"}
 
 wideaccents = {
  "\\widehat", "\\widetilde",
  "\\widebar", "\\widecheck",
  "\\wideoverleftharpoon", "\\wideoverrightharpoon",
  "\\wideoverleftarrow", "\\wideoverrightarrow",
  "\\wideoverleftrightarrow", "\\wideunderbar",
  "\\wideunderleftrightarrow", "\\wideunderrightharpoon",
  "\\wideunderleftharpoon", "\\wideunderleftarrow",
  "\\wideunderrightarrow"
}

integrals = {"\\int","\\iint","\\iiint","\\iiiint","\\oint","\\oiint","\\oiiint","\\ointc","\\aointc","\\barint","\\slashint","\\intc","\\aodownintc"}

operators={
"\\char\"002B",
"\\char\"00B1",
"\\char\"2212",
"\\char\"2213",
"\\char\"2214",
"\\char\"2238",
"\\char\"2242",
"\\char\"00D7",
"\\char\"00F7",
"\\char\"2A2F",
"\\char\"2293",
"\\char\"2294",
"\\char\"29C6",
"\\char\"29C5",
"\\char\"29C4",
"\\char\"29C8",
"\\char\"29C7",
"\\char\"22A1",
"\\char\"229F",
"\\char\"229E",
"\\char\"22A0",
"\\char\"229B",
"\\char\"29B6",
"\\char\"29BF",
"\\char\"29BA",
"\\char\"29B5",
"\\char\"29BB",
"\\char\"229D",
"\\char\"229C",
"\\char\"29BC",
"\\char\"2298",
"\\char\"29C1",
"\\char\"29C0",
"\\char\"2296",
"\\char\"2297",
"\\char\"2A00",
"\\char\"2A01",
"\\char\"2A02",
"\\char\"2299",
"\\char\"29B7",
"\\char\"29B9",
"\\char\"2295",
"\\char\"29B8",
"\\char\"229A",
"\\char\"29BE",
"\\char\"29BD",
"\\char\"2A05",
"\\char\"2A06",
"\\char\"2A09",
"\\char\"2A03",
"\\char\"2A04",
"\\char\"22BC",
"\\char\"22C2",
"\\char\"22C0",
"\\char\"22C1",
"\\char\"22C3",
"\\char\"2227",
"\\char\"2228",
"\\char\"22CF",
"\\char\"22CE",
"\\char\"22D2",
"\\char\"2229",
"\\char\"222A",
"\\char\"22D3",
"\\char\"228C",
-- multiset.heavy
"\\char\"228D",
"\\char\"228E",
"\\char\"22BB",
"\\char\"22BD",
"\\char\"22C4",
"\\char\"22B2",
"\\char\"2241",
"\\char\"22C7",
"\\char\"22AE",
"\\char\"22B9",
"\\char\"223E",
"\\char\"22C9",
"\\char\"221E",
"\\char\"223F",
"\\char\"002F",
"\\char\"005C"
}



equalityrelations={
    "=",
    "⩵",
    "⩶",
    "≔",
    "≕",
    "⩴",
    "≝",
    "≅",
    "≞",
    "≜",
    "≛",
    "≗",
    "≖",
    "≣",
    "≑",
    "∺",
    "≚",
    "≡",
    -- equivalence.lft
    -- equivalence.mid
    -- equivalence.rgt
    -- equivalence.s1
    -- equivalence.s2
    -- equivalence.s3
    "≍",
    "≘",
    "≠",
    "≭",
    "≢",
    "⊭",
    "≉",
    "≟",
    "≈",
    "≒",
    "≆",
    "≃",
    "~",
    "∽",
    "\\mathrel{⋍}",
    "≓",
    "≐",
    "∝",
    "≙",
    "⊩",
    "⌆",
    "⌅",
    "~"
}

comparisonrelations={
    "<",
    ">",
    "≤",
    "≥",
    "≦",
    "≧",
    "⋖",
    "⋗",
    "≨",
    "≩",
    "⋦",
    "⋧",
    "≲",
    "≳",
    "≶",
    "≷",
    "⋚",
    "⋛",
    "⪅",
    "⪆",
    "⩽",
    "⩾",
    "⪕",
    "⪖",
    "⪉",
    "⪊",
    "≪",
    "≫",
    "⋘",
    "⋙",
    "⋜",
    "⋝",
    "≮",
    "≯",
    "≰",
    "≱",
    "≹",
    "≴",
    "≵",
    "≸",
    "⊂",
    "⊃",
    "⊆",
    "⊇",
    "⊊",
    "⊋",
    "⊈",
    "⊉",
    "⊄",
    "⊅",
    "⋐",
    "⋑",
    "⊏",
    "⊑",
    "⋤",
    "⊐",
    "⊒",
    "⋥",
    "⋢",
    "⋣",
    "≺",
    "⋨",
    "≼",
    "≾",
    "⊰",
    "≻",
    "⋩",
    "≽",
    "⋞",
    "⋟",
    "≿",
    "⊱",
    "⊀",
    "⊁",
    "⋠",
    "⋡",
    "⊬",
    "⊴",
    "⊳",
    "⊵",
    "⋪",
    "⋬",
    "⋫",
    "⋭",
    "⋌",
    "⋊",
    "⊦",
    "⊨",
    "⊧",
    "⊫",
    "⊪",
    "⊤",
    "⊣",
    "⊢",
    "⫟",
    "⫞",
    "⫠",
    "⊥",
    "¬",
    "⌐",
    "∹"
}


allrelations=combine_lists(equalityrelations,comparisonrelations)

comparisonrelations_interlaced = {
    "＜", "＞",
    "≤", "≥",
    "≦", "≧",
    "⋖", "⋗",
    "≨", "≩",
    "⋦", "⋧",
    "≲", "≳",
    "≶", "≷",
    "⋚", "⋛",
    "⪅", "⪆",
    "⩽", "⩾",
    "⪕", "⪖",
    "⪉", "⪊",
    "≪", "≫",
    "⋘", "⋙",
    "⋜", "⋝",
    "≮", "≯",
    "≰", "≱",
    "≹", "≵",
    "≸", "≷",
    "⋠", "⋡",
    "⊂", "⊃",
    "⊆", "⊇",
    "⊊", "⊋",
    "⊈", "⊉",
    "⊄", "⊅",
    "⋐", "⋑",
    "⊏", "⊐",
    "⊑", "⊒",
    "⋤", "⋥",
    "⋢", "⋣",
    "≺", "≻",
    "≼", "≽",
    "⊰", "⊱",
    "⋞", "⋟",
    "≿", -- only has one, keep order
    "⊀", "⊁",
    "⊴", "⊳",
    "⊵", -- single
    "⋪", "⋫",
    "⋬", "⋭",
    "⋌", "⋊",
    "⊦", "⊧",
    "⊨", "⊩",
    "⊫", "⊪",
    "⊤", "⊥",
    "⊣", "⊢",
    "⫞", "⫟",
    "⫠", -- no match
    "¬","⌐"
}


 allbraces = {"brace","angle","parenthesis","bracket","bar","ceiling","floor","openbracket"}
