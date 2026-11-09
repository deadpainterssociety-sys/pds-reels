# Visual plan for long video #3 (executed by plan.py: A, sh, ov, IM, MUSIC, SFX are in scope).
# Only public-domain images (the CC BY-SA hell scan, Harrewijn print and Sigüenza photo were dropped on purpose).
# Nudity: the garden is full of small nudes; close-ups go to owls, birds, fruit, monsters, instruments and faces.
P = lambda **kw: kw
IM.update({
 "garden": P(file="src/garden.jpg", depth=True, long=3840, points={
     "left_panel": [0.12, 0.5], "centre_panel": [0.505, 0.5], "hell_panel": [0.88, 0.5], "fountain": [0.505, 0.27],
     "riders": [0.48, 0.36], "pool": [0.505, 0.43], "owl_l": [0.262, 0.645], "owl_r": [0.716, 0.635], "eden": [0.13, 0.66]}),
 "centre": P(file="src/centre.jpg", depth=True, points={
     "owl_l": [0.035, 0.645], "owl_r": [0.905, 0.635], "pool": [0.5, 0.43], "riders": [0.45, 0.36], "fountain": [0.5, 0.25],
     "tower": [0.18, 0.17], "birds": [0.14, 0.57], "fruit": [0.37, 0.62], "sky": [0.5, 0.08], "mussel": [0.3, 0.71]}),
 "left": P(file="src/left.jpg", depth=True, points={"god": [0.52, 0.69], "fountain": [0.5, 0.38], "top": [0.5, 0.1], "animals": [0.5, 0.86]}),
 "hell_pd": P(file="src/hell_pd.jpg", depth=True, points={
     "fire": [0.5, 0.1], "ears": [0.28, 0.28], "tree_face": [0.59, 0.355], "tree": [0.42, 0.40], "tavern": [0.33, 0.40],
     "prince": [0.82, 0.66], "instruments": [0.25, 0.66], "butt": [0.17, 0.77], "pignun": [0.91, 0.93], "lake": [0.65, 0.55]}),
 "closed": P(file="src/closed.jpg", points={"god": [0.135, 0.13], "words": [0.49, 0.075], "sphere": [0.5, 0.5], "land": [0.35, 0.58]}),
 "instruments": P(file="src/instruments.jpg", depth=True, points={"lute": [0.14, 0.55], "harp": [0.25, 0.3], "butt": [0.30, 0.86],
     "book": [0.13, 0.92], "sinner": [0.32, 0.88]}),
 "prince": P(file="src/prince.jpg", depth=True, points={"head": [0.58, 0.38], "throne": [0.5, 0.7]}),
 "treeman": P(file="src/treeman.jpg", depth=True, points={"face": [0.62, 0.9], "disk": [0.5, 0.55], "bagpipe": [0.45, 0.35]}),
 "knife": P(file="src/knife.jpg", points={"blade": [0.5, 0.55]}),
 "strawberry": P(file="src/strawberry.jpg", depth=True, points={"berry": [0.5, 0.45]}),
 "egg": P(file="src/egg.jpg", points={"egg": [0.35, 0.45]}),
 "owl_fountain": P(file="src/owl_fountain.jpg", depth=True, points={"owl": [0.51, 0.53]}),
 "owl_boy": P(file="src/owl_boy.jpg", depth=True, points={"eyes": [0.4, 0.4]}),
 "bosch": P(file="src/bosch.jpg", crop=[0.03, 0.03, 0.03, 0.2], points={"face": [0.47, 0.25]}),
 "lakenmarkt": P(file="src/lakenmarkt.jpg", depth=True, points={"street": [0.5, 0.25], "stalls": [0.5, 0.5], "people": [0.45, 0.85]}),
 "haywain": P(file="src/haywain.jpg", depth=True, points={"wagon": [0.5, 0.45], "hell": [0.88, 0.5]}),
 "engelbert": P(file="src/engelbert.jpg", crop=[0.07, 0.05, 0.07, 0.05], points={"face": [0.5, 0.26]}),
 "henry": P(file="src/henry.jpg", depth=True, points={"face": [0.6, 0.27], "hands": [0.6, 0.85]}),
 "curia": P(file="src/curia.png", depth=True, points={"palace": [0.5, 0.45], "square": [0.3, 0.6]}),
 "william": P(file="src/william.jpg", depth=True, points={"face": [0.56, 0.35]}),
 "alba": P(file="src/alba.jpg", depth=True, points={"face": [0.5, 0.17], "baton": [0.65, 0.75]}),
 "philip": P(file="src/philip.jpg", depth=True, points={"face": [0.52, 0.21], "hand": [0.15, 0.78]}),
 "escorial": P(file="src/escorial.jpg", depth=True, points={"church": [0.5, 0.3], "front": [0.5, 0.55], "people": [0.4, 0.85]}),
 "siguenza2": P(file="src/siguenza2.jpg", points={"face": [0.4, 0.38]}),
 "siguenza3": P(file="src/siguenza3.jpg", crop=[0.08, 0.04, 0.08, 0.04], points={"monk": [0.5, 0.32], "pen": [0.4, 0.38]}),
})

