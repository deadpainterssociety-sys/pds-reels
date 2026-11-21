# Visual plan for long video #5 (21 Nov 2026): Repin's Reply of the Zaporozhian Cossacks. Executed by plan.py: A, sh, ov, IM,
# MUSIC, SFX are in scope. Calm cuts (about one shot per phrase group, slow moves, the depth effect capped in Long.tsx),
# soft sounds, NO big date cards (Gigi, 21 Nov 2026: dates live in the narration and the small labels), a Mussorgsky
# cue sheet (Pictures at an Exhibition, Musopen, public domain): Bydlo opens, Limoges for the insults and the friends,
# the Old Castle for the journey, Catacombs for Ivan and for Kharkiv, the Great Gate of Kiev for the end.
P = lambda **kw: kw
IM.update({
 "cossacks": P(file="src/cossacks.jpg", commons="File:Ilja Jefimowitsch Repin - Reply of the Zaporozhian Cossacks - Yorck.jpg", depth=True, long=3840,
     points={"taras": [0.73, 0.27], "belly": [0.723, 0.45], "scribe": [0.523, 0.555], "quill": [0.50, 0.63], "letter": [0.53, 0.66],
             "sirko": [0.578, 0.43], "pipe": [0.57, 0.46], "bald": [0.597, 0.62], "shirtless": [0.40, 0.57], "back": [0.37, 0.64],
             "oldman": [0.315, 0.48], "young": [0.425, 0.46], "laugher": [0.542, 0.285], "headband": [0.347, 0.23], "fist": [0.43, 0.20],
             "hat": [0.65, 0.12], "left": [0.22, 0.30], "right": [0.82, 0.42], "table": [0.55, 0.66], "sig": [0.535, 0.975],
             "center": [0.5, 0.5], "upper": [0.5, 0.36], "crowd": [0.45, 0.40]}),
 "kharkiv": P(file="src/kharkiv.jpg", commons="File:Reply of the Zaporozhian Cossacks (sketch, 1893, Kharkiv).jpg", depth=True,
     points={"scribe": [0.53, 0.55], "taras": [0.90, 0.29], "shirtless": [0.37, 0.60], "center": [0.5, 0.5], "upper": [0.5, 0.4]}),
 "gtg": P(file="src/gtg.jpg", commons="File:Reply of the Zaporozhian Cossacks (sketch, 1880-90, GTG) 2.jpg", points={"center": [0.5, 0.5], "left": [0.35, 0.45], "right": [0.65, 0.45]}),
 "ateneum": P(file="src/ateneum.jpg", commons="File:Repin Study for Zaporozhian cossacks Ateneum.jpg", points={"center": [0.5, 0.45], "heads": [0.45, 0.4]}),
 "sketch78": P(file="src/sketch78.jpg", commons="File:Repin Zaporozhtsy sketch 1878 2.JPG", points={"center": [0.5, 0.5]}),
 "pencil": P(file="src/pencil.jpg", commons="File:Repin Zaporozhian Cossacks pencil study ca 1880.jpg", points={"center": [0.5, 0.5]}),
 "studyhat": P(file="src/studyhat.jpg", commons="File:Repin Zaporozhian cossack wearing a hat etc end of 1880s gtg.jpg", points={"center": [0.5, 0.45], "left": [0.4, 0.4]}),
 "repin": P(file="src/repin94.jpg", commons="File:1894Репин.jpg", points={"face": [0.56, 0.30], "body": [0.5, 0.5]}),
 "yav": P(file="src/yav.jpg", commons="File:Dmytro Yavornytsky (1855-1940).jpg", points={"face": [0.38, 0.11], "body": [0.45, 0.25]}),
 "drag": P(file="src/drag.jpg", commons="File:Dragomirov Mikhail Ivanovich 2.jpg", points={"face": [0.46, 0.265], "body": [0.48, 0.40]}),
 "dragrepin": P(file="src/dragrepin.jpg", commons="File:Dragomirov by Repin.jpg", points={"face": [0.48, 0.30], "body": [0.5, 0.5]}),
 "sirkostudy": P(file="src/sirko.jpg", commons="File:Sirko by Repin.jpg", points={"face": [0.70, 0.42], "center": [0.5, 0.5]}),
 "strav": P(file="src/strav.jpg", commons="File:Stravinskiy FI.jpg", points={"face": [0.50, 0.25], "body": [0.5, 0.5]}),
 "mehmed": P(file="src/mehmed.jpg", commons="File:Sultan Mehmed IV (2).jpg", depth=True, points={"face": [0.46, 0.235], "bust": [0.47, 0.30], "body": [0.5, 0.45]}),
 "tolstoy": P(file="src/tolstoy.jpg", commons="File:Ilya Efimovich Repin (1844-1930) - Portrait of Leo Tolstoy (1887).jpg", points={"face": [0.55, 0.33], "body": [0.5, 0.5]}),
 "serov": P(file="src/serov.jpg", commons="File:Valentin Alexandrovich Serov - Self-portrait.jpg", points={"face": [0.55, 0.42], "center": [0.5, 0.5]}),
 "mamontov": P(file="src/mamontov.jpg", commons="File:Mamontov by Repin 1878.jpg", depth=True, points={"face": [0.50, 0.32], "body": [0.5, 0.5]}),
 "palace": P(file="src/palace.jpg", commons="File:SPB Palace square and Alexander's column 1890-1900.jpg", depth=True, points={"column": [0.53, 0.42], "square": [0.5, 0.6]}),
 "museum": P(file="src/museum.jpg", commons="File:2018 SPb Mikhailovsky Palace 01.jpg", depth=True,
     credit="The Mikhailovsky Palace (State Russian Museum), St Petersburg: photo Andrey Korzun, CC BY-SA 4.0", points={"facade": [0.5, 0.45], "door": [0.5, 0.6]}),
 "stasov": P(file="src/stasov.jpg", commons="File:Stasov by Repin 1889.jpg", points={"face": [0.45, 0.19], "body": [0.47, 0.42]}),
 "sich": P(file="src/sich.jpg", commons="File:План Запорожской Сечи на 1742 г. Денис де Боскит. Грав.нач.XIXв ГИМ e1.jpg", points={"center": [0.5, 0.5], "river": [0.6, 0.62]}),
 "ivan": P(file="src/ivan.jpg", commons="File:Répine Ivan le Terrible et son fils Ivan principale version 1883 - 1885.jpg", depth=True,
     points={"eyes": [0.495, 0.29], "faces": [0.51, 0.34], "son": [0.525, 0.4], "center": [0.5, 0.52]}),
 "alex3": P(file="src/alex3.jpg", commons="File:Kramskoy Alexander III.jpg", points={"face": [0.47, 0.20], "body": [0.47, 0.45]}),
 "kachan": P(file="src/kachan.jpg", commons="File:Exterior of palace in Kachanivka 24.jpg", depth=True,
     credit="Kachanivka palace: photo Dmytro Petishkin, CC BY 4.0", points={"palace": [0.5, 0.55]}),
 "kmuseum": P(file="src/xudmuzej.jpg", commons="File:Xud-muzej.jpg", credit="Kharkiv Art Museum: photo San4oss, CC BY-SA 4.0", points={"center": [0.5, 0.5]}),
 "kursk": P(file="src/kursk.jpg", commons="File:Ilya Repin - Крестный ход в Курской губернии - Google Art Project.jpg", depth=True, points={"center": [0.45, 0.55], "shrine": [0.88, 0.3]}),
 "nicholas": P(file="src/nicholas.jpg", commons="File:Ilja Jefimowitsch Repin - Saint Nicholas of Myra saves three innocents from death.jpg", points={"saint": [0.45, 0.24], "center": [0.5, 0.45]}),
 "zdravnevo": P(file="src/zdravnevo.jpg", commons="File:109. Здравнево. Усадьба Ильи Репина.jpg", depth=True,
     credit="Zdravnevo, Repin's estate near Vitebsk: photo GAlexandrova, CC BY-SA 4.0", points={"house": [0.5, 0.55]}),
})

