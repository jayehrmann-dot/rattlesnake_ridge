"""World generation: a 7x5 grid of flip-screen rooms, Adventure (1979) style."""
import random

from .constants import (
    SCREEN_W, SCREEN_H, WORLD_W, WORLD_H, TILES,
    SAND, SAND2, ROAD, GRASS, GRASS2, ROCK, CACTUS, TREE, WATER, BRIDGE, WALL,
    DOOR, FENCE, RAIL, RAILBRIDGE, GRAVE, WELL, FIRE, MINE, TENT, BOARDWALK,
)

WORLD_SEED = 2600

LAYOUT = [
    ["mesa",   "mesa",   "canyon", "canyon",   "riverrail",   "depot",    "prairierail"],
    ["mine",   "desert", "desert", "boothill", "river",       "prairie",  "fort"],
    ["ghost",  "desert", "town",   "desert",   "river",       "prairie",  "prairie"],
    ["desert", "canyon", "desert", "ranch",    "riverbridge", "prairie",  "camp"],
    ["desert", "desert", "oasis",  "desert",   "riverdelta",  "badlands", "badlands"],
]

NAMES = {
    (0, 0): "Dead Man's Mesa", (1, 0): "Red Mesa", (2, 0): "Coyote Canyon",
    (3, 0): "Rattler Pass", (4, 0): "Iron Trestle", (5, 0): "Dry Creek Depot",
    (6, 0): "Buffalo Flats",
    (0, 1): "Lucky Strike Mine", (1, 1): "Stagecoach Road", (2, 1): "North Flats",
    (3, 1): "Boot Hill", (4, 1): "Snake River", (5, 1): "Tall Grass",
    (6, 1): "Fort Calloway",
    (0, 2): "Perdition (Ghost Town)", (1, 2): "West Trail", (2, 2): "Rattlesnake Ridge",
    (3, 2): "East Trail", (4, 2): "Snake River Bend", (5, 2): "Antelope Prairie",
    (6, 2): "Homestead Prairie",
    (0, 3): "Sunburnt Flats", (1, 3): "Widow's Canyon", (2, 3): "South Trail",
    (3, 3): "Colter Ranch", (4, 3): "Snake River Crossing", (5, 3): "Bronson Homestead",
    (6, 3): "Outlaw Hollow",
    (0, 4): "Salt Flats", (1, 4): "Bone Desert", (2, 4): "Hidden Oasis",
    (3, 4): "Scorpion Flats", (4, 4): "Snake River Delta", (5, 4): "The Badlands",
    (6, 4): "Kettle's Roost",
}

# short labels + map colour per kind, used by the overview map
KIND_INFO = {
    "mesa": ("MESA", "rock"), "canyon": ("CANYN", "rock_dark"), "riverrail": ("TRSTL", "water"),
    "depot": ("DEPOT", "wall"), "prairierail": ("FLATS", "grass"), "mine": ("MINE", "rock"),
    "desert": ("DESRT", "sand"), "boothill": ("GRAVE", "sand_dark"), "river": ("RIVER", "water"),
    "prairie": ("PRAIR", "grass"), "fort": ("FORT", "wall"), "ghost": ("GHOST", "sand_dark"),
    "town": ("TOWN", "wall"), "ranch": ("RANCH", "wood"), "riverbridge": ("BRIDG", "water"),
    "camp": ("CAMP", "fire"), "oasis": ("OASIS", "water_light"), "riverdelta": ("DELTA", "water"),
    "badlands": ("BADLD", "sand_dark"),
}


def in_corridor(x, y):
    """Central cross kept clear so every random room stays crossable."""
    return 14 <= x <= 17 or 8 <= y <= 9