J = lambda pins, **kw: {"id": "journey", "pins": pins, **kw}
# ---------------------------------------------------------------- shots
sh(A("cold1"), "owl_boy", "eyes@1.3", "eyes@1.12")
sh(A("cold1", "means", off=-0.1), "garden", "full@1.0", "full@1.04", hit="big")
sh(A("cold2"), "philip", "face@1.5", "face@1.7", fade=0.5, gray=0.4)
sh(A("cold2", "Not", 2), "escorial", "church@1.4", "church@1.6", fade=0.5, gray=0.4)
sh(A("cold2", "Not", 3), "centre", "riders@1.9", "pool@2.0", fade=0.6)
sh(A("cold3"), "bosch", "full@0.62", "face@0.9", frame=True, fade=0.8)
sh(A("cold3", "not"), "garden", "centre_panel@1.6", "centre_panel@1.75", fade=0.6)
sh(A("cold4"), "centre", "pool@2.2", "pool@2.5", fade=0.6)
sh(A("cold4", "and"), "centre", "fountain@1.8", "tower@2.0", fade=0.6)
sh(A("cold4", "party"), "centre", "riders@2.4", "riders@2.6", fade=0.3)
sh(A("cold4", "sermon"), "hell_pd", "fire@1.2", "fire@1.35", fade=0.3)
sh(A("cold4", "heresy"), "hell_pd", "tree_face@2.4", "tree_face@2.7", fade=0.3)
sh(A("cold4", "song"), "instruments", "book@2.0", "book@2.3", fade=0.3)
sh(A("cold5"), "garden", "full@0.86", "full@0.9", frame=True, fade=1.0)
sh(A("cold5", "and"), "garden", "full@1.0", "full@1.06", fade=1.0)
# I. The Painter
sh(A("c1a"), "map-journey", kind="map", map=J([{"city": "hertogenbosch", "at": A("c1a", "'s-Hertogenbosch"), "label": "'s-Hertogenbosch"}]), fade=0.8)
sh(A("c1a", "His"), "bosch", "face@1.2", "face@1.4", fade=0.8)
sh(A("c1b"), "lakenmarkt", "street@1.4", "street@1.6", fade=0.8)
sh(A("c1b", "Painting"), "lakenmarkt", "people@1.6", "people@1.8", fade=0.6)
sh(A("c1c"), "lakenmarkt", "stalls@1.3", "stalls@1.5", fade=0.8, gray=0.3)
sh(A("c1d"), "haywain", "full@1.0", "full@1.05", fade=0.8)
sh(A("c1d", "He", 2), "haywain", "wagon@1.7", "wagon@1.9", fade=0.6)
sh(A("c1e"), "bosch", "face@1.5", "face@1.7", fade=0.8)
sh(A("c1e", "Just"), "lakenmarkt", "street@1.8", "stalls@1.8", fade=0.8, gray=0.5)
sh(A("c1f"), "garden", "full@1.0", "full@1.08", fade=1.0)
# II. The Doors
sh(A("c2a"), "garden", "full@0.8", "full@0.84", frame=True, fade=1.0)
sh(A("c2b"), "closed", "full@0.56", "full@0.6", frame=True, fade=1.0)
sh(A("c2b", "A"), "closed", "sphere@1.1", "land@1.4", fade=0.6)
sh(A("c2c"), "closed", "sphere@1.0", "sphere@1.1", fade=0.6)
sh(A("c2c", "Up"), "closed", "god@1.9", "god@2.0", fade=0.6)
sh(A("c2c", "Across"), "closed", "words@1.8", "words@1.9", fade=0.6)
sh(A("c2d"), "closed", "full@0.6", "full@0.62", frame=True, fade=0.5)
sh(A("c2d", "open", off=-0.05), "garden", "full@1.0", "full@1.04", hit="big")
sh(A("c2e"), "left", "top@1.1", "fountain@1.1", fade=0.8)
sh(A("c2e", "God"), "left", "full@0.42", "full@0.45", frame=True, fade=0.8)
sh(A("c2e", "The", 2), "left", "fountain@1.2", "fountain@1.35", fade=0.8)
sh(A("c2e", "and"), "left", "animals@1.3", "animals@1.45", fade=0.6)
sh(A("c2f"), "hell_pd", "fire@1.1", "fire@1.25", fade=0.8)
sh(A("c2f", "torture"), "knife", "blade@1.1", "blade@1.25", fade=0.4)
sh(A("c2f", "and"), "hell_pd", "instruments@1.6", "instruments@1.8", fade=0.5)
sh(A("c2f2"), "prince", "head@1.2", "head@1.4", fade=0.6)
sh(A("c2f2", "and"), "prince", "throne@1.1", "throne@1.2", fade=0.5)
sh(A("c2f2", "A", 2), "hell_pd", "pignun@3.0", "pignun@3.3", fade=0.6)
sh(A("c2f2", "And", 2), "hell_pd", "tree@1.6", "tree@1.8", fade=0.6)
sh(A("c2f2", "One"), "treeman", "face@1.6", "face@1.9", fade=0.6)
sh(A("c2g"), "centre", "full@1.0", "full@1.05", fade=1.0)
sh(A("c2g", "Crowds"), "centre", "riders@1.7", "pool@1.8", fade=0.5)
sh(A("c2g", "Giant"), "centre", "birds@2.2", "birds@2.4", fade=0.4)
sh(A("c2g", "Giant", 2), "strawberry", "berry@1.1", "berry@1.25", fade=0.4)
sh(A("c2g", "Riders"), "centre", "pool@2.3", "pool@2.5", fade=0.4)
sh(A("c2g", "Strange"), "centre", "tower@2.0", "fountain@2.0", fade=0.5)
sh(A("c2h"), "centre", "owl_l@2.6", "owl_l@2.9", fade=0.6)
sh(A("c2h", "Or"), "hell_pd", "lake@1.6", "lake@1.8", fade=0.5)
sh(A("c2h", "People"), "garden", "full@1.0", "full@1.06", fade=0.8)
# III. The Palace
sh(A("c3a"), "bosch", "face@1.3", "face@1.5", fade=0.8)
sh(A("c3a", "The"), "garden", "centre_panel@1.5", "centre_panel@1.6", fade=0.8, gray=0.3)
sh(A("c3b"), "map-journey", kind="map", map=J([{"city": "hertogenbosch", "at": A("c3b"), "label": "'s-Hertogenbosch"},
   {"city": "brussels", "at": A("c3b", "Brussels"), "label": "Brussels"}]), fade=0.8)