# ---------------------------------------------------------------- shots (about one per phrase group; slow moves)
# cold open: the loudest laugh, the reveal, the scribe, the sultan, the faces that were real people
sh(A("cold1"), "cossacks", "taras@2.5", "taras@2.35")
sh(A("cold1", "emperor", off=-0.1), "cossacks", "center@1.0", "center@1.04", hit="big", dolly=[0, 0.03])
sh(A("cold2", "writing", off=-0.1), "cossacks", "scribe@2.2", "scribe@2.35", fade=0.6)
sh(A("cold2", "Sultan", off=-0.1), "mehmed", "bust@1.3", "bust@1.4", fade=0.6)
sh(A("cold3"), "cossacks", "laugher@2.3", "laugher@2.45", fade=0.6)
sh(A("cold3", "Some", off=-0.1), "cossacks", "oldman@2.4", "oldman@2.55", fade=0.5)
sh(A("cold4"), "cossacks", "letter@2.6", "letter@2.45", gray=0.5, fade=0.8)
sh(A("cold4", "But", off=-0.1), "cossacks", "sirko@1.9", "sirko@2.0", fade=0.5)
sh(A("cold5", "general", off=-0.1), "drag", "face@1.5", "face@1.6", gray=1, fade=0.4)
sh(A("cold5", "historian", off=-0.1), "yav", "body@0.62", "body@0.64", frame=True, gray=1, fade=0.4)
sh(A("cold5", "opera", off=-0.1), "strav", "body@0.62", "body@0.64", frame=True, gray=1, fade=0.4)
sh(A("cold5", "coachman", off=-0.1), "cossacks", "right@1.5", "right@1.6", fade=0.4)
sh(A("cold6"), "repin", "face@1.4", "face@1.5", fade=0.8)
sh(A("cold6", "another", off=-0.1), "alex3", "body@0.62", "body@0.64", frame=True, fade=0.6)
sh(A("cold6", "for", off=-0.1), "cossacks", "center@1.0", "center@1.06", dim=0.3, fade=1.2)
# I. The Letter
sh(A("c1a"), "mehmed", "face@1.35", "face@1.45", fade=1.0)
sh(A("c1a", "Zaporozhian", off=-0.1), "cossacks", "crowd@1.3", "crowd@1.4", fade=0.8)
sh(A("c1a", "beyond", off=-0.1), "sich", "river@1.0", "river@1.08", gray=0.4, dim=0.3, fade=0.8)
sh(A("c1a2"), "cossacks", "shirtless@2.0", "shirtless@2.1", fade=0.8)
sh(A("c1a2", "They", off=-0.1), "cossacks", "sirko@1.7", "sirko@1.8", fade=0.6)
sh(A("c1a2", "fighting", off=-0.1), "cossacks", "headband@2.0", "headband@2.1", fade=0.6)
sh(A("c1a3"), "mehmed", "bust@1.0", "face@1.15", fade=1.0)
sh(A("c1a3", "Vienna", off=-0.6), "mehmed", "face@1.6", "face@1.7", dim=0.25, fade=0.6)
sh(A("c1b"), "mehmed", "bust@1.25", "bust@1.35", fade=0.8)
sh(A("c1b", "And", 2, off=-0.1), "cossacks", "scribe@1.8", "scribe@1.9", dim=0.2, fade=0.8)
sh(A("c1c"), "cossacks", "scribe@2.4", "scribe@2.5", fade=0.8)
sh(A("c1c", "Babylonian", off=-0.1), "cossacks", "laugher@2.2", "laugher@2.3", fade=0.4)
sh(A("c1c", "Macedonian", off=-0.1), "cossacks", "oldman@2.2", "oldman@2.3", fade=0.4)
sh(A("c1c", "brewer", off=-0.1), "cossacks", "belly@1.9", "belly@2.0", fade=0.4)
sh(A("c1c", "and", off=-0.1), "cossacks", "young@2.3", "young@2.4", fade=0.4)
sh(A("c1d"), "cossacks", "letter@2.9", "letter@2.75", fade=0.8)
sh(A("c1d", "And", off=-0.1), "cossacks", "hat@1.9", "hat@2.0", fade=0.6)
sh(A("c1e"), "cossacks", "center@1.0", "center@1.05", gray=0.6, fade=1.0)
sh(A("c1e", "Many", off=-0.1), "cossacks", "letter@2.3", "letter@2.4", gray=0.6, fade=0.8)
sh(A("c1f"), "gtg", "center@1.0", "center@1.07", fade=1.0)
sh(A("c1f", "But", off=-0.1), "gtg", "right@1.3", "left@1.3", fade=0.8)
sh(A("c1f", "In", 1, off=-0.1), "repin", "body@0.62", "body@0.64", frame=True, gray=0.3, fade=0.8)
# II. A Laugh at Abramtsevo
sh(A("c2a"), "mamontov", "face@1.3", "face@1.4", fade=1.0)
sh(A("c2a2"), "repin", "face@1.45", "face@1.55", fade=1.0)
sh(A("c2a2", "illustrated", off=-0.1), "cossacks", "taras@2.0", "taras@2.12", fade=0.8)
sh(A("c2a2", "Gogol", off=-0.1), "cossacks", "belly@1.6", "belly@1.7", fade=0.6)
sh(A("c2b"), "cossacks", "center@1.0", "upper@1.15", gray=0.7, dim=0.2, fade=1.0)
sh(A("c2c"), "sketch78", "center@0.52", "center@0.54", frame=True, fade=1.0)
sh(A("c2d"), "pencil", "center@0.6", "center@0.62", frame=True, fade=1.0)
sh(A("c2d", "Valentin", off=-0.1), "serov", "center@0.62", "center@0.64", frame=True, fade=0.8)
sh(A("c2e"), "sich", "center@1.0", "river@1.15", dim=0.3, fade=1.0)
sh(A("c2f"), "studyhat", "center@1.0", "left@1.12", dim=0.25, fade=1.0)
sh(A("c2f", "clothes", off=-0.1), "ateneum", "heads@1.05", "heads@1.15", dim=0.25, fade=0.6)
sh(A("c2f", "A", off=-0.1), "kachan", "palace@1.0", "palace@1.08", dim=0.25, fade=0.8)
sh(A("c2g"), "tolstoy", "body@0.62", "body@0.64", frame=True, fade=1.0)
sh(A("c2g", "Repin", off=-0.1), "gtg", "center@1.0", "center@1.06", fade=0.8)
sh(A("c2h"), "stasov", "face@1.2", "body@1.0", fade=1.0)
sh(A("c2h", "No", off=-0.1), "cossacks", "upper@1.15", "upper@1.22", dim=0.35, fade=0.8)
# III. Friends in Costume
sh(A("c3a"), "cossacks", "center@1.0", "center@1.05", fade=1.0)
sh(A("c3a", "He", 1, off=-0.1), "cossacks", "crowd@1.25", "crowd@1.32", hit="small")
sh(A("c3b"), "cossacks", "scribe@2.4", "scribe@2.55", fade=0.8)
sh(A("c3b", "Dmytro", off=-0.1), "yav", "body@0.62", "body@0.64", frame=True, gray=1, fade=0.6)
sh(A("c3c"), "cossacks", "scribe@2.8", "scribe@3.0", fade=0.8)
sh(A("c3d"), "cossacks", "sirko@2.4", "sirko@2.55", fade=0.8)
sh(A("c3d", "Mikhail", off=-0.1), "drag", "body@1.0", "face@1.4", gray=1, fade=0.6)
sh(A("c3d", "When", off=-0.1), "sirkostudy", "center@0.62", "center@0.64", frame=True, fade=0.8)
sh(A("c3d2"), "dragrepin", "face@0.62", "face@0.64", frame=True, fade=1.0)
sh(A("c3d2", "for", 2, off=-0.1), "cossacks", "pipe@2.5", "pipe@2.6", dim=0.35, fade=0.6)
sh(A("c3e"), "cossacks", "left@1.3", "crowd@1.3", fade=1.0)
sh(A("c3e", "Fyodor", off=-0.1), "strav", "body@0.62", "body@0.64", frame=True, gray=1, fade=0.6)
sh(A("c3f"), "cossacks", "bald@2.3", "bald@2.45", fade=0.8)
sh(A("c3f", "belonging", off=-0.1), "cossacks", "bald@3.0", "bald@3.1", fade=0.6)
sh(A("c3g"), "cossacks", "table@1.6", "table@1.7", fade=0.8)
sh(A("c3g", "Repin", off=-0.1), "cossacks", "bald@2.0", "bald@2.1", fade=0.6)
sh(A("c3g", "It", off=-0.1), "cossacks", "bald@2.7", "bald@2.85", fade=0.6)
sh(A("c3h"), "cossacks", "center@1.15", "center@1.2", fade=0.8)
sh(A("c3h", "professor", off=-0.1), "cossacks", "taras@2.3", "taras@2.4", fade=0.4)
sh(A("c3h", "teacher", off=-0.1), "cossacks", "shirtless@2.3", "shirtless@2.4", fade=0.4)
sh(A("c3h", "student", off=-0.1), "cossacks", "young@2.4", "young@2.5", fade=0.4)
sh(A("c3h", "even", off=-0.1), "cossacks", "oldman@2.4", "oldman@2.55", fade=0.5)
# IV. Eleven Years
sh(A("c4a"), "pencil", "center@0.6", "center@0.62", frame=True, gray=0.6, fade=1.0)
sh(A("c4b"), "kursk", "center@1.0", "center@1.07", dim=0.2, fade=0.8)
sh(A("c4b", "saint", off=-0.1), "nicholas", "saint@1.2", "saint@1.3", fade=0.6)
sh(A("c4b", "Ivan", off=-0.1), "ivan", "faces@1.6", "faces@1.72", fade=0.8)
sh(A("c4c"), "ivan", "eyes@2.4", "eyes@2.55", fade=0.8)
sh(A("c4c", "The", 3, off=-0.1), "alex3", "body@0.62", "body@0.64", frame=True, gray=0.5, fade=0.6)
sh(A("c4c", "We", off=-0.1), "ivan", "center@1.0", "center@1.05", fade=0.8)
sh(A("c4d"), "cossacks", "laugher@1.6", "laugher@1.7", fade=1.0)
sh(A("c4d", "Kuban", off=-0.1), "studyhat", "center@1.0", "left@1.15", dim=0.25, fade=0.8)
sh(A("c4d", "to", 3, off=-0.1), "ateneum", "center@1.0", "heads@1.12", dim=0.25, fade=0.8)
sh(A("c4e"), "cossacks", "center@1.0", "center@1.05", hit="big")
sh(A("c4e", "And", 2, off=-0.1), "cossacks", "sig@2.0", "sig@2.15", fade=0.8)
# V. An Emperor's Price
sh(A("c5a"), "cossacks", "right@1.4", "right@1.5", gray=0.5, fade=1.0)
sh(A("c5a", "Others", off=-0.1), "cossacks", "left@1.4", "left@1.5", gray=0.5, fade=0.8)
sh(A("c5b"), "alex3", "body@1.0", "face@1.3", fade=1.0)
sh(A("c5c"), "palace", "square@1.0", "column@1.12", gray=0.4, dim=0.25, fade=1.0)
sh(A("c5c", "More", off=-0.1), "sich", "center@1.0", "center@1.08", gray=0.6, dim=0.35, fade=0.8)
sh(A("c5c", "Now", off=-0.1), "cossacks", "taras@2.0", "taras@2.1", fade=0.6)
sh(A("c5d"), "yav", "body@0.62", "body@0.64", frame=True, gray=1, fade=0.8)
sh(A("c5d", "hurrah", off=-0.25), "cossacks", "scribe@2.6", "scribe@2.7", fade=0.4)
sh(A("c5e"), "zdravnevo", "house@1.0", "house@1.08", fade=1.0)
sh(A("c5f"), "cossacks", "upper@1.2", "upper@1.28", fade=1.0)
sh(A("c5f", "gave", off=-0.1), "museum", "facade@1.0", "facade@1.08", fade=0.8)
# VI. The Other Cossacks
sh(A("c6a"), "kharkiv", "center@1.0", "center@1.05", dim=0.15, fade=1.2)
sh(A("c6b"), "cossacks", kind="pair", img2="kharkiv", labels=["ST PETERSBURG · 1880–1891", "KHARKIV · 1889–1893"], fade=0.8)
sh(A("c6b", "The", 2, off=-0.1), "kharkiv", "scribe@2.6", "scribe@2.75", fade=0.8)
sh(A("c6c"), "kmuseum", "center@0.62", "center@0.64", frame=True, fade=1.0)
sh(A("c6c", "In", 3, off=-0.1), "dragrepin", "face@0.62", "face@0.64", frame=True, fade=0.8)
sh(A("c6d"), "kharkiv", "upper@1.15", "upper@1.22", gray=1, dim=0.3, fade=1.0)
sh(A("c6e"), "kharkiv", "center@1.0", "center@1.05", gray=1, dim=0.45, fade=1.0)
sh(A("c6e", "The", 2, off=-0.1), "kharkiv", "taras@1.7", "taras@1.8", hit="small")
# VII. The Reply
sh(A("c7a0"), "yav", "body@0.62", "body@0.64", frame=True, fade=1.0)
sh(A("c7a0", "We", off=-0.1), "cossacks", "scribe@1.9", "scribe@2.0", fade=0.8)
sh(A("c7a"), "cossacks", "left@1.25", "right@1.25", dim=0.2, fade=1.0)
sh(A("c7b"), "cossacks", "letter@2.4", "letter@2.55", fade=1.0)
sh(A("c7c"), "cossacks", "taras@2.2", "taras@2.3", fade=0.8)
sh(A("c7c", "Free", off=-0.1), "cossacks", "laugher@2.0", "laugher@2.1", fade=0.6)
sh(A("c7c", "and", off=-0.1), "cossacks", "center@1.0", "center@1.04", hit="big")
sh(A("c7d"), "cossacks", "scribe@1.9", "scribe@2.0", fade=1.0)
sh(A("c7d", "It's", off=-0.1), "cossacks", "quill@2.6", "quill@2.75", fade=0.8)
sh(A("ending"), "cossacks", "center@1.0", "center@1.04", fade=1.2)

