# Visual plan for long video #2 (executed by plan.py: A, sh, ov, IM, MUSIC, SFX are in scope).
P = lambda **kw: kw
IM.update({
 "raft": P(file="src/raft.jpg", depth=True, long=6000, points={
     "cloth": [0.70, 0.11], "waver": [0.705, 0.20], "argus": [0.813, 0.397], "old": [0.29, 0.57], "youth": [0.40, 0.71],
     "facedown": [0.455, 0.80], "mast": [0.37, 0.25], "pointer": [0.52, 0.35], "crowd": [0.62, 0.45], "left_dead": [0.10, 0.70],
     "right_dead": [0.85, 0.88], "waves": [0.08, 0.32], "sail": [0.25, 0.25], "sky": [0.85, 0.15], "planks": [0.45, 0.9]}),
 "argus_sketch": P(file="src/argus_sketch.jpg", depth=True, points={"waver": [0.62, 0.28], "raft": [0.45, 0.6]}),
 "salon1819": P(file="src/salon1819.jpg", depth=True, points={"waver": [0.58, 0.3], "raft": [0.45, 0.6]}),
 "mutiny": P(file="src/mutiny.jpg", points={"fight": [0.5, 0.5]}),
 "book": P(file="src/book.jpg", crop=[0.12, 0.12, 0.12, 0.36], points={"fight": [0.5, 0.55], "sail": [0.6, 0.15]}),
 "frigate": P(file="src/frigate.jpg", crop=[0.08, 0.09, 0.08, 0.13], points={"ship": [0.4, 0.35], "raft": [0.5, 0.72]}),
 "heads": P(file="src/heads.png", crop=[0.11, 0.11, 0.11, 0.12], depth=True, points={"young": [0.25, 0.25], "old": [0.68, 0.3]}),
 "limbs": P(file="src/limbs.jpg", points={"feet": [0.5, 0.4]}),
 "deathbed": P(file="src/deathbed.jpg", depth=True, points={"face": [0.5, 0.45]}),
 "delacroix": P(file="src/delacroix.jpg", crop=[0.2, 0.18, 0.18, 0.18], depth=True, points={"face": [0.52, 0.38]}),
 "dante": P(file="src/dante.jpg", depth=True, points={"dante": [0.45, 0.3], "bodies": [0.4, 0.75]}),
 "egyptian_hall": P(file="src/egyptian_hall.jpg", depth=True, points={"front": [0.55, 0.45]}),
 "louis18": P(file="src/louis18.jpg", crop=[0.08, 0.06, 0.08, 0.1], points={"face": [0.70, 0.26]}),
 "monomaniac": P(file="src/monomaniac.jpg", depth=True, points={"face": [0.42, 0.42]}),
 "plan": P(file="src/plan.jpg", points={"all": [0.5, 0.5]}),
 "rochefort": P(file="src/rochefort.jpg", depth=True, points={"ships": [0.3, 0.15], "dock": [0.5, 0.6]}),
 "gericault": P(file="src/gericault.jpg", crop=[0.2, 0.25, 0.2, 0.3], points={"face": [0.55, 0.33]}),
 "plaster": P(file="tex:plaster"),
})

