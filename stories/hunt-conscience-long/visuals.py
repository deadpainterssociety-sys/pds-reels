# Visual plan for the long video of 26 Nov 2026: Holman Hunt's The Awakening Conscience. Executed by plan.py: A, sh, ov, IM,
# MUSIC, SFX are in scope. Calm cuts (about one shot per phrase group, slow moves), soft sounds, NO big date cards
# (Gigi, 21 Nov 2026). Music: Victorian parlour piano (Schumann, Musopen; Chopin nocturnes, CC0) and the song in the
# painting itself, Moore's Oft in the Stilly Night (CC0 recording).
P = lambda **kw: kw
IM.update({
 "conscience": P(file="src/conscience.jpg", commons="File:William Holman Hunt - The Awakening Conscience - Google Art Project.jpg", depth=True, long=3840,
     points={"center": [0.5, 0.5], "face": [0.535, 0.215], "eyes": [0.535, 0.195], "hands": [0.56, 0.515], "keys": [0.645, 0.49], "man": [0.20, 0.42], "couple": [0.38, 0.36], "cat": [0.05, 0.755], "bird": [0.08, 0.815], "glove": [0.585, 0.925], "wool": [0.86, 0.92], "tears": [0.12, 0.95], "music": [0.80, 0.37], "clock": [0.87, 0.24], "mirror": [0.25, 0.24], "window": [0.27, 0.20], "noteL": [0.12, 0.05], "noteR": [0.86, 0.06], "books": [0.07, 0.58], "piano": [0.82, 0.58], "upper": [0.5, 0.30], "room": [0.5, 0.36], "hem": [0.48, 0.84], "lower": [0.5, 0.75]}),
 "frame": P(file="src/frame.jpg", commons="File:William holman hunt, il risveglio della coscienza, 1853, 01.jpg",
     credit="The Awakening Conscience in its frame: photo Sailko, CC BY 3.0", points={"center": [0.5, 0.5], "painting": [0.43, 0.42], "verse": [0.5, 0.925], "border": [0.07, 0.45], "top": [0.5, 0.07]}),
 "clockph": P(file="src/clockph.jpg", commons="File:William holman hunt, il risveglio della coscienza, 1853, 04 orologio su pianoforte.jpg",
     credit="Detail of the clock: photo Sailko, CC BY 3.0", points={"center": [0.5, 0.5], "clock": [0.58, 0.30], "music": [0.40, 0.70], "title": [0.54, 0.62]}),
 "light": P(file="src/light.jpg", commons="File:Hunt-light-of-the-world.jpeg", depth=True, points={"center": [0.5, 0.5], "face": [0.51, 0.24], "lantern": [0.73, 0.68], "door": [0.12, 0.45], "upper": [0.5, 0.30]}),
 "hunt": P(file="src/hunt.jpg", commons="File:William Holman Hunt - Self-Portrait - Google Art Project.jpg", points={"center": [0.5, 0.5], "face": [0.51, 0.40]}),
 "coasts": P(file="src/coasts.jpg", commons="File:William Holman Hunt - Our English Coasts, 1852 (`Strayed Sheep') - Google Art Project.jpg", depth=True, points={"center": [0.5, 0.5], "sheep": [0.6, 0.45]}),
 "peggotty": P(file="src/peggotty.jpg", commons="File:Rencontre avec Dan Pegpotty poursuivant ses recherches (David Copperfield).jpeg", points={"center": [0.5, 0.52], "men": [0.40, 0.56]}),
 "egg": P(file="src/egg.jpg", commons="File:Past and Present Number One.jpg", points={"center": [0.5, 0.5], "woman": [0.80, 0.86], "husband": [0.72, 0.43]}),
 "annie": P(file="src/annie.jpg", commons="File:Dante Gabriel Rossetti - Annie Miller.jpg", points={"center": [0.6, 0.45], "face": [0.80, 0.32]}),
 "annie2": P(file="src/annie2.jpg", commons="File:Annie Miller by Dante Gabriel Rossetti (1828-1882).jpg", points={"center": [0.5, 0.5], "face": [0.61, 0.50]}),
 "harp": P(file="src/harp.jpg", commons="File:Dante Gabriel Rossetti - The Harp Player (Annie Miller).jpg", points={"center": [0.5, 0.5], "face": [0.44, 0.19], "body": [0.5, 0.45]}),
 "helen": P(file="src/helen.jpg", commons="File:Hamburg Kunsthalle Dante Gabriel Rosetti Helen of Troy.jpg", points={"center": [0.5, 0.5], "face": [0.49, 0.38]}),
 "rossetti": P(file="src/rossetti.jpg", commons="File:Dante Gabriel Rossetti - Self-portrait, 1847.jpg", points={"center": [0.5, 0.5], "face": [0.52, 0.44]}),
 "ruskin": P(file="src/ruskin.jpg", commons="File:Millais Ruskin.jpg", points={"center": [0.5, 0.5], "face": [0.60, 0.20], "body": [0.6, 0.40]}),
 "combe": P(file="src/combe.jpg", commons="File:John Everett Millais (1829-1896) - Thomas Combe (1796–1872) - WA1894.9 - Ashmolean Museum.jpg", points={"center": [0.5, 0.5], "face": [0.53, 0.25], "body": [0.5, 0.45]}),
 "moore": P(file="src/moore.jpg", commons="File:Thomas Lawrence (1769-1830) - Thomas Moore (1779–1852), Poet - TC Oils P 124 - Trinity College.jpg", points={"center": [0.5, 0.5], "face": [0.55, 0.38]}),
 "stilly": P(file="src/stilly.jpg", commons="File:Oft in the stilly night arranged for the Spanish guitar by B.F. Peale LCCN2015650312.jpg", points={"center": [0.5, 0.5], "title": [0.45, 0.10], "lyrics": [0.5, 0.33]}),
 "lear": P(file="src/lear.jpg", commons="File:Edward Lear 1867.jpg", points={"center": [0.5, 0.5], "face": [0.48, 0.30]}),
 "scapegoat": P(file="src/scapegoat.jpg", commons="File:William Holman Hunt - The Scapegoat.jpg", depth=True, points={"center": [0.5, 0.5], "goat": [0.45, 0.60]}),
 "finding": P(file="src/finding.jpg", commons="File:William Holman Hunt - The Finding of the Saviour in the Temple - Google Art Project.jpg", depth=True, long=3840, points={"center": [0.45, 0.5], "boy": [0.63, 0.27]}),
 "cremorne": P(file="src/cremorne.jpg", commons="File:Cremorne The Dancing Platform at Cremorne Gardens by Phoebus Levin 1864.jpg", points={"center": [0.5, 0.55], "dancers": [0.55, 0.70]}),
 "ranelagh": P(file="src/ranelagh.jpg", commons="File:Carlo Pellegrini - Politicians - Vanity Fair ^He has suceeded in volunteering^ Viscount Ranelagh 25 June 1870 - B1979.14.920 - Yale Center for British Art.jpg", points={"center": [0.5, 0.5], "face": [0.42, 0.28], "body": [0.47, 0.45]}),
 "richmond": P(file="src/richmond.jpg", commons="File:John Robert Cozens - The Thames from Richmond Hill Looking Southwest - Google Art Project.jpg", depth=True, points={"center": [0.5, 0.6], "river": [0.5, 0.78]}),
 "tate": P(file="src/tate.jpg", commons="File:Tate Britain 2020.jpg", depth=True, credit="Tate Britain, London: photo Julian Herzog, CC BY 4.0", points={"center": [0.5, 0.5], "facade": [0.45, 0.55]}),
})

