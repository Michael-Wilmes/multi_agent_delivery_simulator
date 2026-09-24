from pathlib import Path

import pygame
from app.shared.constants import (
    AUTO, MANUAL, RESET, AGENT, EXPRESS_AGENT, TASK, QUIT, STRANDED, LOADING,
    OPEN, AWAIT_PICKUP, IN_TRANSIT, DELIVERED, NO_BID,
)
from app.domain.entities.agent import AgentType
from app.domain.entities.graph import NodeKind

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
EXPRESS = (165, 86, 190)
DESTINATION = (220, 180, 40)


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
        self.agent_scroll = 0
        self.agent_scroll_dragging = False
        self.agent_scroll_drag_offset = 0
        self.depot_scroll = 0
        self.depot_scroll_dragging = False
        self.depot_scroll_drag_offset = 0
        self.active_scrollbar = None
        self.icons = self.load_icons()

    def load_icons(self):
        assets_dir = Path(__file__).resolve().parents[1] / "assets"
        icon_files = {
            "auto": "auto.svg",
            "step": "step.svg",
            "reset": "reset.svg",
            "agent": "add-agent.svg",
            "express": "express-agent.svg",
            "task": "add-task.svg",
            "end": "end.svg",
        }
        icons = {}
        for name, filename in icon_files.items():
            path = assets_dir / filename
            try:
                icon = pygame.image.load(path).convert_alpha()
                icons[name] = pygame.transform.smoothscale(icon, (20, 20))
            except (FileNotFoundError, pygame.error):
                icons[name] = None
        return icons

    def run(self):
        active = True
        while active:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    active = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if not self.handle_scrollbar_click(e.pos):
                        self.handle_click(e.pos)
                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    self.agent_scroll_dragging = False
                    self.depot_scroll_dragging = False
                    self.active_scrollbar = None
                elif e.type == pygame.MOUSEMOTION and self.active_scrollbar:
                    self.handle_scrollbar_drag(e.pos[1])
                elif e.type == pygame.KEYDOWN:
                    active = self.handle_key(e.key)
                    if not active:
                        break

            now = pygame.time.get_ticks()
            if self.engine.running and now - self.last_auto_tick >= self.config.simulation.auto_tick_ms:
                self.engine.step()
                self.last_auto_tick = now

            self.draw(self.engine.snapshot())
            pygame.display.flip()
            self.clock.tick(self.config.window.fps)

        pygame.quit()

    def handle_key(self, key):
        actions = {
            pygame.K_1: self.engine.toggle_running,
            pygame.K_2: self.engine.step,
            pygame.K_3: self.engine.reset,
            pygame.K_4: lambda: self.engine.add_agent(AgentType.STANDARD),
            pygame.K_5: lambda: self.engine.add_agent(AgentType.EXPRESS),
            pygame.K_6: self.engine.add_task,
            pygame.K_SPACE: self.engine.step,
        }
        if key == pygame.K_ESCAPE:
            return False
        action = actions.get(key)
        if action:
            action()
        return True

    def handle_click(self, p):
        for b, a in self.buttons:
            if b.hit(p):
                a()
                return

    def handle_scrollbar_click(self, p):
        for name in ("depot", "agent"):
            track = getattr(self, f"{name}_scrollbar_rect", None)
            if track is None or not track.collidepoint(p):
                continue
            thumb = getattr(self, f"{name}_scrollbar_thumb")
            if thumb.collidepoint(p):
                setattr(self, f"{name}_scroll_dragging", True)
                setattr(self, f"{name}_scroll_drag_offset", p[1] - thumb.y)
            else:
                getattr(self, f"set_{name}_scroll_from_y")(p[1] - thumb.height // 2)
            self.active_scrollbar = name
            return True
        return False

    def handle_scrollbar_drag(self, y):
        name = self.active_scrollbar
        if name:
            offset = getattr(self, f"{name}_scroll_drag_offset")
            getattr(self, f"set_{name}_scroll_from_y")(y - offset)

    def set_agent_scroll_from_y(self, thumb_y):
        track = self.agent_scrollbar_rect
        thumb = self.agent_scrollbar_thumb
        travel = track.height - thumb.height
        if travel <= 0:
            self.agent_scroll = 0
            return
        fraction = max(0.0, min(1.0, (thumb_y - track.y) / travel))
        self.agent_scroll = round(fraction * self.agent_scroll_max)

    def set_depot_scroll_from_y(self, thumb_y):
        track = self.depot_scrollbar_rect
        thumb = self.depot_scrollbar_thumb
        travel = track.height - thumb.height
        if travel <= 0:
            self.depot_scroll = 0
            return
        fraction = max(0.0, min(1.0, (thumb_y - track.y) / travel))
        self.depot_scroll = round(fraction * self.depot_scroll_max)

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
        upper_h = h - m * 3 - log_h
        left_w = int(w * 0.56)
        right_x = m + left_w + gap
        right_w = w - right_x - m

        map_r = pygame.Rect(m, m, left_w, upper_h)
        right_r = pygame.Rect(right_x, m, right_w, h - 2 * m)
        log_r = pygame.Rect(m, m + upper_h + gap, left_w, log_h)
        map_content = map_r.copy()
        map_content.height -= controls_h
        controls_r = pygame.Rect(
            map_r.x + 8,
            map_r.bottom - controls_h - 8,
            map_r.width - 16,
            controls_h,
        )

        self.panel(map_r)
        self.draw_map(s, map_content)
        self.draw_controls(controls_r)
        self.draw_right(s, right_r)
        self.panel(log_r, "CONTRACT-NET LOG")
        self.draw_contract(s, log_r)

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
                column_label = self.small.render(str(x), True, MUTED)
                row_label = self.small.render(str(y), True, MUTED)
                self.screen.blit(column_label, column_label.get_rect(center=(cr.centerx, oy - 9)))
                self.screen.blit(row_label, row_label.get_rect(midright=(ox - 7, cr.centery)))
                pygame.draw.rect(self.screen, WALL if n.kind is NodeKind.WALL else ROAD, cr)
                pygame.draw.rect(self.screen, GRID, cr, 1)
                if n.kind is NodeKind.DEPOT:
                    self.marker(cr, n.label or "D", GREEN)
                elif n.kind is NodeKind.TARGET:
                    self.marker(cr, n.label or "Z", DESTINATION)
                if (x, y) in agents:
                    a = agents[(x, y)]
                    stranded = a.status == STRANDED
                    radius = max(4, cell // 3)
                    pygame.draw.circle(
                        self.screen,
                        MUTED if stranded else (BLUE if a.type is AgentType.STANDARD else EXPRESS),
                        cr.center,
                        radius,
                    )
                    if cell >= 20:
                        label = self.small.render(str(a.id), True, TEXT)
                        self.screen.blit(label, label.get_rect(center=cr.center))
                    if stranded:
                        cx, cy = cr.center
                        offset = radius + 2
                        pygame.draw.line(self.screen, RED, (cx - offset, cy - offset), (cx + offset, cy + offset), 3)
                        pygame.draw.line(self.screen, RED, (cx - offset, cy + offset), (cx + offset, cy - offset), 3)

    def marker(self, r, text, c):
        pygame.draw.rect(self.screen, c, r)
        pygame.draw.rect(self.screen, GRID, r, 1)
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
        sim_w = 220

        agents_y = r.y + top_h + gap
        agents_h = min(220, max(150, (r.bottom - agents_y - gap) // 2))
        combined_h = top_h + gap + agents_h

        sim = pygame.Rect(r.x, r.y, sim_w, combined_h)
        agents = pygame.Rect(sim.right + gap, r.y, r.width - sim_w - gap, combined_h)
        depots = pygame.Rect(
            r.x,
            sim.bottom + gap,
            r.width,
            r.bottom - sim.bottom - gap,
        )
        self.agent_panel_rect = agents

        self.panel(sim, "SIMULATION") #todo: use from a centralized place
        self.panel(agents, "AGENTENSTATUS")#    todo: use from a centralized place
        self.panel(depots, f"DEPOT-AUFTRAEGE ({len(s.graph.depots)})")

        self.screen.blit(self.font.render("Tick", True, MUTED), (sim.x + 15, sim.y + 43))
        self.screen.blit(self.title.render(str(s.tick), True, TEXT), (sim.x + 15, sim.y + 67))
        self.screen.blit(
            self.small.render("AUTO" if s.running else "PAUSE", True, GREEN if s.running else MUTED), #todo: use from a centralized place
            (sim.x + 85, sim.y + 72),
        )
        # Spaltenabstaende skalieren mit der (jetzt schmaleren) Agentenspalte.
        scale = agents.width / 809
        id_x = agents.x + round(14 * scale)
        type_x = agents.x + round(72 * scale)
        pos_x = agents.x + round(172 * scale)
        status_x = agents.x + round(255 * scale)
        battery_x = agents.x + round(410 * scale)
        battery_text_x = battery_x + round(62 * scale)
        capacity_x = agents.x + round(535 * scale)
        load_x = agents.x + round(590 * scale)

        self.screen.blit(self.small.render("ID", True, TEXT), (id_x, agents.y + 39))
        self.screen.blit(self.small.render("Typ", True, TEXT), (type_x, agents.y + 39))
        self.screen.blit(self.small.render("Pos", True, TEXT), (pos_x, agents.y + 39))
        self.screen.blit(self.small.render("Aktion", True, TEXT), (status_x, agents.y + 39))
        self.screen.blit(self.small.render("Batterie", True, TEXT), (battery_x, agents.y + 39))
        self.screen.blit(self.small.render("Kap.", True, TEXT), (capacity_x, agents.y + 39))
        self.screen.blit(self.small.render("Ladung", True, TEXT), (load_x, agents.y + 39))

        visible_rows = max(0, (agents.bottom - 8 - (agents.y + 64)) // 21)
        max_scroll = max(0, len(s.agents) - visible_rows)
        self.agent_scroll = min(self.agent_scroll, max_scroll)
        self.agent_scroll_max = max_scroll
        self.draw_agent_scrollbar(agents, len(s.agents), visible_rows)
        y = agents.y + 64
        for a in s.agents[self.agent_scroll:self.agent_scroll + visible_rows]:
            agent_color = RED if a.status == STRANDED else MUTED
            self.screen.blit(self.small.render(str(a.id), True, agent_color), (id_x, y))
            self.screen.blit(self.small.render(a.type.value, True, agent_color), (type_x, y))
            self.screen.blit(self.small.render(str(a.position), True, agent_color), (pos_x, y))
            displayed_action = a.current_action
            self.screen.blit(self.small.render(displayed_action, True, agent_color), (status_x, y))

            if self.config.simulation.battery_enabled:
                self.draw_battery_bar(battery_x, y + 5, a.battery, width=round(54 * scale))
                self.screen.blit(self.small.render(f"{a.battery:.0f}%", True, agent_color), (battery_text_x, y))
            else:
                self.screen.blit(self.small.render("offen", True, agent_color), (battery_x, y))

            self.screen.blit(self.small.render(str(a.capacity), True, agent_color), (capacity_x, y))
            self.screen.blit(self.small.render(f"{a.load}/{a.capacity}", True, agent_color), (load_x, y))
            y += 21

        self.draw_depot_tasks(s, depots)

    def draw_depot_tasks(self, s, panel):
        """Renders depots as a fixed 2x10 grid so card size never depends on message volume."""
        tasks_by_depot = {depot.id: [] for depot in s.graph.depots}
        for task in s.tasks:
            tasks_by_depot.setdefault(task.depot.id, []).append(task)

        content_top = panel.y + 40
        content_bottom = panel.bottom - 8
        content_height = content_bottom - content_top
        gap = 10
        columns = 2
        card_height = 90  # feste Hoehe: Badges duerfen nie ausserhalb der Karte landen
        card_width = (panel.width - 28 - gap * (columns - 1)) // columns
        card_x = panel.x + 14

        total_rows = max(1, -(-len(s.graph.depots) // columns))
        total_height = total_rows * card_height + (total_rows - 1) * gap
        self.depot_scroll_max = max(0, total_height - content_height)
        self.depot_scroll = min(self.depot_scroll, self.depot_scroll_max)

        clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(panel.x + 8, content_top, panel.width - 24, content_height))

        badge_specs = (
            ((OPEN,), "OFFEN", YELLOW),
            ((AWAIT_PICKUP, IN_TRANSIT), "UNTERWEGS", BLUE),
            ((DELIVERED,), "GELIEFERT", GREEN),
            ((NO_BID,), "KEIN GEBOT", RED),
        )

        for depot_index, depot in enumerate(s.graph.depots):
            row = depot_index // columns
            column = depot_index % columns
            card_y = content_top - self.depot_scroll + row * (card_height + gap)
            x = card_x + column * (card_width + gap)
            depot_tasks = tasks_by_depot[depot.id]

            card = pygame.Rect(x, card_y, card_width, card_height)
            pygame.draw.rect(self.screen, (24, 45, 55), card, border_radius=5)
            pygame.draw.rect(self.screen, BORDER, card, 1, border_radius=5)
            self.screen.blit(
                self.small.render(
                    f"Depot {depot.id + 1} Start {depot.position}",
                    True,
                    TEXT,
                ),
                (card.x + 10, card.y + 9),
            )

            counts = [
                (label, sum(task.status in statuses for task in depot_tasks), color)
                for statuses, label, color in badge_specs
            ]
            badge_gap = 6
            badge_w = (card_width - 20 - badge_gap) // 2
            for badge_index, (label, count, color) in enumerate(counts):
                badge_col = badge_index % 2
                badge_row = badge_index // 2
                badge_x = card.x + 10 + badge_col * (badge_w + badge_gap)
                badge_y = card.y + 30 + badge_row * (22 + badge_gap)
                badge = pygame.Rect(badge_x, badge_y, badge_w, 22)
                pygame.draw.rect(self.screen, (16, 26, 30), badge, border_radius=11)
                pygame.draw.rect(self.screen, color, badge, 1, border_radius=11)
                label_surface = self.small.render(label, True, color)
                count_surface = self.small.render(str(count), True, color)
                self.screen.blit(label_surface, label_surface.get_rect(midleft=(badge.x + 10, badge.centery)))
                self.screen.blit(count_surface, count_surface.get_rect(midright=(badge.right - 10, badge.centery)))

        self.screen.set_clip(clip)
        self.draw_depot_scrollbar(panel, total_height, content_height)

    def draw_depot_scrollbar(self, panel, content_height, visible_height):
        self.depot_scrollbar_rect = pygame.Rect(panel.right - 16, panel.y + 40, 7, panel.height - 48)
        track = self.depot_scrollbar_rect
        pygame.draw.rect(self.screen, (32, 45, 53), track, border_radius=3)
        if content_height <= visible_height:
            self.depot_scrollbar_thumb = track.copy()
            return
        thumb_height = max(18, track.height * visible_height // content_height)
        travel = track.height - thumb_height
        thumb_y = track.y + travel * self.depot_scroll / self.depot_scroll_max
        self.depot_scrollbar_thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
        pygame.draw.rect(self.screen, MUTED, self.depot_scrollbar_thumb, border_radius=3)

    def draw_agent_scrollbar(self, panel, agent_count, visible_rows):
        self.agent_scrollbar_rect = pygame.Rect(panel.right - 16, panel.y + 60, 7, panel.height - 68)
        track = self.agent_scrollbar_rect
        pygame.draw.rect(self.screen, (32, 45, 53), track, border_radius=3)
        if agent_count <= visible_rows:
            self.agent_scrollbar_thumb = track.copy()
            return
        thumb_height = max(18, track.height * visible_rows // agent_count)
        travel = track.height - thumb_height
        thumb_y = track.y + travel * self.agent_scroll // self.agent_scroll_max
        self.agent_scrollbar_thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
        pygame.draw.rect(self.screen, MUTED, self.agent_scrollbar_thumb, border_radius=3)

    def draw_contract(self, s, r):
        x = r.x + 15
        y = r.y + 42
        self.screen.blit(
            self.small.render("Tick   Phase             Agent              Details", True, TEXT),
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

        for message in rows:
            if message.type.value == "ANNOUNCE":
                depot = f"Depot D{message.depot_id + 1} {message.depot}"
                destination = f"Ziel Z{message.destination_id + 1} {message.destination}"
                details = f"T-{message.task_id:03d}: {depot} -> {destination}"
                details += f" bis {message.deadline}"
            elif message.type.value == "BID":
                details = f"T-{message.task_id:03d} Agent {message.agent_id} Kosten {message.cost}"
            elif message.type.value == "AWARD":
                details = (
                    f"T-{message.task_id:03d} an Agent {message.agent_id}, "
                    f"Kosten {message.cost}"
                )
            elif message.type.value == "BID_LOST":
                details = f"T-{message.task_id:03d} verloren, Kosten {message.cost}"
            elif message.type.value == "NO_BID":
                details = f"T-{message.task_id:03d} ohne Gebot"
            elif message.type.value == "NO_BID_RESOURCES":
                distance = "unknown" if message.distance is None else f"{message.distance:.1f}"
                energy_range = (
                    "unlimited"
                    if message.energy_range is None
                    else f"{message.energy_range:.1f}"
                )
                details = (
                    f"T-{message.task_id:03d} Agent {message.agent_id}: "
                    f"Not reachable. Distance {distance}, "
                    f"Energy range {energy_range}."
                )
            self.screen.blit(
                self.small.render(
                    f"{message.tick:<6} {message.type.value:<17} {message.agent_id or '-':<18} {details}",
                    True,
                    MUTED,
                ),
                (x, y),
            )
            y += 22

        bx = r.x + int(r.width * 0.56)
        by = r.y + 78
       
    def draw_controls(self, r):
        specs = [
            ("Auto", 92, GREEN, "auto", self.engine.toggle_running),
            ("Schritt", 104, BLUE, "step", self.engine.step),
            ("Reset", 92, (45, 52, 58), "reset", self.engine.reset),
            ("Agent", 100, (31, 76, 121), "agent", lambda: self.engine.add_agent(AgentType.STANDARD)),
            ("Express", 118, EXPRESS, "express", lambda: self.engine.add_agent(AgentType.EXPRESS)),
            ("Task", 92, (120, 88, 19), "task", self.engine.add_task),
            ("Ende", 92, RED, "end", lambda: exit(0)),
        ]
        gap = 8
        row_width = sum(width for _, width, _, _, _ in specs) + gap * (len(specs) - 1)
        x = r.centerx - row_width // 2
        y = r.y + 11
        self.buttons = []
        mouse_position = pygame.mouse.get_pos()
        hovering_button = False

        for label, w, c, icon_name, action in specs:
            b = Button(pygame.Rect(x, y, w, 44), label, c, self.icons[icon_name])
            hovered = b.hit(mouse_position)
            hovering_button = hovering_button or hovered
            b.draw(self.screen, self.font, hovered)
            self.buttons.append((b, action))
            x += w + gap

        cursor = pygame.SYSTEM_CURSOR_HAND if hovering_button else pygame.SYSTEM_CURSOR_ARROW
        pygame.mouse.set_cursor(cursor)
