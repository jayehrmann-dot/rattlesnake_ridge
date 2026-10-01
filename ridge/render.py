"""Curses renderer: chunky 2-column tiles, a 2600-ish palette, and overlay screens."""
import curses
import textwrap

from .constants import (
    SCREEN_W, SCREEN_H, WORLD_W, WORLD_H, VIEW_COLS, VIEW_ROWS, HUD_ROWS, MSG_ROWS,
    MAX_HEARTS, TILES, PALETTE, WALL, FONT, COWBOY,
    PLAYER_SPRITE, HORSE_SPRITE, NPC_SPRITE, BANDIT_SPRITE, OUTLAW_SPRITE, SNAKE_SPRITE,
    COYOTE_SPRITE, CATTLE_SPRITE, LOOT_SPRITE, BULLET_SPRITE,
)
from .world import KIND_INFO, LAYOUT, NAMES
from .characters import OUTLAWS
from .entities import Enemy, Critter

CONTROLS = [
    "ARROWS / WASD ....... walk (twice as fast on a horse)",
    "SPACE ............... fire your six-gun the way you face",
    "E or ENTER .......... talk / examine / call out an outlaw",
    "T ................... drink a tonic (+3 hearts)",
    "I ................... saddlebags and tally",
    "M ................... territory map",
    "B ................... wanted posters (after seeing the Sheriff)",
    "? ................... this help screen",
    "F5 .................. save your game",
    "Q or ESC ............ quit (asks first, auto-saves)",
    "",
    "Walk off the edge of a screen to reach the next one.",
    "Line up with a bandit to shoot him. Step off his line to dodge.",
    "Stand beside a named outlaw and press E for a HIGH NOON duel:",
    "wait for DRAW!, then hit SPACE faster than he does.",
    "Wells and campfires restore a heart. Doc Hart fixes the rest.",
]


