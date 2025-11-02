#MenuTitle: Add Extended Flag property

#Add extendedshape flag to selected Glyphs

font = Glyphs.font  # frontmost font
glyph_list = font.selection

if not glyph_list:
    print("No glyphs selected.")
else:
    print("Selected glyphs:")	
    for g in glyph_list:
        print(g.name)
        print(g.userData)
        print(g.userData["com.nagwa.MATHPlugin.extendedShape"])
        key = "com.nagwa.MATHPlugin.extendedShape"
        g.userData[key] = 1
        print(f"After: {g.name}: {key} = {g.userData[key]}")
        