sh(A("c3b", "they"), "henry", "face@1.2", "face@1.4", fade=0.8)
sh(A("c3c"), "garden", "full@0.86", "full@0.9", frame=True, fade=0.8)
sh(A("c3c", "that"), "hell_pd", "ears@2.0", "ears@2.2", fade=0.8, dim=0.2)
sh(A("c3d"), "curia", "palace@1.2", "palace@1.4", fade=0.8)
sh(A("c3d", "the", 2), "curia", "square@1.4", "square@1.6", fade=0.8, dim=0.2, gray=0.3)
sh(A("c3e"), "centre", "fountain@1.6", "fountain@1.8", fade=0.8)
sh(A("c3e", "Others"), "curia", "palace@1.5", "palace@1.7", fade=0.8, gray=0.3)
sh(A("c3e", "as"), "hell_pd", "ears@1.6", "ears@1.8", fade=0.6)
sh(A("c3f"), "egg", "egg@1.2", "egg@1.35", fade=0.5)
sh(A("c3g"), "engelbert", "face@1.05", "face@1.2", fade=0.8)
sh(A("c3g", "and"), "henry", "face@1.4", "face@1.6", fade=0.8)
# IV. The Duke
sh(A("c4a"), "william", "face@1.2", "face@1.4", fade=0.8)
sh(A("c4b"), "map-journey", kind="map", map=J([{"city": "brussels", "at": A("c4b"), "label": "Brussels"}]), fade=0.8)
sh(A("c4b", "And"), "william", "face@1.35", "face@1.5", fade=0.6, gray=0.4)
sh(A("c4c"), "alba", "face@1.3", "face@1.5", fade=0.8)
sh(A("c4c", "seizes"), "alba", "baton@1.2", "face@1.1", fade=0.6, gray=0.3)
sh(A("c4c", "The", 3), "garden", "full@0.9", "full@0.95", frame=True, fade=0.6, gray=0.5)
sh(A("c4d"), "alba", "face@1.7", "face@1.9", fade=0.8, gray=0.4)
sh(A("c4d", "It"), "map-journey", kind="map", map=J([{"city": "brussels", "at": A("c4d", "It"), "label": "Brussels"},
   {"city": "escorial", "at": A("c4d", "Spain"), "label": "Spain"}],
   route={"from": "brussels", "to": "escorial", "at": A("c4d", "It", off=0.2), "to_at": A("c4d", end=True)}), fade=0.6)
