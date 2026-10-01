"""The people of Rattlesnake Ridge: townsfolk, drifters, and the outlaws worth a bounty."""


def npc(id_, name, screen, pos, color, lines, role="talk"):
    return dict(id=id_, name=name, screen=screen, pos=pos, color=color, lines=lines, role=role)


NPCS = [
    # ---------------------------------------------------------------- Rattlesnake Ridge (town)
    npc("sheriff", "Sheriff Cole Barrett", (2, 2), (5, 6), "blue", [
        "Town's overrun with outlaws and I'm one man with a tin star. Care to earn honest bounty money?",
        "Seven names on my wall. Every one of 'em would shoot you for your boots.",
        "Bring 'em in dead. Alive just means paperwork.",
    ], role="sheriff"),
    npc("deputy", "Deputy Wade Poole", (2, 2), (2, 8), "cyan", [
        "Sheriff says I ain't ready for the badlands. Sheriff says a lot of things.",
        "Keep your gun holstered on Main Street, friend. Folks get nervous.",
        "I once out-drew a rattlesnake. Well... it was asleep.",
    ]),
    npc("red", "'Red' Delaney, Bartender", (2, 2), (14, 6), "rust", [
        "Whiskey's four dollars. Rumors are a dollar. Both'll cost you more in the long run.",
        "Old Gus up at the mine would sell his mule for a bottle. Might sell you a secret instead.",
        "No credit. Not since the Sundown Kid paid his tab in lead.",
    ], role="bar"),
    npc("pearl", "Pearl Dubois", (2, 2), (17, 6), "pink", [
        "The Sundown Kid used to drink here before he went bad. Sat right where you're standing.",
        "Honey, half this town owes me money and the other half owes me an apology.",
        "Perdition ain't a ghost town 'cause of ghosts. It's the Kid's gang keepin' folks out.",
    ]),
    npc("vance", "'Lucky' Vance, Card Sharp", (2, 2), (19, 8), "purple", [
        "Heads or tails, stranger. The coin's honest. I'm the one you should worry about.",
        "I've lost three fortunes and won four. That's arithmetic that keeps a man optimistic.",
    ], role="gambler"),
    npc("tobias", "Tobias Greene, Piano Man", (2, 2), (12, 7), "teal", [
        "Every song I know is about a train, a woman, or a hangin'. Sometimes all three.",
        "Black Jack Kettle shot my piano once. The piano won.",
        "Tips go in the hat. Bullets go somewhere else, please.",
    ]),
    npc("pete", "'Whiskey' Pete", (2, 2), (21, 8), "olive", [
        "*hic* The river's full o' gold, I tell ya. Gold and catfish.",
        "Ruby Lafitte? Sweet as pie... 'til she robbed the stage I was ridin'.",
        "Buy an old man a drink? No? Fine. Fine! Yer still my favorite stranger.",
    ]),
    npc("ezra", "Ezra Finch, Storekeeper", (2, 2), (27, 6), "green", [
        "Shells, tonic, and unsolicited advice. First two cost money.",
        "A box of six shells is three dollars. Cheaper than a funeral.",
    ], role="store"),
    npc("pip", "Pip, Newsboy", (2, 2), (10, 9), "yellow", [
        "EXTRA! EXTRA! Hollister twins seen at the Lucky Strike Mine! Two for the price of one!",
        "Mister, is it true Dead-Eye Dan can shoot a fly off a mule at fifty paces?",
        "Ma says stay off the trails at night. Coyotes and worse.",
    ]),
    npc("doc", "Doc Mabel Hart", (2, 2), (5, 11), "white", [
        "Hold still. I've pulled more lead out of this town than the mine ever pulled silver.",
        "Five dollars gets you patched up. Dying is free but I don't recommend it.",
    ], role="doc"),
    npc("horace", "Horace Pruett, Banker", (2, 2), (12, 11), "navy", [
        "The bank is secure. Mostly. Largely. It has a door.",
        "I buy gold at sixty dollars a nugget. Fair price. Fairer than Kettle's, anyway.",
        "Kettle robbed us twice. Third time I'm just going to hand him the keys.",
    ], role="banker"),
    npc("mayor", "Mayor Cornelius Bly", (2, 2), (20, 11), "gold", [
        "Rattlesnake Ridge will be the jewel of the territory! Once the shooting stops.",
        "Clear the Sheriff's wall of every wanted poster and I'll pin a silver star on you myself.",
        "I was elected on a platform of fewer outlaws. Progress has been... modest.",
    ], role="mayor"),
    npc("eleanor", "Miss Eleanor Pike, Schoolteacher", (2, 2), (22, 9), "violet", [
        "My pupils spell 'outlaw' better than 'arithmetic'. Says something about this town.",
        "Fort Calloway is across the river. Take the wooden bridge south past the ranch.",
        "Reading is a weapon, stranger. Though I grant it's slow on the draw.",
    ]),
    npc("lupe", "Lupe Arriaga, Stable Master", (2, 2), (28, 11), "brown", [
        "Forty dollars buys you a horse that's faster than your feet and smarter than most bandits.",
        "The horses know the way to the fort. It's the riders that get lost.",
    ], role="stable"),
    npc("jonah", "Jonah Kimble, Blacksmith", (2, 2), (30, 8), "grey", [
        "Iron don't lie. Neither do I. That's why I'm poor.",
        "I shod Black Jack's horse once. Didn't know it was his. Still ain't been paid.",
        "Need your six-shooter looked at? Ezra sells the shells, I fix the rest.",
    ]),
    npc("agnes", "Sister Agnes", (2, 2), (8, 9), "lime", [
        "Bless you, child. Even a gunslinger needs a prayer now and then.",
        "The widow Ashby lost her husband's locket in Widow's Canyon. She hasn't smiled since.",
        "Preacher Whitlow is up at Boot Hill. Say hello for me... if you can find him sober.",
    ]),
    npc("moses", "Moses Crane, Blind Fiddler", (2, 2), (9, 10), "magenta", [
        "I can't see your face, but I hear your spurs. Heavy boots. Trouble follows heavy boots.",
        "The Rattler? Cyrus Moss? Hides in the pass north of Boot Hill. Hisses like his namesake.",
        "I play for coins. I play for free. Mostly I just play.",
    ]),

    # ---------------------------------------------------------------- Boot Hill
    npc("amos", "Preacher Amos Whitlow", (3, 1), (13, 7), "white", [
        "Welcome to Boot Hill. Everyone ends up here eventually. Some just arrive early.",
        "Two dollars in the plate and I'll say a word for you. The Lord works on a budget.",
    ], role="preacher"),
    npc("silas", "Silas Grimm, Undertaker", (3, 1), (26, 9), "purple", [
        "Business is good. Too good. I measure every stranger by eye. You're about a six-footer.",
        "Seven outlaws worth burying in these hills. I've got the pine boxes ready.",
        "Ike and Abe Hollister buried their own brother out here. Then dug him up for his boots.",
    ]),
    npc("clara", "Widow Clara Ashby", (3, 1), (8, 12), "violet", [
        "Harold's locket. I dropped it in Widow's Canyon the day they brought him back. I can't go there again.",
        "It's a little silver thing. Worthless to anyone but me.",
    ], role="widow"),

    # ---------------------------------------------------------------- Perdition
    npc("lou", "'Loony' Lou Tuttle", (0, 2), (6, 8), "lime", [
        "THEY'RE IN THE WALLS! No wait, that's just the Sundown Kid's boys. Never mind.",
        "Perdition was a boom town. Then the silver ran out. Then the people. I stayed. I'm stubborn.",
        "There's a money bag in the old bank. The Kid ain't found it. Don't tell him I told you.",
    ]),

    # ---------------------------------------------------------------- Lucky Strike Mine
    npc("gus", "'Old' Gus Tanner, Prospector", (0, 1), (14, 11), "orange", [
        "Forty years I've dug this mountain. Know every crack in it. Know where the big nugget sits, too.",
        "My throat's drier than the Salt Flats. A bottle of Red's whiskey might loosen my memory.",
    ], role="prospector"),
    npc("brigid", "Brigid O'Shea, Miner", (0, 1), (18, 6), "coral", [
        "The Hollister twins run the mine now. Nobody digs, nobody gets paid, nobody complains. Out loud.",
        "There's gold in that mountain yet. Gus swears there's a nugget the size of a hen's egg.",
        "Mind the rail cart tracks. And the twins. Mostly the twins.",
    ]),
    npc("dutch", "Dutch Van Horn, Foreman", (0, 1), (23, 7), "brown", [
        "I was foreman 'til the twins showed up. Now I'm foreman of standing here.",
        "You kill both twins, the mine opens again. Whole town would thank you.",
        "Ike shoots straight. Abe shoots first. Together they're a problem.",
    ]),

    # ---------------------------------------------------------------- canyons and trails
    npc("bear", "'Bear' Jacobs, Trapper", (1, 3), (10, 8), "olive", [
        "Widow's Canyon. Named for all the widows it made. Watch the rattlers.",
        "Saw a shiny little locket up in the northwest nook. Ain't mine to take.",
        "I trap beaver, coyote, and the occasional outlaw. Outlaws pay better.",
    ]),
    npc("quill", "Dr. Phineas Quill, Medicine Man", (1, 2), (15, 8), "magenta", [
        "Step right up! Dr. Quill's Miracle Tonic cures gout, gunshot, and gloom! Six dollars!",
        "Is it snake oil? Madam, it is PREMIUM snake oil.",
    ], role="medicine"),
    npc("buck", "Buck Hensley, Stagecoach Driver", (1, 1), (15, 9), "rust", [
        "Stage don't run no more. Ruby Lafitte hit us three times. Third time she took the horses AND the stage.",
        "Dead Man's Mesa is west then north. Dan Voss picks off riders from the rocks.",
        "Y'know what I miss most? The horses. Good horses. Ask Lupe in town if you want one.",
    ]),
    npc("hiram", "Hiram Tubbs, Farmer", (2, 1), (16, 8), "green", [
        "Tried farmin' sand. Turns out sand don't farm.",
        "Coyote Canyon's just north. Rocks, snakes, and one very lost bandit.",
        "My wife says I'm stubborn. My mule agrees with her.",
    ]),
    npc("nacho", "Ignacio 'Nacho' Ruiz, Vaquero", (3, 2), (16, 9), "orange", [
        "Buenas. I ride for Colter Ranch. Best cattle in the territory, worst boss.",
        "Cross the river at the wooden bridge south by the ranch, or the trestle up north if you like trains.",
        "A vaquero rides with honor. An outlaw rides with a bag over his head. Same horse, different man.",
    ]),
    npc("kate", "Marshal Kate Reyes, Bounty Hunter", (2, 3), (15, 8), "red", [
        "Reyes. U.S. Marshal. I've been tracking Kettle for two years. You're welcome to the small fry.",
        "Kettle's in the far southeast, past the badlands. Bring a horse and a full belt of shells.",
        "Stand next to a named outlaw and press E to call him out. Wait for DRAW. Not before.",
    ]),

    # ---------------------------------------------------------------- Hidden Oasis
    npc("ephraim", "Ephraim the Hermit", (2, 4), (7, 4), "grey", [
        "Forty years by this pond. Water's sweet. Company's rare. You're rarer.",
        "The oasis heals what the desert hurts. Sit a spell. Or don't. I'm not your mother.",
        "Madame Zora over there can see the future. Mostly she sees your money.",
    ]),
    npc("zora", "Madame Zora, Fortune Teller", (2, 4), (24, 12), "purple", [
        "The cards know where the wicked hide. Three dollars and they'll whisper it to you.",
        "I foresee... a stranger with a gun. You. It's always you.",
    ], role="fortune"),

    # ---------------------------------------------------------------- Colter Ranch
    npc("sam", "'Big' Sam Colter, Rancher", (3, 3), (7, 7), "brown", [
        "Colter Ranch. Six hundred head, three good hands, one ornery owner. That's me.",
        "Ruby's gang rustled twenty head last month. Camp's east across the bridge. I'd go if I were younger.",
        "Shoot one of my cows and you'll answer to me. Shoot a bandit and I'll buy you a steak.",
    ]),
    npc("dolores", "Dolores Vega, Ranch Hand", (3, 3), (17, 12), "pink", [
        "I can rope, ride, and shoot better than any man here. Ask any man here.",
        "The corral's got a gap on the west side. Cows don't know it. Don't tell 'em.",
        "Homesteaders across the river keep losin' fence posts. Coyotes don't eat wood. Bandits do.",
    ]),
    npc("wen", "Wen Huang, Camp Cook", (3, 3), (12, 4), "teal", [
        "Beans, biscuits, beef. Every day. The cowboys complain, then ask for seconds.",
        "I cooked for the railroad crews before the tracks ended at Dry Creek. Better tips here.",
        "You look hungry. Everyone looks hungry to a cook.",
    ]),

    # ---------------------------------------------------------------- Dry Creek Depot
    npc("ada", "Ada Lin, Telegraph Operator", (5, 0), (12, 8), "cyan", [
        "Dot dash dot. Telegraph says Kettle's gang hit another train east of here.",
        "The wire runs to the fort. Captain Ward reads every word. Twice.",
        "Nobody sends good news by telegraph. Costs too much per word.",
    ]),
    npc("bertram", "Bertram Hale, Station Master", (5, 0), (18, 8), "navy", [
        "No trains till the trestle's safe. Rattler Moss keeps shootin' at engineers from the canyon.",
        "Follow the tracks east to Buffalo Flats. Follow them west and you'll meet the Rattler.",
        "I've got a schedule. It's a beautiful schedule. Nothing on it arrives.",
    ]),
    npc("felix", "Felix Marchetti, Photographer", (5, 0), (24, 8), "magenta", [
        "Hold still! Wonderful. Another portrait of a stranger who might be dead by Thursday.",
        "I photographed Black Jack Kettle once. He paid me. Then took the camera.",
        "The light here at noon is perfect for duels. Dramatic shadows.",
    ]),

    # ---------------------------------------------------------------- Fort Calloway
    npc("ward", "Captain Elias Ward", (6, 1), (22, 8), "navy", [
        "Black Jack Kettle has robbed three Army payrolls. The Army is offering one hundred dollars for his hide.",
        "I'd ride on Kettle's Roost tomorrow if Washington would answer a single telegram.",
    ], role="captain"),
    npc("dekker", "Sergeant Rufus Dekker", (6, 1), (12, 8), "blue", [
        "Tenth Cavalry, twenty years. Seen a lot of outlaws. Buried a few too.",
        "Kettle's Roost is due south past Outlaw Hollow. Don't go alone. Or do. I'm not your sergeant.",
        "Keep your powder dry and your mouth shut around the Captain. He's got opinions.",
    ]),
    npc("joseph", "Joseph Running Elk, Army Scout", (6, 1), (10, 12), "green", [
        "The land talks, if you listen. Right now it says: the badlands are full of men who want your horse.",
        "I tracked Kettle to the roost. The Captain wouldn't ride without orders. Orders never came.",
        "Rattlesnakes warn before they strike. Men rarely do.",
    ]),
    npc("tommy", "Tommy Fitch, Bugler", (6, 1), (24, 12), "yellow", [
        "I play reveille at dawn. Everyone hates me at dawn.",
        "The Captain lets me polish his sabre. He's never used it. I've never asked why.",
        "When I grow up I want to be a marshal like Kate Reyes. She scares the Sergeant.",
    ]),

    # ---------------------------------------------------------------- river and prairie
    npc("ole", "Ole Lindqvist, Fisherman", (4, 1), (10, 9), "cyan", [
        "Catfish bite at dusk. Outlaws bite anytime.",
        "You can't swim this river. Trust me. I've tried. Use the bridges.",
        "I came from Sweden for gold. Found catfish. Catfish are also fine.",
    ]),
    npc("tillie", "'Ma' Tillie Bronson, Homesteader", (5, 3), (14, 7), "orange", [
        "Bronson homestead. Husband's gone, kids are grown, coyotes are plenty. Still here.",
        "Outlaw Hollow's just east. Ruby's boys ride past at night and shoot my chimney for fun.",
        "You bring me Ruby Lafitte's hat and I'll bake you a pie. That's a promise.",
    ]),
    npc("cass", "Cass Hardin, Buffalo Hunter", (6, 2), (16, 8), "gold", [
        "Herd's up north at the Flats. Hides fetch eight dollars. Meat feeds the fort.",
        "Homestead Prairie. Nothing but grass and grievances.",
        "Coyotes here are bold. Shoot 'em or outrun 'em. Your pick.",
    ]),

    # ---------------------------------------------------------------- Outlaw Hollow
    npc("delroy", "'Snitch' Delroy", (6, 3), (6, 12), "lime", [
        "Psst. I ain't with them. I just... camp near them. For safety. Theirs, not mine.",
        "Ruby's in the big tent up north. Kettle's Roost is south of here past the badlands.",
        "You didn't see me. Nobody ever sees me. It's my one talent.",
    ]),
]

