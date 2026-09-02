from dataclasses import dataclass

import pygame


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    colour: tuple

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.colour, self.rect, border_radius=7)
        pygame.draw.rect(surface, (94, 116, 132), self.rect, 1, border_radius=7)
        label = font.render(self.text, True, (238, 243, 247))
        surface.blit(label, label.get_rect(center=self.rect.center))

    def hit(self, p):
        return self.rect.collidepoint(p)
