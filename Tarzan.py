
import pygame

class Tarzan():
    '''Для заставки'''

    def __init__(self, screen, ai_settings) -> None:
        '''Инициализирует параметры основные'''
        self.image = pygame.image.load('images/Tarzan.png')
        self.rect = self.image.get_rect()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.rect.center = self.screen_rect.center
        self.ai_settings = ai_settings
        self.direction = False

    def update_intro(self):
        '''Обновляет заставку'''
        self.screen.fill(self.ai_settings.bg_color)
        if not self.direction:
            if self.rect.centery != self.screen_rect.centery - 25:
                self.rect.centery -= 1
            else:
                self.direction = True
        else:
            if self.rect.centery != self.screen_rect.centery + 25:
                self.rect.centery += 1
            else:
                self.direction = False
            
        self.screen.blit(self.image, self.rect)
        pygame.display.flip()

    
