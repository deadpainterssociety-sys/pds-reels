# Visual plan for long video #4 (17 Nov 2026): Klimt's Adele Bloch-Bauer I. Executed by plan.py: A, sh, ov, IM, MUSIC,
# SFX are in scope. Calm cuts (about one shot per narrated line, slow moves), the depth effect capped (Long.tsx), soft
# sounds, a Vienna-1900 cue sheet: Mahler's Adagietto opens and closes; Bruno Walter's Vienna recording of the Ninth
# (16 January 1938) plays under 1938. Originals fetched in CI (long-src.yml).
P = lambda **kw: kw
IM.update({
 "adele": P(file="src/adele.jpg", commons="File:Gustav Klimt - Porträt der Adele Bloch-Bauer I (1907).jpg", depth=True, points={
     "eyes": [0.60, 0.115], "face": [0.60, 0.135], "lips": [0.60, 0.155], "choker": [0.61, 0.198], "hands": [0.556, 0.282],
     "bust": [0.60, 0.22], "spirals": [0.77, 0.14], "squares": [0.44, 0.14], "bracelets": [0.64, 0.355], "dress_eyes": [0.62, 0.56],
     "chair": [0.40, 0.62], "center": [0.5, 0.5], "upper": [0.58, 0.3], "sign": [0.95, 0.91]}),
 "adele2": P(file="src/adele2.jpg", commons="File:Klimt - ABBII Portrait.jpg", depth=True, points={"face": [0.5, 0.17], "body": [0.5, 0.45]}),
 "study": P(file="src/study.jpg", commons="File:Gustav Klimt - Study for Portrait of Adele Bloch-Bauer I - Google Art Project.jpg",
            points={"body": [0.38, 0.42], "top": [0.36, 0.2]}),
 "seated": P(file="src/seated.jpeg", commons="File:Gustav Klimt Adele Bloch-Bauer sitzend von vorn 1903.jpeg", points={"body": [0.5, 0.45], "top": [0.5, 0.2]}),
 "adele_photo": P(file="src/adele_photo.jpg", commons="File:Adele Bloch Bauer ca 1910.jpg", points={"face": [0.42, 0.13], "body": [0.55, 0.4], "hand": [0.73, 0.47]}),
 "klimt": P(file="src/klimt.jpg", commons="File:Moriz Nähr Gustav Klimt mit Katze 1911.jpg", points={"face": [0.5, 0.28], "cat": [0.33, 0.56], "body": [0.5, 0.45]}),
 "theodora": P(file="src/theodora.jpg", commons="File:Mosaic of Theodora - Basilica San Vitale (Ravenna).jpg", depth=True,
               credit="Mosaic of Theodora, San Vitale, Ravenna: photo Petar Milošević, CC BY-SA 4.0",
               points={"theodora": [0.45, 0.29], "court": [0.6, 0.45], "center": [0.5, 0.5]}),
 "vienna": P(file="src/vienna.jpg", commons="File:Wien Opernhaus um 1900.jpg", depth=True, points={"opera": [0.5, 0.35], "street": [0.45, 0.8]}),
 "ferdinand": P(file="src/ferdinand.jpg", commons="File:Ferdinand Bloch Baur nel 1935.jpg", points={"face": [0.5, 0.3], "center": [0.5, 0.5]}),
 "factory": P(file="src/factory.jpg", commons="File:Zuccherificio dei Bloch-Bauer - Bruck an der Leitha (Wien).jpg", points={"factory": [0.62, 0.45]}),
 "heldenplatz": P(file="src/heldenplatz.jpg", commons="File:Anschluss Heldenplatz1.jpg", points={"crowd": [0.4, 0.55], "banner": [0.72, 0.3], "square": [0.45, 0.45]}),
 "walter": P(file="src/walter.jpg", commons="File:Dr. Bruno Walter, 1937.jpg", points={"face": [0.7, 0.48], "center": [0.5, 0.5]}),
 "kammer": P(file="src/kammer.jpg", commons="File:Gustav Klimt - Schloss Kammer am Attersee III - 4318 - Österreichische Galerie Belvedere.jpg",
             depth=True, points={"castle": [0.5, 0.35], "lake": [0.5, 0.78]}),
 "birch": P(file="src/birch.jpg", commons="File:Gustav Klimt, Birch Forest, 1903 - Paul G. Allen Collection.jpg", points={"center": [0.5, 0.5]}),
 "unterach": P(file="src/unterach.jpg", commons="File:Houses at Unterach am Attensee.jpg", points={"center": [0.5, 0.5]}),
 "apple": P(file="src/apple.jpg", commons="File:Klimt-Apfelbaum I.jpg", points={"center": [0.5, 0.45]}),
 "belvedere": P(file="src/belvedere.jpg", commons="File:Upper Belvedere LCD-toneedit2 NR.jpg", depth=True,
                credit="Upper Belvedere, Vienna: photo Murdockcrc, CC BY 3.0 (Wikimedia Commons)", points={"palace": [0.5, 0.42], "door": [0.5, 0.45]}),
 "supreme": P(file="src/supreme.jpg", commons="File:U.S. Supreme Court building-m.jpg", depth=True, points={"front": [0.48, 0.45], "pediment": [0.48, 0.22]}),
 "neue": P(file="src/neue.jpg", commons="File:The Neue Galerie, New York.jpg",
           credit="The Neue Galerie, New York: photo Francesca.hyanna19, CC BY-SA 4.0 (Wikimedia Commons)", points={"center": [0.5, 0.5], "entrance": [0.6, 0.8]}),
})