# ---------------------------------------------------------------- overlays (no big date cards)
CH = [("cold6", "c1a", "I", "The Letter"), ("c1f", "c2a", "II", "A Laugh at Abramtsevo"), ("c2h", "c3a", "III", "Friends in Costume"),
      ("c3h", "c4a", "IV", "Eleven Years"), ("c4e", "c5a", "V", "An Emperor's Price"), ("c5f", "c6a", "VI", "The Other Cossacks"),
      ("c6e", "c7a0", "VII", "The Reply")]
ov("title", A("cold6", "for", off=-0.1), A("cold6", end=True, off=0.6), kicker="ILYA REPIN · 1880–1891", text="The Cossacks' Reply")
for prev, nxt, n, name in CH:
    ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("label", A("cold1", "emperor", off=0.3), A("cold2", "writing", off=-0.2), text="REPLY OF THE ZAPOROZHIAN COSSACKS · REPIN")
ov("lower", A("cold2", "Sultan", off=0.1), A("cold2", end=True, off=0.5), text="Mehmed IV", sub="OTTOMAN SULTAN · 1648–1687")
ov("lower", A("cold5", "general", off=0.1), A("cold5", "historian", off=-0.15), text="Mikhail Dragomirov", sub="GENERAL")
ov("lower", A("cold5", "historian", off=0.1), A("cold5", "opera", off=-0.15), text="Dmytro Yavornytsky", sub="HISTORIAN")
ov("lower", A("cold5", "opera", off=0.1), A("cold5", "coachman", off=-0.15), text="Fyodor Stravinsky", sub="OPERA BASS")
ov("lower", A("cold6", off=0.2), A("cold6", "another", off=-0.15), text="Ilya Repin", sub="1844–1930 · SELF-PORTRAIT, 1894")
ov("lower", A("cold6", "another", off=0.1), A("cold6", "for", off=-0.15), text="Alexander III", sub="EMPEROR OF RUSSIA · KRAMSKOI, 1886")
ov("label", A("c1a"), A("c1a", "Zaporozhian", off=-0.15), text="SULTAN MEHMED IV · c. 1682")
ov("label", A("c1a", "beyond"), A("c1a2", off=-0.2), text="THE ZAPOROZHIAN SICH · PLAN OF 1742")
ov("quote", A("c1b", "And", 2, off=-0.1), A("c1b", end=True, off=1.0), text="Voluntarily and without any resistance.", sub="THE SULTAN'S LETTER · AS THE LEGEND TELLS IT")
ov("quote", A("c1c", "They", off=-0.1), A("c1c", "and", off=-0.25), text="Thou Babylonian scullion, Macedonian wheelwright, brewer of Jerusalem…",
   sub="THE COSSACKS' REPLY · ONE TRANSLATION")