# ---------------------------------------------------------------- shots
# cold open: the painting first (validate: shot 1 is a colour close-up of the main image)
sh(A("cold1"), "raft", "waver@2.2", "cloth@2.0")
sh(A("cold1", "really", off=-0.1), "raft", "full@1.0", "full@1.05", hit="big")
sh(A("cold2"), "raft", "crowd@1.6", "waver@1.8", fade=0.5)
sh(A("cold2", "waving"), "raft", "argus@3.2", "argus@3.6", fade=0.5)
sh(A("cold2", "Around"), "raft", "left_dead@1.6", "youth@1.7", fade=0.5)
sh(A("cold3"), "raft", "planks@1.4", "facedown@1.6", fade=0.6)
sh(A("cold3", "When"), "raft", "waver@1.5", "waver@1.8", fade=0.6)
sh(A("cold4"), "gericault", "face@1.2", "face@1.5", fade=0.8, gray=0.3)
sh(A("cold4", "filled"), "heads", "old@1.4", "young@1.4", fade=0.6)
sh(A("cold5"), "raft", "full@0.33", "full@0.35", frame=True, fade=1.0)
sh(A("cold5", "The", 2), "raft", "old@1.5", "old@1.8", fade=0.8)
sh(A("cold5", "and", 1), "raft", "full@0.31", "full@0.34", frame=True, fade=1.0, dim=0.15)
# I. The Captain
sh(A("c1a"), "louis18", "full@0.62", "face@1.3", frame=True, fade=1.0)
sh(A("c1b"), "map-voyage", kind="map", map={"id": "voyage", "pins": [{"city": "rochefort", "at": A("c1b", "Rochefort"), "label": "Rochefort"},
   {"city": "senegal", "at": A("c1b", "Senegal"), "label": "Saint-Louis, Senegal"}]}, fade=0.8)
sh(A("c1c"), "rochefort", "ships@1.3", "dock@1.1", fade=0.8)
sh(A("c1c", "On"), "rochefort", "dock@1.4", "dock@1.6", fade=0.5)
sh(A("c1d"), "rochefort", "ships@1.6", "ships@1.9", fade=0.8, gray=0.4)
sh(A("c1d", "He", 1), "raft", "sail@1.4", "mast@1.5", fade=0.6, dim=0.2)
sh(A("c1e"), "map-voyage", kind="map", map={"id": "voyage", "pins": [{"city": "rochefort", "at": A("c1e"), "label": "Rochefort"},
   {"city": "arguin", "at": A("c1f", "Arguin"), "label": "Arguin Bank"}],
   "route": {"from": "rochefort", "to": "arguin", "at": A("c1e", off=0.3), "to_at": A("c1f", "sandbank")}}, fade=0.8)