# ---------------------------------------------------------------- wanted outlaws
# duel: reaction window in seconds the player must beat once DRAW! appears
OUTLAWS = [
    dict(id="dan", name="'Dead-Eye' Dan Voss", screen=(0, 0), pos=(6, 5), reward=40, hp=4, duel=0.55,
         fire_rate=26, hint="picks off riders from Dead Man's Mesa, far to the northwest",
         taunt="One more step, stranger, and I'll part your hair."),
    dict(id="rattler", name="Cyrus 'Rattler' Moss", screen=(3, 0), pos=(20, 8), reward=45, hp=4, duel=0.5,
         fire_rate=24, hint="hides in Rattler Pass, the canyon north of Boot Hill",
         taunt="Sssomebody wandered into the wrong canyon."),
    dict(id="sundown", name="The Sundown Kid", screen=(0, 2), pos=(16, 8), reward=50, hp=5, duel=0.5,
         fire_rate=22, hint="holds the ghost town of Perdition, two screens west of town",
         taunt="Perdition's closed, friend. Permanently."),
    dict(id="ike", name="Ike Hollister", screen=(0, 1), pos=(12, 6), reward=30, hp=3, duel=0.5,
         fire_rate=24, hint="squats at the Lucky Strike Mine with his brother Abe",
         taunt="Abe! We got company!"),
    dict(id="abe", name="Abe Hollister", screen=(0, 1), pos=(13, 12), reward=30, hp=3, duel=0.5,
         fire_rate=20, hint="squats at the Lucky Strike Mine with his brother Ike",
         taunt="I see 'em, Ike! Shoot first, count later!"),
    dict(id="ruby", name="'Ruthless' Ruby Lafitte", screen=(6, 3), pos=(18, 5), reward=75, hp=5, duel=0.45,
         fire_rate=20, hint="runs her gang out of Outlaw Hollow, east across the wooden bridge",
         taunt="Well, well. Fresh boots for the pile."),
    dict(id="kettle", name="'Black Jack' Kettle", screen=(6, 4), pos=(20, 8), reward=150, hp=7, duel=0.4,
         fire_rate=16, hint="rules Kettle's Roost in the far southeast, beyond the badlands",
         taunt="You came a long way to die, pilgrim."),
]