FOUR = ["birch", "apple", "unterach", "kammer"]                 # Adele's four Klimt landscapes (the 1923 will)
FIVE = ["adele", "adele2", "birch", "apple", "unterach"]         # the five paintings returned in 2006

# ---------------------------------------------------------------- shots (about one per line; slow travelling moves)
# cold open: her eyes, the palace, the face, the reveal on the title line
sh(A("cold1"), "adele", "eyes@2.6", "eyes@2.4")
sh(A("cold2"), "belvedere", "palace@1.0", "palace@1.08", fade=1.0, dolly=[0, 0.04])
sh(A("cold2", "one", off=-0.1), "adele", "face@1.9", "face@2.05", fade=0.8)
sh(A("cold3"), "adele", "hands@2.2", "hands@2.05", fade=0.8)
sh(A("cold4"), "adele", "eyes@2.3", "eyes@2.45", gray=0.85, dim=0.25, fade=0.8)
sh(A("cold5"), "adele", "bust@1.5", "bust@1.62", fade=1.0)
sh(A("cold6"), "adele", "full@0.5625", "full@0.575", frame=True, fade=1.2)
# I. A Present That Came Late
sh(A("c1a"), "vienna", "opera@1.0", "opera@1.1", gray=0.35, fade=1.0, dolly=[0, 0.04])
sh(A("c1a", "Ferdinand", off=-0.1), "ferdinand", "center@0.62", "center@0.64", frame=True, gray=1, fade=0.6)
sh(A("c1b"), "factory", "factory@1.0", "factory@1.08", gray=1, fade=0.8)
sh(A("c1b", "Later", off=-0.1), "adele_photo", "body@0.62", "body@0.64", frame=True, fade=0.8)
sh(A("c1c"), "adele_photo", "face@1.5", "face@1.62", fade=0.8)
sh(A("c1c", "Gustav", off=-0.15), "klimt", "face@1.25", "face@1.35", fade=0.6)
sh(A("c1d"), "adele", "face@1.5", "face@1.6", fade=1.0)
sh(A("c1e"), "adele", "upper@1.15", "upper@1.05", gray=0.4, fade=0.8)
# II. Gold
sh(A("c2a"), "seated", "top@1.0", "body@1.0", fade=1.0)
sh(A("c2a", "standing", off=-0.1), "study", "top@1.0", "body@1.0", fade=0.6)
sh(A("c2a", "More", off=-0.1), "study", kind="grid", imgs=["seated", "study"], fade=0.6)
sh(A("c2b"), "theodora", "center@1.0", "court@1.12", fade=1.0, dolly=[0, 0.04])
sh(A("c2c", "Theodora", off=-0.1), "theodora", "theodora@1.9", "theodora@2.05", fade=0.8)
sh(A("c2c", "He", off=-0.1), "theodora", "center@1.05", "center@1.0", fade=0.8)
sh(A("c2d"), "adele", "face@2.2", "face@2.1", fade=1.0)
sh(A("c2d", "Everything", off=-0.1), "adele", "spirals@2.2", "spirals@2.05", fade=0.6)
sh(A("c2d", "patterns", off=-0.1), "adele", "squares@2.3", "squares@2.15", fade=0.6)
sh(A("c2e"), "adele", "dress_eyes@2.0", "dress_eyes@1.88", fade=0.8)
sh(A("c2e", "chair", off=-0.1), "adele", "chair@1.7", "chair@1.6", fade=0.6)
sh(A("c2e", "museum", off=-0.1), "adele", "center@1.0", "center@1.04", fade=0.8)
sh(A("c2f"), "adele", "hands@2.7", "hands@2.55", fade=0.8)
sh(A("c2g"), "adele", "full@0.5625", "full@0.575", frame=True, fade=1.0)
sh(A("c2g", "One", off=-0.1), "adele", "face@1.7", "face@1.8", fade=0.8)
# III. Adele's Wish
sh(A("c3a"), "adele2", "face@1.35", "face@1.45", fade=1.2)
sh(A("c3a", "another", off=-0.1), "adele2", "full@0.5625", "full@0.575", frame=True, fade=0.8)
sh(A("c3b"), "klimt", "face@1.5", "face@1.6", gray=1, fade=1.0)
sh(A("c3c"), "adele_photo", "face@1.7", "face@1.8", gray=0.3, fade=1.0)
sh(A("c3d"), "adele", "face@1.4", "face@1.5", dim=0.45, gray=0.3, fade=1.0)
sh(A("c3e"), "adele", "eyes@2.7", "eyes@2.85", fade=1.0)
sh(A("c3f"), "birch", kind="grid", imgs=FOUR, fade=1.0)
sh(A("c3f", "He", off=-0.1), "ferdinand", "center@0.62", "center@0.64", frame=True, gray=1, fade=0.8)
sh(A("c3f", "He", 2, off=-0.1), "adele", "eyes@2.3", "eyes@2.4", gray=0.7, fade=0.8)
# IV. 1938
sh(A("c4a"), "vienna", "street@1.4", "street@1.5", gray=0.6, fade=1.2)
sh(A("c4b"), "heldenplatz", "square@1.0", "square@1.06", gray=1, fade=1.0)
sh(A("c4b", "music", off=-0.1), "walter", "center@0.62", "center@0.64", frame=True, gray=1, fade=0.8)
sh(A("c4c"), "heldenplatz", "banner@1.6", "banner@1.7", gray=1, fade=0.8)
sh(A("c4d"), "adele", "eyes@2.4", "eyes@2.55", gray=0.9, dim=0.2, fade=1.0)
sh(A("c4d", "Maria", 2, off=-0.1), "adele", "bust@1.6", "bust@1.7", gray=0.5, fade=0.8)
sh(A("c4e"), "ferdinand", "center@0.62", "center@0.64", frame=True, gray=1, fade=1.0)
sh(A("c4e", "seized", off=-0.1), "factory", "factory@1.25", "factory@1.35", gray=1, fade=0.8)
sh(A("c4f"), "belvedere", "door@1.5", "door@1.62", gray=1, dim=0.15, fade=1.0)
sh(A("c4f", "traded", off=-0.1), "adele", kind="pair", img2="kammer", labels=["ADELE BLOCH-BAUER I", "KAMMER CASTLE III"], fade=0.8)
sh(A("c4f", "which", off=-0.1), "kammer", "castle@1.15", "castle@1.25", fade=0.8)
sh(A("c4g", "he", off=-0.1), "klimt", "face@1.5", "face@1.6", gray=1, fade=0.8)
sh(A("c4h"), "adele", "face@1.7", "face@1.82", gray=0.8, dim=0.3, fade=1.0)
sh(A("c4i"), "adele", "full@0.5625", "full@0.575", frame=True, gray=0.3, fade=1.0)
sh(A("c4j"), "ferdinand", "center@0.62", "center@0.64", frame=True, gray=1, fade=1.0)
sh(A("c4j", "One", off=-0.1), "adele", "eyes@2.4", "eyes@2.55", fade=1.0)
# V. Austria's Mona Lisa
sh(A("c5a"), "belvedere", "palace@1.0", "palace@1.08", fade=1.2, dolly=[0, 0.04])
sh(A("c5b"), "belvedere", "door@1.6", "door@1.7", gray=0.5, fade=0.8)
sh(A("c5b", "In", off=-0.1), "birch", kind="grid", imgs=FOUR, fade=0.8)
sh(A("c5c"), "adele", "full@0.5625", "full@0.575", frame=True, fade=1.0)
sh(A("c5c", "And", off=-0.1), "adele", "face@1.85", "face@1.95", gray=0.6, fade=0.8)
sh(A("c5d"), "belvedere", "palace@1.25", "palace@1.35", fade=1.0)
sh(A("c5e"), "adele", "hands@2.4", "hands@2.3", gray=0.5, fade=0.8)
sh(A("c5f"), "ferdinand", "center@0.62", "center@0.64", frame=True, gray=1, fade=1.0)
sh(A("c5f", "Her", off=-0.1), "adele", "face@1.6", "face@1.7", fade=0.8)
# VI. Maria v. Austria
sh(A("c6a"), "adele", "bust@1.4", "bust@1.5", fade=1.2)
sh(A("c6a", "Randol", off=-0.1), "adele", "spirals@1.8", "spirals@1.9", fade=0.8)
sh(A("c6b"), "belvedere", "door@1.4", "door@1.5", gray=0.4, fade=1.0)
sh(A("c6c"), "adele", "squares@2.0", "squares@2.1", fade=1.0)
sh(A("c6c", "So", off=-0.1), "adele", "face@1.5", "face@1.6", fade=0.8)
sh(A("c6d"), "supreme", "front@1.0", "front@1.1", fade=1.0, dolly=[0, 0.04])
sh(A("c6d", "In", off=-0.1), "supreme", "pediment@1.45", "pediment@1.55", fade=0.8)
sh(A("c6e"), "adele", "bust@1.3", "bust@1.4", fade=1.0)
sh(A("c6e", "Five", off=-0.1), "adele", kind="grid", imgs=FIVE, fade=0.8)
sh(A("c6f"), "adele", "face@1.8", "face@1.9", fade=1.0)
sh(A("c6g"), "adele", "full@0.5625", "full@0.575", frame=True, fade=1.0)
# VII. Home
sh(A("c7a"), "adele2", "face@1.4", "face@1.5", fade=1.2)
sh(A("c7a", "That", off=-0.1), "neue", "entrance@1.28", "entrance@1.38", kind="image", fade=0.8)
sh(A("c7a", "for", 3, off=-0.1), "adele", "bust@1.25", "bust@1.35", fade=0.8)
sh(A("c7b"), "adele", "face@1.7", "face@1.8", fade=0.8)
sh(A("c7c"), "adele", "eyes@2.2", "eyes@2.3", gray=0.3, fade=1.0)
sh(A("c7c", "Four", off=-0.1), "adele", "center@1.0", "center@1.05", fade=0.8)
sh(A("c7d"), "adele", "face@1.3", "face@1.2", fade=1.2)
sh(A("c7d", "A", 2, off=-0.1), "adele", "full@0.5625", "full@0.58", frame=True, fade=1.2)
sh(A("ending"), "adele", "eyes@1.9", "eyes@2.0", fade=1.2)