# ---------------------------------------------------------------- shots (about one per phrase group; slow moves)
FR = dict(frame=True)
# cold open: her face, the reveal, the hands, the painter, the model, the two women
sh(A("cold1"), "conscience", "face@2.6", "face@2.45")
sh(A("cold1", "realised", off=-0.1), "conscience", "center@0.62", "center@0.64", hit="big", **FR)
sh(A("cold2"), "conscience", "couple@1.3", "couple@1.4", fade=0.6)
sh(A("cold2", "Then", off=-0.1), "conscience", "hands@2.6", "hands@2.8", fade=0.6)
sh(A("cold2", "except", off=-0.1), "conscience", "hands@3.4", "hands@3.55", fade=0.5)
sh(A("cold3"), "hunt", "face@1.25", "face@1.35", fade=0.8)
sh(A("cold3", "believed", off=-0.1), "conscience", "window@2.0", "window@2.12", fade=0.6)
sh(A("cold3", "And", off=-0.1), "annie", "face@1.35", "face@1.45", fade=0.6)
sh(A("cold3", "barmaid", off=-0.1), "annie2", "face@1.3", "face@1.4", fade=0.5)
sh(A("cold4"), "conscience", "face@2.2", "face@2.35", fade=0.8)
sh(A("cold4", "Even", off=-0.1), "conscience", "eyes@3.2", "eyes@3.05", fade=0.6)
sh(A("cold5"), "conscience", "face@1.8", "face@1.9", fade=0.8)
sh(A("cold5", "and", off=-0.1), "helen", "face@1.35", "face@1.45", fade=0.6)
sh(A("cold5", end=True, off=-0.6), "conscience", "center@0.62", "center@0.65", dim=0.3, fade=1.2, **FR)
# I. The Still Small Voice
sh(A("c1a"), "hunt", "face@1.15", "face@1.25", fade=1.0)
sh(A("c1a", "one", off=-0.1), "coasts", "center@1.0", "sheep@1.1", fade=0.8)
sh(A("c1b"), "light", "face@1.3", "face@1.4", fade=1.0)
sh(A("c1b", "knocking", off=-0.1), "light", "door@1.3", "door@1.4", dim=0.15, fade=0.6)
sh(A("c1b", "He", off=-0.1), "light", "upper@0.55", "upper@0.57", fade=0.8, **FR)
sh(A("c1c"), "light", "lantern@1.8", "lantern@1.9", fade=0.8)
sh(A("c1c", "but", off=-0.1), "conscience", "couple@1.25", "couple@1.35", fade=0.8)
sh(A("c1d"), "peggotty", "center@0.7", "center@0.72", fade=1.0, **FR)
sh(A("c1e"), "conscience", "upper@1.15", "room@1.25", gray=0.6, dim=0.2, fade=1.0)
sh(A("c1f"), "frame", "painting@0.62", "painting@0.64", fade=1.0, **FR)
sh(A("c1f", "As", off=-0.1), "frame", "verse@1.9", "verse@2.0", fade=0.8)
sh(A("c1g"), "conscience", "keys@2.4", "keys@2.55", fade=0.8)
sh(A("c1g", "who", off=-0.4), "conscience", "man@2.2", "man@2.35", fade=0.6)
sh(A("c1g", "without", off=-0.1), "conscience", "man@2.6", "man@2.7", fade=0.5)
sh(A("c1h"), "egg", "husband@1.3", "husband@1.4", fade=1.0)
sh(A("c1h", "Fairbairn", 2, off=-0.1), "conscience", "center@0.62", "center@0.64", gray=0.3, fade=0.8, **FR)
sh(A("c1h", "And", off=-0.1), "scapegoat", "center@1.0", "goat@1.1", fade=0.8)
# II. A Room in St John's Wood
sh(A("c2a"), "conscience", "window@1.7", "window@1.8", fade=1.0)
sh(A("c2a", "So", off=-0.1), "conscience", "upper@1.2", "upper@1.28", fade=0.8)
sh(A("c2a", "Tate", off=-0.3), "conscience", "room@1.35", "room@1.45", fade=0.8)
sh(A("c2b"), "conscience", "piano@1.8", "piano@1.95", fade=0.8)
sh(A("c2b", "Everything", off=-0.1), "conscience", "books@2.4", "books@2.55", fade=0.6)
sh(A("c2b", "fine", off=-0.1), "conscience", "books@2.9", "books@3.0", fade=0.6)
sh(A("c2c"), "ruskin", "body@0.62", "body@0.64", fade=1.0, **FR)
sh(A("c2c", "Nothing", off=-0.1), "conscience", "piano@1.5", "music@1.6", dim=0.15, fade=0.8)
sh(A("c2e"), "conscience", "center@0.62", "center@0.64", gray=0.6, dim=0.25, fade=1.0, **FR)
sh(A("c2e", "In", off=-0.1), "conscience", "window@1.9", "window@2.05", fade=0.8)
sh(A("c2f"), "hunt", "face@1.4", "face@1.5", gray=0.6, fade=1.0)
sh(A("c2f", "ran", off=-0.1), "light", "lantern@1.6", "lantern@1.7", dim=0.2, fade=0.8)
# III. Annie
sh(A("c3a"), "conscience", "face@2.4", "face@2.55", fade=1.0)
sh(A("c3a", "Her", off=-0.1), "annie", "face@1.6", "face@1.7", fade=0.8)
sh(A("c3b"), "harp", "body@0.62", "body@0.64", fade=1.0, **FR)
sh(A("c3c"), "annie", "center@1.0", "face@1.2", fade=1.0)
sh(A("c3d"), "hunt", "face@1.3", "face@1.4", fade=1.0)
sh(A("c3d", "would", off=-0.3), "annie2", "face@1.2", "face@1.3", fade=0.8)
sh(A("c3d", "when", off=-0.3), "conscience", "hands@2.8", "hands@2.95", fade=0.8)
sh(A("c3e"), "conscience", "face@2.0", "face@2.15", fade=0.8)
sh(A("c3e", "In", off=-0.1), "annie", "face@1.5", "face@1.6", fade=0.8)
sh(A("c3f"), "scapegoat", "center@1.0", "center@1.06", gray=0.4, fade=1.0)
sh(A("c3f", "and", off=-0.1), "annie2", "face@1.4", "face@1.5", fade=0.8)
sh(A("c3g"), "harp", "face@1.6", "face@1.7", fade=0.8)
sh(A("c3g", "Dante", off=-0.1), "rossetti", "center@0.62", "center@0.64", fade=0.6, **FR)
# IV. Look Closely
sh(A("c4a"), "conscience", "center@0.62", "center@0.64", fade=1.2, **FR)
sh(A("c4a", "like", off=-0.1), "conscience", "lower@1.0", "lower@1.05", fade=0.8)
sh(A("c4b"), "conscience", "cat@2.8", "cat@2.95", fade=0.8)
sh(A("c4b", "bird's", off=-0.3), "conscience", "bird@3.4", "bird@3.6", fade=0.6)
sh(A("c4c"), "conscience", "glove@3.0", "glove@3.2", fade=0.8)
sh(A("c4c", "Tate", off=-0.3), "conscience", "hem@2.0", "hem@2.1", dim=0.2, fade=0.8)
sh(A("c4d"), "conscience", "wool@2.8", "wool@3.0", fade=0.8)
sh(A("c4e"), "clockph", "clock@1.3", "clock@1.4", fade=0.8)
sh(A("c4e", "sealed", off=-0.1), "conscience", "clock@3.4", "clock@3.6", fade=0.6)
sh(A("c4f"), "conscience", "tears@3.0", "tears@3.15", fade=0.8)
sh(A("c4f", "set", off=-0.1), "lear", "face@0.62", "face@0.64", fade=0.6, **FR)
sh(A("c4f", "And", off=-0.1), "clockph", "title@1.4", "music@1.3", fade=0.8)
sh(A("c4f", "Thomas", off=-0.1), "moore", "face@0.62", "face@0.64", fade=0.6, **FR)
sh(A("c4f", "about", off=-0.1), "stilly", "lyrics@1.2", "lyrics@1.3", dim=0.3, fade=0.8)
sh(A("c4g"), "conscience", "mirror@2.2", "mirror@2.35", fade=0.8)
sh(A("c4g", "a", 1, off=-0.1), "conscience", "window@3.0", "window@3.2", fade=0.6)
sh(A("c4h"), "frame", "center@0.62", "center@0.64", fade=1.0, **FR)
sh(A("c4h", "bells", off=-0.1), "frame", "border@1.6", "border@1.7", dim=0.2, fade=0.6)
sh(A("c4h", "and", off=-0.1), "frame", "top@1.6", "top@1.7", dim=0.2, fade=0.6)
sh(A("c4i"), "conscience", "face@2.0", "face@2.1", gray=0.3, fade=1.0)
sh(A("c4i", "was", off=-0.3), "combe", "body@0.62", "body@0.64", fade=0.8, **FR)
sh(A("c4i", "Awakening", off=-0.4), "conscience", "center@0.62", "center@0.64", fade=0.8, **FR)
# V. A Painful Face
sh(A("c5a"), "light", kind="pair", img2="conscience", labels=["THE LIGHT OF THE WORLD", "THE AWAKENING CONSCIENCE"], fade=1.0)
sh(A("c5b"), "conscience", "couple@1.4", "couple@1.5", fade=1.0)
sh(A("c5b", "Some", off=-0.1), "conscience", "man@2.2", "man@2.35", fade=0.6)
sh(A("c5c"), "conscience", "center@0.62", "center@0.64", gray=0.5, fade=0.8, **FR)
sh(A("c5d"), "conscience", "face@2.4", "face@2.55", fade=0.8)
sh(A("c5d", "could", off=-0.1), "conscience", "eyes@3.2", "eyes@3.4", fade=0.6)
sh(A("c5e"), "ruskin", "face@1.6", "face@1.7", fade=1.0)
sh(A("c5e", "People", off=-0.1), "conscience", "center@0.62", "center@0.64", gray=0.4, fade=0.8, **FR)
sh(A("c5f"), "conscience", "keys@2.4", "keys@2.5", fade=0.8)
sh(A("c5f", "room", off=-0.2), "conscience", "upper@1.25", "upper@1.32", fade=0.5)
sh(A("c5f", "bird", off=-0.2), "conscience", "bird@3.2", "bird@3.35", fade=0.5)
sh(A("c5f", "And", off=-0.1), "conscience", "face@2.6", "face@2.75", fade=0.6)
sh(A("c5f", "eyes", off=-0.2), "conscience", "eyes@3.4", "eyes@3.55", fade=0.6)
sh(A("c5g"), "conscience", "room@1.0", "room@1.06", fade=0.8)
sh(A("c5g", "but", off=-0.1), "conscience", "piano@1.4", "piano@1.5", fade=0.8)
sh(A("c5h"), "finding", "center@1.0", "boy@1.15", fade=1.0)
sh(A("c5h", "But", off=-0.1), "conscience", "face@2.2", "face@2.35", dim=0.2, fade=0.8)
# VI. While He Was Away
sh(A("c6a"), "annie", "face@1.4", "face@1.5", fade=1.0)
sh(A("c6b"), "annie2", "face@1.25", "face@1.35", fade=0.8)
sh(A("c6b", "But", off=-0.1), "harp", "body@0.62", "body@0.64", fade=0.8, **FR)
sh(A("c6c"), "cremorne", "center@0.75", "center@0.77", fade=1.0, **FR)
sh(A("c6c", "where", off=-0.1), "cremorne", "dancers@1.25", "dancers@1.35", fade=0.8)
sh(A("c6d"), "hunt", "face@1.4", "face@1.5", gray=0.4, fade=1.0)
sh(A("c6d", "I", off=-0.1), "rossetti", "center@0.62", "center@0.64", gray=0.5, fade=0.6, **FR)
sh(A("c6e"), "conscience", "face@2.6", "face@2.75", fade=1.0)
sh(A("c6e", "He", off=-0.1), "conscience", "eyes@3.3", "eyes@3.45", fade=0.6)
sh(A("c6f"), "conscience", "face@2.2", "face@2.3", gray=0.5, fade=0.8)
sh(A("c6f", "The", 1, off=-0.1), "conscience", "center@0.62", "center@0.64", gray=0.3, fade=0.8, **FR)
sh(A("c6f", "The", 2, off=-0.1), "lear", "face@0.62", "face@0.64", fade=0.8, **FR)
sh(A("c6g"), "conscience", "noteL@2.0", "noteL@2.12", fade=1.0)
sh(A("c6g", "make", off=-0.3), "conscience", "face@2.4", "face@2.55", fade=0.8)
# VII. Annie's Choice
sh(A("c7a"), "annie2", "face@1.3", "face@1.4", fade=1.0)
sh(A("c7a", "But", off=-0.1), "ranelagh", "body@0.62", "body@0.64", fade=0.8, **FR)
sh(A("c7b"), "conscience", "hands@3.0", "hands@3.15", gray=0.6, fade=0.8)
sh(A("c7c"), "conscience", "face@2.0", "face@2.1", fade=0.8)
sh(A("c7c", "turns", off=-0.1), "conscience", "window@2.2", "window@2.35", fade=0.6)
sh(A("c7c", "In", 2, off=-0.1), "hunt", "face@1.3", "face@1.4", fade=0.8)
sh(A("c7c", "But", off=-0.1), "helen", "face@1.3", "face@1.42", fade=0.8)
sh(A("c7d"), "ranelagh", "face@1.3", "face@1.4", fade=1.0)
sh(A("c7d", "Instead", off=-0.1), "helen", "face@1.6", "face@1.7", fade=0.8)
sh(A("c7d", "In", off=-0.1), "annie", "face@1.3", "face@1.4", fade=0.8)
sh(A("c7e"), "annie2", "face@1.5", "face@1.6", fade=1.0)
sh(A("c7e", "Hunt's", 2, off=-0.1), "hunt", "face@1.3", "face@1.4", gray=0.5, fade=0.8)
sh(A("c7f"), "richmond", "river@1.25", "river@1.35", fade=1.0)
sh(A("c7f", "A", off=-0.1), "richmond", "river@1.4", "river@1.5", fade=0.6)
sh(A("c7g"), "annie", "face@1.4", "face@1.5", fade=1.0)
sh(A("c7h"), "conscience", "center@0.62", "center@0.64", hit="big", **FR)
sh(A("c7h", "Her", off=-0.1), "conscience", "face@2.6", "face@2.75", fade=0.8)
sh(A("c7h", "But", off=-0.1), "conscience", "hands@3.0", "hands@3.2", fade=0.8)
sh(A("c7i"), "conscience", "window@1.9", "window@2.0", fade=0.8)
sh(A("c7i", "real", off=-0.3), "annie", "face@1.45", "face@1.55", fade=0.8)
sh(A("ending"), "tate", "facade@1.0", "facade@1.06", fade=1.2)
sh(A("ending", end=True, off=0.6), "conscience", "center@0.62", "center@0.64", fade=1.2, **FR)