sh(A("c1f", "And"), "frigate", "ship@1.2", "ship@1.45", fade=0.8, gray=0.2)
# II. The Raft
sh(A("c2a"), "frigate", "full@1.0", "raft@1.3", fade=1.0)
sh(A("c2b"), "plan", "full@0.62", "all@0.9", frame=True, fade=0.8)
sh(A("c2c"), "frigate", "raft@1.5", "raft@1.8", fade=0.6)
sh(A("c2d"), "raft", "planks@1.5", "planks@1.7", fade=0.8, dim=0.1)
sh(A("c2e"), "frigate", "ship@1.6", "ship@1.9", fade=0.6, gray=0.3)
sh(A("c2e", "The", 2), "raft", "sail@1.2", "waves@1.4", fade=0.6)
sh(A("c2f"), "argus_sketch", "full@1.0", "raft@1.2", fade=0.8)
sh(A("c2f", "the", 5), "raft", "waves@1.6", "waves@1.9", fade=0.4, hit="small")
sh(A("c2g"), "raft", "full@0.32", "full@0.29", frame=True, fade=0.8, dim=0.3)
# III. Thirteen Days
sh(A("c3a"), "salon1819", "full@1.0", "raft@1.25", fade=1.0, dim=0.1)
sh(A("c3a", "This"), "raft", "left_dead@1.8", "left_dead@2.1", fade=0.6)
sh(A("c3a", "By"), "raft", "right_dead@1.5", "right_dead@1.8", fade=0.6)
sh(A("c3b"), "book", "full@1.0", "fight@1.3", fade=0.8, gray=0.3)
sh(A("c3b", "Sabres"), "mutiny", "fight@1.0", "fight@1.4", frame=True, fade=0.4)
sh(A("c3b", "By"), "raft", "facedown@1.6", "facedown@1.9", fade=0.6, dim=0.1)
sh(A("c3c"), "raft", "crowd@1.3", "crowd@1.5", fade=0.6)
sh(A("c3c", "And"), "limbs", "full@0.62", "feet@1.0", frame=True, fade=0.8)
sh(A("c3d"), "raft", "youth@1.7", "old@1.6", fade=0.8)
sh(A("c3d", "Those"), "raft", "old@2.2", "old@2.5", fade=0.6, dim=0.15)
sh(A("c3e"), "raft", "crowd@1.6", "pointer@1.8", fade=0.6)
sh(A("c3e", "So"), "raft", "right_dead@1.4", "planks@1.5", fade=0.6, dim=0.1)
sh(A("c3e", "Fifteen"), "raft", "full@1.0", "crowd@1.1", fade=0.8)
sh(A("c3f"), "raft", "sky@1.4", "waves@1.4", fade=1.0, dim=0.2)
sh(A("c3g"), "raft", "full@1.0", "argus@1.6", fade=0.8)
sh(A("c3g", "A", 2), "raft", "argus@3.4", "argus@4.0", fade=0.4)
sh(A("c3g", "They", 1), "raft", "waver@1.9", "cloth@2.2", fade=0.4, hit="small")
sh(A("c3g", "And"), "raft", "argus@3.6", "argus@3.2", fade=0.5, dim=0.2)
sh(A("c3h"), "raft", "old@1.7", "old@1.9", fade=0.8, dim=0.15)
sh(A("c3h", "Then"), "raft", "waver@1.4", "waver@1.6", fade=0.6, hit="big")
sh(A("c3i"), "raft", "crowd@1.2", "full@1.0", fade=0.8)
sh(A("c3i", "Of"), "frigate", "ship@1.3", "ship@1.55", fade=0.8, gray=0.4)
# IV. The Scandal
sh(A("c4a"), "louis18", "full@0.62", "full@0.66", frame=True, fade=1.0, gray=0.2)
sh(A("c4a", "Savigny"), "book", "sail@1.1", "fight@1.3", fade=0.6, gray=0.3)
sh(A("c4b"), "book", "fight@1.5", "fight@1.7", fade=0.6, gray=0.5)
sh(A("c4c"), "raft", "full@1.0", "full@1.06", fade=0.8, dim=0.1)
sh(A("c4c", "the", 2), "argus_sketch", "raft@1.3", "raft@1.5", fade=0.5)
sh(A("c4c", "and", 1), "raft", "youth@1.8", "youth@2.0", fade=0.5, dim=0.15)
sh(A("c4d"), "louis18", "face@1.6", "face@1.9", fade=0.6)
sh(A("c4e"), "rochefort", "dock@1.2", "ships@1.3", fade=0.8, gray=0.3)
sh(A("c4e", "He", 2), "louis18", "face@1.3", "face@1.1", fade=0.6, gray=0.5)
sh(A("c4f"), "book", "full@0.6", "full@0.64", frame=True, fade=0.8)
sh(A("c4g"), "gericault", "full@0.62", "face@1.1", frame=True, fade=0.8)
# V. The Painter
sh(A("c5a"), "gericault", "face@1.3", "face@1.6", fade=1.0)
sh(A("c5a", "He"), "gericault", "face@1.7", "face@1.9", gray=0.3)
sh(A("c5b"), "raft", "full@0.32", "full@0.36", frame=True, fade=0.8)
sh(A("c5c"), "plan", "all@0.7", "all@0.85", frame=True, fade=0.8)
sh(A("c5d"), "gericault", "face@1.5", "face@1.8", fade=0.6, gray=0.5)
sh(A("c5d", "For"), "plaster", "full@1.0", "full@1.1", fade=0.8)
sh(A("c5e"), "heads", "full@1.0", "old@1.4", fade=0.8)
sh(A("c5e", "He", 2), "limbs", "full@0.62", "feet@1.1", frame=True, fade=0.6)
sh(A("c5f"), "monomaniac", "full@0.62", "face@1.2", frame=True, fade=0.8)
sh(A("c5g"), "heads", kind="pair", img2="limbs", labels=["NATIONALMUSEUM, STOCKHOLM", "MUSÉE FABRE, MONTPELLIER"], fade=0.8)
sh(A("c5h"), "delacroix", "face@1.0", "face@1.3", fade=0.8)
sh(A("c5h", "lies"), "raft", "facedown@1.6", "facedown@1.9", fade=0.6)
sh(A("c5h", "Savigny"), "raft", "pointer@1.6", "pointer@1.8", fade=0.6)
sh(A("c5h", "And", 2), "raft", "youth@1.6", "youth@1.8", fade=0.6)
sh(A("c5i"), "argus_sketch", "full@1.0", "full@1.12", fade=0.8)
sh(A("c5i", "He", 2), "mutiny", "full@0.62", "fight@1.0", frame=True, fade=0.6)
sh(A("c5i", "He", 3), "book", "fight@1.2", "fight@1.4", fade=0.5, gray=0.3)
sh(A("c5i", "He", 4), "salon1819", "full@1.0", "waver@1.4", fade=0.5)
sh(A("c5i", "And"), "raft", "full@0.32", "full@0.35", frame=True, fade=0.8)
# VI. The Painting
sh(A("c6a"), "raft", "full@1.0", "argus@1.4", fade=1.0)
sh(A("c6a", "a"), "raft", "argus@3.0", "argus@3.6", fade=0.4)
sh(A("c6b"), "raft", "waver@1.4", "cloth@1.7", fade=0.8)
sh(A("c6b", "On"), "raft", "waver@2.0", "waver@2.3", fade=0.6)
sh(A("c6b", "Géricault"), "raft", "waver@1.6", "crowd@1.3", fade=0.6)
sh(A("c6c"), "raft", "planks@1.0", "cloth@1.0", fade=0.8)
sh(A("c6d"), "raft", "old@1.4", "old@1.7", fade=0.8)
sh(A("c6d", "He", 2), "raft", "old@2.1", "old@2.4", fade=0.5)
sh(A("c6d", "The", 3), "dante", "bodies@1.1", "dante@1.2", fade=0.8, dim=0.1)
sh(A("c6d", "locked"), "raft", "old@1.6", "youth@1.5", fade=0.6)
sh(A("c6e"), "raft", "full@0.3", "full@0.34", frame=True, fade=0.8)
sh(A("c6f"), "salon1819", "full@0.62", "full@0.68", frame=True, fade=0.8)
sh(A("c6f", "Scène"), "raft", "full@1.0", "crowd@1.15", fade=0.6)
sh(A("c6g"), "raft", "left_dead@1.4", "youth@1.4", fade=0.6, dim=0.1)
sh(A("c6g", "The", 1), "louis18", "face@1.3", "face@1.6", fade=0.6)
sh(A("c6h"), "raft", "full@0.32", "full@0.35", frame=True, fade=0.8)
sh(A("c6h", "One"), "delacroix", "face@1.2", "face@1.5", fade=0.6)
sh(A("c6h", "the", 2), "raft", "facedown@1.8", "facedown@2.1", fade=0.5)
sh(A("c6i"), "egyptian_hall", "full@1.0", "front@1.3", fade=0.8)
sh(A("c6i", "It", 3), "raft", "full@1.0", "full@1.05", fade=0.8)
# VII. The Darkness
sh(A("c7a"), "gericault", "face@1.2", "face@1.4", fade=1.0, gray=0.4)
sh(A("c7a", "Théodore"), "deathbed", "full@1.0", "face@1.3", fade=0.8)
sh(A("c7b"), "raft", "full@0.3", "full@0.33", frame=True, fade=0.8)
sh(A("c7c"), "raft", "sail@1.6", "mast@1.8", fade=0.8)
sh(A("c7c", "Over"), "raft", "crowd@2.0", "crowd@2.3", fade=0.6, contrast=1.1)
sh(A("c7d"), "raft", "facedown@1.5", "planks@1.4", fade=0.8, dim=-0.2)
sh(A("c7d", "The", 2), "raft", "full@1.0", "full@0.96", fade=0.8, dim=0.3)
# the horizon
sh(A("end1"), "raft", "full@1.0", "argus@1.8", fade=1.0)
sh(A("end1", "That"), "raft", "argus@3.4", "argus@4.2", fade=0.5)
sh(A("end2"), "raft", "waver@1.6", "cloth@1.9", fade=0.8)
sh(A("end3"), "raft", "full@0.3", "full@0.28", frame=True, fade=1.0)

