# Visual plan v2 for long video #3 (15 Nov 2026 rework: Enceladus voice, Satie cue sheet, calmer cuts — roughly one shot per
# narrated line, slow travelling moves across the painting instead of a cut on every phrase). Executed by plan.py: A, sh, ov,
# IM, MUSIC, SFX are in scope. Only public-domain images. The triptych and its details are cut from the Prado's 30000 px file
# by crops.py (garden, left, centre, hell, fire, ears, treeman, instruments, pignun, prince; signature from The Haywain).
P = lambda **kw: kw
HR = "File:The Garden of Earthly Delights by Bosch High Resolution.jpg"
D = "File:Bosch, Hieronymus - The Garden of Earthly Delights, "
IM.update({
 # ---- the triptych (crops.py)
 "garden": P(file="src/garden.jpg", from_commons=HR, depth=True, long=5120, points={
     "left_panel": [0.115, 0.497], "centre_panel": [0.5, 0.497], "hell_panel": [0.885, 0.497], "owl_l": [0.254, 0.643],
     "owl_r": [0.719, 0.633], "fountain": [0.5, 0.239], "pool": [0.5, 0.425], "riders": [0.48, 0.352],
     "instruments": [0.804, 0.661], "fire": [0.885, 0.105], "treeman": [0.88, 0.4]}),
 "left": P(file="src/left.jpg", from_commons=HR, depth=True, long=7200, points={
     "top": [0.41, 0.063], "fountain_top": [0.5, 0.187], "elephant": [0.32, 0.26], "giraffe": [0.765, 0.29],
     "fountain_globe": [0.5, 0.461], "god": [0.521, 0.703], "animals": [0.41, 0.837], "pond": [0.5, 0.888]}),
 "centre": P(file="src/centre.jpg", from_commons=HR, depth=True, long=7200, points={
     "towers": [0.5, 0.15], "fountain": [0.5, 0.25], "top": [0.5, 0.27], "lake": [0.35, 0.27], "riders": [0.45, 0.35],
     "pool": [0.5, 0.42], "birds": [0.12, 0.56], "fruit": [0.37, 0.62], "owl_l": [0.03, 0.645], "owl_r": [0.89, 0.62],
     "owls": [0.46, 0.63]}),
 "hell": P(file="src/hell.jpg", from_commons=HR, depth=True, long=7200, points={
     "fire": [0.494, 0.084], "lake": [0.494, 0.548], "ears": [0.18, 0.28], "face": [0.596, 0.373], "tavern": [0.364, 0.389],
     "instruments": [0.135, 0.651], "butt": [0.157, 0.727], "prince": [0.742, 0.636], "pignun": [0.854, 0.899]}),
 "fire": P(file="src/fire.jpg", from_commons=HR, depth=True, points={"left": [0.135, 0.44], "centre": [0.494, 0.352], "right": [0.81, 0.44]}),
 "ears": P(file="src/ears.jpg", from_commons=HR, depth=True, points={"ears": [0.326, 0.455], "knife": [0.55, 0.36]}),
 "treeman": P(file="src/treeman.jpg", from_commons=HR, depth=True, points={
     "ears": [0.12, 0.17], "disk": [0.66, 0.25], "face": [0.73, 0.465], "tavern": [0.3, 0.52], "body": [0.45, 0.58], "legs": [0.42, 0.8]}),
 "eden": P(file="src/eden.jpg", from_commons=HR, depth=True, points={"god": [0.386, 0.455], "eve": [0.88, 0.686], "adam": [0.066, 0.917]}),
 "instruments": P(file="src/instruments.jpg", from_commons=HR, depth=True, points={
     "lute": [0.158, 0.395], "harp": [0.42, 0.18], "hurdy": [0.74, 0.24], "choir": [0.47, 0.316], "butt": [0.368, 0.726],
     "book": [0.179, 0.805], "sinner": [0.316, 0.789], "toad": [0.58, 0.605]}),
 "pignun": P(file="src/pignun.jpg", from_commons=HR, depth=True, points={"pig": [0.619, 0.333], "man": [0.4, 0.367], "document": [0.516, 0.6]}),
 "prince": P(file="src/prince.jpg", from_commons=HR, depth=True, points={"head": [0.52, 0.22], "throne": [0.5, 0.45], "bubble": [0.62, 0.7]}),
 # ---- Commons details of the triptych (same panels, separate public-domain files)
 "owl_boy": P(file="src/owl_boy.jpg", commons=D + "central panel - Detail Owl with boy.jpg", depth=True, points={"eyes": [0.37, 0.39]}),
 "owl_fountain": P(file="src/owl_fountain.jpg", commons=D + "left panel - Detail Fountain Of Life with owl (center).jpg", depth=True,
                   points={"owl": [0.51, 0.48]}),
 "strawberry": P(file="src/strawberry.jpg", commons=D + "central panel - Detail Strawberry.jpg", depth=True, points={"berry": [0.5, 0.38]}),
 "birds": P(file="src/birds.jpg", commons=D + "central panel - Detail left bird feeding men.jpg", depth=True,
            points={"eye": [0.28, 0.28], "berry": [0.66, 0.58]}),
 # ---- the story around it
 "closed": P(file="src/closed_hr.jpg", commons="File:El Bosco - Tríptico del Jardín de las delicias.jpg", points={
     "god": [0.13, 0.12], "words": [0.3, 0.075], "words_r": [0.7, 0.075], "sphere": [0.5, 0.55], "land": [0.3, 0.58]}),
 "bosch": P(file="src/bosch.jpg", commons="File:Jheronimus Bosch.jpg", points={"face": [0.44, 0.27]}),
 "lakenmarkt": P(file="src/lakenmarkt.jpg", commons="File:De lakenmarkt te ’s-Hertogenbosch circa 1530 - Noordbrabants Museum.jpg",
                 depth=True, points={"street": [0.5, 0.15], "stalls": [0.5, 0.5], "people": [0.45, 0.85]}),
 "haywain": P(file="src/haywain.jpg", commons="File:Bosch - Haywain Triptych.jpg", depth=True, crop=[0.012, 0.025, 0.012, 0.025],
              points={"wagon": [0.5, 0.45], "hell": [0.87, 0.5], "eden": [0.13, 0.5]}),
 "signature": P(file="src/signature.jpg", from_commons="File:Bosch - Haywain Triptych.jpg", points={"name": [0.5, 0.69]}),
 "engelbert": P(file="src/engelbert.jpeg", commons="File:Portret van Engelbrecht II, graaf van Nassau Rijksmuseum SK-A-3140.jpeg",
                depth=True, crop=[0.08, 0.05, 0.08, 0.05], points={"face": [0.44, 0.32]}),
 "henry": P(file="src/henry.jpg", commons="File:Jan Gossaert - Henry III of Nassau-Breda - Google Art Project.jpg", depth=True,
            points={"face": [0.6, 0.3], "hands": [0.55, 0.85]}),
 "curia": P(file="src/curia.png", commons="File:Curia Brabantiae.png", points={"palace": [0.55, 0.4], "square": [0.3, 0.45]}),
 "william": P(file="src/william_pd.jpg", commons="File:William I, Prince of Orange by Adriaen Thomasz. Key Museo Thyssen-Bornemisza 208 (1928.7) - WGA12161.jpg",
              depth=True, points={"face": [0.52, 0.27]}),
 "alba": P(file="src/alba.jpg", commons="File:Fernando Álvarez de Toledo, III Duque de Alba, retratado por Antonio Moro.jpg", depth=True,
           points={"face": [0.42, 0.14], "baton": [0.6, 0.75]}),
 "philip": P(file="src/philip.jpg", commons="File:Philip II portrait by Titian.jpg", depth=True, points={"face": [0.52, 0.19], "hand": [0.25, 0.8]}),
 "escorial": P(file="src/escorial.jpg", commons="File:Louis de Caullery - View of the Royal Monastery of San Lorenzo de El Escorial.jpg",
               depth=True, points={"dome": [0.49, 0.18], "front": [0.5, 0.55], "people": [0.35, 0.85]}),
 "siguenza": P(file="src/siguenza_print.jpg", commons="File:Manuel salvador carmona-fray jose de Sigüenza.JPG", crop=[0.1, 0.06, 0.04, 0.3],
               points={"face": [0.71, 0.4], "book": [0.4, 0.6]}),
})

