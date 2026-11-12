# Story queue

Claude picks from **Ideas** (or finds better ones), verifies everything, and moves the line to **Done** with the slug.
Every idea here is a lead to check, not a fact. Gigi can suggest ideas any time with the *stories* workflow's `idea` field
or by telling Claude in a chat. Types are the `hook_type`s of PLAYBOOK §2 (a suggestion: the angle decides).

## Pinned (write these first)

Timely stories Gigi asked for. A row with a date: write it in the run that falls within 5 days of that date and schedule it
ON that date with `python automation/plan.py add <slug> <date>`. A row marked *next days*: write it in the next run and
schedule it normally (`plan.py add <slug>`). Move the row to **Done** once it is written.

| When | Painting (museum) | Angle | Type | Notes |
|---|---|---|---|---|
| 2026-11-19 (Thu) | an *Odyssey* painting: Waterhouse, *Ulysses and the Sirens* (National Gallery of Victoria, Melbourne), or Turner, *Ulysses Deriding Polyphemus* (National Gallery, London), or another famous one | find the true twist (e.g. Waterhouse paints the sirens as birds with women's faces, as the Greeks did, not mermaids) | hidden | Nolan's *The Odyssey* reaches digital/VOD on 17 Nov: post on Thursday 19 Nov for the weekend viewers. Name the film only as context ("the story in Nolan's new film"), never use its images |

## Done

| Date | Slug | Painting (museum) | Angle | Type |
|---|---|---|---|---|
| 26 Oct 2026 | (pilot) | Artemisia Gentileschi, *Judith Beheading Holofernes* (Uffizi) | torture at the trial, the bracelet | dark-legend |
| 27 Oct 2026 | goya-saturn | Goya, *Saturn Devouring His Son* (Prado) | painted on his own wall, never meant to be seen | dark |
| 28 Oct 2026 | rokeby-venus | Velázquez, *Rokeby Venus* (National Gallery) | a suffragette attacked it with a meat cleaver in 1914 | damage |
| 29 Oct 2026 | mona-lisa-theft | Leonardo, *Mona Lisa* (Louvre) | stolen in 1911; the theft made it famous | damage |
| 30 Oct 2026 | night-watch-cut | Rembrandt, *The Night Watch* (Rijksmuseum) | cut down in 1715 to fit a wall | damage |
| 31 Oct 2026 | scream-madman | Munch, *The Scream* (National Museum, Oslo) | the pencil "madman" note blamed on a vandal was Munch's own | hidden |
| 2 Nov 2026 | vermeer-cupid | Vermeer, *Girl Reading a Letter at an Open Window* (Gemäldegalerie Alte Meister, Dresden) | Cupid painted over decades after Vermeer died; blamed on Vermeer until a dirt layer proved otherwise; uncovered 2017–2021 | time-gap |
| 3 Nov 2026 | caravaggio-goliath | Caravaggio, *David with the Head of Goliath* (Galleria Borghese, Rome) | his own face on Goliath's severed head; a killer under a death sentence; hedged plea for a pardon | dark-legend |
| 4 Nov 2026 | vangogh-crows | Van Gogh, *Wheatfield with Crows* (Van Gogh Museum, Amsterdam) | called his last painting; finished c. 10 July 1890, weeks before his death; last was probably the unfinished *Tree Roots* | hidden |
| 5 Nov 2026 | sargent-madamex | Sargent, *Madame X* (Met, New York) | the fallen strap at the 1884 Salon; repainted; he left Paris; sold to the Met in 1916 asking to hide her name | hidden |
| 5 Nov 2026 | millais-ophelia | Millais, *Ophelia* (Tate Britain) | Siddal posed in a bath; the lamps went out, she fell ill; her father demanded £50 | craft |
| 6 Nov 2026 | holbein-ambassadors | Holbein, *The Ambassadors* (National Gallery) | the anamorphic skull you only see from the bottom-right corner; the half-hidden crucifix | craft |
| 6 Nov 2026 | david-marat | David, *The Death of Marat* (Royal Museums of Fine Arts of Belgium, Brussels) | the letter in his hand is signed by his killer, Charlotte Corday; David erased her, the skin disease, posed him like Christ | dark |
| 8 Nov 2026 | david-napoleon-alps | David, *Napoleon Crossing the Alps* (Belvedere, Vienna) | he crossed on a mule led by a guide; refused to pose; Delaroche painted the truth in 1850 | hidden |
| 7 Nov 2026 | klimt-adele | Klimt, *Adele Bloch-Bauer I* (Neue Galerie, New York) | seized by the Nazis in 1938, renamed "Lady in Gold" to hide she was Jewish; niece Maria Altmann sued, won it back in 2006 | damage |
| 7 Nov 2026 | bocklin-isle | Böcklin, *Isle of the Dead*, 3rd version 1883 (Alte Nationalgalerie, Berlin) | a widow's "picture to dream on"; Hitler bought the 1883 version, hung it at the Berghof, then the Reich Chancellery | dark |
| 8 Nov 2026 | vaneyck-arnolfini | Van Eyck, *The Arnolfini Portrait* (National Gallery) | the two men in the mirror, one in red probably van Eyck; "Jan van Eyck was here"; Panofsky's witness theory, now doubted | hidden |
| 9 Nov 2026 | gericault-medusa | Géricault, *The Raft of the Medusa* (Louvre) | 150 on a raft cut loose, 15 alive; Géricault painted severed limbs from the morgue as they rotted; hedged severed head on the roof | dark |
| 9 Nov 2026 | vaneyck-justjudges | Van Eyck, *Ghent Altarpiece*, *Just Judges* panel (St Bavo's Cathedral, Ghent) | stolen April 1934; 1 million francs ransom; St John returned in a Brussels luggage locker; Goedertier's deathbed claim; 1945 copy with Leopold III's face; never found | damage |
| 10 Nov 2026 | anthonissen-whale | Van Anthonissen, *View of Scheveningen Sands* (Fitzwilliam Museum, Cambridge) | a beached sperm whale painted out by a later owner (18th–19th c.); uncovered by Shan Kuang in 2014 | time-gap |
| 10 Nov 2026 | fuseli-nightmare | Fuseli, *The Nightmare* (Detroit Institute of Arts) | the 'mare' is a folklore spirit, not a horse; first drawing (March 1781) had no horse; the head is a visual pun; 20 guineas vs £500+ for the prints | hidden |
| 11 Nov 2026 | velazquez-meninas-cross | Velázquez, *Las Meninas* (Prado) | the Santiago cross on his chest was added after 1659; ~150 questioned, papal dispensation, dead 9 months later; Palomino: "some say" the king painted it | hidden |
| 11 Nov 2026 | holbein-dead-christ | Holbein, *The Body of the Dead Christ in the Tomb* (Kunstmuseum Basel) | a rotting Christ, 30.5 × 200 cm; Rhine-corpse legend (hedged); Dostoevsky stunned in 1867 (Anna's memoir/diary, the chair); 'a man's faith might be ruined' in The Idiot | sacred-strange |
| 12 Nov 2026 | whistler-mother | Whistler, *Arrangement in Grey and Black No. 1 (Whistler's Mother)* (Musée d'Orsay) | a 15-year-old model didn't turn up, so his mother (67) stood in, then sat; he called it an 'arrangement'; pawned; bought by France 1891; 1934 Mother's Day stamp | hidden |
| 12 Nov 2026 | repin-ivan | Repin, *Ivan the Terrible and His Son Ivan* (State Tretyakov Gallery, Moscow) | banned by Alexander III in 1885; slashed 3 times through the faces by icon painter Abram Balashov in 1913 (hedged 'Enough blood!'); keeper reportedly killed himself; Repin repainted the faces; 2018 metal-pole attack; back behind bulletproof glass in 2024 | damage |
| 13 Nov 2026 | vermeer-pearl | Vermeer, *Girl with a Pearl Earring* (Mauritshuis, The Hague) | a tronie, not a portrait; the pearl 'too large to be real' (glass? Icke: tin); 2018 scans: eyelashes, faded green curtain, no hook; two strokes of white | hidden |
| 13 Nov 2026 | goya-wellington | Goya, *The Duke of Wellington* (National Gallery, London) | stolen 21 Aug 1961 for pensioners' TV licences; returned via Birmingham New Street left luggage 1965; Kempton Bunton cleared of the painting, jailed for the frame; 2012 files: son John confessed in 1969 | damage |
| 14 Nov 2026 | bosch-butt-song | Bosch, *The Garden of Earthly Delights*, Hell panel (Prado) | the score on a sinner's backside; 2014 student went viral as the first to play it, but scholars wrote it out by 1961 and Atrium Musicae recorded it in 1978; no clef, so every version is a guess | hidden |
| 14 Nov 2026 | caravaggio-virgin | Caravaggio, *Death of the Virgin* (Louvre) | rejected by the Carmelite friars: a swollen dead woman (Baglione: "swollen, bare legs"); Mancini claimed a prostitute model (hedged); Rubens told the Duke of Mantua it was one of his best; shown one week in Rome, April 1607, no copies; then Charles I, then Louis XIV | sacred-strange |

## Ideas (to verify)

| Painting (museum) | Possible angle | Type | Notes |
|---|---|---|---|
| Goya, *The Naked Maja* (Prado) | the Inquisition demanded to know who ordered it | hidden | **nude: safe framing** (PLAYBOOK §1); sources: Prado, the 1815 Inquisition file |
| Botticelli, *The Birth of Venus* (Uffizi) | Simonetta Vespucci, and the painter buried near her | dark-legend | **nude: safe framing**; the model claim is a legend: say so |
| Titian, *Venus of Urbino* (Uffizi) | Mark Twain called it the "vilest" picture in the world | hidden | **nude: safe framing**; check the quote word for word |
| Bruegel, *The Triumph of Death* (Prado) | find the human hook | dark | |
| Manet, *Olympia* (Musée d'Orsay) | the 1865 scandal: guards had to protect it | damage | **nude: safe framing** (face, the black cat, the flowers) |
| Leonardo, *The Last Supper* (Santa Maria delle Grazie, Milan) | a door was cut through Jesus's feet in 1652 | damage | another "cut" story: space it out from the Night Watch. It's a wall painting: the ending "It hangs in…" would be wrong, so decide the last line first (checked 5 Nov: the door is c. 1652, Wikipedia citing Brambilla Barcilon) |
| Delacroix, *Liberty Leading the People* (Louvre) | the state bought it, then hid it for years | hidden | partial nudity: frame Liberty's face and the flag |
| Velázquez, *Portrait of Innocent X* (Galleria Doria Pamphilj, Rome) | Olimpia Maidalchini, the sister-in-law said to decide who could see the Pope (NOT the "troppo vero" angle: Brushstroke Secrets did it, 385k) | dark-legend | topic wave Oct-Nov 2026 (EN 385k, ES 44k/36k, PT 22k); the gossip about her is gossip: hedge it; a good first E2 arm-B story (one painting, a famous man, a concrete payoff) |

## Long videos (to plan)

Ideas for the Monday/Thursday long videos. Claude moves a row into the schedule (the yt-longform-study project doc) when planning the next weeks.

| When | Painting (museum) | Angle | Notes |
|---|---|---|---|
| Thu 3 Dec 2026 (or Mon 30 Nov) | Böcklin, *Isle of the Dead* (Alte Nationalgalerie, Berlin: the 1883 version Hitler owned) | to find: an angle that beats the six existing videos, e.g. where each of the six versions ended up (Hitler's Berghof and Chancellery, one destroyed in the war, the Met, Leipzig, the Hermitage, Basel), the widow's grief, Dalí's tomb facing it; borrowed fame in the title only for names the video delivers | Gigi, 11 Nov: queue it, don't make it yet. Topic wave: Inspiraggio 295k (Jul 2024), Velum ES 733k (May 2026), The Last Layer 392k, Secessio 1.13M (Jul), Russian 979k (Oct). Our Short bocklin-isle (7 Nov, 1,044 views) links to it. Case study: project doc case-secessio-isle-of-the-dead. Music idea: Rachmaninoff wrote a symphonic poem after this painting (1909): only with a recording we may use |
