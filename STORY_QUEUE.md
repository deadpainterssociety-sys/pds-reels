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

## Ideas (to verify)

| Painting (museum) | Possible angle | Type | Notes |
|---|---|---|---|
| Van Eyck, *Arnolfini Portrait* (National Gallery) | "Jan van Eyck was here" over the mirror; the tiny painter in the mirror | craft | |
| Goya, *The Naked Maja* (Prado) | the Inquisition demanded to know who ordered it | hidden | **nude: safe framing** (PLAYBOOK §1); sources: Prado, the 1815 Inquisition file |
| Bosch, *The Garden of Earthly Delights* (Prado) | the music written on a sinner's backside | dark | don't play a melody you can't source; partial nudity: frame the score, not the bodies |
| Botticelli, *The Birth of Venus* (Uffizi) | Simonetta Vespucci, and the painter buried near her | dark-legend | **nude: safe framing**; the model claim is a legend: say so |
| Titian, *Venus of Urbino* (Uffizi) | Mark Twain called it the "vilest" picture in the world | hidden | **nude: safe framing**; check the quote word for word |
| Bruegel, *The Triumph of Death* (Prado) | find the human hook | dark | |
| Fuseli, *The Nightmare* (Detroit Institute of Arts) | the demon on the sleeping woman; the scene echoed in *Frankenstein* | dark | lesser-known-ish; the Mary Shelley link is a scholarly reading: hedge |
| Böcklin, *Isle of the Dead* (Kunstmuseum Basel) | painted five times; one version later hung in Hitler's office | dark | lesser-known; verify which version, where it hangs now |
| Velázquez, *Las Meninas* (Prado) | the knight's cross on his chest was added after the painting was finished | hidden | when and by whom; "the king painted it" is legend |
| Van Eyck, *Ghent Altarpiece* (St Bavo's Cathedral, Ghent) | the *Just Judges* panel was stolen in 1934 and never found | damage | crime; most-stolen artwork claims need care |
| Manet, *Olympia* (Musée d'Orsay) | the 1865 scandal: guards had to protect it | damage | **nude: safe framing** (face, the black cat, the flowers) |
| Géricault, *The Raft of the Medusa* (Louvre) | the real shipwreck: 15 survivors out of ~150 | dark | dark: not next to another dark one |
| Klimt, *Portrait of Adele Bloch-Bauer I* (Neue Galerie, New York) | looted by the Nazis, won back in court by her niece | damage | Klimt †1918: OK |
| Leonardo, *The Last Supper* (Santa Maria delle Grazie, Milan) | a door was cut through Jesus's feet in 1652 | damage | another "cut" story: space it out from the Night Watch. It's a wall painting: the ending "It hangs in…" would be wrong, so decide the last line first (checked 5 Nov: the door is c. 1652, Wikipedia citing Brambilla Barcilon) |
| Vermeer, *Girl with a Pearl Earring* (Mauritshuis) | not a portrait: a "tronie"; the pearl debate | hidden | |
| Delacroix, *Liberty Leading the People* (Louvre) | the state bought it, then hid it for years | hidden | partial nudity: frame Liberty's face and the flag |
| Whistler, *Whistler's Mother* (Musée d'Orsay) | it was meant as an "arrangement in grey and black" | hidden | |