# ---------------------------------------------------------------- overlays
CH = [("cold5", "c1a", "I", "The Captain"), ("c1f", "c2a", "II", "The Raft"), ("c2g", "c3a", "III", "Thirteen Days"),
      ("c3i", "c4a", "IV", "The Scandal"), ("c4g", "c5a", "V", "The Painter"), ("c5i", "c6a", "VI", "The Painting"), ("c6i", "c7a", "VII", "The Darkness")]
ov("title", A("cold5", "and", 1, end=False, off=0.0), A("cold5", end=True, off=0.6), kicker="THÉODORE GÉRICAULT · 1818–1819", text="The Raft of the Medusa")
for prev, nxt, n, name in CH:
    if n == "I": continue
    ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("chapter", A("c1a", off=-0.55), A("c1a", off=2.0), kicker="CHAPTER I", text="The Captain")
ov("label", A("cold1", off=0.3), A("cold2", end=True), text="THE RAFT OF THE MEDUSA · 1818–19 · LOUVRE")
ov("label", A("cold4"), A("cold4", "filled", off=-0.1), text="THÉODORE GÉRICAULT · LITHOGRAPH, c. 1820")
ov("label", A("cold4", "filled"), A("cold4", end=True, off=0.5), text="GÉRICAULT · STUDY OF SEVERED HEADS · c. 1818")
ov("year", A("c1a", off=2.1), A("c1a", "Napoleon", off=-0.2), text="1816")
ov("label", A("c1a", "Napoleon"), A("c1a", end=True, off=0.4), text="LOUIS XVIII · ENGRAVING AFTER GÉRARD")
ov("label", A("c1c"), A("c1c", end=True), text="THE PORT OF ROCHEFORT · JOSEPH VERNET, 1762")
ov("lower", A("c1d", off=-0.1), A("c1d", "He", 1, off=-0.2), text="Hugues Duroy de Chaumareys", sub="CAPTAIN OF THE MÉDUSE · NO PORTRAIT SURVIVES")
ov("label", A("c1f", "And"), A("c1f", end=True), text="THE WRECK OF THE MÉDUSE · 19TH-CENTURY ENGRAVING")
ov("label", A("c2a"), A("c2a", end=True), text="BUILDING THE RAFT · 19TH-CENTURY ENGRAVING")
ov("label", A("c2b"), A("c2b", end=True, off=0.3), text="PLAN OF THE RAFT · FROM CORRÉARD & SAVIGNY, 1817")
ov("stamp", A("c2c", "one", off=0.1), A("c2c", end=True, off=0.6), text="147 ON BOARD")
ov("label", A("c2f"), A("c2f", "the", 3, off=-0.1), text="GÉRICAULT · OIL SKETCH FOR THE RAFT · LOUVRE")
ov("label", A("c3a"), A("c3a", "This", off=-0.1), text="GÉRICAULT · OIL SKETCH FOR THE RAFT · LOUVRE")
ov("quote", A("c3a", "This", off=-0.1), A("c3a", "By", off=-0.2), text="This whole night we contended against death.", sub="SAVIGNY & CORRÉARD · NARRATIVE OF A VOYAGE TO SENEGAL, 1818")
ov("label", A("c3b"), A("c3b", "Sabres", off=-0.1), text="REVOLT ON THE RAFT · PRINT AFTER CORRÉARD, 1818")
ov("label", A("c3b", "Sabres"), A("c3b", "By", off=-0.1), text="GÉRICAULT · THE MUTINY ON THE RAFT · 1818")
ov("stamp", A("c3c", "sixty-seven", off=0.1), A("c3c", "They", off=-0.2), text="67 LEFT")
ov("label", A("c3c", "And"), A("c3c", end=True, off=0.5), text="GÉRICAULT · ANATOMICAL PIECES · 1818–19")
ov("lower", A("c3d", "Henri", off=-0.1), A("c3d", "Those", off=-0.2), text="Henri Savigny", sub="SHIP'S SURGEON · SURVIVOR")
ov("quote", A("c3d", "Those", off=-0.1), A("c3d", end=True, off=0.7), text="Those whom death had spared… fell upon the dead bodies.", sub="SAVIGNY & CORRÉARD · NARRATIVE OF A VOYAGE TO SENEGAL, 1818")
ov("stamp", A("c3e", "Fifteen", off=0.1), A("c3e", end=True, off=0.6), text="15 LEFT")
ov("year", A("c3g"), A("c3g", "someone", off=-0.1), text="17 JULY 1816")
ov("ring", A("c3g", "A", 2, off=0.1), A("c3g", "They", 1, off=-0.1), point="argus", img="raft", rx=70, ry=50, rot=0)
ov("label", A("c4a"), A("c4a", "Savigny", off=-0.1), text="LOUIS XVIII · ENGRAVING AFTER GÉRARD")
ov("year", A("c4a", off=1.8), A("c4a", "Savigny", off=-0.2), text="SEPTEMBER 1816")
ov("label", A("c4a", "Savigny"), A("c4b", end=True), text="REVOLT ON THE RAFT · PRINT AFTER CORRÉARD, 1818")
ov("year", A("c4e", "He", 2, off=-0.1), A("c4e", end=True, off=0.5), text="1817")
ov("lower", A("c4f", "Alexandre", off=-0.1), A("c4f", "publish", off=1.0), text="Alexandre Corréard", sub="ENGINEER · SURVIVOR")
ov("lower", A("c5a", off=0.2), A("c5a", "Rich", off=-0.1), text="Théodore Géricault", sub="1791–1824")
ov("year", A("c5b"), A("c5b", end=True, off=0.3), text="1818")
ov("label", A("c5c"), A("c5c", end=True), text="PLAN OF THE RAFT · FROM CORRÉARD & SAVIGNY, 1817")
ov("label", A("c5e"), A("c5e", "He", 2, off=-0.1), text="GÉRICAULT · SEVERED HEADS · NATIONALMUSEUM, STOCKHOLM")
ov("label", A("c5e", "He", 2), A("c5e", end=True, off=0.5), text="GÉRICAULT · ANATOMICAL PIECES · MUSÉE FABRE, MONTPELLIER")
ov("label", A("c5f"), A("c5f", end=True), text="GÉRICAULT · THE MADWOMAN · c. 1820 · LYON")
ov("lower", A("c5h", "Eugène", off=-0.1), A("c5h", "lies", off=1.0), text="Eugène Delacroix", sub="PAINTER · SELF-PORTRAIT, c. 1837")
ov("ring", A("c5h", "lies", off=0.3), A("c5h", "Savigny", off=-0.1), point="facedown", img="raft", rx=260, ry=120, rot=-8)
ov("label", A("c5i"), A("c5i", "He", 2, off=-0.1), text="GÉRICAULT · OIL SKETCH · LOUVRE")
ov("ring", A("c6a", "a", off=0.1), A("c6a", end=True, off=0.6), point="argus", img="raft", rx=60, ry=44, rot=0)
ov("lower", A("c6b", "Jean", off=-0.1), A("c6b", "He", off=-0.1), text="Jean Charles", sub="SOLDIER · ONE OF THE FIFTEEN")
ov("label", A("c6d", "The", 3), A("c6d", "locked", off=-0.1), text="DELACROIX · THE BARQUE OF DANTE · 1822 · LOUVRE")
ov("year", A("c6f"), A("c6f", "it", off=0.6), text="1819")
ov("label", A("c6f", "it"), A("c6f", "Scène", off=-0.1), text="GÉRICAULT · SKETCH FOR THE SALON OF 1819 · LOUVRE")
ov("title", A("c6f", "Scène", off=-0.1), A("c6f", "Everyone", off=-0.2), kicker="SALON OF 1819", text="Scène de naufrage")
ov("label", A("c6g", "The", 1), A("c6g", end=True, off=0.4), text="LOUIS XVIII · ENGRAVING AFTER GÉRARD")
ov("stamp", A("c6h", off=0.2), A("c6h", "But", off=-0.1), text="GOLD MEDAL")
ov("year", A("c6i", "In"), A("c6i", "about", off=-0.1), text="1820")
ov("label", A("c6i", "in", 2), A("c6i", "It", 3, off=-0.1), text="THE EGYPTIAN HALL · PICCADILLY, LONDON")
ov("credit", A("c6i", "in", 2), A("c6i", "It", 3, off=-0.1), text="WELLCOME COLLECTION · CC BY 4.0")
ov("year", A("c7a", "In"), A("c7a", "Théodore", off=-0.1), text="1824")
ov("label", A("c7a", "Théodore"), A("c7a", end=True, off=0.5), text="GÉRICAULT ON HIS DEATHBED · CHAMPMARTIN, 1824")
ov("label", A("c7b"), A("c7b", end=True, off=0.4), text="THE RAFT OF THE MEDUSA · LOUVRE, PARIS")
ov("ring", A("end1", "That", off=0.2), A("end1", end=True, off=0.4), point="argus", img="raft", rx=60, ry=44, rot=0)
ov("pin", A("end3", off=0.1), A("end3", end=True, off=1.0), text="MUSÉE DU LOUVRE · DENON WING · ROOM 700")
ov("end", A("end3", end=True, off=1.0), A("end3", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound
SFX += [
 {"at": A("cold1", "really"), "fx": "impact", "gain": 0.35},
 {"at": A("c2f", "cut"), "fx": "snip", "gain": 0.6},
 {"at": A("c3g", "Argus"), "fx": "riser", "gain": 0.3},
 {"at": A("c3h", "Then"), "fx": "chime", "gain": 0.25},
 {"at": A("c5d", "shaves"), "fx": "tick", "gain": 0.3},
] + [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.3} for prev, _, n, _ in CH if n != "I"] + \
    [{"at": A("c1a", off=-0.55), "fx": "impact", "gain": 0.3}]
DM = [[38, 45, 50], [38, 45, 49], [34, 41, 50], [33, 40, 49]]
AM = [[33, 40, 48], [29, 36, 45], [36, 43, 52], [28, 40, 44]]
EM = [[28, 40, 47], [36, 43, 48], [31, 38, 47], [35, 42, 47]]
MUSIC.update({"bar": 5.5, "music_db": -13, "transpose": -2, "chords": EM,
         "segments": [{"at": A("c1a"), "chords": DM, "transpose": -2}, {"at": A("c2a"), "chords": AM, "transpose": -1},
                      {"at": A("c3a"), "chords": EM, "transpose": -3}, {"at": A("c4a"), "chords": DM, "transpose": 0},
                      {"at": A("c5a"), "chords": AM, "transpose": 1}, {"at": A("c6a"), "chords": EM, "transpose": 0},
                      {"at": A("c7a"), "chords": DM, "transpose": -3}, {"at": A("end1"), "chords": AM, "transpose": -1}],
         "sections": {"cold": [A("cold1"), A("cold2", end=True)], "choir": [A("c3h", "Then", off=-0.3), A("c3i", off=-0.5)],
                      "drop": [A("c3f"), A("c3f", end=True, off=0.3)]},
         "heartbeat": [A("c3g"), A("c3h", "Then", off=-0.2)]})
