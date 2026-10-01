"""Game loop, input, AI, combat, dialogue, duels, and saving for Rattlesnake Ridge."""
import curses
import json
import os
import random
import time
from collections import deque

from .constants import (
    SCREEN_W, SCREEN_H, WORLD_W, WORLD_H, TICK, MAX_HEARTS, MAX_AMMO, DAY_LENGTH, NIGHT_LENGTH,
    RESPAWN_SECONDS, DOOR, WALL, WELL, GRAVE, MINE, FIRE, TENT,
)
from .world import World, find_entry
from .characters import NPCS, OUTLAWS, ENCOUNTERS, BUILDING_BLURBS
from .entities import Player, NPC, Enemy, Critter, Bullet, Loot
from .render import Renderer

SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save.json")
OUTLAW_BY_ID = {o["id"]: o for o in OUTLAWS}
EPITAPHS = [
    "HERE LIES LESTER. HE DREW SECOND.",
    "BEHOLD THE FASTEST GUN IN... WELL, NOT ANYMORE.",
    "SHE TOLD HIM THE MULE WOULD KICK.",
    "OTIS PRATT. HE WAS RIGHT ABOUT THE WEATHER.",
    "UNKNOWN STRANGER. NICE BOOTS.",
    "HAROLD ASHBY, BELOVED. HE NEVER DID LEARN TO DUCK.",
]
KEYS_UP = (curses.KEY_UP, ord("w"), ord("W"), ord("k"))
KEYS_DOWN = (curses.KEY_DOWN, ord("s"), ord("S"), ord("j"))
KEYS_LEFT = (curses.KEY_LEFT, ord("a"), ord("A"), ord("h"))
KEYS_RIGHT = (curses.KEY_RIGHT, ord("d"), ord("D"), ord("l"))
KEYS_ENTER = (10, 13, curses.KEY_ENTER, ord("e"), ord("E"))
ESC = 27


def sign(v):
    return (v > 0) - (v < 0)


class Dialog:
    def __init__(self, speaker, text, options=None, color="white"):
        self.speaker = speaker
        self.text = text
        self.options = options or []
        self.color = color


