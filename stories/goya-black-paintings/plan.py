"""Writes story.json for the first long-form video (16:9). Shots and overlays are anchored to words by text, so the
plan survives script edits: ("line", "word") -> "line.k" where k is that word's index in the line.
usage: python stories/goya-black-paintings/plan.py"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- script: [text, pause_after_s, speed_mult]
L = [
 # cold open
 ("cold1", [["In the 1870s,", 0.25, 0.95], ["a photographer carried his camera", 0.15, 1.0], ["into an empty house on the edge of Madrid.", 0.6, 0.95]]),
 ("cold2", [["The plaster was cracking.", 0.35, 0.95], ["The house was falling apart.", 0.6, 0.95]]),
 ("cold3", [["And on the walls...", 0.4, 0.9], ["someone had painted *nightmares.*", 0.8, 0.9]]),
 ("cold4", [["A giant, eating a man.", 0.45, 0.9], ["Witches, gathered around a goat.", 0.45, 0.92],
            ["Two old people grinning over a bowl of soup,", 0.25, 0.95], ["like corpses at dinner.", 0.8, 0.9]]),
 ("cold5", [["*Nobody* was supposed to see these.", 0.5, 0.9], ["They had no titles.", 0.25, 0.95], ["No signature.", 0.3, 0.95],
            ["The man who painted them never wrote a single word about them.", 0.7, 0.95]]),
 ("cold6", [["He was the most famous painter in Spain.", 0.35, 0.95], ["Francisco de Goya.", 0.6, 0.88],
            ["And these were the walls of his own home.", 0.9, 0.92]]),
 ("cold7", [["This is the story of the Black Paintings.", 0.35, 0.95], ["Why he painted them,", 0.2, 0.97], ["and how they escaped.", 2.4, 0.9]]),
 # I
 ("c1a", [["Madrid.", 0.3, 0.9], ["February, 1819.", 0.6, 0.92]]),
 ("c1b", [["Goya is seventy-two years old.", 0.3, 0.95], ["He has painted kings, queens and dukes for more than thirty years.", 0.4, 1.0],
          ["He is rich. He is famous.", 0.35, 0.97], ["And he hasn't heard a sound in twenty-six years.", 0.7, 0.92]]),
 ("c1c", [["An illness took his hearing when he was forty-six.", 0.35, 0.97], ["Since then, he has lived through a war with Napoleon,", 0.25, 1.0],
          ["and painted what he saw.", 0.8, 0.93]]),
 ("c1d", [["Now he buys a house outside the city,", 0.25, 1.0], ["across the Manzanares river.", 0.3, 0.97], ["A farmhouse with two large rooms.", 0.7, 0.97]]),
 ("c1e", [["The neighbours already have a name for it.", 0.3, 0.97], ["La Quinta del Sordo.", 0.35, 0.9], ["The Deaf Man's House.", 0.6, 0.9]]),
 ("c1f", [["Not because of Goya.", 0.3, 0.95], ["The man who owned it before him was deaf, too.", 0.8, 0.95]]),
 ("c1g", [["Goya moves in with Leocadia Weiss,", 0.2, 0.97], ["a woman more than forty years younger,", 0.25, 1.0],
          ["his housekeeper and companion,", 0.25, 1.0], ["and her little daughter, Rosario.", 0.7, 0.95]]),
 ("c1h", [["Why here?", 0.35, 0.9], ["Historians think he wanted to get away.", 0.25, 0.97], ["From the court,", 0.2, 0.97], ["and from the king,", 0.2, 0.97],
          ["Ferdinand the Seventh.", 2.2, 0.92]]),
 # II
 ("c2a", [["At the end of that year,", 0.25, 0.97], ["Goya nearly dies.", 0.6, 0.9]]),
 ("c2b", [["We don't know what the illness was.", 0.3, 0.97], ["We know how close it came...", 0.3, 0.95], ["because he painted it.", 0.7, 0.92]]),
 ("c2c", [["A doctor holds him up", 0.15, 1.0], ["and puts a glass to his lips.", 0.35, 0.97], ["Behind them, faces wait in the dark.", 0.7, 0.93]]),
 ("c2d", [["At the bottom, Goya painted a thank-you note.", 0.4, 0.97], ["To his friend, Doctor Arrieta,", 0.25, 0.95], ["for the skill and care", 0.15, 0.97],
          ["with which he saved his life,", 0.3, 0.95], ["in his acute and dangerous illness,", 0.25, 0.97], ["at the end of 1819,", 0.25, 0.97],
          ["at seventy-three years of age.", 0.8, 0.92]]),
 ("c2e", [["He survives.", 0.45, 0.9], ["And when he can stand again,", 0.2, 0.97], ["he picks up his brushes...", 0.35, 0.95], ["and starts on the walls.", 2.2, 0.9]]),
 # III
 ("c3a", [["The rooms were already decorated.", 0.25, 0.97], ["Cheerful country scenes.", 0.2, 0.97], ["Little figures in a landscape.", 0.5, 0.97]]),
 ("c3b", [["Goya paints over all of it.", 0.3, 0.95], ["In oil, straight onto the plaster.", 0.7, 0.95]]),
 ("c3c", [["Downstairs is the dining room.", 0.35, 0.95], ["One wall holds a crowd of pilgrims,", 0.15, 0.97], ["stumbling home through the dark,", 0.25, 1.0],
          ["mouths wide open.", 0.25, 0.95], ["Singing, or screaming.", 0.45, 0.93],
          ["Painted by a man who hadn't heard a voice in almost thirty years.", 0.8, 0.93]]),
 ("c3d", [["On the other long wall,", 0.15, 0.97], ["witches gather around a huge black goat.", 0.3, 0.97], ["The Devil, preaching in the dark.", 0.8, 0.93]]),
 ("c3e", [["By the door, a woman in black", 0.15, 0.97], ["leans on what looks like a grave.", 0.3, 0.95], ["Many think it's Leocadia.", 0.7, 0.95]]),
 ("c3f", [["Two old men.", 0.3, 0.95], ["One shouts into the other's ear,", 0.3, 0.95], ["the way you'd talk to a deaf man.", 0.7, 0.92]]),
 ("c3g", [["Judith, about to cut off a general's head.", 0.7, 0.95]]),
 ("c3h", [["And on the back wall, facing the woman in black,", 0.5, 0.93], ["is *Saturn.*", 1.2, 0.85]]),
 ("c3i", [["Upstairs, there is a second room.", 0.3, 0.95], ["Two men club each other,", 0.15, 0.97], ["sunk to their knees in the earth.", 0.4, 0.95],
          ["The Fates float over the land, one holding scissors.", 0.3, 0.97], ["Two figures fly over a rock while soldiers take aim.", 0.4, 0.97],
          ["Men reading.", 0.25, 0.97], ["Women laughing.", 0.25, 0.97], ["A procession of the Inquisition.", 0.5, 0.95],
          ["And by the door...", 0.35, 0.92], ["a dog.", 0.6, 0.88], ["We'll come back to the dog.", 0.9, 0.95]]),
 ("c3j", [["Fourteen paintings.", 0.35, 0.9], ["No titles.", 0.25, 0.95], ["No signatures.", 0.25, 0.95], ["No dates.", 0.4, 0.95],
          ["Every name you know them by was given later, by other people.", 0.5, 0.97], ["Today we call them the Black Paintings.", 2.2, 0.92]]),
 # IV
 ("c4a", [["In the old legend,", 0.2, 0.97], ["the titan Saturn is warned", 0.15, 0.97], ["that one of his children will overthrow him.", 0.35, 0.97],
          ["So, as each one is born,", 0.2, 0.97], ["he swallows it.", 0.7, 0.9]]),
 ("c4b", [["Rubens painted the scene for the King of Spain,", 0.25, 0.97], ["almost two hundred years earlier.", 0.35, 0.97],
          ["Goya could have seen it in the royal collection.", 0.6, 0.97]]),
 ("c4c", [["In Rubens, Saturn is a god doing his job.", 0.3, 0.97], ["Calm.", 0.25, 0.92], ["Calculating.", 0.7, 0.92]]),
 ("c4d", [["Goya's Saturn is something else.", 0.35, 0.95], ["Look at his eyes.", 0.45, 0.9], ["He doesn't look powerful.", 0.25, 0.95],
          ["He looks *terrified.*", 0.4, 0.9], ["Like someone who can't stop what he's doing.", 0.8, 0.93]]),
 ("c4e", [["And look at who he's eating.", 0.3, 0.95], ["It isn't swallowed. It's being torn apart.", 0.4, 0.95], ["The head is already gone.", 0.4, 0.93],
          ["And it doesn't look like a baby.", 0.3, 0.95], ["One scholar argues it's an adult.", 0.8, 0.95]]),
 ("c4f", [["Here's the strange part.", 0.35, 0.93], ["Even those eyes aren't entirely by Goya.", 0.4, 0.95], ["They were so badly damaged", 0.15, 0.97],
          ["that a restorer had to repaint them.", 0.6, 0.95]]),
 ("c4g", [["And some historians claim the original wall showed something else,", 0.25, 0.97], ["something sexual,", 0.25, 0.95],
          ["that was painted out when the walls came down.", 0.8, 0.95]]),
 ("c4h", [["What does it mean?", 0.35, 0.93], ["Time devouring everything.", 0.25, 0.97], ["Old age eating youth.", 0.25, 0.97],
          ["Spain devouring its own children in war.", 0.25, 0.97], ["A man afraid of going mad.", 0.4, 0.95], ["Every one of these has been argued.", 0.3, 0.97],
          ["Goya never said.", 0.6, 0.9]]),
 ("c4i", [["All we know is where he put it.", 0.3, 0.95], ["In the room where he ate.", 2.2, 0.9]]),
 # V
 ("c5a", [["In 1823,", 0.25, 0.95], ["a French army marches into Spain", 0.15, 1.0], ["and hands King Ferdinand back his absolute power.", 0.5, 0.97]]),
 ("c5b", [["Liberals are arrested,", 0.2, 0.97], ["exiled,", 0.2, 0.97], ["executed.", 0.5, 0.92], ["And Goya has friends on the wrong side.", 0.6, 0.95]]),
 ("c5c", [["That year, he signs the house over to his grandson, Mariano.", 0.3, 0.97], ["Then he goes into hiding,", 0.2, 0.97],
          ["at the home of a friend, a priest.", 0.7, 0.95]]),
 ("c5d", [["In May 1824,", 0.2, 0.97], ["he asks the king for permission to leave,", 0.2, 0.97], ["to take the waters at a spa in France.", 0.6, 0.97]]),
 ("c5e", [["The king says yes.", 0.4, 0.95], ["Goya crosses the border at seventy-eight,", 0.2, 0.97], ["deaf, and alone,", 0.25, 0.95],
          ["and settles in Bordeaux.", 0.7, 0.95]]),
 ("c5f", [["He comes back to Madrid only briefly.", 0.35, 0.97], ["On the sixteenth of April, 1828,", 0.2, 0.97], ["he dies in Bordeaux, at eighty-two.", 0.7, 0.93]]),
 ("c5g", [["He leaves fourteen paintings", 0.15, 0.97], ["on the walls of a house that isn't his anymore.", 0.4, 0.95], ["And in all his letters,", 0.2, 0.97],
          ["not one word about them.", 2.2, 0.9]]),
 # VI
 ("c6a", [["After his death, a painter friend, Antonio Brugada,", 0.2, 0.97], ["walks through the house and lists what's on the walls.", 0.4, 0.97],
          ["Forty years later, a French writer does the same.", 0.4, 0.97], ["Those two lists are how we know where each painting hung.", 0.7, 0.97]]),
 ("c6b", [["The house passes through the family, then to strangers.", 0.35, 0.97], ["Fifty years on, it's falling apart.", 0.7, 0.95]]),
 ("c6c", [["In 1873,", 0.2, 0.97], ["a rich banker from Paris buys it.", 0.2, 0.97], ["Baron Émile d'Erlanger.", 0.6, 0.92]]),
 ("c6d", [["Before anything is touched,", 0.2, 0.97], ["a photographer, Jean Laurent, records the walls.", 0.4, 0.97],
          ["That's the photographer from the beginning of this story.", 0.4, 0.97],
          ["His pictures are the closest we will ever get to what Goya actually painted.", 0.8, 0.95]]),
 ("c6e", [["Then the Baron hires the Prado's chief restorer,", 0.2, 0.97], ["Salvador Martínez Cubells,", 0.3, 0.93], ["to take the paintings off the walls.", 0.6, 0.95]]),
 ("c6f", [["Piece by piece,", 0.2, 0.95], ["the paint is lifted off the plaster", 0.15, 0.97], ["and glued onto canvas.", 0.4, 0.95],
          ["What breaks is painted back in.", 0.6, 0.93], ["Experts agree that much of what we see today was repainted.", 0.7, 0.95]]),
 ("c6h", [["The witches were even cut down,", 0.2, 0.97], ["probably to fit a wall in Paris.", 0.5, 0.95], ["Because that was the plan.", 0.35, 0.95],
          ["Paris.", 0.3, 0.9], ["The World's Fair of 1878.", 0.6, 0.95]]),
 ("c6i", [["They hang in the Trocadéro Palace from May to November.", 0.4, 0.97], ["They don't sell.", 0.6, 0.93],
          ["The next year, a British critic calls Goya", 0.2, 0.97], ["a monster of immorality, impudence, and ingratitude.", 0.8, 0.95]]),
 ("c6j", [["In 1881, the Baron gives them to Spain.", 0.3, 0.97], ["They go to the Prado.", 0.5, 0.95], ["And the Deaf Man's House?", 0.4, 0.93],
          ["Demolished, in 1909.", 2.2, 0.9]]),
 # VII
 ("c7a", [["In 2003,", 0.2, 0.97], ["a Spanish art historian, Juan José Junquera,", 0.2, 0.97], ["makes an explosive claim.", 0.4, 0.95], ["Goya didn't paint them.", 0.8, 0.9]]),
 ("c7b", [["His evidence:", 0.2, 0.95], ["property records that describe the house with only one floor.", 0.35, 0.97],
          ["If the upstairs room didn't exist in Goya's time,", 0.2, 0.97], ["who painted its walls?", 0.8, 0.93]]),
 ("c7c", [["His suspect: Goya's own son, Javier.", 0.35, 0.95], ["And the grandson, Mariano, short of money,", 0.2, 0.97],
          ["would have sold them as his grandfather's.", 0.8, 0.95]]),
 ("c7d", [["Most experts reject it.", 0.3, 0.95], ["The British Goya scholar Nigel Glendinning", 0.15, 0.97], ["said he was totally unconvinced.", 0.35, 0.95],
          ["The Prado still hangs them as Goya's.", 0.5, 0.95], ["But the doubt says something true.", 0.25, 0.95], ["We have no letter,", 0.2, 0.97],
          ["no title,", 0.2, 0.97], ["no witness.", 0.35, 0.95], ["Just the walls.", 1.4, 0.9]]),
 # the dog
 ("end1", [["Which brings us back to the dog.", 0.6, 0.93]]),
 ("end2", [["A small dog,", 0.2, 0.95], ["sunk up to its neck in something.", 0.25, 0.97], ["Sand, or mud. We don't know.", 0.3, 0.97],
           ["Looking up into an enormous empty space.", 0.7, 0.93]]),
 ("end3", [["No legend.", 0.3, 0.93], ["No story.", 0.3, 0.93], ["Just a dog,", 0.25, 0.93], ["and nothing.", 0.8, 0.88]]),
 ("end4", [["The Spanish painter Antonio Saura", 0.15, 0.97], ["called it the most beautiful picture in the world.", 0.8, 0.95]]),
 ("end5", [["Maybe it's the one Goya understood best.", 0.3, 0.95], ["Old.", 0.25, 0.92], ["Deaf.", 0.25, 0.92], ["Looking up", 0.2, 0.93],
           ["at something no one else could see.", 1.0, 0.9]]),
 ("end6", [["Goya painted it on the wall of his house,", 0.25, 0.95], ["for no one.", 0.9, 0.88]]),
 ("end7", [["It hangs in the Prado, in Madrid.", 0.5, 0.92]]),
]

WORDS = {lid: " ".join(p[0] for p in perf).replace("...", "…").split() for lid, perf in L}
norm = lambda w: re.sub(r"[^\w']", "", w.replace("*", "").lower())


def A(lid, word=None, nth=1, end=False, off=0.0):
    """anchor: line start, or the start (end=True: end) of the nth occurrence of `word` in line `lid`"""
    if lid not in WORDS: raise SystemExit(f"no line {lid}")
    if word is None: base = lid + ("$" if end else "")
    else:
        hits = [i for i, w in enumerate(WORDS[lid]) if norm(w) == norm(word)]
        if len(hits) < nth: raise SystemExit(f"'{word}' (#{nth}) not in {lid}: {WORDS[lid]}")
        base = f"{lid}.{hits[nth - 1]}" + ("$" if end else "")
    return base + (f"{off:+.2f}" if off else "")


# ---------------------------------------------------------------- images (file, depth, points of interest)
P = lambda **kw: kw
IM = {
 "saturn": P(file="src/saturn.jpg", depth=True, points={"eyes": [0.37, 0.18], "mouth": [0.37, 0.235], "bite": [0.42, 0.3], "body": [0.45, 0.36], "hands": [0.48, 0.4], "victim": [0.47, 0.44], "legs": [0.45, 0.7]}),
 "judith": P(file="src/judith.jpg", depth=True, points={"face": [0.6, 0.29], "knife": [0.3, 0.2], "victim": [0.22, 0.56]}),
 "leocadia": P(file="src/leocadia.jpg", depth=True, points={"face": [0.31, 0.15], "mound": [0.55, 0.5], "rail": [0.7, 0.24]}),
 "two-old": P(file="src/two-old.jpg", depth=True, points={"old": [0.5, 0.11], "shout": [0.8, 0.12]}),
 "soup": P(file="src/soup.jpg", depth=True, points={"crone": [0.33, 0.32], "skull": [0.72, 0.5], "spoon": [0.22, 0.72]}),
 "pilgrimage": P(file="src/pilgrimage.jpg", depth=True, points={"singers": [0.25, 0.42], "right": [0.85, 0.6], "left": [0.08, 0.5]}),
 "sabbath": P(file="src/sabbath.jpg", depth=True, points={"goat": [0.1, 0.35], "crowd": [0.45, 0.35], "girl": [0.93, 0.55]}),
 "dog": P(file="src/dog.jpg", depth=True, points={"head": [0.38, 0.81], "sky": [0.5, 0.35]}),
 "fight": P(file="src/fight.jpg", depth=True, points={"left": [0.27, 0.32], "right": [0.42, 0.33], "knees": [0.36, 0.68]}),
 "atropos": P(file="src/atropos.jpg", depth=True, points={"lens": [0.33, 0.4], "middle": [0.6, 0.3], "man": [0.86, 0.42]}),
 "asmodea": P(file="src/asmodea.jpg", depth=True, points={"flyers": [0.25, 0.42], "soldiers": [0.88, 0.85], "rock": [0.68, 0.35]}),
 "holy-office": P(file="src/holy-office.jpg", depth=True, points={"crowd": [0.78, 0.55]}),
 "men-reading": P(file="src/men-reading.jpg", depth=True, points={"faces": [0.5, 0.38]}),
 "women-laughing": P(file="src/women-laughing.jpg", depth=True, points={"faces": [0.52, 0.37]}),
 "arrieta": P(file="src/arrieta.jpg", depth=True, points={"doctor": [0.62, 0.27], "goya": [0.79, 0.31], "glass": [0.74, 0.42], "faces": [0.1, 0.42], "hands": [0.73, 0.72]}),
 "selfportrait": P(file="src/selfportrait.jpg", depth=True, points={"face": [0.45, 0.38]}),
 "third-may": P(file="src/third-may.jpg", depth=True, points={"white": [0.31, 0.5], "rifles": [0.62, 0.48], "dead": [0.25, 0.85]}),
 "disasters": P(file="src/disasters.jpg", crop=[0.21, 0.18, 0.22, 0.27], points={"bodies": [0.5, 0.45]}),
 "sleep-reason": P(file="src/sleep-reason.jpg", points={"sleeper": [0.45, 0.62], "owls": [0.55, 0.42]}),
 "milkmaid": P(file="src/milkmaid.jpg", depth=True, points={"face": [0.52, 0.38]}),
 "duaso": P(file="src/duaso.jpg", depth=True, points={"face": [0.48, 0.25]}),
 "ferdinand": P(file="src/ferdinand.jpg", depth=True, points={"face": [0.52, 0.22]}),
 "rubens-saturn": P(file="src/rubens-saturn.jpg", crop=[0.015, 0.012, 0.03, 0.012], depth=True, points={"face": [0.6, 0.35], "child": [0.72, 0.43]}),
 "laurent-soup": P(file="src/laurent-soup.jpg", crop=[0.02, 0.03, 0.02, 0.16], points={"faces": [0.42, 0.42]}),
 "laurent-saturn": P(file="src/laurent-saturn.jpg", crop=[0.08, 0.02, 0.08, 0.1], points={"face": [0.45, 0.17], "all": [0.5, 0.45]}),
 "laurent-dog": P(file="src/laurent-dog.jpg", crop=[0.16, 0.05, 0.1, 0.16], points={"dog": [0.38, 0.72]}),
 "laurent-sabbath": P(file="src/laurent-sabbath.jpg", crop=[0.02, 0.12, 0.02, 0.17], points={"crowd": [0.6, 0.45]}),
 "laurent-judith": P(file="src/laurent-judith.jpg", crop=[0.05, 0.03, 0.05, 0.1], points={"all": [0.5, 0.45]}),
 "quinta-1900": P(file="src/quinta-1900.jpg", depth=True, points={"door": [0.45, 0.48], "people": [0.55, 0.82]}),
 "laurent-twoold": P(file="src/laurent-twoold.jpg", crop=[0.1, 0.03, 0.08, 0.1], points={"all": [0.5, 0.45]}),
 "expo-1878": P(file="src/expo-1878.jpg", crop=[0.08, 0.1, 0.08, 0.08], depth=True, points={"palace": [0.42, 0.3]}),
 "expo-photo": P(file="src/expo-photo.jpg", depth=True, points={"arch": [0.5, 0.45], "wall": [0.12, 0.35]}),
 "erlanger": P(file="src/erlanger.jpg", depth=True, points={"face": [0.45, 0.22]}),
 "pradera": P(file="src/pradera.jpg", depth=True, points={"picnic": [0.3, 0.75], "city": [0.6, 0.45]}),
 "plaster": P(file="tex:plaster"),
}
MAIN = "saturn"

# ---------------------------------------------------------------- shots: (at, img, from, to, extras)
S = []
def sh(at, img, frm="full", to=None, **kw): S.append({"at": at, "img": img, "from": frm, "to": to or frm, **kw})

# cold open: the photographer, the walls, the nightmares
sh(A("cold1"), "laurent-soup", "full@0.92", "faces@1.25", gray=1, frame=False)
sh(A("cold2"), "laurent-saturn", "all@1.0", "face@1.5", gray=1, fade=0.8)
sh(A("cold3", "someone"), "saturn", "bite@1.0", "bite@1.12", fade=0.9)
sh(A("cold4"), "saturn", "mouth@1.6", "eyes@1.9", hit="small")
sh(A("cold4", "Witches"), "sabbath", "crowd@1.4", "goat@1.25", fade=0.5)
sh(A("cold4", "Two"), "soup", "crone@1.3", "skull@1.5", fade=0.5)
sh(A("cold5"), "laurent-dog", "dog@1.0", "dog@1.3", gray=1, fade=0.8)
sh(A("cold5", "The"), "leocadia", "face@1.6", "face@1.3", fade=0.8)
sh(A("cold6"), "selfportrait", "face@1.05", "face@1.4", fade=0.8)
sh(A("cold6", "And"), "two-old", "old@1.4", "shout@1.5", fade=0.8)
sh(A("cold7"), "pilgrimage", "left@1.0", "singers@1.15", fade=0.8)
sh(A("cold7", "and"), "saturn", "full@0.31", "full@0.34", frame=True, fade=1.0, dim=0.15)
# I. the deaf man's house
sh(A("c1a"), "quinta-1900", "full@1.0", "door@1.2", gray=0.85, fade=1.0)
sh(A("c1b"), "selfportrait", "full@1.0", "face@1.35", fade=0.8)
sh(A("c1b", "kings"), "ferdinand", "full@0.55", "face@1.1", fade=0.6)
sh(A("c1b", "rich"), "selfportrait", "face@1.35", "face@1.6", fade=0.6)
sh(A("c1c"), "selfportrait", "face@1.65", "face@1.4")
sh(A("c1c", "war"), "third-may", "full@1.0", "white@1.5", fade=0.6)
sh(A("c1c", "painted"), "disasters", "full@1.0", "bodies@1.3", fade=0.6, gray=0.2)
sh(A("c1d"), "quinta-1900", "door@1.15", "full@1.0", gray=0.85, fade=0.8)
sh(A("c1e", "La"), "quinta-1900", "people@1.5", "door@1.7", gray=0.85, fade=0.6)
sh(A("c1f"), "selfportrait", "face@1.3", "face@1.55", fade=0.6)
sh(A("c1g"), "leocadia", "face@1.6", "full@0.75", fade=0.8)
sh(A("c1h"), "ferdinand", "face@1.3", "full@0.6", fade=0.8)
sh(A("c1h", "Ferdinand"), "ferdinand", "face@1.8", "face@2.1")
# II. the fever
sh(A("c2a"), "arrieta", "full@0.6", "goya@1.4", fade=1.0)
sh(A("c2b"), "arrieta", "goya@1.6", "doctor@1.6", fade=0.6)
sh(A("c2c"), "arrieta", "glass@1.3", "doctor@1.5", fade=0.6)
sh(A("c2c", "Behind"), "arrieta", "faces@1.6", "faces@1.9", fade=0.6, dim=-0.4)
sh(A("c2d"), "arrieta", "full@1.0", "full@1.15", fade=0.8, dim=0.35)
sh(A("c2e"), "arrieta", "goya@2.0", "goya@2.3", fade=0.6)
sh(A("c2e", "picks"), "plaster", "full@1.0", "full@1.1", fade=0.8)
# III. fourteen nightmares
sh(A("c3a"), "pradera", "full@1.0", "picnic@1.25", fade=0.8)
sh(A("c3b"), "laurent-judith", "all@0.9", "all@1.1", gray=1, fade=0.8)
sh(A("c3c"), "saturn", kind="room", room={"back": ["judith", "saturn"], "left": ["pilgrimage"], "right": ["sabbath"], "move": [0, 650], "yaw": [0, 0]}, fade=0.8)
sh(A("c3c", "a"), "pilgrimage", "left@1.0", "singers@1.2", fade=0.8)
sh(A("c3c", "Singing"), "pilgrimage", "singers@1.6", "singers@1.9", fade=0.4)
sh(A("c3c", "Painted"), "pilgrimage", "singers@1.1", "right@1.0")
sh(A("c3d"), "sabbath", "crowd@1.0", "goat@1.1", fade=0.6, dim=-0.25)
sh(A("c3d", "Devil"), "sabbath", "goat@1.5", "goat@1.75", fade=0.4, dim=-0.3)
sh(A("c3e"), "leocadia", "full@0.62", "face@1.2", fade=0.6, frame=True)
sh(A("c3e", "Many"), "leocadia", "face@1.6", "face@1.9")
sh(A("c3f"), "two-old", "old@1.1", "old@1.3", fade=0.6)
sh(A("c3f", "One"), "two-old", "shout@1.6", "shout@1.9", fade=0.4)
sh(A("c3g"), "judith", "knife@1.2", "face@1.5", fade=0.6)
sh(A("c3h"), "saturn", kind="room", room={"back": ["judith", "saturn"], "left": ["pilgrimage"], "right": ["sabbath"], "move": [500, 1150], "yaw": [0, 6]}, fade=0.6)
sh(A("c3h", "Saturn"), "saturn", "eyes@1.9", "eyes@2.2", hit="big")
sh(A("c3i"), "fight", kind="room", room={"back": ["men-reading", "women-laughing"], "left": ["asmodea", "holy-office"], "right": ["atropos", "fight"],
   "move": [0, 600], "yaw": [-4, 4]}, fade=1.0)
sh(A("c3i", "Two", 1), "fight", "left@1.3", "knees@1.25", fade=0.5)
sh(A("c3i", "Fates"), "atropos", "lens@1.2", "middle@1.3", fade=0.5)
sh(A("c3i", "Two", 2), "asmodea", "flyers@1.25", "soldiers@1.3", fade=0.5)
sh(A("c3i", "Men", 2), "men-reading", "faces@1.0", "faces@1.25", fade=0.4)
sh(A("c3i", "Women"), "women-laughing", "faces@1.0", "faces@1.25", fade=0.4)
sh(A("c3i", "procession", off=-0.25), "holy-office", "crowd@1.2", "crowd@1.45", fade=0.4)
sh(A("c3i", "And"), "dog", "full@0.3", "full@0.33", frame=True, fade=0.8)
sh(A("c3i", "We'll"), "dog", "head@1.6", "head@1.9", fade=0.6)
sh(A("c3j"), "saturn", kind="grid", imgs=["saturn", "judith", "pilgrimage", "leocadia", "two-old", "soup", "dog", "sabbath", "men-reading", "women-laughing", "fight", "asmodea", "atropos", "holy-office"], fade=0.6)
sh(A("c3j", "Every"), "laurent-sabbath", "crowd@1.0", "crowd@1.25", gray=1, fade=0.6)
sh(A("c3j", "Today"), "soup", "full@1.0", "crone@1.2", fade=0.8)
# IV. saturn
sh(A("c4a"), "rubens-saturn", "full@0.32", "face@1.0", fade=1.0)
sh(A("c4a", "So"), "rubens-saturn", "child@1.4", "child@1.7", fade=0.5)
sh(A("c4b"), "rubens-saturn", "face@1.2", "full@0.4", fade=0.6)
sh(A("c4c"), "rubens-saturn", kind="pair", img2="saturn", labels=["RUBENS · 1636", "GOYA · c. 1820–23"], fade=0.8)
sh(A("c4d"), "saturn", "full@0.31", "body@1.0", fade=0.8)
sh(A("c4d", "Look"), "saturn", "eyes@1.6", "eyes@2.2", fade=0.4)
sh(A("c4e"), "saturn", "hands@1.4", "body@1.5", fade=0.6)
sh(A("c4e", "The"), "saturn", "mouth@1.9", "mouth@2.2", fade=0.4)
sh(A("c4e", "One"), "saturn", "victim@1.5", "victim@1.35", fade=0.5)
sh(A("c4f"), "laurent-saturn", "face@1.4", "face@1.8", gray=1, fade=0.8)
sh(A("c4f", "They"), "saturn", "eyes@2.2", "eyes@2.6", fade=0.6)
sh(A("c4g"), "laurent-saturn", "all@1.0", "all@1.12", gray=1, fade=0.8, dim=-0.3)
sh(A("c4h"), "saturn", "full@0.31", "full@0.36", frame=True, fade=0.8)
sh(A("c4h", "Spain"), "third-may", "dead@1.4", "rifles@1.3", fade=0.6)
sh(A("c4h", "A"), "sleep-reason", "sleeper@1.2", "owls@1.5", fade=0.6)
sh(A("c4h", "Goya"), "selfportrait", "face@1.7", "face@2.0", fade=0.6)
sh(A("c4i"), "saturn", kind="room", room={"back": ["judith", "saturn"], "left": ["pilgrimage"], "right": ["sabbath"], "move": [200, 900], "yaw": [-6, 0]}, fade=0.8)
# V. the escape
sh(A("c5a"), "ferdinand", "full@0.55", "face@1.3", fade=1.0)
sh(A("c5b"), "third-may", "rifles@1.2", "white@1.6", fade=0.6)
sh(A("c5b", "And"), "selfportrait", "face@1.4", "face@1.7", fade=0.6)
sh(A("c5c"), "quinta-1900", "full@1.0", "door@1.3", gray=0.85, fade=0.6)
sh(A("c5c", "Then"), "duaso", "full@0.7", "face@1.4", fade=0.6)
sh(A("c5d"), "map-exile", kind="map", map={"id": "exile", "pins": [{"city": "madrid", "at": A("c5d", "permission"), "label": "Madrid"},
   {"city": "bordeaux", "at": A("c5e", "settles"), "label": "Bordeaux"}], "route": {"from": "madrid", "to": "bordeaux", "at": A("c5e", "crosses"), "to_at": A("c5e", "settles")}}, fade=0.6)
sh(A("c5f"), "milkmaid", "full@0.62", "face@1.3", fade=0.8)
sh(A("c5f", "On"), "selfportrait", "face@1.2", "face@1.6", fade=0.8, gray=0.6)
sh(A("c5g"), "saturn", kind="room", room={"back": ["judith", "saturn"], "left": ["pilgrimage"], "right": ["sabbath"], "move": [900, 150], "yaw": [0, 0], "dim": 0.35}, fade=0.8)
sh(A("c5g", "And"), "laurent-soup", "full@0.95", "faces@1.3", gray=1, fade=0.8)
# VI. peeled off the walls
sh(A("c6a"), "laurent-sabbath", "full@1.0", "crowd@1.2", gray=1, fade=1.0)
sh(A("c6a", "Those"), "saturn", kind="room", room={"back": ["judith", "saturn"], "left": ["pilgrimage"], "right": ["sabbath"], "front": ["leocadia", "two-old"],
   "door": True, "move": [300, 300], "yaw": [0, 180]}, fade=0.6)
sh(A("c6b"), "quinta-1900", "door@1.1", "full@1.0", gray=0.85, fade=0.8)
sh(A("c6b", "Fifty"), "laurent-twoold", "all@0.95", "all@1.1", gray=1, fade=0.6)
sh(A("c6c"), "quinta-1900", "full@1.1", "full@1.0", gray=1, fade=0.8)
sh(A("c6c", "Baron"), "erlanger", "full@0.62", "face@1.15", fade=0.6)
sh(A("c6d"), "laurent-saturn", "all@0.85", "all@1.0", gray=1, fade=0.8)
sh(A("c6d", "That's"), "laurent-soup", "full@0.9", "full@1.05", gray=1, fade=0.6)
sh(A("c6d", "His"), "laurent-dog", "dog@1.0", "dog@1.35", gray=1, fade=0.6)
sh(A("c6e"), "laurent-judith", "all@0.95", "all@1.15", gray=1, fade=0.8)
sh(A("c6f"), "saturn", "full@0.33", "full@0.35", kind="peel", peel={"at": A("c6f", "lifted"), "to": A("c6f", "canvas", end=True), "under": "plaster"})
sh(A("c6f", "What"), "saturn", "eyes@1.8", "eyes@2.0", fade=0.6, contrast=1.1)
sh(A("c6f", "Experts"), "laurent-saturn", kind="pair", img2="saturn", labels=["1874 · ON THE WALL", "TODAY · ON CANVAS"], fade=0.8)
sh(A("c6h"), "sabbath", "goat@1.0", "crowd@1.0", fade=0.8)
sh(A("c6h", "Paris", 2), "expo-1878", "palace@1.2", "full@1.0", fade=0.8)
sh(A("c6i"), "expo-photo", "arch@1.0", "wall@1.25", gray=0.4, fade=0.8)
sh(A("c6i", "next", off=-0.2), "selfportrait", "face@1.3", "face@1.55", fade=0.6, gray=0.3)
sh(A("c6j"), "saturn", "full@0.31", "full@0.34", frame=True, fade=0.8)
sh(A("c6j", "And"), "quinta-1900", "full@1.0", "full@1.15", gray=1, fade=0.8)
sh(A("c6j", "Demolished"), "quinta-1900", "full@1.0", "full@1.04", gray=1, kind="peel", peel={"at": A("c6j", "Demolished", off=0.4), "to": A("c6j", end=True, off=0.6), "under": "plaster"})
# VII. the doubt
sh(A("c7a"), "fight", "full@1.0", "left@1.2", fade=1.0, dim=0.15)
sh(A("c7a", "Goya"), "fight", "right@1.6", "right@1.9", hit="small")
sh(A("c7b"), "quinta-1900", "full@1.0", "door@1.2", gray=1, fade=0.6)
sh(A("c7b", "If"), "fight", kind="room", room={"back": ["men-reading", "women-laughing"], "left": ["asmodea", "holy-office"], "right": ["atropos", "fight"],
   "move": [600, 200], "yaw": [3, -3], "dim": 0.15}, fade=0.6)
sh(A("c7c"), "two-old", "shout@1.2", "old@1.3", fade=0.6)
sh(A("c7c", "And"), "soup", "crone@1.4", "skull@1.4", fade=0.6)
sh(A("c7d"), "fight", "left@1.15", "right@1.25", fade=0.8, dim=0.1)
sh(A("c7d", "The", 2), "saturn", "full@0.31", "full@0.34", frame=True, fade=0.6)
sh(A("c7d", "But"), "fight", kind="room", room={"move": [100, 700], "yaw": [0, 0], "dim": 0.1}, fade=0.8)
# the dog
sh(A("end1"), "dog", "full@0.3", "full@0.33", frame=True, fade=1.0)
sh(A("end2"), "dog", "sky@1.0", "head@1.1", fade=0.8)
sh(A("end3"), "dog", "head@1.6", "head@2.0", fade=0.8)
sh(A("end4"), "dog", "full@1.0", "sky@1.05", fade=0.8)
sh(A("end5"), "selfportrait", "face@1.5", "face@1.8", fade=0.8, gray=0.4)
sh(A("end5", "Looking"), "dog", "head@1.3", "sky@1.2", fade=0.8)
sh(A("end6"), "dog", "full@0.3", "full@0.29", frame=True, fade=1.0)

# ---------------------------------------------------------------- overlays
O = []
def ov(type, at, to, **kw): O.append({"type": type, "from": at, "to": to, **kw})
CH = [("cold7", "c1a", "I", "The Deaf Man's House"), ("c1h", "c2a", "II", "The Fever"), ("c2e", "c3a", "III", "Fourteen Nightmares"),
      ("c3j", "c4a", "IV", "Saturn"), ("c4i", "c5a", "V", "The Escape"), ("c5g", "c6a", "VI", "Peeled Off the Walls"), ("c7d" if False else "c6j", "c7a", "VII", "The Doubt")]
ov("title", A("cold7", "and", end=True, off=0.9), A("c1a", off=-0.6), kicker="FRANCISCO DE GOYA · 1819–1823", text="The Black Paintings")
for prev, nxt, n, name in CH:
    if n == "I": continue
    ov("chapter", A(prev, end=True, off=0.35), A(nxt, off=1.6), kicker=f"CHAPTER {n}", text=name)
ov("chapter", A("c1a", off=-0.55), A("c1a", off=2.2), kicker="CHAPTER I", text="The Deaf Man's House")
ov("label", A("cold1", off=0.4), A("cold1", end=True, off=0.3), text="QUINTA DEL SORDO · MADRID · 1874")
ov("credit", A("cold1", off=0.4), A("cold2", end=True), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("label", A("cold4"), A("cold4", "Witches", off=-0.1), text="SATURN · c. 1820–23")
ov("label", A("cold4", "Witches"), A("cold4", "Two", off=-0.1), text="WITCHES' SABBATH · c. 1820–23")
ov("label", A("cold4", "Two"), A("cold4", end=True, off=0.6), text="TWO OLD PEOPLE EATING SOUP · c. 1820–23")
ov("lower", A("cold6", "Francisco", off=-0.1), A("cold6", "And", off=-0.2), text="Francisco de Goya", sub="1746–1828")
ov("year", A("c1a", off=2.3), A("c1b", "kings", off=-0.3), text="1819")
ov("label", A("c1b", "kings"), A("c1b", "rich", off=-0.1), text="FERDINAND VII · GOYA, 1814")
ov("label", A("c1c", "war"), A("c1c", "painted", off=-0.1), text="THE THIRD OF MAY 1808 · GOYA, 1814")
ov("label", A("c1c", "painted"), A("c1c", end=True, off=0.6), text="THE DISASTERS OF WAR · PLATE 39")
ov("label", A("c1d"), A("c1e", end=True), text="THE QUINTA DEL SORDO · c. 1900")
ov("credit", A("c1d"), A("c1e", end=True), text="PHOTO: MANUEL ASENJO, c. 1900")
ov("lower", A("c1g", off=0.2), A("c1g", "his", off=-0.2), text="Leocadia Weiss", sub="1788–1856")
ov("label", A("c2a", off=0.3), A("c2c", end=True), text="SELF-PORTRAIT WITH DR ARRIETA · 1820 · MINNEAPOLIS INSTITUTE OF ART")
ov("quote", A("c2d", "To"), A("c2d", end=True, off=0.4), text="Goya thankful, to his friend Arrieta… at the end of 1819, at seventy-three years of age.",   # verbatim (NYU Medical Humanities translation)
   sub="INSCRIPTION ON THE PAINTING, 1820")
ov("label", A("c3a", off=0.3), A("c3a", end=True), text="FOR COMPARISON · GOYA, THE MEADOW OF SAN ISIDRO, 1788")
ov("label", A("c3b"), A("c3b", end=True), text="JUDITH AND HOLOFERNES ON THE WALL · J. LAURENT, 1874")
ov("credit", A("c3b"), A("c3b", end=True), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("pin", A("c3c", off=0.2), A("c3c", "a", off=-0.1), text="GROUND FLOOR · THE DINING ROOM")
ov("credit", A("c3c", off=0.2), A("c3c", "a", off=-0.1), text="RECONSTRUCTION AFTER THE 1828 INVENTORY · APPROXIMATE")
ov("label", A("c3c", "a"), A("c3c", end=True), text="A PILGRIMAGE TO SAN ISIDRO · c. 1820–23")
ov("label", A("c3d"), A("c3d", end=True), text="WITCHES' SABBATH (THE GREAT HE-GOAT) · c. 1820–23")
ov("label", A("c3e"), A("c3e", end=True), text="LA LEOCADIA · c. 1820–23")
ov("label", A("c3f"), A("c3f", end=True), text="TWO OLD MEN · c. 1820–23")
ov("label", A("c3g"), A("c3g", end=True), text="JUDITH AND HOLOFERNES · c. 1820–23")
ov("pin", A("c3i", off=0.2), A("c3i", "Two", off=-0.1), text="FIRST FLOOR")
ov("credit", A("c3i", off=0.2), A("c3i", "Two", off=-0.1), text="RECONSTRUCTION AFTER THE 1828 INVENTORY · APPROXIMATE")
ov("label", A("c3i", "And"), A("c3i", end=True), text="THE DOG · c. 1820–23")
ov("label", A("c3j", "Every"), A("c3j", "Today", off=-0.1), text="WITCHES' SABBATH ON THE WALL · J. LAURENT, 1874")
ov("credit", A("c3j", "Every"), A("c3j", "Today", off=-0.1), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("label", A("c4a", off=0.3), A("c4b", end=True), text="SATURN · PETER PAUL RUBENS, 1636–38 · MUSEO DEL PRADO")
ov("label", A("c4d"), A("c4d", "Look", off=-0.1), text="SATURN · GOYA, c. 1820–23 · MUSEO DEL PRADO")
ov("ring", A("c4d", "eyes", off=0.1), A("c4d", "He", 1, off=-0.1), point="eyes", img="saturn", rx=230, ry=120, rot=-6)
ov("label", A("c4f"), A("c4f", "They", off=-0.1), text="SATURN ON THE WALL · J. LAURENT, 1874")
ov("credit", A("c4f"), A("c4f", "They", off=-0.1), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("label", A("c4h", "A"), A("c4h", "Every", off=-0.1), text="THE SLEEP OF REASON PRODUCES MONSTERS · GOYA, 1799")
ov("pin", A("c4i", off=0.2), A("c4i", end=True, off=0.8), text="THE DINING ROOM")
ov("year", A("c5a", off=0.1), A("c5a", "a", off=1.6), text="1823")
ov("label", A("c5c", "Then"), A("c5c", end=True), text="JOSÉ DUASO Y LATRE · GOYA, 1824")
ov("year", A("c5d"), A("c5d", "permission"), text="1824")
ov("label", A("c5f"), A("c5f", "On", off=-0.1), text="THE MILKMAID OF BORDEAUX · GOYA, c. 1825–27")
ov("year", A("c5f", "On", off=0.2), A("c5f", end=True, off=0.6), text="1828")
ov("credit", A("c5g", "And"), A("c5g", end=True, off=1.0), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("credit", A("c6b", "Fifty"), A("c6b", end=True, off=0.5), text="PHOTO: J. LAURENT, 1874 · IPCE / C. TEIXIDOR CADENAS · CC BY-SA 4.0")
ov("lower", A("c6a", "Antonio", off=-0.1), A("c6a", "walks", off=1.2), text="Antonio Brugada", sub="PAINTER · THE 1828 INVENTORY")
ov("credit", A("c6a"), A("c6a", "Those", off=-0.1), text="PHOTO: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("pin", A("c6a", "Those", off=0.2), A("c6a", end=True, off=0.4), text="THE DINING ROOM · LOOKING BACK TO THE DOOR")
ov("year", A("c6c"), A("c6c", "a", off=1.4), text="1873")
ov("credit", A("c6c"), A("c6c", "Baron", off=-0.1), text="PHOTO: MANUEL ASENJO, c. 1900")
ov("lower", A("c6c", "Baron", off=-0.1), A("c6c", end=True, off=0.6), text="Baron Émile d'Erlanger", sub="BANKER · OWNER FROM 1873")
ov("credit", A("c6c", "Baron"), A("c6c", end=True, off=0.6), text="PHOTO: WIKIMEDIA COMMONS / NELLY12145 · CC BY-SA 4.0")
ov("lower", A("c6d", "a", off=0.2), A("c6d", "That's", off=-0.2), text="Jean Laurent", sub="PHOTOGRAPHER · 1816–1886")
ov("credit", A("c6d"), A("c6e", end=True), text="PHOTOS: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("lower", A("c6e", "Salvador", off=-0.1), A("c6e", end=True, off=0.4), text="Salvador Martínez Cubells", sub="RESTORER, MUSEO DEL PRADO")
ov("credit", A("c6f", "Experts"), A("c6f", end=True, off=0.5), text="LEFT: J. LAURENT, 1874 · IPCE · CC BY-SA 2.5 ES")
ov("year", A("c6h", "The", 2, off=-0.2), A("c6h", end=True, off=0.6), text="1878")
ov("label", A("c6i"), A("c6i", "next", off=-0.3), text="THE SPANISH SECTION · TROCADÉRO, PARIS · 1878")
ov("credit", A("c6i"), A("c6i", "next", off=-0.3), text="PHOTO: WIKIMEDIA COMMONS / C. TEIXIDOR CADENAS · CC BY-SA 4.0")
ov("quote", A("c6i", "a", 2, off=-0.2), A("c6i", end=True, off=0.6), text="Monster of immorality, impudence, and ingratitude.", sub="P. G. HAMERTON · THE PORTFOLIO · 1879")   # verbatim (The Met)
ov("year", A("c6j"), A("c6j", "They", off=-0.1), text="1881")
ov("year", A("c7a", off=0.0), A("c7a", "a", off=1.8), text="2003")
ov("lower", A("c7a", "Juan", off=-0.1), A("c7a", "makes", off=1.0), text="Juan José Junquera", sub="ART HISTORIAN · 2003")
ov("stamp", A("c7a", "Goya", off=0.05), A("c7a", end=True, off=0.5), text="NOT GOYA?")
ov("pin", A("c7b", "If", off=0.1), A("c7b", end=True, off=0.4), text="THE FIRST FLOOR")
ov("lower", A("c7d", "The", 1, off=-0.1), A("c7d", "said", 1, off=1.4), text="Nigel Glendinning", sub="GOYA SCHOLAR")
ov("label", A("end1"), A("end2", end=True), text="THE DOG · c. 1820–23 · MUSEO DEL PRADO")
ov("quote", A("end4", off=0.1), A("end4", end=True, off=0.6), text="The world’s most beautiful picture.", sub="ANTONIO SAURA, ON THE DOG")   # verbatim in every source (narration paraphrases)
ov("end", A("end7", end=True, off=1.0), A("end7", end=True, off=21.0), kicker="NEXT", text="")

# ---------------------------------------------------------------- sound
SFX = [
 {"at": A("cold1", "photographer", off=0.1), "fx": "shutter", "gain": 0.5},
 {"at": A("c6d", "records", off=0.0), "fx": "shutter", "gain": 0.5},
 {"at": A("c3h", "Saturn"), "fx": "riser", "gain": 0.35},
 {"at": A("c6h", "cut"), "fx": "snip", "gain": 0.6},
 {"at": A("c7a", "Goya"), "fx": "sting", "gain": 0.4},
] + [{"at": A(prev, end=True, off=0.35), "fx": "impact", "gain": 0.3} for prev, _, n, _ in CH if n != "I"] + \
    [{"at": A("c1a", off=-0.55), "fx": "impact", "gain": 0.3}]
DM = [[38, 45, 50], [38, 45, 49], [34, 41, 50], [33, 40, 49]]           # Dm  Dm(maj7)  Bb  A   (the Shorts' default)
AM = [[33, 40, 48], [29, 36, 45], [36, 43, 52], [28, 40, 44]]            # Am  F  C  E
EM = [[28, 40, 47], [36, 43, 48], [31, 38, 47], [35, 42, 47]]            # Em  C  G  B
MUSIC = {"bar": 5.5, "music_db": -13, "transpose": 0, "chords": DM,
         "segments": [{"at": A("c1a"), "chords": AM, "transpose": 0}, {"at": A("c2a"), "chords": DM, "transpose": -2},
                      {"at": A("c3a"), "chords": EM, "transpose": 0}, {"at": A("c4a"), "chords": DM, "transpose": -3},
                      {"at": A("c5a"), "chords": AM, "transpose": 2}, {"at": A("c6a"), "chords": EM, "transpose": -1},
                      {"at": A("c7a"), "chords": DM, "transpose": 1}, {"at": A("end1"), "chords": AM, "transpose": 0}],
         "sections": {"cold": [A("cold1"), A("cold2", end=True)], "choir": [A("c3h", "Saturn", off=-0.3), A("c4a", off=-1.0)],
                      "drop": [A("c6i", "They", 2, off=-0.1), A("c6i", "sell", end=True, off=0.3)]},
         "heartbeat": [A("c3g"), A("c3h", "Saturn", off=-0.2)]}
# a second choir for the ending: the engine has one "choir" section, so the ending gets the riser+choir via sfx/segments instead
SFX.append({"at": A("end4", off=-0.2), "fx": "chime", "gain": 0.25})


FACTS = [
 {"claim": "Goya bought the Quinta del Sordo on 27 February 1819, from a previous owner who was deaf; he was 72", "source": "https://fundaciongoyaenaragon.es/eng/obra/la-leocadia/654 ; https://en.wikipedia.org/wiki/Quinta_del_Sordo ; https://en.wikipedia.org/wiki/Black_Paintings"},
 {"claim": "An illness at 46 (1792-93) left Goya deaf", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://en.wikipedia.org/wiki/Francisco_Goya"},
 {"claim": "Leocadia Weiss (1790-1856) lived with him at the Quinta with her daughter Rosario (b. 1814)", "source": "https://en.wikipedia.org/wiki/Francisco_Goya"},
 {"claim": "He wanted distance from the court of Ferdinand VII", "source": "https://en.wikipedia.org/wiki/Quinta_del_Sordo"},
 {"claim": "Late 1819 acute illness; Self-Portrait with Dr Arrieta (1820, Minneapolis Institute of Art) and its inscription (card: 'Goya thankful, to his friend Arrieta… at the end of 1819, at seventy-three years of age.')", "source": "https://en.wikipedia.org/wiki/Self-Portrait_with_Dr_Arrieta ; https://medhum.med.nyu.edu/view/10321 ; https://search.artsmia.org/id/1226"},
 {"claim": "14 murals in oil directly on the plaster of two rooms, c. 1820-23, painted over earlier rural scenes; never titled, signed or written about", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://en.wikipedia.org/wiki/Saturn_Devouring_His_Son ; https://stephenphelan.co.uk/articles/the-black-paintings/"},
 {"claim": "Ground-floor/dining-room and first-floor arrangement (Brugada 1828, Yriarte 1867)", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://fundaciongoyaenaragon.es/eng/obra/la-leocadia/654"},
 {"claim": "Saturn traditionally faced La Leocadia; the eyes were badly damaged and repainted", "source": "https://fundaciongoyaenaragon.es/eng/obra/saturno-devorando-a-un-hijo/660"},
 {"claim": "Rubens's Saturn (1636-38) for the king; calm vs Goya's madness; Ciofalo: the victim appears to be an adult; claim of an erased sexual detail", "source": "https://en.wikipedia.org/wiki/Saturn_Devouring_His_Son"},
 {"claim": "1823 restoration of absolutism; house signed over to grandson Mariano in 1823; hiding at priest José Duaso's; 2 May 1824 request to take the waters at Plombières", "source": "https://fundaciongoyaenaragon.es/eng/obra/jose-duaso-y-latre/195 ; https://fundaciongoyaenaragon.es/eng/obra/la-leocadia/654"},
 {"claim": "Goya died in Bordeaux on 16 April 1828, aged 82; he did not write of the Black Paintings", "source": "https://en.wikipedia.org/wiki/Francisco_Goya"},
 {"claim": "Mariano gave the house to Javier in 1830 and inherited it again in 1854; bought by Émile d'Erlanger in 1873", "source": "https://fundaciongoyaenaragon.es/eng/obra/la-leocadia/654"},
 {"claim": "J. Laurent photographed the murals in situ in 1874; transfer to canvas by Salvador Martínez Cubells, the Prado's chief restorer, with extensive repainting", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://en.wikipedia.org/wiki/Saturn_Devouring_His_Son ; https://www.eeweems.com/goya/lubow5.html"},
 {"claim": "Witches' Sabbath was cut, possibly to fit a space in Paris; shown at the Trocadéro, 20 May - 10 Nov 1878; donated to the State (decree 20 Dec 1881)", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://fundaciongoyaenaragon.es/eng/obra/la-leocadia/654"},
 {"claim": "Hamerton (The Portfolio, 1879) called Goya a 'monster of immorality, impudence, and ingratitude'", "source": "https://www.metmuseum.org/art/collection/search/626365"},
 {"claim": "The house was demolished in 1909", "source": "https://en.wikipedia.org/wiki/Quinta_del_Sordo"},
 {"claim": "Junquera (2003): one-storey records, Javier as author, Mariano selling; Glendinning 'totally unconvinced'; the Prado accepts them", "source": "https://en.wikipedia.org/wiki/Black_Paintings ; https://www.eeweems.com/goya/lubow5.html"},
 {"claim": "Antonio Saura called The Dog 'the world's most beautiful picture'", "source": "https://en.wikipedia.org/wiki/The_Dog_(Goya) ; https://stephenphelan.co.uk/articles/the-black-paintings/"},
]

story = {
 "slug": "goya-black-paintings", "format": "long", "voice": "af_heart", "speed": 0.94, "tail": 22.0,
 "meta": {"painter": "Francisco de Goya", "born": 1746, "died": 1828, "painting": "The Black Paintings", "year": "c. 1820–1823",
          "museum": "Museo del Prado", "city": "Madrid", "image": MAIN, "image_credit": "Museo del Prado, via Wikimedia Commons (public domain)"},
 "youtube": {"titles": ["The House Where Goya Painted His Nightmares", "Nobody Was Supposed to See These Paintings"],
             "description_lead": "In 1819, a deaf, 72-year-old Francisco de Goya bought a farmhouse outside Madrid and covered two of its rooms with fourteen nightmares. He never titled them, never signed them and never wrote a word about them. This is the story of the Black Paintings: why he painted them, how they were peeled off the walls, and why some historians once doubted he painted them at all.",
             "hashtags": ["#arthistory", "#goya", "#blackpaintings"],
             "credits": ["Paintings and prints by Francisco de Goya and Peter Paul Rubens: public domain (Museo del Prado; Minneapolis Institute of Art; The Metropolitan Museum of Art, CC0).",
                         "Photographs of the murals in the Quinta del Sordo, 1874: J. Laurent, Fototeca del IPCE (Spain), via Wikimedia Commons, CC BY-SA 2.5 ES (creativecommons.org/licenses/by-sa/2.5/es) and CC BY-SA 4.0 (uploads by Carlos Teixidor Cadenas).",
                         "The Spanish section at the Trocadéro, Paris, 1878: via Wikimedia Commons (Carlos Teixidor Cadenas), CC BY-SA 4.0 (creativecommons.org/licenses/by-sa/4.0).",
                         "Baron Frédéric Émile d'Erlanger: via Wikimedia Commons (Nelly12145), CC BY-SA 4.0.",
                         "The Quinta del Sordo, c. 1900: Manuel Asenjo, public domain. Exposition Universelle 1878 lithograph: Gallica (BnF), public domain."],
             "thumbnail": {"image": "saturn", "focus": [0.37, 0.185], "span": 0.2, "words": "HIS DINING ROOM"}},
 "say": {"1870s": "eighteen seventies", "1819": "eighteen nineteen", "1823": "eighteen twenty-three", "1824": "eighteen twenty-four",
         "1828": "eighteen twenty-eight", "1873": "eighteen seventy-three", "1878": "eighteen seventy-eight", "1881": "eighteen eighty-one",
         "1909": "nineteen oh nine", "2003": "two thousand three"},
 "ipa": {"Goya": "ɡˈɔɪə", "Goya's": "ɡˈɔɪəz", "Prado": "pɹˈɑːdoʊ", "Prado's": "pɹˈɑːdoʊz", "Saturn": "sˈætɚn", "Leocadia": "lˌeɪoʊkˈɑːdiə",
         "Rosario": "ɹoʊsˈɑːɹioʊ", "Manzanares": "mˌɑːnsɑːnˈɑːɹɛs", "Quinta": "kˈiːntə", "Sordo": "sˈɔːɹdoʊ", "Arrieta": "ˌɑːɹiˈeɪtə",
         "Mariano": "mˌɑːɹiˈɑːnoʊ", "Bordeaux": "bɔːɹdˈoʊ", "Brugada": "bɹuːɡˈɑːdə", "Erlanger": "ˈɛɹlɑːnʒeɪ", "Émile": "eɪmˈiːl",
         "Laurent": "loʊɹˈɑːn", "Martínez": "mɑːɹtˈiːnɛs", "Cubells": "kuːbˈɛlz", "Trocadéro": "tɹˌoʊkədˈɛɹoʊ", "Junquera": "huːŋkˈɛɹə",
         "Javier": "hɑːvjˈɛɹ", "Saura": "sˈaʊɹə", "Weiss": "vˈaɪs", "Rubens": "ɹˈuːbənz"},
 "lines": [{"id": lid, "perf": [[x, round(min(p * 1.3, 2.6) if p < 2 else p, 2), v] for x, p, v in perf]} for lid, perf in L],   # long-form pacing: 30% longer breaths
 "images": IM, "shots": S, "overlays": O, "sfx": SFX, "music": MUSIC,
 "maps": {"exile": {"bbox": [[-9.5, 36.0], [3.5, 47.5]], "focus": ["724", "250"], "cities": {"madrid": [-3.70, 40.42], "bordeaux": [-0.58, 44.84]}}},
 "next": False, "facts": FACTS,
 "rights": {"creator_died": 1828, "note": "All paintings public domain; CC BY-SA archive photos credited on screen and in the description."},
}
json.dump(story, open(os.path.join(HERE, "story.json"), "w"), indent=1, ensure_ascii=False)
n = sum(len(w) for w in WORDS.values())
print(f"story.json: {len(L)} lines, {n} words, {len(S)} shots, {len(O)} overlays")