ov("label", A("c1f"), A("c1f", "In", 1, off=-0.15), text="OIL SKETCH · TRETYAKOV GALLERY")
ov("lower", A("c2a", off=0.3), A("c2a", end=True, off=0.6), text="Savva Mamontov", sub="1841–1918 · PORTRAIT BY REPIN, 1878")
ov("label", A("c2c"), A("c2c", end=True, off=0.6), text="FIRST SKETCH · ABRAMTSEVO · 1878")
ov("label", A("c2d"), A("c2d", "Valentin", off=-0.15), text="PENCIL STUDY · c. 1880")
ov("lower", A("c2d", "Valentin", off=0.1), A("c2d", end=True, off=0.6), text="Valentin Serov", sub="1865–1911 · SELF-PORTRAIT")
ov("label", A("c2e"), A("c2e", end=True, off=0.5), text="THE ZAPOROZHIAN SICH · PLAN OF 1742")
ov("label", A("c2f"), A("c2f", "A", off=-0.15), text="REPIN'S STUDIES OF COSSACKS")
ov("label", A("c2f", "A"), A("c2f", end=True, off=0.6), text="KACHANIVKA · TARNOVSKY'S ESTATE")
ov("credit", A("c2f", "A"), A("c2f", end=True, off=0.6), text="Photo: Dmytro Petishkin, CC BY 4.0, Wikimedia Commons")
ov("lower", A("c2g", off=0.3), A("c2g", "Repin", off=-0.15), text="Leo Tolstoy", sub="PORTRAIT BY REPIN, 1887")
ov("lower", A("c2h", off=0.3), A("c2h", "No", off=-0.15), text="Vladimir Stasov", sub="CRITIC · PORTRAIT BY REPIN, 1889")
ov("quote", A("c2h", "No", off=-0.1), A("c2h", end=True, off=1.0), text="No one on this earth has felt liberty, equality and fraternity as deeply as they!",
   sub="REPIN TO VLADIMIR STASOV · 6 NOVEMBER 1880")
