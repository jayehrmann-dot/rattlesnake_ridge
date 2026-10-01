"""Actors that live on a screen: the player, townsfolk, outlaws, critters, bullets and loot."""
from .constants import MAX_HEARTS


class Player:
    def __init__(self):
        self.sx, self.sy = 2, 2
        self.x, self.y = 15, 8
        self.hearts = MAX_HEARTS
        self.ammo = 12
        self.money = 20
        self.facing = (0, 1)
        self.horse = False
        self.invuln = 0
        self.fire_cd = 0

    def to_dict(self):
        return dict(sx=self.sx, sy=self.sy, x=self.x, y=self.y, hearts=self.hearts,
                    ammo=self.ammo, money=self.money, horse=self.horse,
                    facing=list(self.facing))

    def from_dict(self, d):
        self.sx, self.sy = d["sx"], d["sy"]
        self.x, self.y = d["x"], d["y"]
        self.hearts, self.ammo, self.money = d["hearts"], d["ammo"], d["money"]
        self.horse = d.get("horse", False)
        self.facing = tuple(d.get("facing", (0, 1)))


class NPC:
    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.x, self.y = data["pos"]
        self.color = data["color"]
        self.role = data.get("role", "talk")
        self.lines = data["lines"]


class Enemy:
    """A bandit or a named outlaw."""

    def __init__(self, x, y, slot, name="Bandit", color="bandit", hp=2, named=False, oid=None,
                 reward=0, duel=0.5, fire_rate=30, speed=4, aggro=12, taunt=""):
        self.x, self.y = x, y
        self.slot = slot
        self.name = name
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.named = named
        self.oid = oid
        self.reward = reward
        self.duel = duel
        self.fire_rate = fire_rate
        self.speed = speed
        self.aggro = aggro
        self.taunt = taunt
        self.alive = True
        self.dead_at = 0.0
        self.cooldown = fire_rate // 2
        self.move_timer = speed
        self.hurt = 0


class Critter:
    """snake / coyote / cattle / buffalo."""

    HP = {"snake": 1, "coyote": 2, "cattle": 3, "buffalo": 4}

    def __init__(self, x, y, kind, slot):
        self.x, self.y = x, y
        self.home = (x, y)
        self.kind = kind
        self.slot = slot
        self.name = {"snake": "Rattlesnake", "coyote": "Coyote", "cattle": "Longhorn",
                     "buffalo": "Buffalo"}[kind]
        self.color = kind
        self.hp = self.HP[kind]
        self.alive = True
        self.dead_at = 0.0
        self.move_timer = 0
        self.bite_cd = 0
        self.hurt = 0
        self.named = False


class Bullet:
    def __init__(self, x, y, dx, dy, owner, speed):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.owner = owner       # 'player' or 'enemy'
        self.speed = speed
        self.alive = True


class Loot:
    def __init__(self, x, y, kind, amount, lid):
        self.x, self.y = x, y
        self.kind = kind
        self.amount = amount
        self.id = lid
