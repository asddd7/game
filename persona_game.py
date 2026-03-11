"""
PERSONA: SHADOW OF TWILIGHT
A Persona 3-inspired RPG prototype built with Python tkinter.
Features: Calendar System, Social Links, Turn-based Battle, Dungeon Exploration
"""

import tkinter as tk
from tkinter import font as tkfont
import random
import math
import time

# ─────────────────────────────────────────────
#  GAME DATA
# ─────────────────────────────────────────────

MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
DAYS_IN_MONTH = [30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 31]

SOCIAL_LINKS = [
    {"name": "Yuki Tanaka",  "arcana": "The Star",      "rank": 1, "max": 10, "color": "#4fc3f7", "exp": 0},
    {"name": "Ren Mochida",  "arcana": "The Moon",      "rank": 1, "max": 10, "color": "#ce93d8", "exp": 0},
    {"name": "Sora Aoyama",  "arcana": "The Hermit",    "rank": 1, "max": 10, "color": "#a5d6a7", "exp": 0},
    {"name": "Nao Fujiwara", "arcana": "Judgement",     "rank": 1, "max": 10, "color": "#ffcc80", "exp": 0},
]

ENEMIES = [
    {"name": "Slime Shadow",    "hp": 30,  "atk": 8,  "def": 3,  "weak": "fire",    "color": "#66bb6a"},
    {"name": "Iron Shade",      "hp": 50,  "atk": 12, "def": 8,  "weak": "ice",     "color": "#78909c"},
    {"name": "Flame Spectre",   "hp": 40,  "atk": 15, "def": 5,  "weak": "ice",     "color": "#ef5350"},
    {"name": "Frost Wraith",    "hp": 45,  "atk": 13, "def": 6,  "weak": "fire",    "color": "#42a5f5"},
    {"name": "Dark Omen",       "hp": 70,  "atk": 18, "def": 10, "weak": "electric","color": "#7e57c2"},
    {"name": "Thunder Beast",   "hp": 60,  "atk": 20, "def": 8,  "weak": "wind",    "color": "#ffca28"},
    {"name": "BOSS: Nyx Shard", "hp": 150, "atk": 25, "def": 15, "weak": "light",   "color": "#e91e63"},
]

SKILLS = [
    {"name": "Agi",      "type": "fire",     "power": 20, "cost": 5,  "target": "enemy"},
    {"name": "Bufu",     "type": "ice",      "power": 20, "cost": 5,  "target": "enemy"},
    {"name": "Zio",      "type": "electric", "power": 20, "cost": 5,  "target": "enemy"},
    {"name": "Garu",     "type": "wind",     "power": 20, "cost": 5,  "target": "enemy"},
    {"name": "Kouha",    "type": "light",    "power": 25, "cost": 8,  "target": "enemy"},
    {"name": "Dia",      "type": "heal",     "power": 30, "cost": 6,  "target": "self"},
    {"name": "Attack",   "type": "physical", "power": 15, "cost": 0,  "target": "enemy"},
    {"name": "Guard",    "type": "defense",  "power": 0,  "cost": 0,  "target": "self"},
]

COLORS = {
    "bg":        "#0a0a14",
    "panel":     "#111124",
    "panel2":    "#1a1a30",
    "accent":    "#00e5ff",
    "accent2":   "#ff4081",
    "gold":      "#ffd54f",
    "text":      "#e0e0ff",
    "text_dim":  "#7070a0",
    "hp_bar":    "#00e676",
    "sp_bar":    "#2979ff",
    "exp_bar":   "#ffd740",
    "enemy_bar": "#ff1744",
    "border":    "#2a2a50",
    "white":     "#ffffff",
}

# ─────────────────────────────────────────────
#  MAIN GAME
# ─────────────────────────────────────────────

class PersonaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("PERSONA: SHADOW OF TWILIGHT")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        # Player state
        self.player = {
            "name": "Protagonist",
            "level": 1,
            "hp": 100, "max_hp": 100,
            "sp": 60,  "max_sp": 60,
            "atk": 15, "def": 10,
            "exp": 0,  "next_exp": 100,
            "skills": SKILLS.copy(),
            "guarding": False,
        }

        # Calendar
        self.month_idx = 0
        self.day = 1
        self.time_of_day = "Afternoon"  # Afternoon / Evening / Night
        self.actions_left = 2

        # Dungeon
        self.dungeon_floor = 1
        self.dungeon_max = 10
        self.in_battle = False

        # Current state
        self.state = "main_menu"  # main_menu, calendar, social, dungeon, battle, game_over, victory

        # Battle vars
        self.battle_enemy = None
        self.battle_log = []
        self.selected_skill = 0
        self.player_turn = True
        self.battle_result = None

        self.build_ui()
        self.show_main_menu()

    # ───────── UI BUILD ─────────

    def build_ui(self):
        self.W, self.H = 900, 620

        self.canvas = tk.Canvas(
            self.root, width=self.W, height=self.H,
            bg=COLORS["bg"], highlightthickness=0
        )
        self.canvas.pack()

        # Fonts
        self.f_title  = tkfont.Font(family="Courier New", size=28, weight="bold")
        self.f_head   = tkfont.Font(family="Courier New", size=14, weight="bold")
        self.f_body   = tkfont.Font(family="Courier New", size=11)
        self.f_small  = tkfont.Font(family="Courier New", size=9)
        self.f_big    = tkfont.Font(family="Courier New", size=18, weight="bold")

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)

        self.buttons = []  # list of (x1,y1,x2,y2,callback,tag)
        self.anim_frame = 0
        self.animate()

    def animate(self):
        self.anim_frame += 1
        if self.state in ("main_menu",):
            self.draw_main_menu_anim()
        self.root.after(50, self.animate)

    # ───────── HELPERS ─────────

    def clear(self):
        self.canvas.delete("all")
        self.buttons.clear()

    def draw_panel(self, x1, y1, x2, y2, fill=None, outline=None, radius=8):
        f = fill or COLORS["panel"]
        o = outline or COLORS["border"]
        # Rounded rect via polygon approximation
        r = radius
        pts = [
            x1+r,y1, x2-r,y1,
            x2,y1+r, x2,y2-r,
            x2-r,y2, x1+r,y2,
            x1,y2-r, x1,y1+r
        ]
        self.canvas.create_polygon(pts, fill=f, outline=o, smooth=True, width=2)

    def draw_bar(self, x, y, w, h, val, max_val, color, bg="#1a1a30"):
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=bg, outline=COLORS["border"], width=1)
        ratio = max(0, min(1, val/max_val)) if max_val > 0 else 0
        if ratio > 0:
            self.canvas.create_rectangle(x+1, y+1, x+1+int((w-2)*ratio), y+h-1, fill=color, outline="")

    def draw_button(self, x1, y1, x2, y2, text, callback, fill=None, text_color=None, outline=None):
        f = fill or COLORS["panel2"]
        tc = text_color or COLORS["accent"]
        o = outline or COLORS["accent"]
        self.draw_panel(x1, y1, x2, y2, fill=f, outline=o)
        cx = (x1+x2)//2
        cy = (y1+y2)//2
        self.canvas.create_text(cx, cy, text=text, fill=tc, font=self.f_body, anchor="center")
        self.buttons.append((x1, y1, x2, y2, callback, text))

    def on_click(self, e):
        for (x1,y1,x2,y2,cb,_) in self.buttons:
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                cb()
                return

    def on_key(self, e):
        if self.state == "battle":
            if e.keysym == "Up":
                self.selected_skill = (self.selected_skill - 1) % len(self.player["skills"])
                self.show_battle()
            elif e.keysym == "Down":
                self.selected_skill = (self.selected_skill + 1) % len(self.player["skills"])
                self.show_battle()
            elif e.keysym == "Return" or e.keysym == "space":
                if self.player_turn and not self.battle_result:
                    self.player_act(self.player["skills"][self.selected_skill])

    # ───────── MAIN MENU ─────────

    def show_main_menu(self):
        self.state = "main_menu"
        self.clear()
        self.draw_main_menu_anim()

        # Title
        self.canvas.create_text(450, 120, text="PERSONA", fill=COLORS["accent"],
                                 font=self.f_title, anchor="center")
        self.canvas.create_text(450, 158, text="S H A D O W   O F   T W I L I G H T",
                                 fill=COLORS["accent2"], font=self.f_body, anchor="center")

        # Divider
        self.canvas.create_line(200, 175, 700, 175, fill=COLORS["border"], width=1)

        # Buttons
        bw, bh = 260, 44
        bx = 450 - bw//2
        for i, (label, cb) in enumerate([
            ("▶  NEW JOURNEY",   self.start_game),
            ("📖  HOW TO PLAY",  self.show_help),
        ]):
            by = 220 + i * 65
            self.draw_button(bx, by, bx+bw, by+bh, label, cb,
                             fill=COLORS["panel"], outline=COLORS["accent"])

        self.canvas.create_text(450, 580, text="Use ARROW KEYS + ENTER in battle | Click elsewhere",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="center")

    def draw_main_menu_anim(self):
        # Draw animated background particles
        for i in range(20):
            x = (i * 47 + self.anim_frame * (i % 3 + 1)) % self.W
            y = (i * 31 + self.anim_frame * ((i+1) % 2 + 1)) % self.H
            r = 2 if i % 3 == 0 else 1
            color = COLORS["accent"] if i % 2 == 0 else COLORS["accent2"]
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")

    def show_help(self):
        self.clear()
        self.draw_panel(80, 60, 820, 560)
        self.canvas.create_text(450, 90, text="HOW TO PLAY", fill=COLORS["accent"], font=self.f_big)

        lines = [
            ("CALENDAR", "Each day has 2 action slots: Afternoon & Evening."),
            ("",          "Spend them on Social Links or entering the Dungeon."),
            ("SOCIAL LINKS", "Spend time with characters to rank up your bonds."),
            ("",             "Higher rank = stronger Personas in battle!"),
            ("DUNGEON",   "Explore Tartarus floors. Each floor has a battle."),
            ("",          "Reach floor 10 to face the Boss!"),
            ("BATTLE",   "Turn-based combat. Select skills with ↑↓ keys."),
            ("",          "Press ENTER or SPACE to use a skill."),
            ("",          "Every element has a weakness — exploit them for 1.5x!"),
            ("LEVELING",  "Defeat enemies to gain EXP and level up."),
            ("",          "Max HP/SP and stats increase each level."),
        ]
        y = 135
        for title, desc in lines:
            if title:
                self.canvas.create_text(160, y, text=title, fill=COLORS["gold"],
                                         font=self.f_head, anchor="w")
            if desc:
                self.canvas.create_text(160, y+18, text=desc, fill=COLORS["text"],
                                         font=self.f_small, anchor="w")
                y += 40
            else:
                y += 18

        self.draw_button(340, 510, 560, 548, "← BACK", self.show_main_menu)

    def start_game(self):
        self.show_calendar()

    # ───────── CALENDAR ─────────

    def show_calendar(self):
        self.state = "calendar"
        self.clear()

        # Header
        self.draw_panel(0, 0, self.W, 60, fill=COLORS["panel"], outline=COLORS["border"])
        month_str = MONTHS[self.month_idx]
        self.canvas.create_text(450, 30, text=f"✦  {month_str} {self.day:02d}  —  {self.time_of_day}  ✦",
                                 fill=COLORS["accent"], font=self.f_head, anchor="center")

        # Player stats bar top-right
        p = self.player
        self.canvas.create_text(750, 15, text=f"Lv.{p['level']}  {p['name']}", fill=COLORS["gold"], font=self.f_small)
        self.draw_bar(620, 28, 200, 10, p["hp"], p["max_hp"], COLORS["hp_bar"])
        self.canvas.create_text(620, 25, text="HP", fill=COLORS["text_dim"], font=self.f_small, anchor="e")
        self.draw_bar(620, 44, 200, 10, p["sp"], p["max_sp"], COLORS["sp_bar"])
        self.canvas.create_text(620, 41, text="SP", fill=COLORS["text_dim"], font=self.f_small, anchor="e")

        # Actions remaining
        self.canvas.create_text(30, 80, text=f"Actions: {'●' * self.actions_left}{'○' * (2-self.actions_left)}",
                                 fill=COLORS["accent2"], font=self.f_body, anchor="w")

        # Calendar grid
        self.draw_calendar_grid()

        # Action buttons
        self.canvas.create_text(450, 390, text="── CHOOSE YOUR ACTION ──",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="center")

        actions = [
            ("🏰  ENTER DUNGEON",    self.enter_dungeon,  "#1a0030", COLORS["accent2"]),
            ("💬  SOCIAL LINKS",     self.show_social,    "#001a30", COLORS["accent"]),
            ("😴  REST (restore SP)", self.do_rest,       "#0a1a0a", COLORS["hp_bar"]),
        ]
        bw = 220
        gap = 20
        total = len(actions) * bw + (len(actions)-1) * gap
        sx = (self.W - total) // 2
        for i, (label, cb, fill, out) in enumerate(actions):
            bx = sx + i * (bw + gap)
            enabled = self.actions_left > 0
            alpha_fill = fill if enabled else COLORS["panel"]
            alpha_out  = out  if enabled else COLORS["border"]
            self.draw_button(bx, 410, bx+bw, 460, label, cb if enabled else lambda: None,
                             fill=alpha_fill, outline=alpha_out,
                             text_color=out if enabled else COLORS["text_dim"])

        if self.actions_left == 0:
            self.draw_button(340, 480, 560, 518, "▶ ADVANCE TO NEXT PERIOD", self.advance_time,
                             fill="#1a1000", outline=COLORS["gold"], text_color=COLORS["gold"])

        # Dungeon status
        self.draw_panel(50, 530, 450, 600, fill=COLORS["panel2"])
        self.canvas.create_text(60, 545, text="TARTARUS STATUS", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.canvas.create_text(60, 565, text=f"Current Floor: {self.dungeon_floor} / {self.dungeon_max}",
                                 fill=COLORS["accent"], font=self.f_body, anchor="w")
        self.draw_bar(60, 580, 370, 10, self.dungeon_floor, self.dungeon_max, COLORS["accent2"])

        # Social link summary
        self.draw_panel(460, 530, 850, 600, fill=COLORS["panel2"])
        self.canvas.create_text(470, 545, text="SOCIAL LINKS", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        for i, sl in enumerate(SOCIAL_LINKS[:4]):
            x = 470 + i * 96
            self.canvas.create_text(x, 562, text=sl["name"].split()[0], fill=sl["color"], font=self.f_small, anchor="w")
            self.draw_bar(x, 572, 88, 6, sl["rank"]-1, sl["max"]-1, sl["color"])
            self.canvas.create_text(x, 582, text=f"Rank {sl['rank']}", fill=COLORS["text_dim"], font=self.f_small, anchor="w")

    def draw_calendar_grid(self):
        # Mini calendar showing month
        days_total = DAYS_IN_MONTH[self.month_idx]
        cols = 7
        cx_start, cy_start = 50, 100
        cell_w, cell_h = 38, 32

        # Day labels
        day_names = ["Mo","Tu","We","Th","Fr","Sa","Su"]
        for i, dn in enumerate(day_names):
            x = cx_start + i * cell_w + cell_w//2
            self.canvas.create_text(x, cy_start, text=dn,
                                     fill=COLORS["text_dim"], font=self.f_small, anchor="center")

        for d in range(1, days_total+1):
            col = (d-1) % cols
            row = (d-1) // cols
            x = cx_start + col * cell_w
            y = cy_start + 16 + row * cell_h
            is_current = (d == self.day)
            is_past    = (d < self.day)
            fill = COLORS["accent"] if is_current else (COLORS["panel2"] if is_past else COLORS["panel"])
            out  = COLORS["accent"] if is_current else COLORS["border"]
            tc   = COLORS["bg"]     if is_current else (COLORS["text_dim"] if is_past else COLORS["text"])
            self.canvas.create_rectangle(x+1, y+1, x+cell_w-2, y+cell_h-2,
                                          fill=fill, outline=out, width=1 if not is_current else 2)
            self.canvas.create_text(x+cell_w//2, y+cell_h//2, text=str(d),
                                     fill=tc, font=self.f_small, anchor="center")

        # Side info
        self.draw_panel(330, 90, 580, 360, fill=COLORS["panel2"])
        self.canvas.create_text(345, 108, text="SCHEDULE", fill=COLORS["accent"], font=self.f_head, anchor="w")
        self.canvas.create_text(345, 135, text=f"Month : {MONTHS[self.month_idx]}",
                                 fill=COLORS["text"], font=self.f_body, anchor="w")
        self.canvas.create_text(345, 158, text=f"Day   : {self.day}",
                                 fill=COLORS["text"], font=self.f_body, anchor="w")
        self.canvas.create_text(345, 181, text=f"Period: {self.time_of_day}",
                                 fill=COLORS["gold"], font=self.f_body, anchor="w")

        # EXP bar
        p = self.player
        self.canvas.create_text(345, 215, text=f"── PROTAGONIST Lv.{p['level']} ──",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(345, 232, 215, 10, p["exp"], p["next_exp"], COLORS["exp_bar"])
        self.canvas.create_text(345, 248, text=f"EXP: {p['exp']} / {p['next_exp']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(345, 265, 215, 10, p["hp"], p["max_hp"], COLORS["hp_bar"])
        self.canvas.create_text(345, 281, text=f"HP: {p['hp']} / {p['max_hp']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(345, 298, 215, 10, p["sp"], p["max_sp"], COLORS["sp_bar"])
        self.canvas.create_text(345, 314, text=f"SP: {p['sp']} / {p['max_sp']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        self.canvas.create_text(345, 338, text=f"ATK: {p['atk']}  DEF: {p['def']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        # Upcoming days hint
        self.draw_panel(595, 90, 870, 360, fill=COLORS["panel2"])
        self.canvas.create_text(610, 108, text="ACTIVITY LOG", fill=COLORS["accent2"], font=self.f_head, anchor="w")
        log_items = [
            f"Day {max(1,self.day-2)}: Explored Tartarus",
            f"Day {max(1,self.day-1)}: Spent time with friends",
            f"Day {self.day}: {self.time_of_day} — Free",
            "─────────────────",
            "REMINDER:",
            "Full moon approaches...",
            "Prepare for battle!",
        ]
        for i, item in enumerate(log_items):
            color = COLORS["text_dim"] if i < 3 else (COLORS["accent2"] if i > 3 else COLORS["border"])
            self.canvas.create_text(610, 135 + i*28, text=item, fill=color, font=self.f_small, anchor="w")

    def advance_time(self):
        times = ["Afternoon", "Evening", "Night"]
        idx = times.index(self.time_of_day)
        if idx < len(times) - 1:
            self.time_of_day = times[idx+1]
            self.actions_left = 2
        else:
            # Next day
            self.time_of_day = "Afternoon"
            self.actions_left = 2
            self.day += 1
            days_total = DAYS_IN_MONTH[self.month_idx]
            if self.day > days_total:
                self.day = 1
                self.month_idx = (self.month_idx + 1) % 12
        self.show_calendar()

    def use_action(self):
        self.actions_left -= 1
        self.show_calendar()

    def do_rest(self):
        p = self.player
        old_sp = p["sp"]
        p["sp"] = min(p["max_sp"], p["sp"] + 30)
        p["hp"] = min(p["max_hp"], p["hp"] + 20)
        restored_sp = p["sp"] - old_sp
        self.actions_left -= 1
        self.show_message(f"You rested...\n\nHP restored: +20\nSP restored: +{restored_sp}",
                          COLORS["hp_bar"], self.show_calendar)

    def show_message(self, msg, color, callback):
        self.clear()
        self.draw_panel(250, 200, 650, 420)
        self.canvas.create_text(450, 290, text=msg, fill=color,
                                 font=self.f_body, anchor="center", justify="center")
        self.draw_button(340, 370, 560, 408, "CONTINUE", callback)

    # ───────── SOCIAL LINKS ─────────

    def show_social(self):
        self.state = "social"
        self.clear()

        self.draw_panel(0, 0, self.W, 60, fill=COLORS["panel"], outline=COLORS["border"])
        self.canvas.create_text(450, 30, text="✦  SOCIAL LINKS  ✦",
                                 fill=COLORS["accent"], font=self.f_head, anchor="center")

        self.canvas.create_text(450, 80, text="Choose someone to spend time with:",
                                 fill=COLORS["text_dim"], font=self.f_body, anchor="center")

        for i, sl in enumerate(SOCIAL_LINKS):
            row = i // 2
            col = i % 2
            px = 60 + col * 420
            py = 110 + row * 200
            self.draw_social_card(px, py, sl, i)

        self.draw_button(340, 560, 560, 598, "← BACK", self.show_calendar)

    def draw_social_card(self, x, y, sl, idx):
        w, h = 380, 170
        self.draw_panel(x, y, x+w, y+h, fill=COLORS["panel2"], outline=sl["color"])

        # Arcana symbol
        self.canvas.create_text(x+20, y+20, text="✦", fill=sl["color"], font=self.f_big, anchor="w")
        self.canvas.create_text(x+50, y+18, text=sl["arcana"], fill=sl["color"], font=self.f_head, anchor="w")
        self.canvas.create_text(x+50, y+36, text=sl["name"], fill=COLORS["text"], font=self.f_body, anchor="w")

        # Rank progress
        self.canvas.create_text(x+20, y+65, text=f"RANK  {sl['rank']} / {sl['max']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        # Rank dots
        for r in range(sl["max"]):
            dot_x = x+20 + r*24
            dot_y = y+80
            filled = r < sl["rank"]
            self.canvas.create_oval(dot_x, dot_y, dot_x+16, dot_y+16,
                                     fill=sl["color"] if filled else COLORS["panel"],
                                     outline=sl["color"], width=1)
        # EXP bar
        exp_needed = sl["rank"] * 10
        self.draw_bar(x+20, y+105, w-40, 8, sl["exp"], exp_needed, sl["color"])
        self.canvas.create_text(x+20, y+120, text=f"Bond EXP: {sl['exp']} / {exp_needed}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        if sl["rank"] < sl["max"]:
            self.draw_button(x+20, y+135, x+w-20, y+160,
                             f"Spend time with {sl['name'].split()[0]}",
                             lambda s=sl: self.hangout(s),
                             fill=COLORS["panel"], outline=sl["color"],
                             text_color=sl["color"])
        else:
            self.canvas.create_text(x+w//2, y+148, text="★ MAX RANK ★",
                                     fill=COLORS["gold"], font=self.f_body, anchor="center")

    def hangout(self, sl):
        gain = random.randint(15, 30)
        sl["exp"] += gain
        exp_needed = sl["rank"] * 10
        leveled = False
        while sl["exp"] >= exp_needed and sl["rank"] < sl["max"]:
            sl["exp"] -= exp_needed
            sl["rank"] += 1
            exp_needed = sl["rank"] * 10
            leveled = True
        self.actions_left -= 1
        msg = f"You spent time with {sl['name']}.\n\nBond EXP +{gain}!"
        if leveled:
            msg += f"\n\n✦ SOCIAL LINK RANK UP! ✦\n{sl['arcana']} → Rank {sl['rank']}"
            # Reward player
            self.player["max_sp"] += 5
            self.player["sp"] = min(self.player["max_sp"], self.player["sp"] + 5)
            msg += f"\nMax SP increased!"
        self.show_message(msg, sl["color"], self.show_calendar)

    # ───────── DUNGEON ─────────

    def enter_dungeon(self):
        self.state = "dungeon"
        self.clear()

        self.draw_panel(0, 0, self.W, 60, fill=COLORS["panel"], outline=COLORS["border"])
        self.canvas.create_text(450, 30, text="✦  TARTARUS  ✦",
                                 fill=COLORS["accent2"], font=self.f_head, anchor="center")

        # Dungeon map visualization
        self.draw_dungeon_map()

        # Info panel
        self.draw_panel(580, 80, 870, 400, fill=COLORS["panel2"])
        self.canvas.create_text(595, 100, text="FLOOR STATUS", fill=COLORS["accent2"], font=self.f_head, anchor="w")
        self.canvas.create_text(595, 130, text=f"Current Floor: {self.dungeon_floor}",
                                 fill=COLORS["text"], font=self.f_body, anchor="w")
        self.canvas.create_text(595, 155, text=f"Max Floor: {self.dungeon_max}",
                                 fill=COLORS["text_dim"], font=self.f_body, anchor="w")
        self.draw_bar(595, 175, 255, 12, self.dungeon_floor, self.dungeon_max, COLORS["accent2"])

        # Player stats
        p = self.player
        self.canvas.create_text(595, 205, text=f"── {p['name']} Lv.{p['level']} ──",
                                 fill=COLORS["gold"], font=self.f_body, anchor="w")
        self.draw_bar(595, 225, 255, 10, p["hp"], p["max_hp"], COLORS["hp_bar"])
        self.canvas.create_text(595, 242, text=f"HP {p['hp']}/{p['max_hp']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(595, 258, 255, 10, p["sp"], p["max_sp"], COLORS["sp_bar"])
        self.canvas.create_text(595, 275, text=f"SP {p['sp']}/{p['max_sp']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        # Warnings
        if self.dungeon_floor >= self.dungeon_max:
            self.canvas.create_text(595, 310, text="⚠ BOSS FLOOR ⚠",
                                     fill=COLORS["accent2"], font=self.f_head, anchor="w")
            self.canvas.create_text(595, 335, text="Prepare for Nyx Shard!",
                                     fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        # Buttons
        self.draw_button(595, 360, 865, 395, "⚔  EXPLORE THIS FLOOR", self.start_battle,
                         fill="#200010", outline=COLORS["accent2"], text_color=COLORS["accent2"])

        self.draw_button(50, 430, 310, 468, "← BACK TO CALENDAR",
                         lambda: (setattr(self, 'state', 'calendar'), self.show_calendar()),
                         fill=COLORS["panel2"], outline=COLORS["border"])

        if self.dungeon_floor > 1:
            self.draw_button(340, 430, 560, 468, "↓ RETREAT ONE FLOOR",
                             self.retreat_floor)

        # Spoils log
        self.draw_panel(50, 490, 560, 590, fill=COLORS["panel2"])
        self.canvas.create_text(65, 508, text="TARTARUS INTEL", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        enemies_here = self.get_floor_enemy()
        self.canvas.create_text(65, 528, text=f"Enemy: {enemies_here['name']}",
                                 fill=enemies_here["color"], font=self.f_body, anchor="w")
        self.canvas.create_text(65, 550, text=f"Weakness: {enemies_here['weak'].upper()}",
                                 fill=COLORS["gold"], font=self.f_small, anchor="w")
        self.canvas.create_text(65, 568, text=f"Danger Level: {'★' * min(5, (self.dungeon_floor//2)+1)}",
                                 fill=COLORS["accent2"], font=self.f_small, anchor="w")

    def draw_dungeon_map(self):
        # Visual floor map
        self.draw_panel(30, 80, 565, 410, fill="#0a0010", outline=COLORS["accent2"])
        self.canvas.create_text(297, 100, text="TARTARUS TOWER", fill=COLORS["accent2"],
                                 font=self.f_small, anchor="center")

        floors_visible = 10
        floor_h = 28
        for i in range(floors_visible, 0, -1):
            floor_num = i
            fy = 115 + (floors_visible - i) * floor_h
            fx1, fx2 = 50, 545
            is_current = (floor_num == self.dungeon_floor)
            is_past    = (floor_num < self.dungeon_floor)
            is_boss    = (floor_num == self.dungeon_max)

            fill = COLORS["accent2"]   if is_current else (
                   "#200010"            if is_boss and not is_past else (
                   "#0f0020"            if is_past else "#050010"))
            out  = COLORS["accent2"]  if is_current else (
                   COLORS["accent2"]   if is_boss else COLORS["border"])

            self.canvas.create_rectangle(fx1, fy, fx2, fy+floor_h-2,
                                          fill=fill, outline=out, width=2 if is_current else 1)

            label = f"B{floor_num}F"
            if is_boss:   label += "  ◆ BOSS"
            if is_current: label += "  ← YOU ARE HERE"
            if is_past:    label += "  ✓"

            tc = COLORS["white"] if is_current else (
                 COLORS["accent2"] if is_boss else (
                 COLORS["text_dim"] if is_past else COLORS["text_dim"]))
            self.canvas.create_text(fx1+10, fy+floor_h//2, text=label,
                                     fill=tc, font=self.f_small, anchor="w")

    def get_floor_enemy(self):
        idx = min(self.dungeon_floor - 1, len(ENEMIES) - 1)
        if self.dungeon_floor >= self.dungeon_max:
            return ENEMIES[-1]  # Boss
        return ENEMIES[idx % (len(ENEMIES)-1)]

    def retreat_floor(self):
        self.dungeon_floor = max(1, self.dungeon_floor - 1)
        self.enter_dungeon()

    def start_battle(self):
        enemy_template = self.get_floor_enemy()
        self.battle_enemy = {
            "name":    enemy_template["name"],
            "hp":      enemy_template["hp"],
            "max_hp":  enemy_template["hp"],
            "atk":     enemy_template["atk"],
            "def":     enemy_template["def"],
            "weak":    enemy_template["weak"],
            "color":   enemy_template["color"],
        }
        self.player["guarding"] = False
        self.selected_skill = 0
        self.player_turn = True
        self.battle_result = None
        self.battle_log = [f"A {self.battle_enemy['name']} appeared!", "Choose your action!"]
        self.show_battle()

    # ───────── BATTLE ─────────

    def show_battle(self):
        self.state = "battle"
        self.clear()

        e = self.battle_enemy
        p = self.player

        # BG
        self.canvas.create_rectangle(0, 0, self.W, self.H, fill="#05000f", outline="")

        # Scanlines effect
        for yy in range(0, self.H, 4):
            self.canvas.create_line(0, yy, self.W, yy, fill="#ffffff", stipple="gray12")

        # ── ENEMY SIDE ──
        self.draw_panel(80, 30, 520, 260, fill="#0a0020", outline=e["color"])
        # Enemy "sprite" (geometric shape)
        ex, ey = 300, 145
        self.draw_enemy_sprite(ex, ey, e)
        self.canvas.create_text(ex, 35, text=e["name"], fill=e["color"], font=self.f_head, anchor="center")
        self.canvas.create_text(ex, 55, text=f"Weak: {e['weak'].upper()}", fill=COLORS["gold"], font=self.f_small, anchor="center")
        # Enemy HP bar
        self.canvas.create_text(100, 225, text="HP", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(120, 220, 370, 18, e["hp"], e["max_hp"], COLORS["enemy_bar"])
        self.canvas.create_text(495, 225, text=f"{e['hp']}/{e['max_hp']}", fill=COLORS["text_dim"], font=self.f_small, anchor="e")

        # ── PLAYER SIDE ──
        self.draw_panel(560, 30, 870, 260, fill="#000a20", outline=COLORS["accent"])
        self.canvas.create_text(715, 45, text=f"{p['name']}  Lv.{p['level']}",
                                 fill=COLORS["accent"], font=self.f_head, anchor="center")
        # HP
        self.canvas.create_text(580, 80, text="HP", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(600, 75, 250, 14, p["hp"], p["max_hp"], COLORS["hp_bar"])
        self.canvas.create_text(855, 80, text=f"{p['hp']}/{p['max_hp']}", fill=COLORS["hp_bar"], font=self.f_small, anchor="e")
        # SP
        self.canvas.create_text(580, 102, text="SP", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(600, 97, 250, 14, p["sp"], p["max_sp"], COLORS["sp_bar"])
        self.canvas.create_text(855, 102, text=f"{p['sp']}/{p['max_sp']}", fill=COLORS["sp_bar"], font=self.f_small, anchor="e")
        # EXP
        self.canvas.create_text(580, 124, text="EXP", fill=COLORS["text_dim"], font=self.f_small, anchor="w")
        self.draw_bar(600, 119, 250, 10, p["exp"], p["next_exp"], COLORS["exp_bar"])

        self.canvas.create_text(715, 148, text=f"ATK: {p['atk']}   DEF: {p['def']}",
                                 fill=COLORS["text_dim"], font=self.f_small, anchor="center")
        if p["guarding"]:
            self.canvas.create_text(715, 168, text="[ GUARDING ]", fill=COLORS["gold"], font=self.f_body, anchor="center")

        # Turn indicator
        turn_text = "YOUR TURN" if self.player_turn else "ENEMY TURN..."
        turn_color = COLORS["accent"] if self.player_turn else COLORS["accent2"]
        self.canvas.create_text(715, 210, text=turn_text, fill=turn_color, font=self.f_big, anchor="center")

        # ── SKILL MENU ──
        self.draw_panel(30, 270, 430, 590, fill=COLORS["panel"], outline=COLORS["border"])
        self.canvas.create_text(45, 288, text="SKILLS  (↑↓ + ENTER)", fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        for i, sk in enumerate(p["skills"]):
            sy = 305 + i * 38
            selected = (i == self.selected_skill)
            can_use = (sk["cost"] <= p["sp"] or sk["cost"] == 0)
            fill = COLORS["panel2"] if selected else COLORS["panel"]
            out  = COLORS["accent"] if selected else COLORS["border"]

            self.canvas.create_rectangle(45, sy, 415, sy+32, fill=fill, outline=out, width=2 if selected else 1)
            type_colors = {"fire":"#ff5722","ice":"#29b6f6","electric":"#ffee58",
                           "wind":"#66bb6a","light":"#fffde7","heal":"#00e676",
                           "physical":"#ef9a9a","defense":"#b0bec5"}
            tc = type_colors.get(sk["type"], COLORS["text"])
            self.canvas.create_text(55, sy+16, text=f"{'▶ ' if selected else '  '}{sk['name']}", fill=tc, font=self.f_body, anchor="w")
            self.canvas.create_text(300, sy+10, text=sk["type"].upper(), fill=tc, font=self.f_small, anchor="w")
            cost_color = COLORS["sp_bar"] if can_use else COLORS["accent2"]
            cost_text = f"SP:{sk['cost']}" if sk["cost"] > 0 else "Free"
            self.canvas.create_text(300, sy+24, text=cost_text, fill=cost_color, font=self.f_small, anchor="w")
            pwr_text = f"PWR:{sk['power']}" if sk["power"] > 0 else ""
            self.canvas.create_text(360, sy+16, text=pwr_text, fill=COLORS["text_dim"], font=self.f_small, anchor="w")

            if self.player_turn and not self.battle_result:
                self.draw_button(45, sy, 415, sy+32, "", lambda s=sk: self.player_act(s),
                                 fill="", outline="", text_color="")

        # ── BATTLE LOG ──
        self.draw_panel(440, 270, 870, 590, fill=COLORS["panel"], outline=COLORS["border"])
        self.canvas.create_text(455, 288, text="BATTLE LOG", fill=COLORS["text_dim"], font=self.f_small, anchor="w")

        log_to_show = self.battle_log[-10:]
        for i, line in enumerate(log_to_show):
            ly = 308 + i * 28
            color = COLORS["text"]
            if "WEAK" in line or "critical" in line.lower(): color = COLORS["gold"]
            if "damage" in line.lower() and p["name"] in line: color = COLORS["accent2"]
            if "KO" in line or "defeated" in line.lower(): color = COLORS["accent"]
            if "LEVEL UP" in line: color = COLORS["gold"]
            self.canvas.create_text(455, ly, text=line, fill=color, font=self.f_small, anchor="w")

        # Battle result overlay
        if self.battle_result:
            self.draw_battle_result()

    def draw_enemy_sprite(self, cx, cy, e):
        # Geometric enemy sprite
        color = e["color"]
        n = e["name"]
        if "Slime" in n:
            self.canvas.create_oval(cx-40, cy-30, cx+40, cy+30, fill=color, outline=COLORS["white"], width=2)
            self.canvas.create_oval(cx-15, cy-15, cx+15, cy+15, fill="#000", outline="")
        elif "Iron" in n:
            pts = [cx, cy-50, cx+40, cy+30, cx-40, cy+30]
            self.canvas.create_polygon(pts, fill=color, outline=COLORS["white"], width=2)
        elif "Flame" in n or "Frost" in n:
            self.canvas.create_rectangle(cx-35, cy-45, cx+35, cy+35, fill=color, outline=COLORS["white"], width=2)
            self.canvas.create_oval(cx-20, cy-60, cx+20, cy-20, fill=color, outline=COLORS["white"], width=2)
        elif "BOSS" in n:
            pts = [cx, cy-60, cx+50, cy-20, cx+35, cy+45, cx-35, cy+45, cx-50, cy-20]
            self.canvas.create_polygon(pts, fill=color, outline=COLORS["white"], width=3)
            self.canvas.create_text(cx, cy, text="NYX", fill=COLORS["white"], font=self.f_head, anchor="center")
        else:
            self.canvas.create_oval(cx-35, cy-45, cx+35, cy+35, fill=color, outline=COLORS["white"], width=2)
        # Eyes
        self.canvas.create_oval(cx-12, cy-8, cx-4, cy+2, fill=COLORS["white"], outline="")
        self.canvas.create_oval(cx+4, cy-8, cx+12, cy+2, fill=COLORS["white"], outline="")

    def player_act(self, skill):
        if not self.player_turn or self.battle_result:
            return
        p = self.player
        e = self.battle_enemy

        if skill["cost"] > p["sp"]:
            self.battle_log.append(f"Not enough SP for {skill['name']}!")
            self.show_battle()
            return

        p["guarding"] = False
        p["sp"] = max(0, p["sp"] - skill["cost"])

        if skill["type"] == "heal":
            heal = skill["power"] + random.randint(-5, 5)
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            self.battle_log.append(f"Used {skill['name']}! Restored {heal} HP.")
        elif skill["type"] == "defense":
            p["guarding"] = True
            self.battle_log.append("You take a defensive stance!")
        else:
            # Calculate damage
            is_weak = (skill["type"] == e["weak"])
            base_dmg = skill["power"] + p["atk"] - e["def"] + random.randint(-3, 5)
            dmg = max(1, int(base_dmg * (1.5 if is_weak else 1.0)))
            e["hp"] = max(0, e["hp"] - dmg)
            log = f"{skill['name']}! {dmg} damage"
            if is_weak: log += "  ★ WEAK!"
            self.battle_log.append(log)

        if e["hp"] <= 0:
            self.end_battle(True)
            return

        self.player_turn = False
        self.show_battle()
        self.root.after(900, self.enemy_act)

    def enemy_act(self):
        if self.battle_result:
            return
        p = self.player
        e = self.battle_enemy

        atk = e["atk"] + random.randint(-3, 4)
        defense = p["def"] * (2 if p["guarding"] else 1)
        dmg = max(1, atk - defense)
        p["hp"] = max(0, p["hp"] - dmg)
        guard_txt = " (blocked!)" if p["guarding"] else ""
        self.battle_log.append(f"{e['name']} attacks! {dmg} damage{guard_txt}")
        p["guarding"] = False

        if p["hp"] <= 0:
            self.end_battle(False)
            return

        self.player_turn = True
        self.show_battle()

    def end_battle(self, player_won):
        self.battle_result = "win" if player_won else "lose"
        if player_won:
            exp_gain = 20 + self.dungeon_floor * 8
            self.grant_exp(exp_gain)
            self.battle_log.append(f"Victory! Gained {exp_gain} EXP!")
            # Restore some HP
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + 15)
        else:
            self.battle_log.append("You were defeated...")
        self.show_battle()

    def grant_exp(self, amount):
        p = self.player
        p["exp"] += amount
        while p["exp"] >= p["next_exp"]:
            p["exp"] -= p["next_exp"]
            p["level"] += 1
            p["next_exp"] = int(p["next_exp"] * 1.3)
            p["max_hp"] += 15
            p["max_sp"] += 8
            p["atk"] += 2
            p["def"] += 1
            p["hp"] = p["max_hp"]
            p["sp"] = p["max_sp"]
            self.battle_log.append(f"★ LEVEL UP! Now Lv.{p['level']} ★")

    def draw_battle_result(self):
        won = self.battle_result == "win"
        overlay_color = "#001000" if won else "#200000"
        self.canvas.create_rectangle(200, 200, 700, 440, fill=overlay_color, outline=COLORS["gold"], width=3)

        if won:
            self.canvas.create_text(450, 240, text="✦ VICTORY ✦",
                                     fill=COLORS["gold"], font=self.f_title, anchor="center")
            boss = self.battle_enemy["name"] == ENEMIES[-1]["name"]
            if boss:
                self.canvas.create_text(450, 290, text="The Nyx Shard has been defeated!\nTwilight fades from Tartarus...",
                                         fill=COLORS["text"], font=self.f_body, anchor="center", justify="center")
                self.draw_button(320, 360, 580, 398, "★ CREDITS / BACK TO MENU ★",
                                 self.show_main_menu, fill="#001010", outline=COLORS["gold"],
                                 text_color=COLORS["gold"])
            else:
                self.canvas.create_text(450, 290, text=f"Floor {self.dungeon_floor} cleared!",
                                         fill=COLORS["accent"], font=self.f_body, anchor="center")
                self.draw_button(280, 340, 500, 375, "▶ NEXT FLOOR",
                                 self.next_floor, fill="#001000", outline=COLORS["hp_bar"],
                                 text_color=COLORS["hp_bar"])
                self.draw_button(510, 340, 700, 375, "← RETREAT",
                                 self.retreat_from_battle)
        else:
            self.canvas.create_text(450, 240, text="✦ DEFEATED ✦",
                                     fill=COLORS["accent2"], font=self.f_title, anchor="center")
            self.canvas.create_text(450, 295, text="You have fallen in Tartarus...\nBut the journey isn't over.",
                                     fill=COLORS["text"], font=self.f_body, anchor="center", justify="center")
            self.player["hp"] = self.player["max_hp"] // 2
            self.player["sp"] = self.player["max_sp"] // 2
            self.draw_button(320, 370, 580, 408, "↩ RETURN (HP/SP half restored)",
                             self.retreat_from_battle, fill="#200000", outline=COLORS["accent2"],
                             text_color=COLORS["accent2"])

    def next_floor(self):
        self.dungeon_floor = min(self.dungeon_max, self.dungeon_floor + 1)
        self.actions_left -= 1
        self.state = "dungeon"
        self.enter_dungeon()

    def retreat_from_battle(self):
        self.actions_left -= 1
        self.state = "calendar"
        self.show_calendar()

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    game = PersonaGame(root)
    root.mainloop()