sh(A("c4e"), "garden", "centre_panel@1.4", "centre_panel@1.5", fade=0.8, gray=0.3)
sh(A("c4e", "the"), "philip", "full@1.0", "face@1.2", fade=0.8)
# V. The King and the Monk
sh(A("c5a"), "philip", "face@1.5", "face@1.7", fade=0.8)
sh(A("c5a", "And"), "haywain", "hell@1.8", "hell@2.0", fade=0.6)
sh(A("c5b"), "escorial", "full@1.0", "church@1.2", fade=0.8)
sh(A("c5b", "in", 2), "map-journey", kind="map", map=J([{"city": "escorial", "at": A("c5b", "in", 2), "label": "El Escorial"}]), fade=0.6)
sh(A("c5c"), "garden", "full@1.0", "full@1.05", fade=0.8)
sh(A("c5c", "The", 2), "strawberry", "berry@1.2", "berry@1.4", fade=0.6)
sh(A("c5d"), "hell_pd", "tree_face@2.0", "tree_face@2.3", fade=0.8, dim=0.15)
sh(A("c5e"), "siguenza3", "full@0.6", "monk@0.8", frame=True, fade=0.8)
sh(A("c5e", "Fray"), "siguenza2", "face@1.2", "face@1.35", fade=0.8)
sh(A("c5f"), "strawberry", "berry@1.0", "berry@1.15", fade=0.8)
sh(A("c5f", "Sweet"), "centre", "fruit@2.2", "fruit@2.4", fade=0.5)
sh(A("c5f", "and"), "strawberry", "berry@1.3", "berry@1.5", fade=0.6, gray=0.4)
sh(A("c5g"), "siguenza2", "face@1.4", "face@1.6", fade=0.8)
sh(A("c5g", "show"), "garden", "full@0.95", "full@1.0", fade=0.6)
sh(A("c5g", "Bosch", 2), "hell_pd", "tavern@2.4", "tavern@2.7", fade=0.6)
sh(A("c5h"), "escorial", "front@1.3", "people@1.5", fade=0.8, gray=0.3)
# VI. The Heretic
sh(A("c6a"), "centre", "full@1.0", "full@1.05", fade=0.8, gray=0.5)
sh(A("c6b"), "centre", "pool@1.8", "pool@2.0", fade=0.8)
sh(A("c6b", "It's"), "centre", "riders@1.8", "riders@2.0", fade=0.6)
sh(A("c6c"), "owl_fountain", "owl@1.1", "owl@1.3", fade=0.8)
sh(A("c6c", "and"), "centre", "tower@2.1", "tower@2.3", fade=0.6)
sh(A("c6d"), "centre", "birds@1.9", "birds@2.1", fade=0.6)
sh(A("c6e"), "lakenmarkt", "people@1.4", "people@1.6", fade=0.8, gray=0.4)
sh(A("c6e", "And"), "philip", "face@1.6", "face@1.8", fade=0.6)
sh(A("c6f"), "garden", "full@1.0", "full@1.04", fade=0.8)
sh(A("c6f", "Between"), "garden", "left_panel@2.4", "left_panel@2.6", fade=0.6)
sh(A("c6f", "and"), "garden", "hell_panel@2.4", "hell_panel@2.6", fade=0.6)
# VII. The Song
sh(A("c7a"), "hell_pd", "instruments@1.2", "instruments@1.35", fade=0.8)
sh(A("c7b"), "hell_pd", "instruments@1.6", "butt@1.6", fade=0.8)
sh(A("c7b", "is"), "instruments", "full@1.0", "full@1.08", fade=0.6)
sh(A("c7c"), "instruments", "lute@1.5", "lute@1.7", fade=0.6)
sh(A("c7c", "And"), "instruments", "sinner@1.9", "butt@2.3", fade=0.6)
sh(A("c7d"), "instruments", "book@2.0", "book@2.2", fade=0.6)
sh(A("c7d", "The", 2), "instruments", "butt@2.2", "butt@2.4", fade=0.6)
sh(A("c7e"), "instruments", "full@1.1", "full@1.2", fade=0.8, gray=0.3)
sh(A("c7e", "Scholars"), "instruments", "book@2.4", "book@2.6", fade=0.6, gray=0.3)
sh(A("c7f"), "instruments", "butt@2.5", "butt@2.7", fade=0.6)
sh(A("c7f", "Bosch"), "haywain", "hell@1.8", "hell@2.0", fade=0.6)
sh(A("c7f", "It"), "instruments", "book@2.2", "book@2.0", fade=0.6)
sh(A("c7g"), "instruments", "lute@1.3", "lute@1.4", fade=0.8, dim=0.35)
# ending
sh(A("end1"), "garden", "full@1.0", "full@1.03", fade=0.8)
sh(A("end1", "Five"), "centre", "full@1.0", "full@1.06", fade=0.8)
sh(A("end2"), "owl_boy", "eyes@1.0", "eyes@1.12", fade=0.8)
sh(A("end2", "At"), "owl_boy", "eyes@1.45", "eyes@1.65", fade=0.4)
sh(A("end3"), "garden", "full@0.86", "full@0.84", frame=True, fade=1.0)