# ---------------------------------------------------------------- overlays
CH = [("cold6", "c1a", "I", "A Present That Came Late"), ("c1e", "c2a", "II", "Gold"), ("c2g", "c3a", "III", "Adele's Wish"),
      ("c3f", "c4a", "IV", "1938"), ("c4j", "c5a", "V", "Austria's Mona Lisa"), ("c5f", "c6a", "VI", "Maria v. Austria"),
      ("c6g", "c7a", "VII", "Home")]
ov("title", A("cold6", "the"), A("cold6", end=True, off=0.6), kicker="GUSTAV KLIMT · 1903–1907", text="Adele Bloch-Bauer I")
for prev, nxt, n, name in CH:
    ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("label", A("cold1", off=0.3), A("cold1", end=True, off=0.6), text="ADELE BLOCH-BAUER I · GUSTAV KLIMT · 1907")
ov("label", A("cold2"), A("cold2", "one", off=-0.15), text="THE BELVEDERE · VIENNA")
ov("credit", A("cold2"), A("cold2", "one", off=-0.15), text="Photo: Murdockcrc, CC BY 3.0, Wikimedia Commons")
ov("quote", A("cold4", "with", off=-0.1), A("cold4", end=True, off=0.9), text="Heil Hitler.", sub="COVER NOTE DELIVERING THE PORTRAIT · 1941")
ov("year", A("c1a"), A("c1a", "Adele", off=-0.1), text="1899")
ov("label", A("c1a"), A("c1a", "Ferdinand", off=-0.15), text="VIENNA · THE OPERA · c. 1900")
ov("lower", A("c1a", "Ferdinand", off=0.1), A("c1a", end=True, off=0.6), text="Ferdinand Bloch", sub="1864–1945 · PHOTOGRAPH, 1935")
ov("label", A("c1b"), A("c1b", "Later", off=-0.15), text="THE BLOCH-BAUER SUGAR FACTORY")
ov("lower", A("c1b", "Bloch-Bauer", off=0.1), A("c1c", "Writers", off=-0.1), text="Adele Bloch-Bauer", sub="1881–1925 · PHOTOGRAPH, c. 1910")
ov("lower", A("c1c", "Gustav", off=0.1), A("c1c", end=True, off=0.6), text="Gustav Klimt", sub="1862–1918 · MORIZ NÄHR, 1911")
ov("year", A("c1d"), A("c1d", "Ferdinand", off=-0.1), text="1903")
ov("label", A("c2a"), A("c2a", "More", off=-0.15), text="STUDIES FOR THE PORTRAIT · 1903–1904")
ov("year", A("c2b"), A("c2b", "Klimt", off=-0.1), text="DECEMBER 1903")
ov("label", A("c2b", "Klimt"), A("c2c", "He", off=-0.15), text="SAN VITALE · RAVENNA · 6TH CENTURY")
ov("credit", A("c2b"), A("c2c", end=True, off=0.5), text="Photo: Petar Milošević, CC BY-SA 4.0")
ov("quote", A("c2c", "He", off=-0.1), A("c2c", end=True, off=0.9), text="Mosaics of unprecedented splendor.", sub="KLIMT ON RAVENNA · NEUE GALERIE")
ov("ring", A("c2f", "look", off=0.1), A("c2f", end=True, off=0.6), point="hands", img="adele", rx=150, ry=120, rot=-12)
ov("year", A("c2g"), A("c2g", "Critics", off=-0.1), text="1907")
ov("quote", A("c2g", "Mehr", off=-0.15), A("c2g", end=True, off=1.2), text="Mehr Blech als Bloch.", sub="«MORE BRASS THAN BLOCH» · NEUES WIENER TAGBLATT")
ov("lower", A("c3a", "another", off=0.1), A("c3a", end=True, off=0.8), text="Adele Bloch-Bauer II", sub="GUSTAV KLIMT · 1912")
ov("year", A("c3b", "in"), A("c3b", "Klimt", off=-0.1), text="FEBRUARY 1918")
ov("year", A("c3c"), A("c3c", "Adele", off=-0.1), text="1923")
ov("quote", A("c3d", off=-0.1), A("c3d", end=True, off=1.0), text="I ask my husband after his death to leave my two portraits and the four landscapes by Gustav Klimt to the Austrian State Gallery in Vienna.",
   sub="ADELE BLOCH-BAUER · WILL, 1923")