# ---------------------------------------------------------------- overlays (no big date cards)
CH = [("cold5", "c1a", "I", "The Still Small Voice"), ("c1h", "c2a", "II", "A Room in St John's Wood"), ("c2f", "c3a", "III", "Annie"),
      ("c3g", "c4a", "IV", "Look Closely"), ("c4i", "c5a", "V", "A Painful Face"), ("c5h", "c6a", "VI", "While He Was Away"),
      ("c6g", "c7a", "VII", "Annie's Choice")]
ov("title", A("cold5", end=True, off=-0.5), A("c1a", off=-0.6), kicker="WILLIAM HOLMAN HUNT · 1853", text="The Awakening Conscience")
for prev, nxt, n, name in CH:
    if n != "I": ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("chapter", A("c1a", off=-0.5), A("c1a", off=1.8), kicker="CHAPTER I", text="The Still Small Voice")
ov("label", A("cold1", "realised", off=0.3), A("cold2", "Then", off=-0.2), text="THE AWAKENING CONSCIENCE · HUNT · 1853")
ov("ring", A("cold2", "except", off=0.2), A("cold2", end=True, off=0.6), point="hands", img="conscience", rx=170, ry=130, rot=0)
ov("lower", A("cold3", off=0.2), A("cold3", "believed", off=-0.15), text="William Holman Hunt", sub="1827–1910 · SELF-PORTRAIT, 1845")
ov("lower", A("cold3", "And", off=0.1), A("cold3", end=True, off=0.6), text="Annie Miller", sub="1835–1925 · DRAWN BY ROSSETTI")
ov("label", A("cold5", "and"), A("cold5", end=True, off=-0.7), text="ANNIE MILLER AS HELEN OF TROY · ROSSETTI")
ov("label", A("c1a", "one", off=0.1), A("c1b", off=-0.2), text="HUNT · OUR ENGLISH COASTS · 1852")
ov("label", A("c1b", off=1.7), A("c1c", "but", off=-0.15), text="THE LIGHT OF THE WORLD · HUNT · 1851–53")
ov("label", A("c1d"), A("c1d", end=True, off=0.6), text="DAVID COPPERFIELD · PHIZ · 1850")
ov("label", A("c1f"), A("c1f", end=True, off=1.0), text="HUNT'S FRAME · PROVERBS 25:20")
ov("credit", A("c1f"), A("c1f", end=True, off=1.0), text="Photo: Sailko, CC BY 3.0, Wikimedia Commons")
ov("label", A("c1h"), A("c1h", "Fairbairn", 2, off=-0.15), text="AUGUSTUS EGG · PAST AND PRESENT No. 1 · 1858")
ov("label", A("c1h", "And"), A("c1h", end=True, off=0.6), text="HUNT · THE SCAPEGOAT · THE DEAD SEA, 1854")
ov("label", A("c2a", "So", off=0.1), A("c2b", off=-0.2), text="WOODBINE VILLA · ST JOHN'S WOOD")
ov("lower", A("c2c", off=0.2), A("c2c", "Nothing", off=-0.15), text="John Ruskin", sub="1819–1900 · PORTRAIT BY MILLAIS, 1853–54")
ov("lower", A("c3a", "Her", off=0.2), A("c3a", end=True, off=0.6), text="Annie Miller", sub="1835–1925 · DRAWN BY ROSSETTI, c. 1860")
ov("label", A("c3b"), A("c3b", end=True, off=0.6), text="ANNIE MILLER · ROSSETTI, THE HARP PLAYER")
ov("label", A("c3f"), A("c3f", "and", off=-0.15), text="HUNT · THE SCAPEGOAT · 1854–56")
ov("lower", A("c3g", "Dante", off=0.1), A("c3g", end=True, off=0.6), text="Dante Gabriel Rossetti", sub="1828–1882 · SELF-PORTRAIT, 1847")
ov("ring", A("c4b", "a", 1, off=0.0), A("c4b", end=True, off=0.6), point="bird", img="conscience", rx=200, ry=120, rot=0)
ov("ring", A("c4c", "glove", off=-0.1), A("c4c", "Tate", off=-0.4), point="glove", img="conscience", rx=170, ry=110, rot=0)
ov("label", A("c4e"), A("c4e", "sealed", off=-0.15), text="THE CLOCK UNDER ITS GLASS DOME")
ov("credit", A("c4e"), A("c4e", "sealed", off=-0.15), text="Photo: Sailko, CC BY 3.0, Wikimedia Commons")
ov("lower", A("c4f", "set", off=0.1), A("c4f", "And", off=-0.15), text="Edward Lear", sub="1812–1888 · POET, PAINTER, COMPOSER")
ov("credit", A("c4f", "And"), A("c4f", "Thomas", off=-0.15), text="Photo: Sailko, CC BY 3.0, Wikimedia Commons")
ov("lower", A("c4f", "Thomas", off=0.1), A("c4f", "about", off=-0.15), text="Thomas Moore", sub="1779–1852 · BY THOMAS LAWRENCE")
ov("label", A("c4f", "about"), A("c4f", end=True, off=0.6), text="OFT IN THE STILLY NIGHT · SHEET MUSIC, 1826")
ov("label", A("c4h"), A("c4h", end=True, off=0.8), text="THE FRAME, DESIGNED BY HUNT")
ov("credit", A("c4h"), A("c4h", end=True, off=0.8), text="Photo: Sailko, CC BY 3.0, Wikimedia Commons")
ov("lower", A("c4i", "was", off=0.0), A("c4i", "Awakening", off=-0.45), text="Thomas Combe", sub="1796–1872 · PORTRAIT BY MILLAIS, 1850")
ov("quote", A("c5c", off=-0.1), A("c5c", end=True, off=0.9), text="This is an absolutely disagreeable picture.", sub="MORNING CHRONICLE · 29 APRIL 1854")
ov("quote", A("c5d", "could", off=-0.1), A("c5d", end=True, off=1.0), text="The author of \"The Bridge of Sighs\" could not have conceived a more painful-looking face.", sub="THE ATHENAEUM · 1854")
ov("lower", A("c5e", off=0.2), A("c5e", "People", off=-0.15), text="John Ruskin", sub="LETTER TO THE TIMES · 25 MAY 1854")
ov("quote", A("c5g", off=-0.1), A("c5g", end=True, off=1.0), text="There is not a single object in all that room… but it becomes tragical, if rightly read.", sub="JOHN RUSKIN · THE TIMES · 25 MAY 1854")
ov("label", A("c5h"), A("c5h", "But", off=-0.15), text="HUNT · THE FINDING OF THE SAVIOUR IN THE TEMPLE")
ov("label", A("c6b", "But"), A("c6b", end=True, off=0.6), text="ROSSETTI · THE HARP PLAYER (ANNIE MILLER)")
ov("label", A("c6c"), A("c6c", end=True, off=0.6), text="CREMORNE GARDENS · PHOEBUS LEVIN · 1864")
ov("quote", A("c6d", "I", off=-0.1), A("c6d", end=True, off=1.0), text="I will never forgive Gabriel.", sub="HUNT ON ROSSETTI · AS QUOTED BY G. H. FLEMING")
ov("quote", A("c6f", "I", off=-0.1), A("c6f", end=True, off=1.0), text="I think that I have materially bettered it now.", sub="HUNT TO EDWARD LEAR · 16 APRIL 1857")
ov("ring", A("c6g", off=0.3), A("c6g", "make", off=-0.4), point="noteL", img="conscience", rx=260, ry=110, rot=0)
ov("quote", A("c6g", "make", off=-0.3), A("c6g", end=True, off=1.0), text="…to make certain that its last state compensated for its first.", sub="HUNT · MEMOIRS, 1905")
ov("lower", A("c7a", "But", off=0.1), A("c7a", end=True, off=0.6), text="Viscount Ranelagh", sub="1812–1885 · VANITY FAIR, 1870")
ov("label", A("c7c", "But"), A("c7c", end=True, off=0.6), text="ANNIE MILLER AS HELEN OF TROY · ROSSETTI, 1863")
ov("label", A("c7f"), A("c7f", end=True, off=0.6), text="THE THAMES FROM RICHMOND HILL · J. R. COZENS")
ov("ring", A("c7h", "rings", off=-0.1), A("c7h", end=True, off=0.8), point="hands", img="conscience", rx=200, ry=150, rot=0)
ov("pin", A("ending", off=0.1), A("ending", end=True, off=1.0), text="TATE BRITAIN · LONDON · ROOM 10")
ov("credit", A("ending"), A("ending", end=True, off=0.6), text="Photo: Julian Herzog, CC BY 4.0, Wikimedia Commons")
ov("end", A("ending", end=True, off=1.0), A("ending", end=True, off=21.0), kicker="NEXT", text="")