# ---------------------------------------------------------------- overlays
CH = [("cold5", "c1a", "I", "The Painter"), ("c1f", "c2a", "II", "The Doors"), ("c2h", "c3a", "III", "The Palace"),
      ("c3g", "c4a", "IV", "The Duke"), ("c4e", "c5a", "V", "The King and the Monk"), ("c5h", "c6a", "VI", "The Heretic"),
      ("c6f", "c7a", "VII", "The Song")]
ov("title", A("cold5", "and"), A("cold5", end=True, off=0.6), kicker="HIERONYMUS BOSCH · c. 1490–1500", text="The Garden of Earthly Delights")
for prev, nxt, n, name in CH:
    if n == "I": continue
    ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("chapter", A("c1a", off=-0.55), A("c1a", off=2.0), kicker="CHAPTER I", text="The Painter")
ov("label", A("cold1", off=0.3), A("cold1", end=True, off=0.6), text="THE GARDEN OF EARTHLY DELIGHTS · PRADO")
ov("label", A("cold2"), A("cold2", "Not", 2, off=-0.1), text="PHILIP II · TITIAN")
ov("label", A("cold2", "Not", 2), A("cold2", "Not", 3, off=-0.1), text="EL ESCORIAL · LOUIS DE CAULLERY")
ov("label", A("cold3"), A("cold3", "not", off=-0.1), text="PORTRAIT DRAWING · c. 1550 · ARRAS")
ov("lower", A("c1a", "His", off=0.1), A("c1a", end=True, off=0.6), text="Jheronimus van Aken", sub="c. 1450–1516 · DRAWING, c. 1550")
ov("label", A("c1b"), A("c1c", end=True), text="'S-HERTOGENBOSCH · THE CLOTH MARKET · c. 1530")
ov("label", A("c1d"), A("c1d", end=True, off=0.4), text="BOSCH · THE HAYWAIN · PRADO")
ov("label", A("c1e", "Just"), A("c1e", end=True, off=0.4), text="'S-HERTOGENBOSCH · c. 1530")
ov("stamp", A("c1f", "twenty-five", off=0.1), A("c1f", end=True, off=0.3), text="25 PAINTINGS")
ov("label", A("c2b"), A("c2c", end=True), text="THE OUTER PANELS · GRISAILLE")
ov("ring", A("c2c", "Up", off=0.3), A("c2c", "Across", off=-0.2), point="god", img="closed", rx=90, ry=110, rot=0)
ov("quote", A("c2c", "For", off=-0.1), A("c2c", end=True, off=0.6), text="For he spake, and it was done. For he commanded, and they were created.",
   sub="PSALMS 33:9 AND 148:5 · INSCRIBED ON THE OUTER PANELS")