ov("ring", A("c3b", "grinning", off=0.0), A("c3b", "Dmytro", off=-0.2), point="scribe", img="cossacks", rx=150, ry=170, rot=0)
ov("lower", A("c3b", "Dmytro", off=0.1), A("c3b", end=True, off=0.6), text="Dmytro Yavornytsky", sub="1855–1940 · HISTORIAN OF THE COSSACKS")
ov("ring", A("c3d", "leaning", off=0.0), A("c3d", "Mikhail", off=-0.2), point="sirko", img="cossacks", rx=150, ry=170, rot=0)
ov("lower", A("c3d", "Mikhail", off=0.1), A("c3d", "When", off=-0.15), text="Mikhail Dragomirov", sub="1830–1905 · GENERAL, KIEV MILITARY DISTRICT")
ov("label", A("c3d", "When"), A("c3d", end=True, off=0.6), text="REPIN · STUDY FOR SIRKO · 1889")
ov("label", A("c3d2"), A("c3d2", "for", 2, off=-0.15), text="GENERAL DRAGOMIROV · BY REPIN, 1889")
ov("quote", A("c3d2", "for", 2, off=-0.1), A("c3d2", end=True, off=1.0), text="For the third day we've been drinking to Your Majesty's health.",
   sub="DRAGOMIROV'S TELEGRAM · AS THE STORY GOES")