SFX += [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.22} for prev, _, n, _ in CH if n != "I"]

# ---------------------------------------------------------------- music: Victorian parlour piano (the room has a piano)
CM = {"m_dreaming.ogg": "File:Robert Schumann - scenes from childhood, op. 15 - vii. dreaming.ogg",
      "m_poet.ogg": "File:Robert Schumann - scenes from childhood, op. 15 - xiii. the poet speaks.ogg",
      "m_asleep.ogg": "File:Robert Schumann - scenes from childhood, op. 15 - xii. child falling asleep.ogg",
      "m_fright.ogg": "File:Robert Schumann - scenes from childhood, op. 15 - xi. frightening.ogg",
      "m_n37.ogg": "File:Chopin- Nocturne op. 37 no. 1.ogg",
      "m_n55.ogg": "File:Chopin - Nocturne-op-55-no-1.ogg",
      "m_n72.ogg": "File:Chopin Nocturne in Em, Op. posth. 72.ogg"}
T = lambda f, frm, to, credit, **kw: {"file": f"src/music/{f}", "commons": CM[f], "from": frm, **({"to": to} if to is not None else {}), "start": kw.pop("start", 0),
                                     "gain_db": kw.pop("gain_db", 0), "fade_in": kw.pop("fade_in", 2.5), "fade_out": kw.pop("fade_out", 3.0), "credit": credit}