class Renderer:
    def __init__(self, stdscr):
        self.scr = stdscr
        self.night = False
        self.pairs = {}
        self.colors_ok = curses.has_colors()
        if self.colors_ok:
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass
        self.many = self.colors_ok and curses.COLORS >= 256
        self.max_pairs = curses.COLOR_PAIRS if self.colors_ok else 0
        self.oy = self.ox = 0

    # ------------------------------------------------------------ colours
    def cidx(self, name):
        day, night, basic = PALETTE[name]
        if self.many:
            return night if self.night else day
        return basic

    def attr(self, fg, bg, bold=False):
        if not self.colors_ok:
            return curses.A_BOLD if bold else 0
        key = (self.cidx(fg), self.cidx(bg))
        if key not in self.pairs:
            n = len(self.pairs) + 1
            if n >= self.max_pairs:
                return 0
            try:
                curses.init_pair(n, key[0], key[1])
            except curses.error:
                return 0
            self.pairs[key] = n
        a = curses.color_pair(self.pairs[key])
        return a | curses.A_BOLD if bold else a

    def put(self, y, x, s, attr=0):
        try:
            self.scr.addstr(y, x, s, attr)
        except curses.error:
            pass

    def fill(self, y0, x0, rows, cols, attr):
        for y in range(y0, y0 + rows):
            self.put(y, x0, " " * cols, attr)

    def center(self, y, text, attr=0, width=VIEW_COLS):
        self.put(y, self.ox + (width - len(text)) // 2, text, attr)

    def big(self, y, x, text, attr):
        """Draw text in the 3x5 block font (4 columns per character)."""
        for i, ch in enumerate(text.upper()):
            glyph = FONT.get(ch, FONT[" "])
            for r, row in enumerate(glyph):
                for c, px in enumerate(row):
                    if px == "█":
                        self.put(y + r, x + i * 4 + c, "█", attr)

    def big_center(self, y, text, attr):
        w = len(text) * 4 - 1
        self.big(y, self.ox + (VIEW_COLS - w) // 2, text, attr)

    def cowboy(self, y, x, attr, flip=False):
        for r, row in enumerate(COWBOY):
            row = row[::-1] if flip else row
            for c, px in enumerate(row):
                if px == "#":
                    self.put(y + r, x + c, "█", attr)

    # ------------------------------------------------------------ frame
    def draw(self, g):
        self.night = g.is_night()
        self.scr.erase()
        rows, cols = self.scr.getmaxyx()
        if rows < VIEW_ROWS or cols < VIEW_COLS:
            self.put(0, 0, "Rattlesnake Ridge needs a terminal of at least "
                           "%dx%d (you have %dx%d)." % (VIEW_COLS, VIEW_ROWS, cols, rows))
            self.put(1, 0, "Enlarge the window, then press any key.")
            self.scr.refresh()
            return
        self.oy = (rows - VIEW_ROWS) // 2
        self.ox = (cols - VIEW_COLS) // 2

        mode = g.mode
        if mode == "title":
            self.draw_title(g)
        elif mode in ("play", "dialog", "dead", "quit"):
            self.draw_play(g)
            if mode == "dead":
                self.fill(self.oy + 7, self.ox + 14, 9, 36, self.attr("white", "black"))
                self.big_center(self.oy + 9, "YOU DIED", self.attr("red", "black", True))
        elif mode == "duel":
            self.draw_duel(g)
        elif mode == "map":
            self.draw_map(g)
        elif mode == "help":
            self.draw_panel("HOW TO PLAY", CONTROLS)
        elif mode == "inv":
            self.draw_inventory(g)
        elif mode == "wanted":
            self.draw_wanted(g)
        elif mode == "ending":
            self.draw_ending(g)
        self.scr.refresh()

    # ------------------------------------------------------------ title
    def draw_title(self, g):
        sky = self.attr("sky", "sky")
        sand = self.attr("sand", "sand")
        self.fill(self.oy, self.ox, 17, VIEW_COLS, sky)
        self.fill(self.oy + 17, self.ox, 7, VIEW_COLS, sand)
        self.fill(self.oy + 2, self.ox + 52, 2, 6, self.attr("sun", "sun"))
        self.big_center(self.oy + 3, "RATTLESNAKE", self.attr("wall", "sky", True))
        self.big_center(self.oy + 9, "RIDGE", self.attr("wall", "sky", True))
        self.center(self.oy + 15, "A  2600-STYLE  FRONTIER  ADVENTURE", self.attr("white", "sky", True))
        self.cowboy(self.oy + 8, self.ox + 4, self.attr("player", "sky"))
        self.cowboy(self.oy + 8, self.ox + 53, self.attr("outlaw", "sky"), flip=True)
        rock = self.attr("rock_dark", "rock")
        self.put(self.oy + 17, self.ox + 2, "▓▓▓▓", rock)
        self.put(self.oy + 17, self.ox + 58, "▓▓▓▓", rock)
        cactus = self.attr("cactus", "sand")
        for cx in (12, 20, 44):
            self.put(self.oy + 18, self.ox + cx, "▚▞", cactus)
        txt = self.attr("black", "sand", True)
        if g.tick % 20 < 14:
            self.center(self.oy + 19, "N) NEW GAME" + ("     C) CONTINUE" if g.has_save else ""), txt)
        self.center(self.oy + 21, "Q) QUIT           H) HOW TO PLAY", self.attr("black", "sand"))
        self.center(self.oy + 23, "explore. talk. draw.", self.attr("wood_dark", "sand"))

    # ------------------------------------------------------------ play
    def draw_play(self, g):
        p = g.player
        scr = g.screen
        oy, ox = self.oy, self.ox

        # HUD
        hud = self.attr("hud", "hud_bg", True)
        self.fill(oy, ox, HUD_ROWS, VIEW_COLS, hud)
        self.put(oy, ox + 1, "RATTLESNAKE RIDGE", hud)
        self.center(oy, scr.name.upper(), hud)
        self.put(oy, ox + VIEW_COLS - 6, "NIGHT" if self.night else "  DAY", hud)
        hearts = "".join("█" if i < p.hearts else "░" for i in range(MAX_HEARTS))
        self.put(oy + 1, ox + 1, hearts, self.attr("red", "hud_bg", True))
        paid = sum(1 for s in g.bounties.values() if s == "paid")
        self.put(oy + 1, ox + 9, "SHELLS %2d   $%-4d   BOUNTY %d/%d" % (p.ammo, p.money, paid, len(OUTLAWS)), hud)
        if p.horse:
            self.put(oy + 1, ox + VIEW_COLS - 6, "HORSE", hud)
        if g.inv.get("tonic"):
            self.put(oy + 1, ox + 44, "TONIC x%d" % g.inv["tonic"], hud)

        # cell buffer -------------------------------------------------
        cells = [[None] * SCREEN_W for _ in range(SCREEN_H)]
        for y in range(SCREEN_H):
            row = scr.tiles[y]
            for x in range(SCREEN_W):
                glyph, fg, bg, _, _ = TILES[row[x]]
                cells[y][x] = (glyph, fg, bg)
        for (cx, cy, text) in scr.labels:
            for i in range((len(text) + 1) // 2):
                x = cx + i
                if scr.in_bounds(x, cy) and scr.get(x, cy) == WALL:
                    cells[cy][x] = (text[2 * i:2 * i + 2].ljust(2), "label", "wall")

        def sprite(x, y, glyph, fg):
            if 0 <= x < SCREEN_W and 0 <= y < SCREEN_H:
                cells[y][x] = (glyph, fg, cells[y][x][2])

        for lt in scr.loots:
            fg = {"locket": "white", "nugget": "gold", "tonic": "lime"}.get(lt.kind, "loot")
            sprite(lt.x, lt.y, LOOT_SPRITE[lt.kind], fg)
        for a in scr.actors:
            if not a.alive:
                continue
            if isinstance(a, Enemy):
                glyph = OUTLAW_SPRITE if a.named else BANDIT_SPRITE
            else:
                glyph = {"snake": SNAKE_SPRITE, "coyote": COYOTE_SPRITE}.get(a.kind, CATTLE_SPRITE)
            sprite(a.x, a.y, glyph, "white" if a.hurt > 0 else a.color)
        for n in scr.npcs:
            sprite(n.x, n.y, NPC_SPRITE, n.color)
        for b in g.bullets:
            sprite(b.x, b.y, BULLET_SPRITE[(b.dx, b.dy)], "bullet_p" if b.owner == "player" else "bullet_e")
        if not (p.invuln > 0 and g.tick % 4 < 2) and g.mode != "dead":
            table = HORSE_SPRITE if p.horse else PLAYER_SPRITE
            sprite(p.x, p.y, table[p.facing], "player")

        # flush rows as runs of identical colour --------------------------
        for y in range(SCREEN_H):
            run, run_key, run_x = [], None, 0
            for x in range(SCREEN_W):
                glyph, fg, bg = cells[y][x]
                key = (fg, bg)
                if key != run_key and run:
                    self.put(oy + HUD_ROWS + y, ox + run_x * 2, "".join(run), self.attr(*run_key))
                    run = []
                if not run:
                    run_key, run_x = key, x
                run.append(glyph)
            if run:
                self.put(oy + HUD_ROWS + y, ox + run_x * 2, "".join(run), self.attr(*run_key))

        # bottom panel ------------------------------------------------------
        py = oy + HUD_ROWS + SCREEN_H
        panel = self.attr("panel_fg", "panel")
        self.fill(py, ox, MSG_ROWS, VIEW_COLS, panel)
        if g.mode == "dialog" and g.dialog:
            d = g.dialog
            self.put(py, ox + 1, d.speaker.upper(), self.attr(d.color, "panel", True))
            for i, line in enumerate(textwrap.wrap(d.text, VIEW_COLS - 2)[:2]):
                self.put(py + 1 + i, ox + 1, line, panel)
            opts = "  ".join("%d) %s" % (i + 1, label) for i, (label, _) in enumerate(d.options))
            opts = (opts + "   [E] Done") if d.options else "[E] Done"
            self.put(py + 3, ox + 1, opts[:VIEW_COLS - 2], self.attr("white", "panel", True))
        elif g.mode == "quit":
            self.put(py + 1, ox + 1, "Ride off into the sunset?  Your progress will be saved.", panel)
            self.put(py + 3, ox + 1, "Y) Yes, quit     N) Keep playing", self.attr("white", "panel", True))
        else:
            msgs = list(g.messages)[-3:]
            for i, m in enumerate(msgs):
                self.put(py + i, ox + 1, m[:VIEW_COLS - 2], panel if i < len(msgs) - 1 else self.attr("white", "panel", True))
            self.put(py + 3, ox + 1, g.adjacent_hint()[:VIEW_COLS - 2], self.attr("sand_dark", "panel"))

    # ------------------------------------------------------------ duel
    def draw_duel(self, g):
        d = g.duel
        e = d["enemy"]
        oy, ox = self.oy, self.ox
        sky = self.attr("sky", "sky")
        sand = self.attr("sand", "sand")
        self.fill(oy, ox, 15, VIEW_COLS, sky)
        self.fill(oy + 15, ox, 9, VIEW_COLS, sand)
        self.fill(oy + 1, ox + 29, 2, 6, self.attr("sun", "sun"))
        self.big_center(oy + 3, "HIGH NOON", self.attr("black", "sky", True))
        self.center(oy + 9, "vs.  " + e.name, self.attr("black", "sky", True))
        self.cowboy(oy + 10, ox + 10, self.attr("player", "sky"))
        self.cowboy(oy + 10, ox + 47, self.attr(e.color, "sky"), flip=True)
        phase = d["phase"]
        txt = self.attr("black", "sand", True)
        if phase == "wait":
            self.center(oy + 20, "Steady...  wait for it...", txt)
            self.center(oy + 22, "SPACE to fire.  Draw too soon and you lose.  ESC backs down.",
                        self.attr("wood_dark", "sand"))
        elif phase == "draw":
            if g.tick % 4 < 3:
                self.big_center(oy + 16, "DRAW!", self.attr("red", "sand", True))
        else:
            res = d["result"]
            if res == "win":
                self.put(oy + 14, ox + 17, "•" * 30, self.attr("bullet_p", "sky", True))
                self.center(oy + 20, "You out-drew %s!  (%.2f seconds)" % (e.name, d["rt"]), txt)
                self.center(oy + 22, "The bounty is yours.", self.attr("wood_dark", "sand"))
            elif res == "early":
                self.put(oy + 14, ox + 17, "•" * 30, self.attr("bullet_e", "sky", True))
                self.center(oy + 20, "TOO SOON! You fumble the draw and %s fires." % e.name, txt)
            elif res == "late":
                self.put(oy + 14, ox + 17, "•" * 30, self.attr("bullet_e", "sky", True))
                self.center(oy + 20, "Too slow!  %s puts two in you." % e.name, txt)
            else:
                self.center(oy + 20, "You back down. %s laughs." % e.name, txt)

    # ------------------------------------------------------------ overlays
    def draw_panel(self, title, lines, footer="press any key to return"):
        oy, ox = self.oy, self.ox
        panel = self.attr("panel_fg", "panel")
        self.fill(oy, ox, VIEW_ROWS, VIEW_COLS, panel)
        self.center(oy + 1, title, self.attr("wall", "panel", True))
        for i, line in enumerate(lines[:VIEW_ROWS - 5]):
            self.put(oy + 3 + i, ox + 3, line[:VIEW_COLS - 6], panel)
        self.center(oy + VIEW_ROWS - 2, footer, self.attr("dim", "panel"))

    def draw_map(self, g):
        oy, ox = self.oy, self.ox
        panel = self.attr("panel_fg", "panel")
        self.fill(oy, ox, VIEW_ROWS, VIEW_COLS, panel)
        self.center(oy + 1, "TERRITORY MAP", self.attr("wall", "panel", True))
        p = g.player
        gx0, gy0 = ox + 4, oy + 3
        known = g.flags.get("met_sheriff", False)
        for sy in range(WORLD_H):
            for sx in range(WORLD_W):
                kind = LAYOUT[sy][sx]
                short, col = KIND_INFO[kind]
                cx, cy = gx0 + sx * 8, gy0 + sy * 3
                if (sx, sy) in g.visited:
                    a = self.attr("black", col)
                    self.fill(cy, cx, 3, 8, a)
                    self.put(cy + 1, cx + (8 - len(short)) // 2, short, a)
                    if known:
                        for o in OUTLAWS:
                            if tuple(o["screen"]) == (sx, sy) and g.bounties[o["id"]] == "open":
                                self.put(cy, cx + 6, "$", self.attr("gold", col, True))
                else:
                    a = self.attr("dim", "panel")
                    self.fill(cy, cx, 3, 8, a)
                    self.put(cy + 1, cx + 3, "??", a)
                if (sx, sy) == (p.sx, p.sy) and g.tick % 10 < 7:
                    self.put(cy + 2, cx + 2, "YOU", self.attr("white", "player", True))
        self.center(oy + 19, "You are at: " + NAMES[(p.sx, p.sy)], self.attr("white", "panel", True))
        self.center(oy + 20, "%d of %d screens explored" % (len(g.visited), WORLD_W * WORLD_H), panel)
        if known:
            self.center(oy + 21, "$ marks a wanted outlaw still at large", self.attr("gold", "panel"))
        self.center(oy + VIEW_ROWS - 2, "press any key to return", self.attr("dim", "panel"))

    def draw_inventory(self, g):
        p = g.player
        lines = [
            "Six-shooter ............ %d shells (max %d)" % (p.ammo, 48),
            "Money .................. $%d" % p.money,
            "Hearts ................. %d / %d" % (p.hearts, MAX_HEARTS),
            "Horse .................. %s" % ("chestnut mare (double speed)" if p.horse else "none, you walk"),
            "",
        ]
        names = {"tonic": "Snake-oil tonic (T to drink, +3 hearts)", "whiskey": "Bottle of Red's whiskey",
                 "locket": "Harold Ashby's silver locket", "nugget": "Gold nugget, hen's-egg sized",
                 "map": "Old Gus's scrawled map", "star": "The Mayor's SILVER STAR"}
        items = [(k, v) for k, v in g.inv.items() if v]
        if items:
            for k, v in items:
                lines.append("%-2s x%-2d %s" % ("", v, names.get(k, k)))
        else:
            lines.append("Saddlebags: empty but for dust.")
        lines += ["", "Bandits shot ........... %d" % g.kills]
        for o in OUTLAWS:
            st = g.bounties[o["id"]]
            mark = {"open": "at large", "killed": "DEAD - collect bounty", "paid": "bounty collected"}[st]
            lines.append("  %-26s $%-4d %s" % (o["name"], o["reward"], mark))
        self.draw_panel("SADDLEBAGS", lines)

    def draw_wanted(self, g):
        lines = []
        for o in OUTLAWS:
            st = g.bounties[o["id"]]
            if st == "paid":
                lines.append("  %-26s  $%-4d  -- BOUNTY PAID --" % (o["name"], o["reward"]))
            elif st == "killed":
                lines.append("  %-26s  $%-4d  DEAD. See the Sheriff." % (o["name"], o["reward"]))
            else:
                lines.append("  %-26s  $%-4d  WANTED" % (o["name"], o["reward"]))
                lines.append("      ...%s." % o["hint"])
        self.draw_panel("W A N T E D   -   DEAD OR ALIVE", lines)

    def draw_ending(self, g):
        oy, ox = self.oy, self.ox
        sky = self.attr("sky", "sky")
        sand = self.attr("sand", "sand")
        self.fill(oy, ox, 15, VIEW_COLS, sky)
        self.fill(oy + 15, ox, 9, VIEW_COLS, sand)
        self.fill(oy + 1, ox + 29, 2, 6, self.attr("sun", "sun"))
        self.big_center(oy + 3, "SILVER STAR", self.attr("wall", "sky", True))
        self.center(oy + 10, "Mayor Bly pins the star to your vest.", self.attr("black", "sky", True))
        self.center(oy + 12, "Seven outlaws dead. The frontier sleeps a little easier.", self.attr("black", "sky"))
        self.cowboy(oy + 10, ox + 28, self.attr("player", "sky"))
        self.center(oy + 20, "YOU TAMED RATTLESNAKE RIDGE", self.attr("black", "sand", True))
        self.center(oy + 22, "The territory is still yours to roam.  Press any key.", self.attr("wood_dark", "sand"))