J = lambda pins, **kw: {"id": "journey", "pins": pins, **kw}
# ---------------------------------------------------------------- shots (about one per line; slow travelling moves)
# cold open: the owl, then the whole garden on the hook's last word
sh(A("cold1"), "owl_boy", "eyes@1.12", "eyes@1.0")
sh(A("cold1", "means", off=-0.1), "garden", "full@1.0", "centre_panel@1.35", hit="big", dolly=[0, 0.03])
sh(A("cold3"), "bosch", "face@1.0", "face@1.15", fade=0.8)
sh(A("cold4"), "garden", "centre_panel@1.7", "instruments@2.1", fade=0.8, dolly=[0, 0.02])
sh(A("cold5"), "garden", "full@0.84", "full@0.88", frame=True, fade=1.0)
# I. The Painter
sh(A("c1a"), "map-journey", kind="map", map=J([{"city": "hertogenbosch", "at": A("c1a", "'s-Hertogenbosch"), "label": "'s-Hertogenbosch"}]), fade=0.8)
sh(A("c1a", "His"), "bosch", "face@1.2", "face@1.4", fade=0.8)
sh(A("c1b"), "lakenmarkt", "street@1.15", "people@1.2", fade=0.8)
sh(A("c1d"), "signature", "name@1.0", "name@1.12", fade=0.8)
sh(A("c1e"), "bosch", "face@1.5", "face@1.7", fade=0.8)
sh(A("c1f"), "garden", "full@1.0", "full@1.08", fade=1.0, dolly=[0, 0.03])
# II. The Doors
sh(A("c2a"), "garden", "full@0.82", "full@0.86", frame=True, fade=1.0)
sh(A("c2b"), "closed", "full@0.5", "full@0.54", frame=True, fade=1.0)
sh(A("c2b", "A"), "closed", "sphere@1.0", "land@1.25", fade=0.8)
sh(A("c2c", "Up", off=-0.1), "closed", "god@1.35", "words@1.3", fade=0.8)
sh(A("c2d"), "closed", "full@0.5", "full@0.52", frame=True, fade=0.5)
sh(A("c2d", "open", off=-0.05), "garden", "full@1.0", "left_panel@1.45", hit="big")
sh(A("c2e", "God", off=-0.1), "eden", "full@1.0", "god@1.12", fade=0.8)
sh(A("c2f"), "hell", "fire@1.0", "instruments@1.05", fade=0.8)
sh(A("c2f2"), "prince", "head@1.15", "bubble@1.15", fade=0.8)
sh(A("c2f2", "pig", off=-0.2), "pignun", "pig@1.1", "document@1.2", fade=0.6)
sh(A("c2f2", "And", 2, off=-0.05), "treeman", "legs@1.0", "tavern@1.2", fade=0.6)
sh(A("c2f2", "One", off=-0.05), "treeman", "face@1.6", "face@1.8", fade=0.6)
sh(A("c2g"), "centre", "top@1.0", "top@1.06", fade=1.0, dolly=[0, 0.03])
sh(A("c2g", "Giant", off=-0.05), "centre", "birds@1.7", "pool@1.7", fade=0.6)
sh(A("c2h"), "garden", "centre_panel@1.4", "hell_panel@1.4", fade=0.8)
# III. The Palace
sh(A("c3a"), "garden", "centre_panel@1.25", "centre_panel@1.35", fade=1.0, gray=0.6)
sh(A("c3b"), "map-journey", kind="map", map=J([{"city": "hertogenbosch", "at": A("c3b"), "label": "'s-Hertogenbosch"},
   {"city": "brussels", "at": A("c3b", "Brussels"), "label": "Brussels"}]), fade=0.8)
