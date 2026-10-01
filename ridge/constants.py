"""Constants, tile definitions and the Atari-style palette for Rattlesnake Ridge."""

SCREEN_W = 32          # tiles across one "room" (each tile is 2 terminal columns)
SCREEN_H = 18          # tiles down one room
WORLD_W = 7            # rooms across the world
WORLD_H = 5            # rooms down the world
FPS = 20
TICK = 1.0 / FPS

VIEW_COLS = SCREEN_W * 2          # 64 terminal columns
HUD_ROWS = 2
MSG_ROWS = 4
VIEW_ROWS = HUD_ROWS + SCREEN_H + MSG_ROWS   # 24 terminal rows

MAX_HEARTS = 6
MAX_AMMO = 48
DAY_LENGTH = 150.0      # seconds of daylight
NIGHT_LENGTH = 60.0     # seconds of night
RESPAWN_SECONDS = 120   # generic bandits/critters come back after this long

# ---------------------------------------------------------------- tiles
(SAND, SAND2, ROAD, GRASS, GRASS2, ROCK, CACTUS, TREE, WATER, BRIDGE, WALL,
 DOOR, FENCE, RAIL, RAILBRIDGE, GRAVE, WELL, FIRE, MINE, TENT, BOARDWALK) = range(21)

# tile -> (glyph, fg colour, bg colour, passable, blocks bullets)
TILES = {
    SAND:       ("  ", "sand", "sand", True, False),
    SAND2:      ("· ", "sand_dark", "sand", True, False),
    ROAD:       ("  ", "road", "road", True, False),
    GRASS:      ("  ", "grass", "grass", True, False),
    GRASS2:     ("' ", "grass_dark", "grass", True, False),
    ROCK:       ("▓▓", "rock_dark", "rock", False, True),
    CACTUS:     ("▚▞", "cactus", "sand", False, True),
    TREE:       ("▓▓", "tree_dark", "tree", False, True),
    WATER:      ("≈ ", "water_light", "water", False, False),
    BRIDGE:     ("══", "wood_dark", "wood", True, False),
    WALL:       ("██", "wall", "wall", False, True),
    DOOR:       ("▐▌", "door", "wall", False, True),
    FENCE:      ("╪╪", "wood_dark", "sand", False, False),
    RAIL:       ("≡≡", "rail", "sand", True, False),
    RAILBRIDGE: ("≡≡", "rail", "wood", True, False),
    GRAVE:      ("▟▙", "grave", "sand", False, True),
    WELL:       ("▒▒", "water_light", "rock", False, True),
    FIRE:       ("▲▲", "fire", "sand", False, False),
    MINE:       ("▛▜", "black", "rock", False, True),
    TENT:       ("▟▙", "tent", "sand", False, True),
    BOARDWALK:  ("  ", "wood", "wood", True, False),
}

# ---------------------------------------------------------------- palette
# name -> (day 256-colour index, night 256-colour index, basic 8-colour index)
# basic: 0 black 1 red 2 green 3 yellow 4 blue 5 magenta 6 cyan 7 white
PALETTE = {
    "sand":        (180, 95, 3),
    "sand_dark":   (136, 58, 1),
    "road":        (137, 94, 3),
    "grass":       (64, 22, 2),
    "grass_dark":  (100, 28, 3),
    "rock":        (245, 238, 7),
    "rock_dark":   (240, 235, 0),
    "cactus":      (34, 22, 2),
    "tree":        (28, 22, 2),
    "tree_dark":   (22, 16, 0),
    "water":       (27, 17, 4),
    "water_light": (39, 24, 6),
    "wood":        (130, 52, 1),
    "wood_dark":   (94, 16, 0),
    "wall":        (173, 95, 1),
    "door":        (52, 16, 0),
    "rail":        (250, 240, 7),
    "grave":       (252, 245, 7),
    "fire":        (202, 208, 1),
    "black":       (16, 16, 0),
    "white":       (231, 250, 7),
    "label":       (231, 250, 7),
    "tent":        (101, 58, 3),
    "sky":         (117, 60, 6),
    "sun":         (226, 250, 3),
    "hud":         (16, 16, 0),
    "hud_bg":      (180, 95, 3),
    "panel":       (16, 16, 0),
    "panel_fg":    (222, 180, 3),
    "dim":         (240, 238, 0),

    # actors
    "player":      (21, 27, 4),
    "bandit":      (196, 124, 1),
    "outlaw":      (16, 16, 0),
    "snake":       (46, 28, 2),
    "coyote":      (250, 240, 7),
    "cattle":      (94, 52, 1),
    "buffalo":     (58, 52, 1),
    "bullet_p":    (226, 220, 3),
    "bullet_e":    (196, 160, 1),
    "loot":        (220, 178, 3),

    # NPC colours
    "red":     (196, 160, 1),
    "blue":    (33, 33, 4),
    "green":   (40, 34, 2),
    "yellow":  (226, 220, 3),
    "magenta": (201, 165, 5),
    "cyan":    (51, 44, 6),
    "orange":  (208, 172, 1),
    "purple":  (93, 57, 5),
    "pink":    (213, 170, 5),
    "brown":   (94, 52, 1),
    "grey":    (245, 240, 7),
    "lime":    (118, 76, 2),
    "teal":    (30, 23, 6),
    "maroon":  (88, 52, 1),
    "gold":    (220, 178, 3),
    "navy":    (19, 18, 4),
    "olive":   (100, 58, 2),
    "coral":   (209, 167, 1),
    "violet":  (135, 97, 5),
    "rust":    (166, 130, 1),
}