ov("label", A("c2e"), A("c2e", end=True, off=0.3), text="LEFT PANEL · THE GARDEN OF EDEN")
ov("label", A("c2f"), A("c2f2", end=True, off=0.3), text="RIGHT PANEL · HELL")
ov("ring", A("c2f2", "One", off=0.2), A("c2f2", end=True, off=0.6), point="face", img="treeman", rx=170, ry=150, rot=0)
ov("label", A("c2g"), A("c2h", "People", off=-0.1), text="CENTRE PANEL · THE GARDEN")
ov("ring", A("c2h", off=0.3), A("c2h", "Or", off=-0.1), point="owl_l", img="centre", rx=150, ry=170, rot=0)
ov("year", A("c3a"), A("c3a", "The", off=-0.1), text="AUGUST 1516")
ov("year", A("c3b"), A("c3b", "Antonio", off=-0.2), text="1517")
ov("lower", A("c3b", "Antonio", off=-0.05), A("c3b", "In", 2, off=-0.2), text="Antonio de Beatis", sub="SECRETARY TO CARDINAL LUIGI D'ARAGONA · NO PORTRAIT")
ov("lower", A("c3b", "they", off=0.4), A("c3b", end=True, off=0.8), text="Henry III of Nassau", sub="1483–1538 · JAN GOSSAERT")
ov("quote", A("c3c", "that", off=-0.1), A("c3c", end=True, off=0.9), text="There are some panels on which bizarre things have been painted.",
   sub="ANTONIO DE BEATIS · TRAVEL JOURNAL, 1517")
ov("label", A("c3d"), A("c3d", "the", 2, off=-0.1), text="BRUSSELS · THE COURT QUARTER · 17TH-C. PRINT")
ov("quote", A("c3d", "the", 2, off=-0.1), A("c3d", end=True, off=0.9), text="The Count had it made because he liked to hold frequent banquets and to see his guests get drunk.",
   sub="ANTONIO DE BEATIS · TRAVEL JOURNAL, 1517 (TR. J. R. HALE)")