sh(A("c3b", "they"), "henry", "face@1.2", "face@1.35", fade=0.8)
sh(A("c3c"), "ears", "ears@1.0", "knife@1.12", fade=0.8)
sh(A("c3d"), "curia", "palace@1.0", "square@1.05", fade=0.8, gray=0.3)
sh(A("c3e"), "centre", "fountain@1.5", "pool@1.6", fade=0.8)
sh(A("c3e", "Others", off=-0.05), "curia", "square@1.08", "palace@1.0", fade=0.8, gray=0.6)
sh(A("c3g"), "engelbert", "face@1.0", "face@1.1", fade=0.8)
# IV. The Duke
sh(A("c4a"), "william", "face@1.0", "face@1.2", fade=0.8)
sh(A("c4c"), "alba", "face@1.25", "face@1.05", fade=0.8)
sh(A("c4d"), "map-journey", kind="map", map=J([{"city": "brussels", "at": A("c4d"), "label": "Brussels"},
   {"city": "escorial", "at": A("c4d", "Spain"), "label": "Spain"}],
   route={"from": "brussels", "to": "escorial", "at": A("c4d", "It", off=0.2), "to_at": A("c4d", end=True)}), fade=0.8)
sh(A("c4e", "the", off=-0.05), "philip", "full@1.0", "face@1.3", fade=0.8)
# V. The King and the Monk
sh(A("c5a"), "haywain", "full@1.0", "wagon@1.15", fade=1.0)
sh(A("c5b"), "escorial", "full@1.0", "dome@1.25", fade=0.8)
sh(A("c5c"), "garden", "full@1.0", "full@1.06", fade=0.8, dolly=[0, 0.02])
sh(A("c5c", "strawberry", off=-0.25), "strawberry", "berry@1.0", "berry@1.12", fade=0.6)
sh(A("c5d"), "fire", "left@1.05", "right@1.05", fade=0.8, dim=-0.15)
sh(A("c5e"), "siguenza", "full@0.5", "full@0.53", frame=True, fade=0.8)
sh(A("c5f"), "birds", "eye@1.0", "berry@1.1", fade=0.8)
sh(A("c5g"), "siguenza", "full@0.53", "full@0.56", frame=True, fade=0.8)
sh(A("c5g", "Bosch", 2, off=-0.1), "treeman", "tavern@1.3", "tavern@1.5", fade=0.6)
sh(A("c5h"), "escorial", "front@1.2", "people@1.3", fade=0.8, gray=0.4)
# VI. The Heretic
sh(A("c6a"), "centre", "towers@1.2", "pool@1.45", fade=1.0)
sh(A("c6c"), "owl_fountain", "owl@1.0", "owl@1.2", fade=0.8)
sh(A("c6e"), "lakenmarkt", "people@1.4", "people@1.6", fade=0.8, gray=0.4)
sh(A("c6e", "And", off=-0.05), "philip", "face@1.5", "face@1.7", fade=0.6, gray=0.3)
sh(A("c6f"), "garden", "full@1.0", "full@1.04", fade=0.8)
sh(A("c6f", "Between", off=-0.05), "garden", "left_panel@1.9", "hell_panel@1.9", fade=0.6)
# VII. The Song
sh(A("c7a"), "hell", "lake@1.0", "instruments@1.15", fade=1.0)
sh(A("c7c"), "instruments", "lute@1.0", "butt@1.3", fade=0.8)
sh(A("c7d"), "instruments", "butt@1.6", "butt@1.85", fade=0.6)
sh(A("c7e"), "instruments", "full@1.0", "choir@1.15", fade=0.8, gray=0.4)
sh(A("c7f"), "instruments", "butt@1.7", "book@1.5", fade=0.8)
sh(A("c7g"), "instruments", "lute@1.2", "harp@1.3", fade=0.8, dim=0.3)
# ending
sh(A("end1"), "garden", "full@1.08", "full@1.0", fade=1.0, dolly=[0.03, 0])
sh(A("end2"), "centre", "owls@1.0", "owls@1.04", fade=0.8)
sh(A("end2", "At", off=-0.05), "owl_boy", "eyes@1.05", "eyes@1.2", fade=0.4)
sh(A("end3"), "garden", "full@0.84", "full@0.82", frame=True, fade=1.0)

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
ov("label", A("cold3"), A("cold3", end=True, off=0.4), text="PORTRAIT DRAWING · c. 1550 · ARRAS")
ov("lower", A("c1a", "His", off=0.1), A("c1a", end=True, off=0.6), text="Jheronimus van Aken", sub="c. 1450–1516 · DRAWING, c. 1550")
ov("label", A("c1b"), A("c1c", end=True), text="'S-HERTOGENBOSCH · THE CLOTH MARKET · c. 1530")
ov("label", A("c1d"), A("c1d", end=True, off=0.4), text="SIGNATURE · THE HAYWAIN · PRADO")
ov("stamp", A("c1f", "twenty-five", off=0.1), A("c1f", end=True, off=0.3), text="25 PAINTINGS")
ov("label", A("c2b"), A("c2c", "Up", off=-0.2), text="THE OUTER PANELS · GRISAILLE")
ov("ring", A("c2c", "Up", off=0.3), A("c2c", "Across", off=-0.2), point="god", img="closed", rx=90, ry=110, rot=0)
ov("quote", A("c2c", "For", off=-0.1), A("c2c", end=True, off=0.6), text="For he spake, and it was done. For he commanded, and they were created.",
   sub="PSALMS 33:9 AND 148:5 · INSCRIBED ON THE OUTER PANELS")
