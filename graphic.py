
import pygame
from MC import MainCharacter
from settings import Settings
from boss import Boss
from path_handling import load_image

def set_caption_and_icon():
    '''Устанавливает иконку и название игры'''
    icon = load_image('icon.png')
    pygame.display.set_caption('KvK')
    pygame.display.set_icon(icon)

def draw_health(mc: MainCharacter, ai_settings: Settings):
    '''Визуальное отображение здоровья главного персонажа'''
    # Рисуем полосу вверху для вывода здоровья
    stripe_width = 35 * (1 + 2 * ai_settings.mc_health)
    stripe = pygame.Surface((stripe_width, 55))
    stripe.fill((49, 4, 138))
    mc.mediator.blit_surface(stripe, (0,0))
    for i in range(mc.health):
        new_healthbar = load_image(f'K{mc.surname}_health.png')
        rect = new_healthbar.get_rect()
        rect.top = mc.mediator.get_value('screen_rect', 'top')
        rect.left = rect.width + i * 2 * rect.width
        mc.mediator.blit_surface(new_healthbar, rect)

def draw_invincibility(mc: MainCharacter):
    '''Визуальное отображение неуязвимости'''
    if mc.invincible:
        # Рисуем прямоугольник вверху для вывода значка неуязвимости
        stripe = pygame.Surface((55,55))
        stripe.fill((49, 4, 138))
        mc.mediator.blit_surface(
            stripe, (mc.mediator.get_value('screen_rect', 'width') - 105, 0))
        inv_bar = load_image(f'K{mc.surname}_invincibility.png')
        mc.mediator.blit_surface(
            inv_bar,(mc.mediator.get_value('screen_rect', 'width') - 100, 2))

class BossHealth:
    '''Здоровье босса'''

    def __init__(self, boss: Boss) -> None:
        self.bar_image = load_image('boss_health.png')
        self.rect = self.bar_image.get_rect()
        self.boss = boss
        self.mediator = boss.mediator
        self.rect.centerx = self.mediator.get_value('screen_rect', 'centerx')
        self.rect.bottom = self.mediator.get_value('screen_rect', 'bottom')
        self.boss_full_health = self.mediator.get_value('ai_settings', 'boss_health')

    def blitme(self):
        '''Отображение здоровья босса на экране'''
        # 461 - полная ширина полосы здоровья, 16 - ее высота
        health_to_draw = pygame.Surface((int(self.boss.health/self.boss_full_health * 461), 16))
        # светло-зеленый цвет
        health_to_draw.fill((22, 250, 45))
        # Полоса здоровья по середине отображающего элемента, за рамкой
        self.mediator.blit_surface(
            health_to_draw, (self.rect.left + 19, self.rect.top + 54))
        # Прорисовка рамки
        self.mediator.blit_surface(self.bar_image, self.rect)