ov("lower", A("c3e", "Fyodor", off=0.1), A("c3e", end=True, off=0.6), text="Fyodor Stravinsky", sub="1843–1902 · BASS, MARIINSKY THEATRE")
ov("ring", A("c3g", "Repin", off=0.1), A("c3g", "It", off=-0.2), point="bald", img="cossacks", rx=190, ry=180, rot=0)
ov("lower", A("c3f", "Georgy", off=0.0), A("c3f", end=True, off=0.6), text="Georgy Alekseyev", sub="IMPERIAL COURT OFFICIAL · THE BACK OF HIS HEAD")
ov("label", A("c4b"), A("c4b", "saint", off=-0.15), text="RELIGIOUS PROCESSION IN KURSK PROVINCE · 1880–1883")
ov("label", A("c4b", "saint"), A("c4b", "Ivan", off=-0.15), text="SAINT NICHOLAS STOPS AN EXECUTION · 1888")
ov("label", A("c4b", "Ivan"), A("c4c", "The", 3, off=-0.15), text="IVAN THE TERRIBLE AND HIS SON · 1885")
ov("label", A("c4d", "Kuban"), A("c4d", end=True, off=0.6), text="STUDIES · END OF THE 1880s")
ov("ring", A("c4e", "next", off=0.2), A("c4e", end=True, off=1.0), point="sig", img="cossacks", rx=260, ry=90, rot=0)
ov("stamp", A("c5b", "thirty-five", off=0.1), A("c5b", "Alexander", off=-0.1), text="35,000 RUBLES")
ov("lower", A("c5b", "Alexander", off=0.1), A("c5b", end=True, off=0.6), text="Alexander III", sub="EMPEROR OF RUSSIA 1881–1894")
ov("label", A("c5c"), A("c5c", "More", off=-0.15), text="PALACE SQUARE · ST PETERSBURG · 1890s")
ov("label", A("c5c", "More"), A("c5c", "Now", off=-0.15), text="THE LAST SICH · DESTROYED 1775")
ov("label", A("c5e"), A("c5e", end=True, off=0.6), text="ZDRAVNEVO · NEAR VITEBSK")
ov("credit", A("c5e"), A("c5e", end=True, off=0.6), text="Photo: GAlexandrova, CC BY-SA 4.0, Wikimedia Commons")
ov("label", A("c5f", "gave"), A("c5f", end=True, off=1.0), text="THE RUSSIAN MUSEUM · ST PETERSBURG")
ov("credit", A("c5f", "gave"), A("c5f", end=True, off=1.0), text="Photo: Andrey Korzun, CC BY-SA 4.0, Wikimedia Commons")
ov("label", A("c6a"), A("c6b", off=-0.15), text="THE SECOND VERSION · KHARKIV ART MUSEUM")
ov("ring", A("c6b", "spectacles", off=-0.4), A("c6b", end=True, off=0.8), point="scribe", img="kharkiv", rx=150, ry=150, rot=0)
ov("label", A("c6c"), A("c6c", "In", 3, off=-0.15), text="KHARKIV ART MUSEUM")
ov("credit", A("c6c"), A("c6c", "In", 3, off=-0.15), text="Photo: San4oss, CC BY-SA 4.0, Wikimedia Commons")
ov("label", A("c6c", "In", 3), A("c6c", end=True, off=0.6), text="GENERAL DRAGOMIROV · BY REPIN, 1889")
ov("label", A("c6d"), A("c6e", end=True, off=0.6), text="KHARKIV · 2022 · 2026")
ov("label", A("c7a"), A("c7a", end=True, off=0.6), text="RESTAGED BY UKRAINIAN SOLDIERS SINCE 2014")
ov("lower", A("c7d", "It's", off=-0.1), A("c7d", end=True, off=1.2), text="Reply of the Zaporozhian Cossacks", sub="ILYA REPIN · 1880–1891 · STATE RUSSIAN MUSEUM")
ov("pin", A("ending", off=0.1), A("ending", end=True, off=1.0), text="STATE RUSSIAN MUSEUM · ST PETERSBURG · ROOM 34")
ov("end", A("ending", end=True, off=1.0), A("ending", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound: Mussorgsky (Musopen, public domain), soft effects
SFX += [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.22} for prev, _, _, _ in CH] + [
 {"at": A("c5b", "thirty-five", off=0.1), "fx": "impact", "gain": 0.22},
]
CM = {"m_bydlo.ogg": "File:Modest Mussorgsky - pictures at an exhibition - iv. bydlo - sempre moderato, pesante.ogg",
      "m_limoges.ogg": "File:Modest Mussorgsky - pictures at an exhibition - vii. limoges. le marche - allegretto vivo, sempre scherzando.ogg",
      "m_castle.ogg": "File:Modest Mussorgsky - pictures at an exhibition - ii. il vecchio castello - andante.ogg",
      "m_promenade.ogg": "File:Modest Mussorgsky - pictures at an exhibition - promenade - moderato comodo e con delicatezza.ogg",
      "m_catacombae.ogg": "File:Modest Mussorgsky - pictures at an exhibition - viii. catacombae. sepulcrum romanum - largo.ogg",
      "m_bald.ogg": "File:Modest Mussorgsky - night on bald mountain.ogg",
      "m_kiev.ogg": "File:Modest Mussorgsky - pictures at an exhibition - x. la grande porte de kiev - allegro alla breve. maestoso. con grandezza.ogg"}
T = lambda f, frm, to, credit, **kw: {"file": f"src/music/{f}", "commons": CM[f], "from": frm, **({"to": to} if to is not None else {}), "start": kw.pop("start", 0),
                                     "gain_db": kw.pop("gain_db", 0), "fade_in": kw.pop("fade_in", 2.5), "fade_out": kw.pop("fade_out", 3.0), "credit": credit}
PX = "Mussorgsky, Pictures at an Exhibition: {} · Musopen, public domain"
# track start points (s) in each recording, tuned to the voice timeline (loudness maps, 5-s windows): Bydlo's build under the
# cold open, its climax on "it was finally done" (c4e), Catacombs' loudest bar on the Kharkiv fire (c6e), the Great Gate's
# finale under the last lines and the end screen
MUSIC.update({
 "pad": False, "whooshes": False, "music_db": -8.0, "duck_db": -7, "fx_db": -12, "transpose": 0, "bar": 5.5,
 "_tracks_note": "Mussorgsky cue sheet (21 Nov 2026), Pictures at an Exhibition (1874) and Night on Bald Mountain, Musopen recordings: "
                 "Bydlo (the heavy ox-cart) under the cold open and the finished painting, Limoges (market chatter) for the insults and "
                 "the friends in costume, the Old Castle for the journey south, the Promenade for the casting, Catacombs for Ivan and "
                 "for Kharkiv, Bald Mountain's quiet dawn for the emperor's purchase, the Great Gate of Kiev for the end.",
 "tracks": [
  T("m_bydlo.ogg", 0, A("c1a", off=1.5), PX.format("Bydlo"), start=30.0, fade_in=0.8),
  T("m_limoges.ogg", A("cold6", end=True, off=-0.5), A("c2a", off=1.5), PX.format("Limoges"), start=0.0, gain_db=-1),
  T("m_castle.ogg", A("c1f", end=True, off=-0.5), A("c3a", off=1.5), PX.format("The Old Castle"), start=0.0, gain_db=2),
  T("m_promenade.ogg", A("c2h", end=True, off=-0.5), A("c3d2", off=1.5), PX.format("Promenade"), start=0.0, gain_db=3),
  T("m_limoges.ogg", A("c3d", end=True, off=-0.5), A("c4a", off=1.5), PX.format("Limoges"), start=34.0, gain_db=-1),
  T("m_catacombae.ogg", A("c3h", end=True, off=-0.5), A("c4d", off=1.5), PX.format("Catacombs"), start=0.0, gain_db=-2),
  T("m_bydlo.ogg", A("c4c", end=True, off=-0.5), A("c5a", off=1.5), PX.format("Bydlo"), start=71.5),
  T("m_bald.ogg", A("c4e", end=True, off=-0.5), A("c6a", off=1.5), "Mussorgsky, Night on Bald Mountain · Musopen, public domain", start=600.0, gain_db=4),
  T("m_catacombae.ogg", A("c5f", end=True, off=-0.5), A("c7a0", off=1.5), PX.format("Catacombs"), start=40.0, gain_db=-2),
  T("m_kiev.ogg", A("c6e", end=True, off=-0.5), None, PX.format("The Great Gate of Kiev"), start=256.0, gain_db=-3, fade_out=8.0),
 ],
})