ov("label", A("c2e", "God"), A("c2e", end=True, off=0.3), text="LEFT PANEL · THE GARDEN OF EDEN")
ov("label", A("c2f"), A("c2f2", end=True, off=0.3), text="RIGHT PANEL · HELL")
ov("ring", A("c2f2", "One", off=0.2), A("c2f2", end=True, off=0.6), point="face", img="treeman", rx=170, ry=150, rot=0)
ov("label", A("c2g"), A("c2h", off=-0.1), text="CENTRE PANEL · THE GARDEN")
ov("year", A("c3a"), A("c3a", "The", off=-0.1), text="AUGUST 1516")
ov("year", A("c3b"), A("c3b", "Antonio", off=-0.2), text="1517")
ov("lower", A("c3b", "Antonio", off=-0.05), A("c3b", "In", 2, off=-0.2), text="Antonio de Beatis", sub="SECRETARY TO CARDINAL LUIGI D'ARAGONA · NO PORTRAIT")
ov("lower", A("c3b", "they", off=0.4), A("c3b", end=True, off=0.8), text="Henry III of Nassau", sub="1483–1538 · JAN GOSSAERT")
ov("quote", A("c3c", "that", off=-0.1), A("c3c", end=True, off=0.9), text="There are some panels on which bizarre things have been painted.",
   sub="ANTONIO DE BEATIS · TRAVEL JOURNAL, 1517")