# ---------------------------------------------------------------- sprites
PLAYER_SPRITE = {(0, -1): "▟▙", (0, 1): "▜▛", (-1, 0): "◀█", (1, 0): "█▶"}
HORSE_SPRITE = {(0, -1): "▟█", (0, 1): "▜█", (-1, 0): "◀▙", (1, 0): "▟▶"}
NPC_SPRITE = "▟▙"
BANDIT_SPRITE = "▜▛"
OUTLAW_SPRITE = "▙▟"
SNAKE_SPRITE = "∿∿"
COYOTE_SPRITE = "▞▚"
CATTLE_SPRITE = "▄▄"
LOOT_SPRITE = {"money": "$$", "ammo": "▪▪", "tonic": "++", "locket": "◆◆", "nugget": "◆◆"}
BULLET_SPRITE = {(0, -1): "• ", (0, 1): "• ", (-1, 0): "• ", (1, 0): " •"}

# ---------------------------------------------------------------- 3x5 block font
FONT = {
    "A": (" █ ", "█ █", "███", "█ █", "█ █"),
    "B": ("██ ", "█ █", "██ ", "█ █", "██ "),
    "C": (" ██", "█  ", "█  ", "█  ", " ██"),
    "D": ("██ ", "█ █", "█ █", "█ █", "██ "),
    "E": ("███", "█  ", "██ ", "█  ", "███"),
    "F": ("███", "█  ", "██ ", "█  ", "█  "),
    "G": (" ██", "█  ", "█ █", "█ █", " ██"),
    "H": ("█ █", "█ █", "███", "█ █", "█ █"),
    "I": ("███", " █ ", " █ ", " █ ", "███"),
    "J": ("  █", "  █", "  █", "█ █", " █ "),
    "K": ("█ █", "█ █", "██ ", "█ █", "█ █"),
    "L": ("█  ", "█  ", "█  ", "█  ", "███"),
    "M": ("█ █", "███", "███", "█ █", "█ █"),
    "N": ("██ ", "█ █", "█ █", "█ █", "█ █"),
    "O": ("███", "█ █", "█ █", "█ █", "███"),
    "P": ("██ ", "█ █", "██ ", "█  ", "█  "),
    "Q": ("███", "█ █", "█ █", "███", "  █"),
    "R": ("██ ", "█ █", "██ ", "█ █", "█ █"),
    "S": (" ██", "█  ", " █ ", "  █", "██ "),
    "T": ("███", " █ ", " █ ", " █ ", " █ "),
    "U": ("█ █", "█ █", "█ █", "█ █", "███"),
    "V": ("█ █", "█ █", "█ █", "█ █", " █ "),
    "W": ("█ █", "█ █", "███", "███", "█ █"),
    "X": ("█ █", "█ █", " █ ", "█ █", "█ █"),
    "Y": ("█ █", "█ █", " █ ", " █ ", " █ "),
    "Z": ("███", "  █", " █ ", "█  ", "███"),
    "!": (" █ ", " █ ", " █ ", "   ", " █ "),
    "'": (" █ ", " █ ", "   ", "   ", "   "),
    " ": ("   ", "   ", "   ", "   ", "   "),
}

# Duelling cowboy, 7 wide x 9 tall.  '#' = body block
COWBOY = (
    " ##### ",
    "   #   ",
    "#######",
    "  ###  ",
    " ##### ",
    "# ### #",
    "# ### #",
    "  # #  ",
    "  # #  ",
)
