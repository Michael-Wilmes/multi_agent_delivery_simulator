from pathlib import Path

import pygame
from app.shared.constants import (
    AUTO, MANUAL, RESET, AGENT, EXPRESS_AGENT, TASK, QUIT, STRANDED, LOADING,
    OPEN, AWAIT_PICKUP, IN_TRANSIT, DELIVERED, NO_BID,
)
from app.domain.entities.agent import AgentType
from app.domain.entities.graph import NodeKind
from app.domain.entities.contractnetmessage import describe

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
        self.mode_label = "AUTO" if engine.running else "PAUSE"
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
        self.contract_scroll = 0
        self.contract_scroll_max = 0
        self.contract_scroll_drag_offset = 0
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
                elif e.type == pygame.MOUSEWHEEL:
                    log_rect = getattr(self, "contract_log_rect", None)
                    if log_rect and log_rect.collidepoint(pygame.mouse.get_pos()):
                        self.contract_scroll = max(
                            0,
                            min(
                                self.contract_scroll_max,
                                self.contract_scroll + e.y * 3,
                            ),
                        )
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
                self._run_button_action(b.text, a)
                return

    def _run_button_action(self, label, action):
        action()
        self.mode_label = (
            ("AUTO" if self.engine.running else "PAUSE")
            if label == "Auto"
            else label.upper()
        )

    def handle_scrollbar_click(self, p):
        for name in ("depot", "agent", "contract"):
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

    def set_contract_scroll_from_y(self, thumb_y):
        track = self.contract_scrollbar_rect
        thumb = self.contract_scrollbar_thumb
        travel = track.height - thumb.height
        if travel <= 0:
            self.contract_scroll = 0
            return
        fraction = max(0.0, min(1.0, (thumb_y - track.y) / travel))
        self.contract_scroll = round((1 - fraction) * self.contract_scroll_max)

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
        inner = r.inflate(-28, -28)
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
        gap = 10
        sim_h = 105
        agents_h = min(240, max(140, round((r.height - sim_h - gap * 2) * 0.35))) + 50

        sim = pygame.Rect(r.x, r.y, r.width, sim_h)
        agents = pygame.Rect(r.x, sim.bottom + gap, r.width, agents_h)
        depots = pygame.Rect(
            r.x,
            agents.bottom + gap,
            r.width,
            r.bottom - agents.bottom - gap,
        )
        self.agent_panel_rect = agents

        self.panel(sim)
        self.panel(agents, "AGENTENSTATUS")#    todo: use from a centralized place
        self.panel(depots, f"DEPOT-AUFTRAEGE ({len(s.graph.depots)})")

        simulation_summary = self.font.render(
            f"Karte: {s.graph.name} ({s.graph.width}x{s.graph.height})   "
            f"Tick: {s.tick}   Modus: {self.mode_label}",
            True,
            TEXT,
        )
        max_summary_width = sim.width - 28
        if simulation_summary.get_width() > max_summary_width:
            summary_height = max(
                1,
                round(
                    simulation_summary.get_height()
                    * max_summary_width
                    / simulation_summary.get_width()
                ),
            )
            simulation_summary = pygame.transform.smoothscale(
                simulation_summary,
                (max_summary_width, summary_height),
            )
        self.screen.blit(
            simulation_summary,
            simulation_summary.get_rect(center=sim.center),
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
        pickup_x = agents.x + round(650 * scale)

        self.screen.blit(self.small.render("ID", True, TEXT), (id_x, agents.y + 39))
        self.screen.blit(self.small.render("Typ", True, TEXT), (type_x, agents.y + 39))
        self.screen.blit(self.small.render("Pos", True, TEXT), (pos_x, agents.y + 39))
        self.screen.blit(self.small.render("Aktion", True, TEXT), (status_x, agents.y + 39))
        self.screen.blit(self.small.render("Batterie", True, TEXT), (battery_x, agents.y + 39))
        self.screen.blit(self.small.render("Kap.", True, TEXT), (capacity_x, agents.y + 39))
        self.screen.blit(self.small.render("Ladung", True, TEXT), (load_x, agents.y + 39))
        self.screen.blit(self.small.render("Abhol.", True, TEXT), (pickup_x, agents.y + 39))

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
            pickup_count = s.awaiting_pickup_counts.get(a.id, 0)
            self.screen.blit(self.small.render(str(pickup_count), True, agent_color), (pickup_x, y))
            y += 21

        self.draw_depot_tasks(s, depots)

    def draw_depot_tasks(self, s, panel):
        """Render one compact status-count row per depot."""
        tasks_by_depot = {depot.id: [] for depot in s.graph.depots}
        for task in s.tasks:
            tasks_by_depot.setdefault(task.depot.id, []).append(task)

        status_columns = (
            ((OPEN,), ("OPEN",), YELLOW),
            ((AWAIT_PICKUP,), ("AWAIT", "PICK-OFF"), BLUE),
            ((IN_TRANSIT,), ("IN", "TRANSIT"), BLUE),
            ((DELIVERED,), ("DELIVERED",), GREEN),
            ((NO_BID,), ("NO", "BID"), RED),
        )
        table_x = panel.x + 14
        table_width = panel.width - 38
        depot_column_width = min(190, max(110, round(table_width * 0.27)))
        status_column_width = (table_width - depot_column_width) / len(status_columns)
        header_y = panel.y + 39
        header_height = 38
        rows_y = header_y + header_height
        row_height = 28
        visible_height = max(0, panel.bottom - 8 - rows_y)
        total_height = (len(s.graph.depots) + 1) * row_height
        self.depot_scroll_max = max(0, total_height - visible_height)
        self.depot_scroll = min(self.depot_scroll, self.depot_scroll_max)

        clip = self.screen.get_clip()
        self.screen.set_clip(
            pygame.Rect(panel.x + 8, header_y, panel.width - 24, panel.bottom - header_y - 8)
        )

        depot_header = pygame.Rect(table_x, header_y, depot_column_width, header_height)
        pygame.draw.rect(self.screen, (16, 26, 30), depot_header)
        pygame.draw.rect(self.screen, BORDER, depot_header, 1)
        depot_label = self.small.render("DEPOT", True, TEXT)
        self.screen.blit(
            depot_label,
            depot_label.get_rect(midleft=(depot_header.x + 10, depot_header.centery)),
        )

        for column_index, (_, label_lines, color) in enumerate(status_columns):
            column_x = table_x + depot_column_width + round(column_index * status_column_width)
            next_column_x = table_x + depot_column_width + round((column_index + 1) * status_column_width)
            header = pygame.Rect(
                column_x,
                header_y,
                next_column_x - column_x,
                header_height,
            )
            pygame.draw.rect(self.screen, (16, 26, 30), header)
            pygame.draw.rect(self.screen, color, header, 1)
            line_height = self.small.get_linesize()
            first_line_y = header.centery - (len(label_lines) * line_height) // 2
            for line_index, label in enumerate(label_lines):
                label_surface = self.small.render(label, True, color)
                max_label_width = max(1, header.width - 8)
                if label_surface.get_width() > max_label_width:
                    scaled_height = max(
                        1,
                        round(label_surface.get_height() * max_label_width / label_surface.get_width()),
                    )
                    label_surface = pygame.transform.smoothscale(
                        label_surface,
                        (max_label_width, scaled_height),
                    )
                self.screen.blit(
                    label_surface,
                    label_surface.get_rect(
                        center=(header.centerx, first_line_y + line_index * line_height + line_height // 2)
                    ),
                )

        visible_rows = max(0, visible_height // row_height)
        visible_depots = s.graph.depots[
            self.depot_scroll // row_height:self.depot_scroll // row_height + visible_rows + 1
        ]
        for row_index, depot in enumerate(visible_depots):
            depot_y = rows_y + row_index * row_height - self.depot_scroll % row_height
            row_rect = pygame.Rect(table_x, depot_y, table_width, row_height)
            pygame.draw.rect(self.screen, (24, 45, 55), row_rect)
            pygame.draw.rect(self.screen, BORDER, row_rect, 1)
            depot_text = self.small.render(
                f"Depot {depot.id + 1}  {depot.position}",
                True,
                TEXT,
            )
            self.screen.blit(
                depot_text,
                depot_text.get_rect(midleft=(row_rect.x + 10, row_rect.centery)),
            )

            depot_tasks = tasks_by_depot[depot.id]
            for column_index, (statuses, _, color) in enumerate(status_columns):
                column_x = table_x + depot_column_width + round(column_index * status_column_width)
                next_column_x = table_x + depot_column_width + round((column_index + 1) * status_column_width)
                count = sum(task.status in statuses for task in depot_tasks)
                count_surface = self.small.render(str(count), True, color)
                self.screen.blit(
                    count_surface,
                    count_surface.get_rect(
                        center=((column_x + next_column_x) // 2, row_rect.centery)
                    ),
                )

        summary_y = rows_y + len(s.graph.depots) * row_height - self.depot_scroll
        summary_rect = pygame.Rect(table_x, summary_y, table_width, row_height)
        pygame.draw.rect(self.screen, (16, 26, 30), summary_rect)
        pygame.draw.line(
            self.screen,
            TEXT,
            (summary_rect.x, summary_rect.y),
            (summary_rect.right, summary_rect.y),
            2,
        )
        total_counts = [
            sum(task.status in statuses for task in s.tasks)
            for statuses, _, _ in status_columns
        ]
        total_label = self.small.render(f"TOTAL ({sum(total_counts)})", True, TEXT)
        self.screen.blit(
            total_label,
            total_label.get_rect(midleft=(summary_rect.x + 10, summary_rect.centery)),
        )
        for column_index, ((_, _, color), count) in enumerate(
            zip(status_columns, total_counts)
        ):
            column_x = table_x + depot_column_width + round(column_index * status_column_width)
            next_column_x = table_x + depot_column_width + round((column_index + 1) * status_column_width)
            count_surface = self.small.render(str(count), True, color)
            self.screen.blit(
                count_surface,
                count_surface.get_rect(
                    center=((column_x + next_column_x) // 2, summary_rect.centery)
                ),
            )

        self.screen.set_clip(clip)
        self.draw_depot_scrollbar(panel, total_height, visible_height, rows_y)

    def draw_depot_scrollbar(self, panel, content_height, visible_height, content_top):
        track_height = max(0, panel.bottom - 8 - content_top)
        self.depot_scrollbar_rect = pygame.Rect(panel.right - 16, content_top, 7, track_height)
        track = self.depot_scrollbar_rect
        pygame.draw.rect(self.screen, (32, 45, 53), track, border_radius=3)
        if content_height <= visible_height or visible_height <= 0 or track.height <= 0:
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
        self.contract_log_rect = r.copy()
        x = r.x + 15
        column_gap = self.small.size(" ")[0]
        tick_column_width = self.small.size("0" * 6)[0]
        phase_column_width = self.small.size("0" * 17)[0] + 50
        agent_column_width = self.small.size("0" * 18)[0]
        tick_x = x
        phase_x = tick_x + tick_column_width + column_gap
        agent_x = phase_x + phase_column_width + column_gap
        details_x = agent_x + agent_column_width + column_gap
        header_y = r.y + 42
        for label, column_x in (
            ("Tick", tick_x),
            ("Phase", phase_x),
            ("Agent", agent_x),
            ("Details", details_x),
        ):
            self.screen.blit(self.small.render(label, True, TEXT), (column_x, header_y))
        content_top = r.y + 65
        content_bottom = r.bottom - 8
        content_height = max(0, content_bottom - content_top)
        line_height = 22
        visible_rows = content_height // line_height
        self.contract_scroll_max = max(0, len(s.contract_log) - visible_rows)
        self.contract_scroll = min(self.contract_scroll, self.contract_scroll_max)
        row_end = len(s.contract_log) - self.contract_scroll
        row_start = max(0, row_end - visible_rows)
        rows = s.contract_log[row_start:row_end]

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(
            pygame.Rect(r.x + 8, content_top, r.width - 24, content_height)
        )
        y = content_top
        if not rows:
            self.screen.blit(
                self.small.render(
                    "Noch keine Contract-Net-Nachrichten.",
                    True,
                    MUTED,
                ),
                (x, y),
            )

        for message in rows:
            details = describe(message)
            phase = message.type.value
            phase_surface = self.small.render(phase, True, MUTED)
            if phase_surface.get_width() > phase_column_width:
                phase_surface = pygame.transform.smoothscale(
                    phase_surface,
                    (phase_column_width, phase_surface.get_height()),
                )
            agent_id = str(message.agent_id) if message.agent_id is not None else "-"
            self.screen.blit(
                self.small.render(str(message.tick), True, MUTED),
                (tick_x, y),
            )
            self.screen.blit(phase_surface, (phase_x, y))
            self.screen.blit(
                self.small.render(agent_id, True, MUTED),
                (agent_x, y),
            )
            self.screen.blit(self.small.render(details, True, MUTED), (details_x, y))
            y += 22

        self.screen.set_clip(previous_clip)
        self.draw_contract_scrollbar(r, len(s.contract_log), visible_rows)

    def draw_contract_scrollbar(self, panel, event_count, visible_rows):
        content_top = panel.y + 65
        content_height = max(0, panel.bottom - 8 - content_top)
        track = pygame.Rect(panel.right - 16, content_top, 7, content_height)
        self.contract_scrollbar_rect = track
        pygame.draw.rect(self.screen, (32, 45, 53), track, border_radius=3)
        if event_count <= visible_rows or visible_rows <= 0:
            self.contract_scrollbar_thumb = track.copy()
            return
        thumb_height = max(18, track.height * visible_rows // event_count)
        travel = track.height - thumb_height
        thumb_y = track.y + round(
            travel * (1 - self.contract_scroll / self.contract_scroll_max)
        )
        self.contract_scrollbar_thumb = pygame.Rect(
            track.x,
            thumb_y,
            track.width,
            thumb_height,
        )
        pygame.draw.rect(
            self.screen,
            MUTED,
            self.contract_scrollbar_thumb,
            border_radius=3,
        )
       
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