ov("label", A("c3d"), A("c3d", "the", 2, off=-0.1), text="BRUSSELS · THE COURT QUARTER · 17TH-C. PRINT")
ov("quote", A("c3d", "the", 2, off=-0.1), A("c3d", end=True, off=0.9), text="The Count had it made because he liked to hold frequent banquets and to see his guests get drunk.",
   sub="ANTONIO DE BEATIS · TRAVEL JOURNAL, 1517 (TR. J. R. HALE)")
ov("lower", A("c3g", "Engelbert", off=-0.1), A("c3g", end=True, off=0.6), text="Engelbert II of Nassau", sub="DIED 1504 · RIJKSMUSEUM")
ov("lower", A("c4a", "William", off=-0.1), A("c4a", end=True, off=0.8), text="William of Orange", sub="1533–1584 · ADRIAEN THOMASZ. KEY")
ov("year", A("c4c"), A("c4c", "the", off=-0.1), text="1568")
ov("lower", A("c4c", "the", 2, off=-0.05), A("c4c", end=True, off=0.6), text="The Duke of Alba", sub="1507–1582 · ANTONIS MOR")
ov("year", A("c4e", "And"), A("c4e", "the", off=-0.1), text="1591")
ov("lower", A("c4e", "Philip", off=-0.1), A("c4e", end=True, off=1.2), text="Philip II of Spain", sub="1527–1598 · WORKSHOP OF TITIAN")
ov("label", A("c5a", off=0.8), A("c5a", end=True, off=0.3), text="BOSCH · THE HAYWAIN · PRADO")
ov("year", A("c5b"), A("c5b", "he", off=-0.1), text="1593")
ov("label", A("c5b", "he"), A("c5b", end=True, off=0.4), text="EL ESCORIAL · LOUIS DE CAULLERY")
ov("title", A("c5c", "a", off=-0.1), A("c5c", "And", off=-0.1), kicker="ESCORIAL DELIVERY RECORD · 1593", text="The Variety of the World")
ov("title", A("c5c", "strawberry", off=-0.25), A("c5c", end=True, off=0.7), kicker="«DEL MADROÑO»", text="The Strawberry Tree")
ov("year", A("c5e"), A("c5e", "a", off=-0.1), text="1605")
ov("lower", A("c5e", "Fray", off=-0.05), A("c5e", end=True, off=0.8), text="Fray José de Sigüenza", sub="1544–1606 · LIBRARIAN AND HISTORIAN OF EL ESCORIAL")
ov("year", A("c6a", "in"), A("c6a", "a", off=-0.1), text="1947")
ov("lower", A("c6a", "Wilhelm", off=-0.1), A("c6a", end=True, off=0.8), text="Wilhelm Fraenger", sub="GERMAN ART HISTORIAN · NO PUBLIC-DOMAIN PORTRAIT")
ov("label", A("c6c"), A("c6d", end=True, off=0.3), text="LEFT PANEL · THE FOUNTAIN OF LIFE")
ov("quote", A("c6f", "as", off=-0.1), A("c6f", "Between", off=-0.1), text="A false Paradise given over to the sin of lust.", sub="MUSEO DEL PRADO")
ov("year", A("c7a", "in"), A("c7a", "the", off=-0.1), text="FEBRUARY 2014")
ov("lower", A("c7b", "Amelia", off=-0.1), A("c7b", end=True, off=0.5), text="Amelia Hamrick", sub="MUSIC STUDENT · OKLAHOMA CHRISTIAN UNIVERSITY")
ov("ring", A("c7c", "there", off=0.1), A("c7c", end=True, off=0.6), point="butt", img="instruments", rx=200, ry=150, rot=-10)
ov("quote", A("c7g", "I", off=-0.1), A("c7g", end=True, off=1.2), text="I think Bosch may have just been slapping notes up there to make it look like music.",
   sub="AMELIA HAMRICK · ASSOCIATED PRESS, 2014")
