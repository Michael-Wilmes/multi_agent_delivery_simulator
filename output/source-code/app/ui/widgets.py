from dataclasses import dataclass

import pygame


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    colour: tuple
    icon: pygame.Surface | None = None

    def draw(self, surface, font, hovered=False):
        if hovered:
            pygame.draw.rect(surface, (94, 116, 132), self.rect, 1, border_radius=7)
        label = font.render(self.text, True, (238, 243, 247))
        icon_width = self.icon.get_width() if self.icon else 0
        gap = 6 if self.icon else 0
        content_width = icon_width + gap + label.get_width()
        content_left = self.rect.centerx - content_width // 2
        if self.icon:
            icon_rect = self.icon.get_rect(midleft=(content_left, self.rect.centery))
            surface.blit(self.icon, icon_rect)
            content_left += icon_width + gap
        surface.blit(label, label.get_rect(midleft=(content_left, self.rect.centery)))

    def hit(self, p):
        return self.rect.collidepoint(p)