# ---------------------------------------------------------------- generic encounters per screen
# ('bandit'|'snake'|'coyote'|'cattle'|'buffalo', x, y)  or  ('money', x, y, amount) / ('ammo'|'tonic'|'locket', x, y)
ENCOUNTERS = {
    (0, 0): [("bandit", 20, 12), ("snake", 10, 14), ("money", 26, 3, 15)],
    (1, 0): [("bandit", 8, 4), ("snake", 22, 13), ("snake", 5, 12), ("ammo", 27, 15)],
    (2, 0): [("bandit", 24, 8), ("snake", 6, 9), ("snake", 12, 8)],
    (3, 0): [("snake", 8, 8), ("snake", 26, 9), ("money", 4, 9, 10)],
    (0, 1): [("snake", 24, 14)],
    (1, 1): [("snake", 5, 4), ("snake", 26, 14)],
    (2, 1): [("snake", 6, 13), ("bandit", 26, 3)],
    (5, 1): [("coyote", 6, 4), ("coyote", 24, 14)],
    (6, 0): [("buffalo", 8, 4), ("buffalo", 10, 5), ("buffalo", 12, 4), ("coyote", 24, 14), ("money", 3, 15, 12)],
    (0, 2): [("bandit", 6, 9), ("bandit", 24, 13), ("money", 5, 13, 20)],
    (1, 2): [("snake", 5, 4), ("snake", 26, 14)],
    (3, 2): [("snake", 6, 3), ("coyote", 26, 14)],
    (5, 2): [("coyote", 8, 5), ("coyote", 22, 13), ("ammo", 27, 3)],
    (6, 2): [("coyote", 6, 4), ("bandit", 24, 4)],
    (0, 3): [("bandit", 20, 5), ("snake", 8, 14), ("snake", 24, 12), ("ammo", 3, 3)],
    (1, 3): [("snake", 20, 8), ("snake", 10, 11), ("snake", 24, 4), ("locket", 4, 4)],
    (2, 3): [("snake", 6, 4)],
    (3, 3): [("cattle", 22, 12), ("cattle", 25, 13), ("cattle", 27, 11), ("cattle", 23, 14), ("cattle", 28, 14)],
    (5, 3): [("coyote", 24, 4), ("coyote", 5, 14)],
    (6, 3): [("bandit", 10, 7), ("bandit", 22, 4), ("bandit", 14, 12), ("bandit", 24, 12),
             ("money", 12, 3, 25), ("ammo", 26, 14)],
    (0, 4): [("snake", 10, 5), ("snake", 20, 12), ("bandit", 25, 4), ("money", 3, 14, 10)],
    (1, 4): [("snake", 8, 8), ("snake", 22, 6), ("snake", 15, 14)],
    (2, 4): [("snake", 4, 14), ("tonic", 27, 3)],
    (3, 4): [("bandit", 24, 5), ("snake", 8, 13), ("ammo", 28, 15)],
    (4, 4): [("snake", 6, 14)],
    (5, 4): [("bandit", 8, 4), ("bandit", 24, 13), ("snake", 15, 3), ("snake", 5, 13), ("money", 28, 2, 18)],
    (6, 4): [("bandit", 10, 4), ("bandit", 24, 4), ("bandit", 14, 14), ("snake", 6, 14),
             ("money", 27, 15, 30), ("ammo", 4, 3)],
}

BUILDING_BLURBS = {
    "SHERIFF": "Sheriff's Office. Wanted posters cover the window. Barrett's out front.",
    "SALOON": "The Dry Gulch Saloon. Piano's out of tune and so are the patrons.",
    "STORE": "Finch's General Store. Ezra does business on the boardwalk.",
    "DOC": "Doc Hart's surgery. Smells of carbolic and bad news.",
    "BANK": "First Territorial Bank. Robbed twice. Door still works.",
    "HOTEL": "The Grand Hotel. Neither grand nor, strictly speaking, a hotel.",
    "LIVERY": "Arriaga's Livery. Horses inside, Lupe outside.",
    "CHURCH": "A whitewashed church. The bell hasn't rung since the Kid shot it.",
    "ASSAY": "The assay office. Padlocked since the twins arrived.",
    "DRY CREEK DEPOT": "Dry Creek Depot. The schedule board just says SOON.",
    "BARRACKS": "Cavalry barracks. Somebody inside is snoring.",
    "HQ": "Fort headquarters. A telegraph clatters within.",
    "RANCH": "The Colter ranch house. Smells like beans.",
    "BARN": "The barn. Something large shifts in the hay.",
    "JAIL": "Perdition's jail. The bars are the only thing still standing.",
}