SCH = "Schumann, Scenes from Childhood: {} · Musopen, public domain"
CHO = "Chopin, Nocturne {} · Musopen, Constantin Stephan, CC0"
MUSIC.update({
 "pad": False, "whooshes": False, "music_db": -8.0, "duck_db": -7, "fx_db": -12, "transpose": 0, "bar": 5.5,
 "tracks": [
  T("m_n72.ogg", 0, A("c1a", off=1.5), CHO.format("in E minor, Op. 72 No. 1"), start=0.0, fade_in=0.8),
  T("m_dreaming.ogg", A("cold5", end=True, off=-0.5), A("c2a", off=1.5), SCH.format("Dreaming"), start=0.0),
  T("m_n37.ogg", A("c1h", end=True, off=-0.5), A("c3a", off=1.5), CHO.format("Op. 37 No. 1"), start=0.0),
  T("m_poet.ogg", A("c2f", end=True, off=-0.5), A("c4a", off=1.5), SCH.format("The Poet Speaks"), start=0.0),
  T("m_n55.ogg", A("c3g", end=True, off=-0.5), A("c5a", off=1.5), CHO.format("Op. 55 No. 1"), start=0.0),
  T("m_n37.ogg", A("c4i", end=True, off=-0.5), A("c6a", off=1.5), CHO.format("Op. 37 No. 1"), start=60.0),
  T("m_fright.ogg", A("c5h", end=True, off=-0.5), A("c6e", off=0.5), SCH.format("Frightening"), start=0.0),
  T("m_n72.ogg", A("c6d", end=True, off=-0.5), A("c7a", off=1.5), CHO.format("in E minor, Op. 72 No. 1"), start=40.0),
  T("m_asleep.ogg", A("c6g", end=True, off=-0.5), A("c7h", off=1.5), SCH.format("Child Falling Asleep"), start=0.0),
  T("m_dreaming.ogg", A("c7g", end=True, off=-0.5), None, SCH.format("Dreaming"), start=0.0, fade_out=8.0),
 ],
})