class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.r = Renderer(stdscr)
        self.rng = random.Random()
        self.world = World()
        self.place_npcs()
        self.messages = deque(maxlen=3)
        self.bullets = []
        self.dialog = None
        self.duel = None
        self.dead_until = 0.0
        self.mode = "title"
        self.has_save = os.path.exists(SAVE_PATH)
        self.running = True
        self.tick = 0
        self.start = time.time()
        self.time_offset = 0.0
        self.was_night = False
        self.reset_state()

    # ------------------------------------------------------------ setup
    def place_npcs(self):
        for d in NPCS:
            scr = self.world.get(*d["screen"])
            n = NPC(d)
            scr.ensure_floor(n.x, n.y)
            scr.npcs.append(n)

    def reset_state(self):
        self.player = Player()
        self.flags = {}
        self.inv = {"tonic": 1}
        self.bounties = {o["id"]: "open" for o in OUTLAWS}
        self.collected = set()
        self.visited = set()
        self.kills = 0
        self.npc_line = {}
        for scr in self.world.screens.values():
            scr.actors, scr.loots, scr.spawned = [], [], False
        self.screen = self.world.get(2, 2)

    def start_new(self):
        self.reset_state()
        self.start = time.time()
        self.time_offset = 0.0
        self.mode = "play"
        self.messages.clear()
        self.enter_screen()
        self.msg("You ride into Rattlesnake Ridge with $20, twelve shells and a bad reputation to earn.")
        self.msg("Sheriff Barrett is out front of his office, north side of the street.")

    # ------------------------------------------------------------ helpers
    def msg(self, text):
        self.messages.append(text)

    def elapsed(self):
        return time.time() - self.start + self.time_offset

    def is_night(self):
        return (self.elapsed() % (DAY_LENGTH + NIGHT_LENGTH)) >= DAY_LENGTH

    def occupied(self, x, y, ignore=None):
        p = self.player
        if (x, y) == (p.x, p.y) and ignore is not p:
            return True
        for n in self.screen.npcs:
            if (n.x, n.y) == (x, y):
                return True
        for a in self.screen.actors:
            if a.alive and a is not ignore and (a.x, a.y) == (x, y):
                return True
        return False

    def actor_at(self, x, y):
        for a in self.screen.actors:
            if a.alive and (a.x, a.y) == (x, y):
                return a
        return None

    def npc_at(self, x, y):
        for n in self.screen.npcs:
            if (n.x, n.y) == (x, y):
                return n
        return None

    def adjacent_npc(self):
        p = self.player
        for n in self.screen.npcs:
            if max(abs(n.x - p.x), abs(n.y - p.y)) <= 1:
                return n
        return None

    def adjacent_named(self):
        p = self.player
        for a in self.screen.actors:
            if a.alive and a.named and max(abs(a.x - p.x), abs(a.y - p.y)) <= 1:
                return a
        return None

    def adjacent_hint(self):
        n = self.adjacent_npc()
        if n:
            return "[E] Talk to %s" % n.name
        e = self.adjacent_named()
        if e:
            return "[E] Call out %s for a HIGH NOON duel" % e.name
        return "[ARROWS/WASD] Move  [SPACE] Shoot  [E] Talk  [T] Tonic  [I] Inv  [M] Map  [?] Help"

    def line_clear(self, x0, y0, x1, y1):
        dx, dy = sign(x1 - x0), sign(y1 - y0)
        x, y = x0 + dx, y0 + dy
        while (x, y) != (x1, y1):
            if self.screen.blocks_bullet(x, y):
                return False
            x, y = x + dx, y + dy
        return True

    # ------------------------------------------------------------ main loop
    def run(self):
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        next_t = time.time()
        while self.running:
            self.handle_input()
            if self.mode == "play":
                self.update()
            elif self.mode == "duel":
                self.update_duel()
            elif self.mode == "dead" and time.time() >= self.dead_until:
                self.respawn()
            self.r.draw(self)
            self.tick += 1
            next_t += TICK
            delay = next_t - time.time()
            if delay > 0:
                time.sleep(delay)
            else:
                next_t = time.time()

    def handle_input(self):
        moved = False
        while True:
            k = self.stdscr.getch()
            if k == -1:
                break
            if k == curses.KEY_RESIZE:
                continue
            if self.mode == "play":
                is_move = k in KEYS_UP + KEYS_DOWN + KEYS_LEFT + KEYS_RIGHT
                if is_move and moved:
                    continue
                if is_move:
                    moved = True
            getattr(self, "keys_" + self.mode)(k)

    # ------------------------------------------------------------ key handlers
    def keys_title(self, k):
        if k in (ord("n"), ord("N")):
            self.start_new()
        elif k in (ord("c"), ord("C")) and self.has_save:
            self.load_game()
        elif k in (ord("h"), ord("H")):
            self.mode = "help"
            self.help_return = "title"
        elif k in (ord("q"), ord("Q"), ESC):
            self.running = False

    def keys_play(self, k):
        p = self.player
        if k in KEYS_UP:
            self.move(0, -1)
        elif k in KEYS_DOWN:
            self.move(0, 1)
        elif k in KEYS_LEFT:
            self.move(-1, 0)
        elif k in KEYS_RIGHT:
            self.move(1, 0)
        elif k == ord(" "):
            self.shoot()
        elif k in KEYS_ENTER:
            self.interact()
        elif k in (ord("t"), ord("T")):
            self.use_tonic()
        elif k in (ord("i"), ord("I")):
            self.mode = "inv"
        elif k in (ord("m"), ord("M")):
            self.mode = "map"
        elif k in (ord("?"), curses.KEY_F1):
            self.help_return = "play"
            self.mode = "help"
        elif k in (ord("b"), ord("B")):
            if self.flags.get("met_sheriff"):
                self.mode = "wanted"
            else:
                self.msg("You haven't read the Sheriff's wanted wall yet.")
        elif k == curses.KEY_F5:
            self.save_game()
        elif k in (ord("q"), ord("Q"), ESC):
            self.mode = "quit"
        # 'S' is taken by movement, so saving lives on F5 and on quit; 'H' is movement too (vi keys)

    def keys_dialog(self, k):
        d = self.dialog
        if d and ord("1") <= k <= ord("9"):
            i = k - ord("1")
            if i < len(d.options):
                d.options[i][1]()
                return
        if k in KEYS_ENTER + (ESC, ord(" ")):
            self.dialog = None
            if self.mode == "dialog":
                self.mode = "play"

    def keys_duel(self, k):
        d = self.duel
        if k == ord(" "):
            if d["phase"] == "wait":
                self.resolve_duel("early")
            elif d["phase"] == "draw":
                d["rt"] = time.time() - d["draw_at"]
                self.resolve_duel("win" if d["rt"] <= d["enemy"].duel else "late")
        elif k == ESC and d["phase"] == "wait":
            self.resolve_duel("chicken")

    def keys_map(self, k):
        self.mode = "play"

    def keys_inv(self, k):
        self.mode = "play"

    def keys_wanted(self, k):
        self.mode = "play"

    def keys_help(self, k):
        self.mode = getattr(self, "help_return", "play")

    def keys_ending(self, k):
        self.mode = "play"

    def keys_dead(self, k):
        pass

    def keys_quit(self, k):
        if k in (ord("y"), ord("Y")):
            self.save_game()
            self.running = False
        elif k in (ord("n"), ord("N"), ESC, ord("q"), ord("Q")):
            self.mode = "play"

    # ------------------------------------------------------------ player actions
    def move(self, dx, dy):
        p = self.player
        p.facing = (dx, dy)
        steps = 2 if p.horse else 1
        for _ in range(steps):
            nx, ny = p.x + dx, p.y + dy
            if not self.screen.in_bounds(nx, ny):
                self.change_screen(dx, dy)
                return
            if not self.screen.passable(nx, ny) or self.occupied(nx, ny, ignore=p):
                return
            p.x, p.y = nx, ny
            self.pickup()

    def change_screen(self, dx, dy):
        p = self.player
        nsx, nsy = p.sx + dx, p.sy + dy
        if not (0 <= nsx < WORLD_W and 0 <= nsy < WORLD_H):
            self.msg("The territory ends here. Nothing that way but more nothing.")
            return
        nscr = self.world.get(nsx, nsy)
        x = 0 if dx > 0 else (SCREEN_W - 1 if dx < 0 else p.x)
        y = 0 if dy > 0 else (SCREEN_H - 1 if dy < 0 else p.y)
        entry = find_entry(nscr, x, y, vary_x=(dy != 0))
        if entry is None:
            self.msg("No way through on this side.")
            return
        p.sx, p.sy = nsx, nsy
        p.x, p.y = entry
        self.enter_screen()

    def enter_screen(self):
        p = self.player
        self.screen = self.world.get(p.sx, p.sy)
        self.bullets = []
        first = (p.sx, p.sy) not in self.visited
        self.visited.add((p.sx, p.sy))
        self.spawn_screen(self.screen)
        if first:
            self.msg("-- %s --" % self.screen.name)
        for a in self.screen.actors:
            if a.alive and a.named and a.taunt:
                self.msg('%s: "%s"' % (a.name, a.taunt))

    def shoot(self):
        p = self.player
        if p.fire_cd > 0:
            return
        if p.ammo <= 0:
            self.msg("Click. Out of shells! Ezra at the store sells more.")
            p.fire_cd = 6
            return
        p.ammo -= 1
        p.fire_cd = 5
        self.bullets.append(Bullet(p.x, p.y, p.facing[0], p.facing[1], "player", 2))

    def use_tonic(self):
        p = self.player
        if self.inv.get("tonic", 0) <= 0:
            self.msg("No tonic. Ezra sells it, and Dr. Quill sells something like it.")
        elif p.hearts >= MAX_HEARTS:
            self.msg("You're already in fine fettle. Save the tonic.")
        else:
            self.inv["tonic"] -= 1
            p.hearts = min(MAX_HEARTS, p.hearts + 3)
            self.msg("You gulp the tonic. Tastes like turpentine and courage. (+3 hearts)")

    def interact(self):
        p = self.player
        n = self.adjacent_npc()
        if n:
            self.talk(n)
            return
        e = self.adjacent_named()
        if e:
            self.start_duel(e)
            return
        fx, fy = p.x + p.facing[0], p.y + p.facing[1]
        scr = self.screen
        if not scr.in_bounds(fx, fy):
            self.msg("The wide open frontier. Keep walking and you'll be in it.")
            return
        t = scr.get(fx, fy)
        if t in (DOOR, WALL):
            label = scr.building_at(fx, fy)
            if label:
                self.msg(BUILDING_BLURBS.get(label, "%s. Locked. Folks do business out front." % label.title()))
            else:
                self.msg("Solid timber. Somebody built this to last.")
        elif t == WELL:
            if p.hearts < MAX_HEARTS:
                p.hearts += 1
                self.msg("Cool water. You drink deep and feel a mite better. (+1 heart)")
            else:
                self.msg("Cool water. You splash your face.")
        elif t == FIRE:
            if p.hearts < MAX_HEARTS:
                p.hearts += 1
                self.msg("Beans in the pot. You help yourself. (+1 heart)")
            else:
                self.msg("A crackling fire. Somebody's coffee is boiling over.")
        elif t == GRAVE:
            self.msg(self.rng.choice(EPITAPHS))
        elif t == MINE:
            self.msg("The shaft is boarded up. Gus swears the nugget's right near the mouth.")
        elif t == TENT:
            self.msg("Somebody's tent. Bedroll, whiskey, and a wanted poster of... you?")
        else:
            self.msg("Nothing here but dust and wind.")

    def pickup(self):
        p = self.player
        for lt in list(self.screen.loots):
            if (lt.x, lt.y) != (p.x, p.y):
                continue
            if lt.kind == "money":
                p.money += lt.amount
                self.msg("You pocket $%d." % lt.amount)
            elif lt.kind == "ammo":
                p.ammo = min(MAX_AMMO, p.ammo + lt.amount)
                self.msg("A box of shells. (+%d)" % lt.amount)
            elif lt.kind == "tonic":
                self.inv["tonic"] = self.inv.get("tonic", 0) + 1
                self.msg("A bottle of tonic, still corked. (T to drink)")
            elif lt.kind == "locket":
                self.inv["locket"] = 1
                self.msg("A little silver locket, engraved 'H.A.' Widow Ashby at Boot Hill will want this.")
            elif lt.kind == "nugget":
                self.inv["nugget"] = 1
                self.msg("A gold nugget the size of a hen's egg! Horace at the bank buys gold.")
            if lt.id:
                self.collected.add(lt.id)
            self.screen.loots.remove(lt)

    # ------------------------------------------------------------ spawning
    def spawn_screen(self, scr):
        now = time.time()
        key = (scr.sx, scr.sy)
        if not scr.spawned:
            scr.spawned = True
            for i, enc in enumerate(ENCOUNTERS.get(key, [])):
                kind, x, y = enc[0], enc[1], enc[2]
                pos = scr.nearest_passable(x, y)
                if pos is None:
                    continue
                x, y = pos
                if kind == "bandit":
                    scr.actors.append(Enemy(x, y, (x, y), name="Bandit", color="bandit", hp=2,
                                            fire_rate=40, speed=4, aggro=11))
                elif kind in ("snake", "coyote", "cattle", "buffalo"):
                    scr.actors.append(Critter(x, y, kind, (x, y)))
                else:
                    lid = "%d_%d_%d" % (scr.sx, scr.sy, i)
                    if lid in self.collected:
                        continue
                    amount = enc[3] if kind == "money" else (6 if kind == "ammo" else 1)
                    scr.loots.append(Loot(x, y, kind, amount, lid))
            for o in OUTLAWS:
                if tuple(o["screen"]) == key and self.bounties[o["id"]] == "open":
                    pos = scr.nearest_passable(*o["pos"])
                    if pos is None:
                        continue
                    scr.actors.append(Enemy(pos[0], pos[1], pos, name=o["name"], color="outlaw",
                                            hp=o["hp"], named=True, oid=o["id"], reward=o["reward"],
                                            duel=o["duel"], fire_rate=o["fire_rate"], speed=3,
                                            aggro=14, taunt=o["taunt"]))
        else:
            for a in scr.actors:
                if not a.alive and not a.named and now - a.dead_at > RESPAWN_SECONDS:
                    if not self.occupied(*a.slot):
                        a.alive = True
                        a.x, a.y = a.slot
                        a.hp = a.max_hp if isinstance(a, Enemy) else Critter.HP[a.kind]
        if key == (0, 1) and self.flags.get("has_map") and "nugget" not in self.collected \
                and not any(lt.kind == "nugget" for lt in scr.loots):
            pos = scr.nearest_passable(9, 7)
            if pos:
                scr.loots.append(Loot(pos[0], pos[1], "nugget", 1, "nugget"))

    # ------------------------------------------------------------ update
    def update(self):
        p = self.player
        p.invuln = max(0, p.invuln - 1)
        p.fire_cd = max(0, p.fire_cd - 1)
        night = self.is_night()
        if night != self.was_night:
            self.was_night = night
            self.msg("Night falls over the territory." if night else "Dawn breaks. The desert warms.")
        self.update_bullets()
        for a in list(self.screen.actors):
            if not a.alive:
                continue
            a.hurt = max(0, a.hurt - 1)
            if isinstance(a, Enemy):
                self.update_enemy(a)
            else:
                self.update_critter(a)
        self.bullets = [b for b in self.bullets if b.alive]

    def update_bullets(self):
        p = self.player
        scr = self.screen
        for b in self.bullets:
            for _ in range(b.speed):
                b.x += b.dx
                b.y += b.dy
                if not scr.in_bounds(b.x, b.y) or scr.blocks_bullet(b.x, b.y):
                    b.alive = False
                    break
                if b.owner == "player":
                    a = self.actor_at(b.x, b.y)
                    if a:
                        self.hit_actor(a)
                        b.alive = False
                        break
                    n = self.npc_at(b.x, b.y)
                    if n:
                        self.msg("You nearly shot %s! Mind your aim." % n.name)
                        b.alive = False
                        break
                else:
                    if (b.x, b.y) == (p.x, p.y):
                        self.damage_player(1, "A bullet")
                        b.alive = False
                        break
                    if self.actor_at(b.x, b.y) or self.npc_at(b.x, b.y):
                        b.alive = False
                        break

    def update_enemy(self, e):
        p = self.player
        if e.cooldown > 0:
            e.cooldown -= 1
        dx, dy = p.x - e.x, p.y - e.y
        dist = abs(dx) + abs(dy)
        if dist <= e.aggro:
            aligned = (dx == 0 and abs(dy) <= 9) or (dy == 0 and abs(dx) <= 12)
            if aligned and e.cooldown == 0 and self.line_clear(e.x, e.y, p.x, p.y):
                self.bullets.append(Bullet(e.x, e.y, sign(dx), sign(dy), "enemy", 1))
                e.cooldown = e.fire_rate + self.rng.randint(0, 10)
                return
            e.move_timer -= 1
            if e.move_timer <= 0:
                e.move_timer = e.speed
                if dx == 0 or dy == 0:
                    # already aligned but blocked or reloading: close in a little, or sidestep
                    moves = [(sign(dx), sign(dy))] if dist > 3 else [(sign(dy), sign(dx)), (-sign(dy), -sign(dx))]
                elif abs(dx) < abs(dy):
                    moves = [(sign(dx), 0), (0, sign(dy))]
                else:
                    moves = [(0, sign(dy)), (sign(dx), 0)]
                if self.rng.random() < 0.25:
                    self.rng.shuffle(moves)
                for mx, my in moves:
                    if self.try_step(e, mx, my):
                        break
        else:
            e.move_timer -= 1
            if e.move_timer <= 0:
                e.move_timer = e.speed * 3
                mx, my = self.rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                self.try_step(e, mx, my)

    def try_step(self, a, mx, my):
        nx, ny = a.x + mx, a.y + my
        if (mx or my) and self.screen.passable(nx, ny) and not self.occupied(nx, ny, ignore=a):
            a.x, a.y = nx, ny
            return True
        return False

    def update_critter(self, c):
        p = self.player
        c.bite_cd = max(0, c.bite_cd - 1)
        c.move_timer -= 1
        adjacent = max(abs(c.x - p.x), abs(c.y - p.y)) <= 1
        if c.kind == "snake":
            if adjacent and c.bite_cd == 0:
                self.damage_player(1, "The rattlesnake")
                c.bite_cd = 40
            if c.move_timer <= 0:
                c.move_timer = 12
                mx, my = self.rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                if abs(c.x + mx - c.home[0]) <= 3 and abs(c.y + my - c.home[1]) <= 3:
                    self.try_step(c, mx, my)
        elif c.kind == "coyote":
            dist = abs(c.x - p.x) + abs(c.y - p.y)
            if adjacent and c.bite_cd == 0:
                self.damage_player(1, "The coyote")
                c.bite_cd = 30
            if c.move_timer <= 0:
                if dist <= 9:
                    c.move_timer = 3
                    dx, dy = p.x - c.x, p.y - c.y
                    moves = [(sign(dx), 0), (0, sign(dy))] if abs(dx) > abs(dy) else [(0, sign(dy)), (sign(dx), 0)]
                    for mx, my in moves:
                        if self.try_step(c, mx, my):
                            break
                else:
                    c.move_timer = 8
                    mx, my = self.rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                    self.try_step(c, mx, my)
        else:  # cattle, buffalo
            if c.move_timer <= 0:
                c.move_timer = 20
                mx, my = self.rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                if abs(c.x + mx - c.home[0]) <= 4 and abs(c.y + my - c.home[1]) <= 3:
                    self.try_step(c, mx, my)

    # ------------------------------------------------------------ combat
    def hit_actor(self, a):
        a.hp -= 1
        a.hurt = 3
        if a.hp <= 0:
            self.kill_actor(a)
        elif isinstance(a, Enemy) and a.named:
            self.msg("%s staggers! (%d more hits)" % (a.name, a.hp))
        elif isinstance(a, Critter) and a.kind == "cattle":
            self.msg("The longhorn bellows. Big Sam won't like this.")

    def kill_actor(self, a, by_duel=False):
        a.alive = False
        a.dead_at = time.time()
        p = self.player
        if isinstance(a, Enemy):
            self.kills += 1
            if a.named:
                self.bounties[a.oid] = "killed"
                extra = " Captain Ward at the fort pays too." if a.oid == "kettle" else ""
                verb = "You out-drew" if by_duel else "You gunned down"
                self.msg("%s %s! Collect $%d from Sheriff Barrett.%s" % (verb, a.name, a.reward, extra))
                self.screen.loots.append(Loot(a.x, a.y, "money", self.rng.randint(8, 20), None))
            else:
                r = self.rng.random()
                if r < 0.55:
                    self.screen.loots.append(Loot(a.x, a.y, "money", self.rng.randint(3, 9), None))
                    self.msg("Bandit down! He drops a coin purse.")
                elif r < 0.85:
                    self.screen.loots.append(Loot(a.x, a.y, "ammo", 4, None))
                    self.msg("Bandit down! He drops some shells.")
                else:
                    self.msg("Bandit down!")
        else:
            if a.kind == "buffalo":
                self.screen.loots.append(Loot(a.x, a.y, "money", 8, None))
                self.msg("The buffalo falls. Its hide will fetch a fair price.")
            elif a.kind == "cattle":
                fine = min(10, p.money)
                p.money -= fine
                self.msg("You shot one of Big Sam's longhorns! He docks you $%d." % fine)
            else:
                self.msg("The %s is dead." % a.name.lower())

    def damage_player(self, n, source, force=False):
        p = self.player
        if p.invuln > 0 and not force:
            return
        p.hearts -= n
        p.invuln = 20
        if p.hearts <= 0:
            p.hearts = 0
            self.die(source)
        else:
            self.msg("%s hits you!%s" % (source, "  Careful, you're hurt bad." if p.hearts <= 2 else ""))

    def die(self, source):
        self.msg("%s finishes you. Everything goes dark..." % source)
        self.bullets = []
        self.mode = "dead"
        self.dead_until = time.time() + 3.0

    def respawn(self):
        p = self.player
        lost = p.money // 2
        p.money -= lost
        p.hearts = MAX_HEARTS
        p.invuln = 30
        p.sx, p.sy = 2, 2
        p.x, p.y = 4, 10
        p.facing = (0, 1)
        self.mode = "play"
        self.enter_screen()
        self.msg("Doc Hart dragged you off the street and patched you up. Silas took $%d as a deposit." % lost)

    # ------------------------------------------------------------ duel
    def start_duel(self, e):
        self.bullets = []
        self.duel = dict(enemy=e, phase="wait", draw_at=time.time() + self.rng.uniform(1.8, 4.5),
                         result=None, result_at=0.0, rt=0.0)
        self.mode = "duel"

    def update_duel(self):
        d = self.duel
        now = time.time()
        if d["phase"] == "wait" and now >= d["draw_at"]:
            d["phase"] = "draw"
        elif d["phase"] == "draw" and now - d["draw_at"] > 1.2:
            d["rt"] = 1.2
            self.resolve_duel("late")
        elif d["phase"] == "result" and now >= d["result_at"]:
            self.finish_duel()

    def resolve_duel(self, result):
        d = self.duel
        d["phase"] = "result"
        d["result"] = result
        d["result_at"] = time.time() + (2.6 if result != "chicken" else 1.5)

    def finish_duel(self):
        d = self.duel
        e = d["enemy"]
        self.duel = None
        self.mode = "play"
        if d["result"] == "win":
            self.kill_actor(e, by_duel=True)
        elif d["result"] in ("early", "late"):
            e.cooldown = e.fire_rate
            self.damage_player(2, e.name, force=True)
        else:
            self.msg("You back down from %s. He won't forget it." % e.name)

    # ------------------------------------------------------------ dialogue
    def say(self, n, text, options=None):
        return Dialog(n.name, text, options, n.color)

    def next_line(self, n):
        i = self.npc_line.get(n.id, 0)
        self.npc_line[n.id] = (i + 1) % len(n.lines)
        return n.lines[i]

    def talk(self, n):
        handler = getattr(self, "role_" + n.role, self.role_talk)
        d = handler(n)
        if d is not None:          # a handler may switch modes itself (the Mayor's ending)
            self.dialog = d
            self.mode = "dialog"

    def close_dialog(self):
        self.dialog = None
        self.mode = "play"

    def role_talk(self, n, text=None):
        return self.say(n, text or self.next_line(n))

    def role_sheriff(self, n, text=None):
        self.flags["met_sheriff"] = True
        killed = [o for o in OUTLAWS if self.bounties[o["id"]] == "killed"]
        opts = [("See the wanted wall", self.open_wanted)]
        if killed:
            total = sum(o["reward"] for o in killed)
            for o in killed:
                self.bounties[o["id"]] = "paid"
            self.player.money += total
            names = ", ".join(o["name"] for o in killed)
            return self.say(n, "You got %s! Here's $%d and the thanks of a grateful town." % (names, total), opts)
        if all(s == "paid" for s in self.bounties.values()):
            return self.say(n, "Wall's clean for the first time in ten years. Go see the Mayor. He's been waiting.", opts)
        return self.say(n, text or self.next_line(n), opts)

    def open_wanted(self):
        self.dialog = None
        self.mode = "wanted"

    def role_doc(self, n, text=None):
        if self.player.hearts >= MAX_HEARTS:
            return self.say(n, text or "You're fit as a fiddle. Don't let me see you again today.")
        return self.say(n, text or self.next_line(n), [("Patch me up ($5)", lambda: self.doc_heal(n))])

    def doc_heal(self, n):
        p = self.player
        if p.money >= 5:
            p.money -= 5
            p.hearts = MAX_HEARTS
            self.dialog = self.say(n, "There. Good as new. Try to stay that way for an hour.")
        elif not self.flags.get("doc_free"):
            self.flags["doc_free"] = True
            p.hearts = MAX_HEARTS
            self.dialog = self.say(n, "No money? This one's on the house. Once.")
        else:
            self.dialog = self.say(n, "Come back when you can pay. I'm a doctor, not a charity. Try the well.")

    def store_opts(self, n):
        return [("Six shells - $3", lambda: self.buy(n, "ammo", 3)),
                ("Tonic - $8", lambda: self.buy(n, "tonic", 8))]

    def role_store(self, n, text=None):
        return self.say(n, text or self.next_line(n), self.store_opts(n))

    def buy(self, n, kind, price, thanks="Pleasure doing business."):
        p = self.player
        if p.money < price:
            self.dialog = self.say(n, "Your pockets are lighter than your trigger finger. Come back with $%d." % price,
                                   self.dialog.options if self.dialog else None)
            return
        p.money -= price
        if kind == "ammo":
            p.ammo = min(MAX_AMMO, p.ammo + 6)
            self.msg("+6 shells.")
        else:
            self.inv[kind] = self.inv.get(kind, 0) + 1
            self.msg("You buy a %s." % kind)
        self.dialog = self.say(n, thanks, self.dialog.options if self.dialog else None)

    def role_bar(self, n, text=None):
        opts = [("Whiskey - $4", lambda: self.buy(n, "whiskey", 4, "Red slides a bottle down the bar.")),
                ("Rumor - $1", lambda: self.rumor(n))]
        return self.say(n, text or self.next_line(n), opts)

    def rumor(self, n):
        p = self.player
        if p.money < 1:
            self.dialog = self.say(n, "A dollar. It's one dollar. Get out.", self.dialog.options)
            return
        p.money -= 1
        open_ = [o for o in OUTLAWS if self.bounties[o["id"]] == "open"]
        if not open_:
            self.dialog = self.say(n, "No rumors left. You've killed everybody interesting.", self.dialog.options)
        else:
            o = self.rng.choice(open_)
            self.dialog = self.say(n, "Word is %s %s." % (o["name"], o["hint"]), self.dialog.options)

    def role_stable(self, n, text=None):
        if self.player.horse:
            return self.say(n, "How's the mare treating you? Fastest legs in the territory.")
        return self.say(n, text or self.next_line(n), [("Buy a horse - $40", lambda: self.buy_horse(n))])

    def buy_horse(self, n):
        p = self.player
        if p.money < 40:
            self.dialog = self.say(n, "Forty dollars, amigo. A horse is worth more than a bandit's bounty.",
                                   self.dialog.options)
            return
        p.money -= 40
        p.horse = True
        self.msg("You ride out on a chestnut mare. You move twice as fast!")
        self.dialog = self.say(n, "Treat her well. She's smarter than most of my customers.")

    def role_banker(self, n, text=None):
        if self.inv.get("nugget"):
            return self.say(n, "Is that... gold? Genuine gold? Horace Pruett will make you a fair offer.",
                            [("Sell the nugget - $60", lambda: self.sell_nugget(n))])
        return self.say(n, text or self.next_line(n))

    def sell_nugget(self, n):
        self.inv["nugget"] = 0
        self.flags["nugget_sold"] = True
        self.player.money += 60
        self.msg("+$60. The banker's hands are shaking.")
        self.dialog = self.say(n, "Sixty dollars. And please don't mention this to anyone with a mask.")

    def role_gambler(self, n, text=None):
        return self.say(n, text or self.next_line(n),
                        [("Bet $5", lambda: self.bet(n, 5)), ("Bet $20", lambda: self.bet(n, 20))])

    def bet(self, n, amt):
        p = self.player
        if p.money < amt:
            self.dialog = self.say(n, "Come back when your wallet's as bold as your mouth.", self.dialog.options)
            return
        if self.rng.random() < 0.5:
            p.money += amt
            self.dialog = self.say(n, "Heads! Vance grimaces and pays out $%d." % amt, self.dialog.options)
        else:
            p.money -= amt
            self.dialog = self.say(n, "Tails. Vance smiles like a cat and pockets your $%d." % amt, self.dialog.options)

    def role_widow(self, n, text=None):
        if self.flags.get("locket_returned"):
            return self.say(n, "Thank you again, stranger. Harold would have liked you.")
        if self.inv.get("locket"):
            return self.say(n, "Is that... oh. Oh, that's Harold's. You found it.",
                            [("Return the locket", lambda: self.return_locket(n))])
        return self.say(n, text or self.next_line(n))

    def return_locket(self, n):
        self.inv["locket"] = 0
        self.flags["locket_returned"] = True
        self.player.money += 25
        self.msg("+$25. Widow Ashby smiles for the first time in a year.")
        self.dialog = self.say(n, "Bless you. Take this. Harold's reward money. He'd want it used for good.")

    def role_prospector(self, n, text=None):
        if self.flags.get("has_map"):
            if self.inv.get("nugget") or self.flags.get("nugget_sold"):
                return self.say(n, "Ha! Told ya! Hen's egg! Horace'll give you sixty for it, no less.")
            return self.say(n, "Mouth of the shaft, north side, like I said. Something glints there now.")
        if self.inv.get("whiskey"):
            return self.say(n, "Is that Red's whiskey? Well now. My memory's feeling looser already.",
                            [("Give Gus the whiskey", lambda: self.give_whiskey(n))])
        return self.say(n, text or self.next_line(n))

    def give_whiskey(self, n):
        self.inv["whiskey"] -= 1
        self.flags["has_map"] = True
        self.inv["map"] = 1
        if (self.player.sx, self.player.sy) == (0, 1):
            self.spawn_screen(self.screen)
        self.msg("Gus scrawls a map. Something now glints near the mine entrance.")
        self.dialog = self.say(n, "*glug* Ahhh. Right. The nugget sits at the mouth of the shaft, north side, under a loose rock.")

    def role_captain(self, n, text=None):
        if self.bounties["kettle"] in ("killed", "paid") and not self.flags.get("captain_paid"):
            self.flags["captain_paid"] = True
            self.player.money += 100
            self.msg("+$100 from the United States Army.")
            return self.say(n, "Kettle's dead? By God. The Army thanks you. One hundred dollars, as promised.")
        return self.say(n, text or self.next_line(n))

    def role_mayor(self, n, text=None):
        if all(s == "paid" for s in self.bounties.values()) and not self.flags.get("star"):
            self.flags["star"] = True
            self.inv["star"] = 1
            self.dialog = None
            self.mode = "ending"
            return None
        if self.flags.get("star"):
            return self.say(n, "The town's hero! Wear that star proudly. And maybe run for mayor. No, wait, don't.")
        return self.say(n, text or self.next_line(n))

    def role_preacher(self, n, text=None):
        return self.say(n, text or self.next_line(n), [("Donate $2 for a blessing", lambda: self.bless(n))])

    def bless(self, n):
        p = self.player
        if p.hearts >= MAX_HEARTS:
            self.dialog = self.say(n, "You're already blessed, friend. Try sinning a little first.", self.dialog.options)
        elif p.money < 2:
            self.dialog = self.say(n, "Faith is free. Blessings are two dollars. Church has expenses.", self.dialog.options)
        else:
            p.money -= 2
            p.hearts += 1
            self.dialog = self.say(n, "Amen. Go with God, and reload.", self.dialog.options)

    def role_medicine(self, n, text=None):
        return self.say(n, text or self.next_line(n), [("Miracle Tonic - $6", lambda: self.quill_tonic(n))])

    def quill_tonic(self, n):
        p = self.player
        if p.money < 6:
            self.dialog = self.say(n, "Six dollars, madam, sir, whichever. Miracles aren't free.", self.dialog.options)
            return
        p.money -= 6
        if self.rng.random() < 0.7:
            self.inv["tonic"] = self.inv.get("tonic", 0) + 1
            self.dialog = self.say(n, "A genuine article! Probably. Drink it with T when you're hurting.", self.dialog.options)
        else:
            self.dialog = self.say(n, "You uncork it. It's colored water. Quill has already turned to the next customer.",
                                   self.dialog.options)

    def role_fortune(self, n, text=None):
        return self.say(n, text or self.next_line(n), [("Cross her palm - $3", lambda: self.fortune(n))])

    def fortune(self, n):
        p = self.player
        if p.money < 3:
            self.dialog = self.say(n, "The cards say you are poor. That one was free.", self.dialog.options)
            return
        p.money -= 3
        open_ = [o for o in OUTLAWS if self.bounties[o["id"]] == "open"]
        if not open_:
            self.dialog = self.say(n, "The cards show... peace. How dull. Go see the Mayor.", self.dialog.options)
            return
        o = min(open_, key=lambda o: abs(o["screen"][0] - p.sx) + abs(o["screen"][1] - p.sy))
        dx, dy = o["screen"][0] - p.sx, o["screen"][1] - p.sy
        ns = ("south" if dy > 0 else "north") if dy else ""
        ew = ("east" if dx > 0 else "west") if dx else ""
        where = (ns + ew) if (ns or ew) else "right here"
        self.dialog = self.say(n, "The cards show %s... %s of here. He %s." % (o["name"], where, o["hint"]),
                               self.dialog.options)

    def role_informant(self, n, text=None):
        return self.say(n, text or self.next_line(n))

    # ------------------------------------------------------------ save / load
    def save_game(self):
        data = dict(player=self.player.to_dict(), flags=self.flags, inv=self.inv, bounties=self.bounties,
                    collected=sorted(self.collected), visited=sorted(list(v) for v in self.visited),
                    kills=self.kills, npc_line=self.npc_line, elapsed=self.elapsed())
        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f, indent=1)
            self.has_save = True
            self.msg("Game saved.")
        except OSError as exc:
            self.msg("Couldn't save: %s" % exc)

    def load_game(self):
        try:
            with open(SAVE_PATH) as f:
                data = json.load(f)
        except (OSError, ValueError):
            self.msg("The save file is unreadable. Starting fresh.")
            self.start_new()
            return
        self.reset_state()
        self.player.from_dict(data["player"])
        self.flags = data.get("flags", {})
        self.inv = data.get("inv", {})
        self.bounties.update(data.get("bounties", {}))
        self.collected = set(data.get("collected", []))
        self.visited = set(tuple(v) for v in data.get("visited", []))
        self.kills = data.get("kills", 0)
        self.npc_line = data.get("npc_line", {})
        self.start = time.time()
        self.time_offset = data.get("elapsed", 0.0)
        self.was_night = self.is_night()
        self.mode = "play"
        self.messages.clear()
        self.enter_screen()
        self.msg("Welcome back to the frontier.")
