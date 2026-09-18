from pathlib import Path

import pygame

from app.config import load_config
from app.simulation.engine import SimulationEngine
import app.ui.app


def show_startup_error(message):
    pygame.init()
    screen = pygame.display.set_mode((720, 180))
    pygame.display.set_caption("Multi-Agent Delivery Simulator")
    font = pygame.font.SysFont("segoeui", 20)
    clock = pygame.time.Clock()
    text = font.render(message, True, (225, 235, 240))
    text_rect = text.get_rect(center=screen.get_rect().center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                return
        screen.fill((7, 18, 28))
        pygame.draw.rect(screen, (45, 69, 82), screen.get_rect(), 2)
        screen.blit(text, text_rect)
        pygame.display.flip()
        clock.tick(30)


def main():
    root = Path(__file__).resolve().parent
    try:
        config = load_config(root / "config" / "app.json")
        engine = SimulationEngine(config)
    except ValueError as error:
        show_startup_error(str(error))
        return
    app.ui.app.SimulatorApp(engine, config).run()


if __name__ == "__main__":
    main()