ov("year", A("c3e", "in"), A("c3e", "Adele", off=-0.1), text="JANUARY 1925")
ov("label", A("c3f"), A("c3f", "He", off=-0.15), text="ADELE'S FOUR KLIMT LANDSCAPES")
ov("year", A("c4a"), A("c4a", "Adele's", off=-0.1), text="DECEMBER 1937")
ov("year", A("c4b"), A("c4b", "German", off=-0.1), text="MARCH 1938")
ov("label", A("c4b", "German"), A("c4b", "music", off=-0.15), text="HELDENPLATZ · VIENNA · 15 MARCH 1938")
ov("lower", A("c4b", "music", off=0.1), A("c4b", end=True, off=0.6), text="Bruno Walter", sub="MAHLER, SYMPHONY NO. 9 · VIENNA, 16 JANUARY 1938")
ov("label", A("c4e"), A("c4e", "seized", off=-0.15), text="FERDINAND BLOCH-BAUER · 1935")
ov("lower", A("c4f", "Erich", off=0.0), A("c4f", "In", off=-0.1), text="Erich Führer", sub="NAZI LAWYER · ADMINISTRATOR OF THE ESTATE")
ov("year", A("c4f", "In"), A("c4f", "he", off=-0.1), text="1941")
ov("lower", A("c4f", "Gustav", off=0.0), A("c4g", "he", off=-0.4), text="Gustav Ucicky", sub="1899–1961 · FILM DIRECTOR")
ov("quote", A("c4h", "Signed", off=-0.1), A("c4h", end=True, off=1.0), text="Heil Hitler.", sub="ERICH FÜHRER · 1941")
ov("title", A("c4i", "The", 3, off=-0.2), A("c4i", end=True, off=1.0), kicker="NEW TITLE · 1941", text="Dame in Gold")
ov("year", A("c4j", "He"), A("c4j", "almost", off=-0.1), text="NOVEMBER 1945")
ov("label", A("c5a"), A("c5b", "In", off=-0.15), text="THE BELVEDERE · VIENNA")
ov("year", A("c5b", "In"), A("c5b", "the", off=-0.1), text="1948")
ov("label", A("c5c"), A("c5c", "And", off=-0.15), text="«AUSTRIA'S MONA LISA»")
ov("year", A("c5d"), A("c5d", "Austria", off=-0.1), text="1998")
ov("lower", A("c5d", "Hubertus", off=0.0), A("c5d", end=True, off=0.6), text="Hubertus Czernin", sub="JOURNALIST · 1956–2006")
ov("lower", A("c6a"), A("c6a", "Randol", off=-0.1), text="Maria Altmann", sub="1916–2011 · ADELE'S NIECE")
ov("lower", A("c6a", "Randol", off=0.0), A("c6a", end=True, off=0.6), text="E. Randol Schoenberg", sub="LAWYER · LOS ANGELES")
ov("year", A("c6b"), A("c6b", "Austria's", off=-0.1), text="1999")
ov("stamp", A("c6c", "about", off=0.1), A("c6c", "up", off=0.8), text="$1.5 MILLION")
ov("year", A("c6d", "In"), A("c6d", "it", off=-0.1), text="JUNE 2004")
ov("title", A("c6d", "it"), A("c6d", end=True, off=1.0), kicker="REPUBLIC OF AUSTRIA v. ALTMANN", text="Six to three")
ov("year", A("c6e", "In"), A("c6e", "they", off=-0.1), text="JANUARY 2006")
ov("label", A("c6e", "Five"), A("c6e", end=True, off=0.8), text="THE FIVE PAINTINGS RETURNED")
ov("title", A("c6g", "Ciao", off=-0.1), A("c6g", end=True, off=1.6), kicker="POSTERS ACROSS VIENNA · 2006", text="Ciao Adele")
ov("year", A("c7a"), A("c7a", "the", off=-0.1), text="MARCH 2006")
ov("credit", A("c7a", "That"), A("c7a", "for", 3, off=-0.15), text="Photo: Francesca.hyanna19, CC BY-SA 4.0, Wikimedia Commons")
ov("label", A("c7a", "That"), A("c7a", "for", 3, off=-0.15), text="NEUE GALERIE · NEW YORK")
ov("quote", A("c7b"), A("c7b", end=True, off=1.0), text="Our Mona Lisa.", sub="RONALD LAUDER · 2006")
ov("year", A("c7c"), A("c7c", "at", off=-0.1), text="2011")
ov("title", A("c7c", "Woman", off=-0.2), A("c7c", end=True, off=1.2), kicker="2015 · HELEN MIRREN AS MARIA ALTMANN", text="Woman in Gold")
ov("lower", A("c7d", "Adele", 2, off=-0.1), A("c7d", end=True, off=1.2), text="Adele Bloch-Bauer I", sub="GUSTAV KLIMT · 1907 · NEUE GALERIE NEW YORK")
ov("pin", A("ending", off=0.1), A("ending", end=True, off=1.0), text="NEUE GALERIE · NEW YORK · 1048 FIFTH AVENUE")
ov("end", A("ending", end=True, off=1.0), A("ending", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound: a Vienna-1900 cue sheet (public domain / CC0), soft effects
SFX += [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.22} for prev, _, _, _ in CH] + [
 {"at": A("cold4", "Heil", off=-0.05), "fx": "impact", "gain": 0.25},
 {"at": A("c4h", "Heil", off=-0.05), "fx": "impact", "gain": 0.25},
 {"at": A("c6g", "Ciao"), "fx": "chime", "gain": 0.16},
]
# track start points (s), from each recording's loudness map and the voice timeline: the Adagietto's first climax lands on
# Adele's will (c3d), its last on the closing reflection (c7d)
AD_OPEN, M4_START, AD_MID, M4R_LATE, M4_LATE, AD_CLIMAX = 0.0, 0.0, 152.0, 200.0, 300.0, 518.0
T = lambda f, frm, to, credit, **kw: {"file": f"src/music/{f}", "from": frm, **({"to": to} if to is not None else {}), "start": kw.pop("start", 0),
                                     "gain_db": kw.pop("gain_db", 0), "fade_in": kw.pop("fade_in", 2.5), "fade_out": kw.pop("fade_out", 3.0), "credit": credit}
AD = "Mahler, Symphony No. 5: Adagietto · Peabody Symphony Orchestra, CC0"
M4 = "Mahler, Symphony No. 4 · European Archive, public domain"
M9 = "Mahler, Symphony No. 9: Adagio · Vienna Philharmonic, Bruno Walter, 16 January 1938, public domain"
MUSIC.update({
 "pad": False, "whooshes": False, "music_db": -7.5, "duck_db": -7, "fx_db": -12, "transpose": 0, "bar": 5.5,
 "_tracks_note": "Vienna-1900 cue sheet (17 Nov 2026): the Adagietto (1901-02) for Adele, Mahler's Fourth for Klimt's Vienna, "
                 "Bruno Walter's live Vienna recording of the Ninth (16 Jan 1938, weeks before the Anschluss) for 1938.",
 "tracks": [
  T("m_adagietto.ogg", 0, A("c1a", off=1.5), AD, start=AD_OPEN, fade_in=0.6),
  T("m_m4first.ogg", A("cold6", end=True, off=-0.5), A("c2a", off=1.5), M4, start=M4_START, gain_db=-2),
  T("m_m4ruhe.ogg", A("c1e", end=True, off=-0.5), A("c3a", off=1.5), M4, start=0.5, gain_db=-1),
  T("m_adagietto.ogg", A("c2g", end=True, off=-0.5), A("c4a", off=1.5), AD, start=AD_MID),
  T("m_m9walter.ogg", A("c3f", end=True, off=-0.5), A("c5a", off=1.5), M9, start=0.5, gain_db=1),
  T("m_m4ruhe.ogg", A("c4j", end=True, off=-0.5), A("c6a", off=1.5), M4, start=M4R_LATE, gain_db=-1),
  T("m_m4first.ogg", A("c5f", end=True, off=-0.5), A("c7a", off=1.5), M4, start=M4_LATE, gain_db=-2),
  T("m_adagietto.ogg", A("c6g", end=True, off=-0.5), None, AD, start=AD_CLIMAX, fade_out=8.0),
 ],
 "heartbeat": [A("cold4", off=-0.6), A("cold4", "Heil", off=-0.2)], "heartbeat_gain": 0.22,
})