ov("ring", A("end2", "two", off=0.1), A("end2", "At", off=-0.1), point="owl_l", img="centre", rx=110, ry=130, rot=0)
ov("ring", A("end2", "two", off=0.3), A("end2", "At", off=-0.1), point="owl_r", img="centre", rx=110, ry=130, rot=0)
ov("pin", A("end3", off=0.1), A("end3", end=True, off=1.0), text="MUSEO DEL PRADO · MADRID · ROOM 56A")
ov("end", A("end3", end=True, off=1.0), A("end3", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound: a Satie cue sheet (all piano; public domain / CC0 / CC BY)
SFX += [
 {"at": A("cold1", "means"), "fx": "impact", "gain": 0.35},
 {"at": A("c2d", "open"), "fx": "impact", "gain": 0.4},
 {"at": A("c7c", "notes"), "fx": "chime", "gain": 0.2},
 {"at": A("end2", "At"), "fx": "chime", "gain": 0.18},
] + [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.25} for prev, _, n, _ in CH if n != "I"] + \
    [{"at": A("c1a", off=-0.55), "fx": "impact", "gain": 0.25}]
LP = "La Pianista (Wikimedia Commons), public domain"
T = lambda f, frm, to, credit, **kw: {"file": f"src/music/{f}", "from": frm, **({"to": to} if to is not None else {}), "start": kw.pop("start", 0),
                                     "gain_db": kw.pop("gain_db", 0), "fade_in": kw.pop("fade_in", 2.5), "fade_out": kw.pop("fade_out", 3.0), "credit": credit}
MUSIC.update({
 "pad": False, "whooshes": False, "music_db": -7.5, "duck_db": -7, "fx_db": -12, "transpose": 1, "bar": 5.5,
 "_tracks_note": "Satie cue sheet (15 Nov 2026 rework): the Gnossiennes for the strange and the dark, the Gymnopédies for the calm "
                 "chapters; Gnossienne No. 1 opens and closes the film.",
 "tracks": [
  T("m_gnoss1.ogg", 0, A("c1a", off=1.0), f"Satie, Gnossienne No. 1 · {LP}", start=1.0, fade_in=0.8),
  T("m_gymno1.ogg", A("cold5", end=True), A("c2a", off=1.5), "Satie, Gymnopédie No. 1 · Robin Alciatore (Musopen), public domain", start=2.0),
  T("m_gnoss3.ogg", A("c1f", end=True), A("c2d", off=0.2), f"Satie, Gnossienne No. 3 · {LP}", start=2.2, fade_out=2.0),
  T("m_gnoss4.ogg", "c2d$-0.35", A("c3a", off=1.0), f"Satie, Gnossienne No. 4 · {LP}", start=1.0, fade_in=1.5),
  T("m_gnoss2.ogg", A("c2h", end=True), A("c4a", off=1.0), f"Satie, Gnossienne No. 2 · {LP}", start=0.8),
  T("m_gnoss6.ogg", A("c3g", end=True), A("c5a", off=1.0), f"Satie, Gnossienne No. 6 · {LP}", gain_db=-1),
  T("m_gymno3.ogg", A("c4e", end=True), A("c6a", off=1.0), "Satie, Gymnopédie No. 3 · Teknopazzo, CC0", gain_db=-1),
  T("m_gnoss5.ogg", A("c5h", end=True), A("c7a", off=1.0), f"Satie, Gnossienne No. 5 · {LP}", gain_db=-1),
  T("m_gymno2.ogg", A("c6f", end=True), A("end1", off=1.0), "Satie, Gymnopédie No. 2 · Kevin MacLeod (incompetech.com), CC BY 3.0", gain_db=-1),
  T("m_gnoss1.ogg", A("c7g", end=True), None, f"Satie, Gnossienne No. 1 · {LP}", start=1.0, fade_out=6.0),
 ],
 "sections": {"drop": [A("c3f"), A("c3f", end=True, off=0.3)]},
 "heartbeat": [A("c2d", off=-1.4), A("c2d", "open", off=-0.2)], "heartbeat_gain": 0.3,
})
