# Rattlesnake Ridge

An open-world wild west adventure that looks and plays like it fell out of an
Atari 2600 cartridge, running entirely inside your terminal.

<p align="center">
<img width="448" height="405" alt="rattlesnake_ridge" src="https://github.com/user-attachments/assets/181c43f2-a565-4916-b953-d1dbd5007531" />
</p>

```bash
./play.sh
```

or `python3 -m ridge` from this folder. Needs Python 3 (ships with macOS) and a
terminal at least 64 columns by 24 rows. A 256-colour terminal gives the proper
sun-bleached palette; 8-colour terminals still work.

## The game

You ride into Rattlesnake Ridge with twenty dollars, twelve shells and no
reputation. The territory is a 7x5 grid of flip-screen rooms, Adventure-style:
walk off one edge and you're on the next screen. Desert, mesas, canyons, a
river with two crossings, a ghost town, a silver mine, a cavalry fort, a
railroad depot, a cattle ranch, a hidden oasis, an outlaw camp and the
badlands beyond.

- **53 named characters.** Forty-six townsfolk and drifters, each with their own
  lines, plus seven wanted outlaws. Stand next to someone and press E.
- **Bounties.** The Sheriff has seven names on his wall. Every outlaw hides in
  a different corner of the map, guarded by bandits, rattlesnakes or coyotes.
  Bring them down and collect at the Sheriff's office. Clear the wall and the
  Mayor has something for you.
- **Gunfights.** Bandits shoot when they line up with you. Step off their row
  or column to dodge, line up to fire back. Named outlaws take more hits.
- **High-noon duels.** Stand beside a named outlaw and press E to call them
  out. Wait for `DRAW!`, then hit SPACE before they do. Draw early and you eat
  lead.
- **Side quests.** Return a widow's locket, trade whiskey to a prospector for a
  map to a gold nugget, sell it to the banker, buy a horse, gamble with a card
  sharp, get fleeced by a fortune teller.
- **Day and night.** The palette dims when night falls.
- **Save anywhere** with F5; quitting also saves. Continue from the title screen.

## Controls

| Key | Action |
| --- | --- |
| Arrows / WASD | Walk (twice as fast on a horse) |
| Space | Fire in the direction you face |
| E / Enter | Talk, examine, or call out a duel |
| T | Drink a tonic (+3 hearts) |
| I | Saddlebags and tally |
| M | Territory map |
| B | Wanted posters (after meeting the Sheriff) |
| ? | Help |
| F5 | Save |
| Q / Esc | Quit (asks first, saves) |

## Layout

```
ridge/
  constants.py   screen sizes, tiles, palette, block font, sprites
  world.py       the 7x5 world and per-screen generators
  characters.py  every NPC, outlaw, and encounter table
  entities.py    Player, NPC, Enemy, Critter, Bullet, Loot
  render.py      curses drawing: HUD, tiles, overlays, duel screen
  engine.py      game loop, input, AI, combat, dialogue, saving
  __main__.py    entry point
save.json        created when you save
```

The world is generated from a fixed seed, so it's the same every time. To add
a character, append to `NPCS` in `characters.py`. To add a screen type, write a
generator in `world.py` and reference it in `LAYOUT`.
