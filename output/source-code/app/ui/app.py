import pygame

from app.domain.agent import AgentType
from app.domain.graph import NodeKind

from .widgets import Button

BG = (7, 18, 28)
PANEL = (11, 28, 40)
BORDER = (45, 69, 82)
ROAD = (49, 57, 63)
WALL = (5, 14, 21)
GRID = (91, 105, 113)
TEXT = (225, 235, 240)
MUTED = (151, 170, 180)
GREEN = (45, 150, 74)
YELLOW = (234, 164, 25)
BLUE = (47, 111, 195)
RED = (215, 67, 51)


class SimulatorApp:
    def __init__(self, engine, config):
        pygame.init()
        pygame.display.set_caption("Multi-Agent Delivery Simulator")
        self.screen = pygame.display.set_mode(
            (config.window.width, config.window.height),
            pygame.RESIZABLE,
        )
        self.clock = pygame.time.Clock()
        self.engine = engine
        self.config = config
        self.font = pygame.font.SysFont("segoeui", 16)
        self.small = pygame.font.SysFont("consolas", 13)
        self.title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.last_auto_tick = pygame.time.get_ticks()
        self.buttons = []

    def run(self):
        active = True
        while active:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    active = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.handle_click(e.pos)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    self.engine.step()

            now = pygame.time.get_ticks()
            if self.engine.running and now - self.last_auto_tick >= self.config.simulation.auto_tick_ms:
                self.engine.step()
                self.last_auto_tick = now

            self.draw(self.engine.snapshot())
            pygame.display.flip()
            self.clock.tick(self.config.window.fps)

        pygame.quit()

    def handle_click(self, p):
        for b, a in self.buttons:
            if b.hit(p):
                a()
                return

    def panel(self, r, title=None):
        pygame.draw.rect(self.screen, PANEL, r, border_radius=8)
        pygame.draw.rect(self.screen, BORDER, r, 1, border_radius=8)
        if title:
            self.screen.blit(self.title.render(title, True, TEXT), (r.x + 14, r.y + 9))

    def draw(self, s):
        self.screen.fill(BG)
        w, h = self.screen.get_size()
        m = 12
        gap = 12
        controls_h = 66
        log_h = 205
        upper_h = h - m * 4 - controls_h - log_h
        left_w = int(w * 0.56)
        right_x = m + left_w + gap
        right_w = w - right_x - m

        map_r = pygame.Rect(m, m, left_w, upper_h)
        right_r = pygame.Rect(right_x, m, right_w, upper_h)
        log_r = pygame.Rect(m, m + upper_h + gap, w - 2 * m, log_h)
        controls_r = pygame.Rect(m, h - controls_h - m, w - 2 * m, controls_h)

        self.panel(map_r)
        self.draw_map(s, map_r)
        self.draw_right(s, right_r)
        self.panel(log_r, "CONTRACT-NET LOG")
        self.draw_contract(s, log_r)
        self.panel(controls_r)
        self.draw_controls(controls_r)

    def draw_map(self, s, r):
        g = s.graph
        self.screen.blit(
            self.title.render(f"KARTE: {g.name} ({g.width}x{g.height})", True, TEXT),
            (r.x + 14, r.y + 9),
        )
        inner = r.inflate(-28, -58)
        inner.y += 16
        cell = max(7, min(inner.width // g.width, inner.height // g.height))
        ox = inner.x + (inner.width - cell * g.width) // 2
        oy = inner.y + (inner.height - cell * g.height) // 2
        agents = {a.position: a for a in s.agents}

        for y in range(g.height):
            for x in range(g.width):
                n = g.node_at((x, y))
                cr = pygame.Rect(ox + x * cell, oy + y * cell, cell, cell)
                pygame.draw.rect(self.screen, WALL if n.kind is NodeKind.WALL else ROAD, cr)
                pygame.draw.rect(self.screen, GRID, cr, 1)
                if n.kind is NodeKind.DEPOT:
                    self.marker(cr, "D", GREEN)
                elif n.kind is NodeKind.TARGET:
                    self.marker(cr, "Z", YELLOW)
                if (x, y) in agents:
                    a = agents[(x, y)]
                    pygame.draw.circle(
                        self.screen,
                        BLUE if a.type is AgentType.STANDARD else RED,
                        cr.center,
                        max(4, cell // 3),
                    )
                    if cell >= 20:
                        label = self.small.render(str(a.id), True, TEXT)
                        self.screen.blit(label, label.get_rect(center=cr.center))

    def marker(self, r, text, c):
        q = r.inflate(-max(3, r.width // 3), -max(3, r.height // 3))
        pygame.draw.rect(self.screen, c, q, border_radius=2)
        if r.width >= 20:
            lab = self.small.render(text, True, (8, 18, 24))
            self.screen.blit(lab, lab.get_rect(center=r.center))

    def draw_battery_bar(self, x, y, value, width=54, height=8):
        pct = max(0.0, min(1.0, value / 100.0))
        bg = pygame.Rect(x, y, width, height)
        fill = pygame.Rect(x, y, int(width * pct), height)
        pygame.draw.rect(self.screen, (32, 38, 46), bg, border_radius=4)
        color = GREEN if pct > 0.6 else YELLOW if pct > 0.25 else RED
        pygame.draw.rect(self.screen, color, fill, border_radius=4)

    def draw_right(self, s, r):
        gap = 12
        top_h = 125

        tasks_w = int(r.width * 0.67)
        sim = pygame.Rect(r.x, r.y, r.width - tasks_w - gap - 30, top_h)
        tasks = pygame.Rect(sim.right + gap, r.y, tasks_w + 30, top_h)
        messages = pygame.Rect(r.x, r.y + top_h + gap, r.width, 175)
        agents = pygame.Rect(r.x, messages.bottom + gap, r.width, r.bottom - messages.bottom - gap)

        self.panel(sim, "SIMULATION")
        self.panel(tasks, "AKTIVE AUFTRAEGE")
        self.panel(messages, "NACHRICHTEN (LETZTE 10)")
        self.panel(agents, "AGENTENSTATUS")

        self.screen.blit(self.font.render("Tick", True, MUTED), (sim.x + 15, sim.y + 43))
        self.screen.blit(self.title.render(str(s.tick), True, TEXT), (sim.x + 15, sim.y + 67))
        self.screen.blit(
            self.small.render("AUTO" if s.running else "PAUSE", True, GREEN if s.running else MUTED),
            (sim.x + 85, sim.y + 72),
        )
        y = tasks.y + 42

        for t in s.tasks[-3:]:
            self.screen.blit(
                self.small.render(f"T-{t.id:03d} {t.depot}->{t.destination} {t.status}", True, TEXT),
                (tasks.x + 14, y),
            )
            y += 22

        if not s.tasks:
            self.screen.blit(self.small.render("Noch keine Tasks", True, MUTED), (tasks.x + 14, y))

        y = messages.y + 40
        for msg in s.messages[-6:]:
            self.screen.blit(self.small.render(msg, True, MUTED), (messages.x + 14, y))
            y += 21

        id_x = agents.x + 14
        type_x = agents.x + 72
        pos_x = agents.x + 172
        status_x = agents.x + 255
        battery_x = agents.x + 350
        battery_text_x = battery_x + 62
        capacity_x = agents.x + 475
        load_x = agents.x + 530

        self.screen.blit(self.small.render("ID", True, TEXT), (id_x, agents.y + 39))
        self.screen.blit(self.small.render("Typ", True, TEXT), (type_x, agents.y + 39))
        self.screen.blit(self.small.render("Pos", True, TEXT), (pos_x, agents.y + 39))
        self.screen.blit(self.small.render("Status", True, TEXT), (status_x, agents.y + 39))
        self.screen.blit(self.small.render("Batterie", True, TEXT), (battery_x, agents.y + 39))
        self.screen.blit(self.small.render("Kap.", True, TEXT), (capacity_x, agents.y + 39))
        self.screen.blit(self.small.render("Ladung", True, TEXT), (load_x, agents.y + 39))

        y = agents.y + 64
        for a in s.agents[:8]:
            self.screen.blit(self.small.render(str(a.id), True, MUTED), (id_x, y))
            self.screen.blit(self.small.render(a.type.value, True, MUTED), (type_x, y))
            self.screen.blit(self.small.render(str(a.position), True, MUTED), (pos_x, y))
            self.screen.blit(self.small.render(a.status, True, MUTED), (status_x, y))

            if self.config.simulation.battery_enabled:
                self.draw_battery_bar(battery_x, y + 5, a.battery)
                self.screen.blit(self.small.render(f"{a.battery:.0f}%", True, MUTED), (battery_text_x, y))
            else:
                self.screen.blit(self.small.render("offen", True, MUTED), (battery_x, y))

            self.screen.blit(self.small.render(str(a.capacity), True, MUTED), (capacity_x, y))
            self.screen.blit(self.small.render(f"{a.load}/{a.capacity}", True, MUTED), (load_x, y))
            y += 21

    def draw_contract(self, s, r):
        x = r.x + 15
        y = r.y + 42
        self.screen.blit(
            self.small.render("Tick   Phase       Nachricht          Details", True, TEXT),
            (x, y),
        )
        y += 23

        rows = s.contract_log[-5:]
        if not rows:
            self.screen.blit(
                self.small.render(
                    "Noch keine Eintraege. Contract-Net wird in Aufgabe 2 implementiert.",
                    True,
                    MUTED,
                ),
                (x, y),
            )

        for tick, phase, msg, details in rows:
            self.screen.blit(
                self.small.render(f"{tick:<6} {phase:<11} {msg:<18} {details}", True, MUTED),
                (x, y),
            )
            y += 22

        bx = r.x + int(r.width * 0.56)
        by = r.y + 78
        # for text,c,w in [('ANNOUNCE',YELLOW,125),('BID',BLUE,105),('AWARD',GREEN,110)]:
        # q=pygame.Rect(bx,by,w,52);pygame.draw.rect(self.screen,(12,24,35),q,border_radius=7);pygame.draw.rect(self.screen,c,q,2,border_radius=7);lab=self.font.render(text,True,c);self.screen.blit(lab,lab.get_rect(center=q.center));bx=q.right+34
        # if text!='AWARD':pygame.draw.line(self.screen,TEXT,(q.right+5,q.centery),(q.right+27,q.centery),2);pygame.draw.polygon(self.screen,TEXT,[(q.right+27,q.centery),(q.right+20,q.centery-5),(q.right+20,q.centery+5)])

    def draw_controls(self, r):
        specs = [
            ("AUTO", 118, GREEN, self.engine.toggle_running),
            ("STEP", 118, BLUE, self.engine.step),
            ("RESET", 118, (45, 52, 58), self.engine.reset),
            ("AGENT", 135, (31, 76, 121), lambda: self.engine.add_agent(AgentType.STANDARD)),
            ("EXPRESS AGENT", 175, (116, 48, 42), lambda: self.engine.add_agent(AgentType.EXPRESS)),
            ("TASK", 120, (120, 88, 19), self.engine.add_task),
        ]
        x = r.x + 16
        y = r.y + 11
        self.buttons = []

        for label, w, c, a in specs:
            b = Button(pygame.Rect(x, y, w, 44), label, c)
            b.draw(self.screen, self.font)
            self.buttons.append((b, a))
            x += w + 12