ov("lower", A("c3g", "Engelbert", off=-0.1), A("c3g", "and", off=-0.1), text="Engelbert II of Nassau", sub="DIED 1504 · RIJKSMUSEUM")
ov("lower", A("c4a", "William", off=-0.1), A("c4a", end=True, off=0.8), text="William of Orange", sub="1533–1584 · ADRIAEN THOMASZ. KEY")
ov("year", A("c4c"), A("c4c", "the", off=-0.1), text="1568")
ov("lower", A("c4c", "the", 2, off=-0.05), A("c4c", "seizes", off=-0.1), text="The Duke of Alba", sub="1507–1582 · ANTONIS MOR")
ov("year", A("c4e", "And"), A("c4e", "the", off=-0.1), text="1591")
ov("lower", A("c4e", "Philip", off=-0.1), A("c4e", end=True, off=1.2), text="Philip II of Spain", sub="1527–1598 · TITIAN")
ov("label", A("c5a", "And"), A("c5a", end=True, off=0.3), text="BOSCH · THE HAYWAIN · HELL (DETAIL)")
ov("year", A("c5b"), A("c5b", "he", off=-0.1), text="1593")
ov("label", A("c5b", "he"), A("c5b", "in", 2, off=-0.1), text="EL ESCORIAL · LOUIS DE CAULLERY")
ov("title", A("c5c", "a", off=-0.1), A("c5c", "And", off=-0.1), kicker="ESCORIAL DELIVERY RECORD · 1593", text="The Variety of the World")
ov("title", A("c5c", "The", 2, off=-0.1), A("c5c", end=True, off=0.7), kicker="«DEL MADROÑO»", text="The Strawberry Tree")
ov("year", A("c5e"), A("c5e", "a", off=-0.1), text="1605")
ov("lower", A("c5e", "Fray", off=-0.05), A("c5e", end=True, off=0.8), text="Fray José de Sigüenza", sub="1544–1606 · LIBRARIAN AND HISTORIAN OF EL ESCORIAL")
ov("year", A("c6a", "in"), A("c6a", "a", off=-0.1), text="1947")
ov("lower", A("c6a", "Wilhelm", off=-0.1), A("c6a", end=True, off=0.8), text="Wilhelm Fraenger", sub="GERMAN ART HISTORIAN · NO PUBLIC-DOMAIN PORTRAIT")
ov("label", A("c6c"), A("c6c", "and", off=-0.1), text="LEFT PANEL · THE FOUNTAIN OF LIFE")
ov("quote", A("c6f", "as", off=-0.1), A("c6f", "Between", off=-0.1), text="A false Paradise given over to the sin of lust.", sub="MUSEO DEL PRADO")
ov("year", A("c7a", "in"), A("c7a", "the", off=-0.1), text="FEBRUARY 2014")
ov("lower", A("c7b", "Amelia", off=-0.1), A("c7b", end=True, off=0.5), text="Amelia Hamrick", sub="MUSIC STUDENT · OKLAHOMA CHRISTIAN UNIVERSITY")
ov("ring", A("c7c", "there", off=0.1), A("c7c", end=True, off=0.6), point="butt", img="instruments", rx=200, ry=150, rot=-10)
ov("label", A("c7f", "Bosch"), A("c7f", "It", off=-0.1), text="BOSCH · THE HAYWAIN · HELL (DETAIL)")
ov("quote", A("c7g", "I", off=-0.1), A("c7g", end=True, off=1.2), text="I think Bosch may have just been slapping notes up there to make it look like music.",
   sub="AMELIA HAMRICK · ASSOCIATED PRESS, 2014")
ov("pin", A("end3", off=0.1), A("end3", end=True, off=1.0), text="MUSEO DEL PRADO · MADRID · ROOM 56A")
ov("end", A("end3", end=True, off=1.0), A("end3", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound
SFX += [
 {"at": A("cold1", "means"), "fx": "impact", "gain": 0.35},
 {"at": A("c2d", "open"), "fx": "impact", "gain": 0.4},
 {"at": A("c4c", "seizes"), "fx": "tick", "gain": 0.3},
 {"at": A("c7c", "notes"), "fx": "chime", "gain": 0.25},
 {"at": A("end2", "At"), "fx": "chime", "gain": 0.2},
] + [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.3} for prev, _, n, _ in CH if n != "I"] + \
    [{"at": A("c1a", off=-0.55), "fx": "impact", "gain": 0.3}]
DM = [[38, 45, 50], [38, 45, 49], [34, 41, 50], [33, 40, 49]]
AM = [[33, 40, 48], [29, 36, 45], [36, 43, 52], [28, 40, 44]]
EM = [[28, 40, 47], [36, 43, 48], [31, 38, 47], [35, 42, 47]]
MUSIC.update({"bar": 5.5, "music_db": -13, "transpose": 1, "chords": AM,
         "segments": [{"at": A("c1a"), "chords": DM, "transpose": 1}, {"at": A("c2a"), "chords": EM, "transpose": 2},
                      {"at": A("c3a"), "chords": AM, "transpose": 0}, {"at": A("c4a"), "chords": DM, "transpose": -1},
                      {"at": A("c5a"), "chords": EM, "transpose": 1}, {"at": A("c6a"), "chords": AM, "transpose": 2},
                      {"at": A("c7a"), "chords": DM, "transpose": 0}, {"at": A("end1"), "chords": AM, "transpose": 1}],
         "sections": {"cold": [A("cold1"), A("cold3", end=True)], "choir": [A("c2d", off=-0.2), A("c2e", off=-0.3)],
                      "drop": [A("c7d", "The", 2), A("c7d", end=True, off=0.3)]},
         "heartbeat": [A("c2c"), A("c2d", "open", off=-0.2)]})