class Screen:
    def __init__(self, sx, sy, kind):
        self.sx, self.sy, self.kind = sx, sy, kind
        self.name = NAMES[(sx, sy)]
        self.floor = GRASS if kind.startswith("prairie") or kind == "fort" else SAND
        self.tiles = [[self.floor] * SCREEN_W for _ in range(SCREEN_H)]
        self.labels = []      # (cell_x, cell_y, text)
        self.buildings = []   # (x0, y0, x1, y1, label)
        # live state, filled by the engine
        self.npcs = []
        self.actors = []
        self.loots = []
        self.spawned = False

    # -- tile access ------------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < SCREEN_W and 0 <= y < SCREEN_H

    def get(self, x, y):
        return self.tiles[y][x]

    def set(self, x, y, t):
        if self.in_bounds(x, y):
            self.tiles[y][x] = t

    def passable(self, x, y):
        return self.in_bounds(x, y) and TILES[self.tiles[y][x]][3]

    def blocks_bullet(self, x, y):
        return not self.in_bounds(x, y) or TILES[self.tiles[y][x]][4]

    def ensure_floor(self, x, y):
        if self.in_bounds(x, y) and not self.passable(x, y):
            self.tiles[y][x] = self.floor

    def nearest_passable(self, x, y, radius=4):
        if self.passable(x, y):
            return x, y
        for r in range(1, radius + 1):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if self.passable(x + dx, y + dy):
                        return x + dx, y + dy
        return None

    # -- construction helpers -------------------------------------------
    def fill_rect(self, x0, y0, x1, y1, t):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, t)

    def building(self, x0, y0, x1, y1, label=None, door=None, ruin=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if ruin is not None and ruin.random() < 0.35:
                    self.set(x, y, self.floor)
                else:
                    self.set(x, y, WALL)
        if door:
            self.set(door[0], door[1], DOOR)
        if label:
            cells = (len(label) + 1) // 2
            cx = x0 + ((x1 - x0 + 1) - cells) // 2
            cy = y0 + (y1 - y0) // 2
            self.labels.append((cx, cy, label))
        self.buildings.append((x0, y0, x1, y1, label))

    def fence_rect(self, x0, y0, x1, y1, gaps=()):
        for x in range(x0, x1 + 1):
            self.set(x, y0, FENCE)
            self.set(x, y1, FENCE)
        for y in range(y0, y1 + 1):
            self.set(x0, y, FENCE)
            self.set(x1, y, FENCE)
        for gx, gy in gaps:
            self.set(gx, gy, self.floor)

    def building_at(self, x, y):
        for (x0, y0, x1, y1, label) in self.buildings:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return label
        return None


# ---------------------------------------------------------------- generators
def base(scr, rng, floor, detail, rate):
    scr.floor = floor
    for y in range(SCREEN_H):
        for x in range(SCREEN_W):
            scr.set(x, y, detail if rng.random() < rate else floor)


def border(scr):
    if scr.sx == 0:
        scr.fill_rect(0, 0, 0, SCREEN_H - 1, ROCK)
    if scr.sx == WORLD_W - 1:
        scr.fill_rect(SCREEN_W - 1, 0, SCREEN_W - 1, SCREEN_H - 1, ROCK)
    if scr.sy == 0:
        scr.fill_rect(0, 0, SCREEN_W - 1, 0, ROCK)
    if scr.sy == WORLD_H - 1:
        scr.fill_rect(0, SCREEN_H - 1, SCREEN_W - 1, SCREEN_H - 1, ROCK)


def scatter(scr, rng, tile, count, cluster=1):
    ok = (SAND, SAND2, GRASS, GRASS2)
    for _ in range(count):
        x = rng.randrange(1, SCREEN_W - 1)
        y = rng.randrange(1, SCREEN_H - 1)
        for _ in range(cluster):
            if not in_corridor(x, y) and scr.get(x, y) in ok:
                scr.set(x, y, tile)
            x = max(1, min(SCREEN_W - 2, x + rng.choice((-1, 0, 1))))
            y = max(1, min(SCREEN_H - 2, y + rng.choice((-1, 0, 1))))


def gen_desert(scr, rng):
    base(scr, rng, SAND, SAND2, 0.08)
    scatter(scr, rng, ROCK, 5, 3)
    scatter(scr, rng, CACTUS, 9, 2)


def gen_badlands(scr, rng):
    base(scr, rng, SAND, SAND2, 0.2)
    scatter(scr, rng, ROCK, 11, 3)
    scatter(scr, rng, CACTUS, 4, 1)


def gen_prairie(scr, rng):
    base(scr, rng, GRASS, GRASS2, 0.12)
    scatter(scr, rng, TREE, 4, 2)
    scatter(scr, rng, ROCK, 2, 2)


def gen_prairierail(scr, rng):
    gen_prairie(scr, rng)
    scr.fill_rect(0, 9, SCREEN_W - 1, 9, RAIL)


def gen_mesa(scr, rng):
    base(scr, rng, SAND, SAND2, 0.06)
    placed = 0
    tries = 0
    while placed < 5 and tries < 60:
        tries += 1
        w, h = rng.randint(4, 9), rng.randint(2, 4)
        x0, y0 = rng.randint(1, SCREEN_W - 2 - w), rng.randint(1, SCREEN_H - 2 - h)
        if any(in_corridor(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)):
            continue
        scr.fill_rect(x0, y0, x0 + w - 1, y0 + h - 1, ROCK)
        placed += 1
    scatter(scr, rng, CACTUS, 5, 1)


def carve(scr, x, y, w=1):
    for dy in range(-w, w + 1):
        for dx in range(-w, w + 1):
            if 1 <= x + dx <= SCREEN_W - 2 and 1 <= y + dy <= SCREEN_H - 2:
                scr.set(x + dx, y + dy, SAND2 if (x + dx + y + dy) % 7 == 0 else SAND)


def gen_canyon(scr, rng):
    scr.floor = SAND
    scr.fill_rect(0, 0, SCREEN_W - 1, SCREEN_H - 1, ROCK)
    # winding east-west pass
    y = 8
    for x in range(0, SCREEN_W):
        carve(scr, x, y)
        if x % 3 == 2:
            y = max(3, min(14, y + rng.choice((-1, 0, 0, 1))))
        if x in (0, SCREEN_W - 1):
            for dy in (-1, 0, 1):
                scr.set(x, y + dy, SAND)
    # north-south passage through the middle
    x = 15
    for yy in range(0, SCREEN_H):
        carve(scr, x, yy)
        if yy % 3 == 2:
            x = max(4, min(27, x + rng.choice((-1, 0, 0, 1))))
        if yy in (0, SCREEN_H - 1):
            for dx in (-1, 0, 1):
                scr.set(x + dx, yy, SAND)
    if scr.sy == 3:  # Widow's Canyon: a hidden nook for the locket
        scr.fill_rect(3, 3, 6, 6, SAND)
        for yy in range(6, 10):
            scr.set(5, yy, SAND)
            scr.set(6, yy, SAND)
    border(scr)


def gen_river(scr, rng, bridge=False, rail=False, delta=False):
    for y in range(SCREEN_H):
        for x in range(SCREEN_W):
            if x < 13:
                scr.set(x, y, SAND2 if rng.random() < 0.08 else SAND)
            elif x > 18:
                scr.set(x, y, GRASS2 if rng.random() < 0.12 else GRASS)
            else:
                scr.set(x, y, WATER)
    scr.floor = SAND
    if delta:
        for _ in range(6):
            px, py = rng.randint(2, 10), rng.randint(2, 15)
            scr.fill_rect(px, py, px + 2, py + 1, WATER)
    if bridge:
        scr.fill_rect(13, 8, 18, 9, BRIDGE)
        scr.fill_rect(12, 7, 12, 7, FENCE)
        scr.fill_rect(12, 10, 12, 10, FENCE)
        scr.fill_rect(19, 7, 19, 7, FENCE)
        scr.fill_rect(19, 10, 19, 10, FENCE)
    if rail:
        for x in range(SCREEN_W):
            scr.set(x, 9, RAILBRIDGE if 13 <= x <= 18 else RAIL)
    scatter(scr, rng, TREE, 2, 2)
    scatter(scr, rng, CACTUS, 3, 1)
    border(scr)


def gen_depot(scr, rng):
    base(scr, rng, SAND, SAND2, 0.06)
    scr.fill_rect(0, 9, SCREEN_W - 1, 9, RAIL)
    scr.fill_rect(9, 8, 22, 8, BOARDWALK)
    scr.building(10, 3, 21, 7, "DRY CREEK DEPOT", door=(15, 7))
    scr.fill_rect(25, 4, 26, 5, WELL)   # water tank
    scatter(scr, rng, CACTUS, 4, 1)
    border(scr)


def gen_town(scr, rng):
    base(scr, rng, SAND, SAND2, 0.05)
    scr.fill_rect(1, 6, 30, 6, BOARDWALK)
    scr.fill_rect(0, 7, 31, 10, ROAD)
    scr.fill_rect(1, 11, 30, 11, BOARDWALK)
    scr.building(1, 1, 8, 5, "SHERIFF", door=(4, 5))
    scr.building(11, 1, 20, 5, "SALOON", door=(15, 5))
    scr.building(23, 1, 30, 5, "STORE", door=(26, 5))
    scr.building(1, 12, 7, 16, "DOC", door=(4, 12))
    scr.building(9, 12, 15, 16, "BANK", door=(12, 12))
    scr.building(17, 12, 23, 16, "HOTEL", door=(20, 12))
    scr.building(25, 12, 30, 16, "LIVERY", door=(27, 12))
    scr.set(15, 9, WELL)
    scr.set(23, 7, FENCE)   # hitching posts
    scr.set(6, 10, FENCE)


def gen_boothill(scr, rng):
    base(scr, rng, SAND, SAND2, 0.1)
    scr.building(12, 2, 19, 6, "CHURCH", door=(15, 6))
    scr.fence_rect(3, 10, 28, 16, gaps=((15, 10), (16, 10)))
    for gx in range(5, 27, 3):
        for gy in (12, 14):
            scr.set(gx, gy, GRAVE)
    scatter(scr, rng, TREE, 2, 1)


def gen_ghost(scr, rng):
    base(scr, rng, SAND, SAND2, 0.15)
    scr.building(2, 2, 9, 6, "HOTEL", door=(5, 6), ruin=rng)
    scr.building(12, 2, 19, 6, "SALOON", door=(15, 6), ruin=rng)
    scr.building(3, 11, 9, 15, "BANK", door=(6, 11), ruin=rng)
    scr.building(22, 11, 29, 15, "JAIL", door=(25, 11), ruin=rng)
    scatter(scr, rng, CACTUS, 5, 1)
    scatter(scr, rng, FENCE, 4, 2)
    border(scr)


def gen_mine(scr, rng):
    base(scr, rng, SAND, SAND2, 0.08)
    scr.fill_rect(0, 0, 8, SCREEN_H - 1, ROCK)
    scr.fill_rect(0, 0, SCREEN_W - 1, 0, ROCK)
    scr.set(8, 8, MINE)
    scr.set(8, 9, MINE)
    scr.fill_rect(9, 9, 22, 9, RAIL)
    scr.building(20, 2, 26, 5, "ASSAY", door=(23, 5))
    scatter(scr, rng, ROCK, 5, 3)
    scatter(scr, rng, CACTUS, 3, 1)
    border(scr)


def gen_fort(scr, rng):
    base(scr, rng, GRASS, GRASS2, 0.1)
    # stockade
    scr.fill_rect(5, 2, 28, 2, WALL)
    scr.fill_rect(5, 15, 28, 15, WALL)
    scr.fill_rect(5, 2, 5, 15, WALL)
    scr.fill_rect(28, 2, 28, 15, WALL)
    for gx, gy in ((5, 8), (5, 9), (15, 2), (16, 2), (15, 15), (16, 15)):
        scr.set(gx, gy, GRASS)
    scr.building(8, 4, 13, 6, "BARRACKS", door=(10, 6))
    scr.building(19, 4, 25, 6, "HQ", door=(22, 6))
    scr.set(20, 11, FIRE)
    scr.set(11, 12, WELL)
    scatter(scr, rng, TREE, 2, 1)
    border(scr)


def gen_ranch(scr, rng):
    base(scr, rng, SAND, SAND2, 0.07)
    scr.building(3, 2, 10, 5, "RANCH", door=(6, 5))
    scr.building(20, 2, 27, 6, "BARN", door=(23, 6))
    scr.fence_rect(19, 10, 30, 15, gaps=((19, 12), (19, 13)))
    scr.set(5, 12, WELL)
    scatter(scr, rng, CACTUS, 4, 1)
    scatter(scr, rng, GRASS, 6, 3)


def gen_oasis(scr, rng):
    base(scr, rng, SAND, SAND2, 0.08)
    cx, cy = 15.5, 8.5
    for y in range(SCREEN_H):
        for x in range(SCREEN_W):
            d = ((x - cx) / 5.0) ** 2 + ((y - cy) / 2.6) ** 2
            if d <= 1.0:
                scr.set(x, y, WATER)
            elif d <= 2.6:
                scr.set(x, y, GRASS2 if rng.random() < 0.15 else GRASS)
                if d > 1.8 and rng.random() < 0.18:
                    scr.set(x, y, TREE)
    scatter(scr, rng, CACTUS, 3, 1)
    border(scr)


def gen_camp(scr, rng):
    base(scr, rng, SAND, SAND2, 0.1)
    for tx, ty in ((10, 5), (14, 4), (19, 4), (23, 6), (12, 13), (22, 13)):
        scr.set(tx, ty, TENT)
    scr.set(17, 7, FIRE)
    scr.fill_rect(4, 3, 6, 4, ROCK)
    scr.fill_rect(26, 9, 28, 10, ROCK)
    scr.fill_rect(8, 15, 12, 16, ROCK)
    scatter(scr, rng, FENCE, 3, 2)
    scatter(scr, rng, CACTUS, 3, 1)
    border(scr)


GENERATORS = {
    "desert": gen_desert, "badlands": gen_badlands, "prairie": gen_prairie,
    "prairierail": gen_prairierail, "mesa": gen_mesa, "canyon": gen_canyon,
    "river": lambda s, r: gen_river(s, r),
    "riverbridge": lambda s, r: gen_river(s, r, bridge=True),
    "riverrail": lambda s, r: gen_river(s, r, rail=True),
    "riverdelta": lambda s, r: gen_river(s, r, delta=True),
    "depot": gen_depot, "town": gen_town, "boothill": gen_boothill, "ghost": gen_ghost,
    "mine": gen_mine, "fort": gen_fort, "ranch": gen_ranch, "oasis": gen_oasis,
    "camp": gen_camp,
}


class World:
    def __init__(self):
        self.screens = {}
        for sy in range(WORLD_H):
            for sx in range(WORLD_W):
                kind = LAYOUT[sy][sx]
                scr = Screen(sx, sy, kind)
                rng = random.Random(WORLD_SEED * 1000 + sy * 31 + sx)
                GENERATORS[kind](scr, rng)
                if kind not in ("canyon", "mine", "fort", "camp", "ghost", "oasis", "depot") \
                        and not kind.startswith("river"):
                    border(scr)
                self.screens[(sx, sy)] = scr

    def get(self, sx, sy):
        return self.screens.get((sx, sy))


def find_entry(scr, x, y, vary_x):
    """Find a passable tile on the edge near (x, y) for a player walking in."""
    if scr.passable(x, y):
        return x, y
    for d in range(1, 12):
        for s in (-d, d):
            nx, ny = (x + s, y) if vary_x else (x, y + s)
            if scr.passable(nx, ny):
                return nx, ny
    return None
