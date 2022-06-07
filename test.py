import pygame as pg
from MC import MainCharacter
from fist import Fist
from mediator import Mediator
import unittest
from settings import Settings

class Container(pg.sprite.Sprite):
    '''Контейнер-спрайт, который используется при тестировании посредника'''
    
    def __init__(self) -> None:
        self.rect = pg.Rect(0, 0, 50, 50)

    def update(self, *args, **kwargs) -> None:
        self.rect.centerx += 50
        self.rect.centery += 50




class TestMediator(unittest.TestCase):

    def test_rect_updating(self):
        sprite = Container()
        mediator = Mediator()
        mediator.add(sprite=sprite)
        sprite.update()
        mediator_sprite_rect: pg.Rect = mediator.get_value('sprite', 'rect')
        self.assertEqual(mediator_sprite_rect.centerx, sprite.rect.centerx)
        self.assertEqual(mediator_sprite_rect.centery, sprite.rect.centerx)
        self.assertIs(mediator_sprite_rect, sprite.rect)

    def test_mc_rect(self):
        
        screen = pg.Surface((500, 500))
        ai_settings = Settings()
        mediator = Mediator()
        mediator.add(screen=screen, ai_settings=ai_settings, 
            screen_rect = screen.get_rect())
        mc = MainCharacter(mediator, 'S')
        mediator.add(mc=mc)
        mc.rect.centerx += 50
        mc.rect.centery += 50
        mediator_mc_rect: pg.Rect = mediator.get_value('mc', 'rect')
        self.assertEqual(mediator_mc_rect.centerx, mc.rect.centerx,
            "mc.rect.centerx != mediator._mc.rect.centerx")
        self.assertEqual(mediator_mc_rect.centery, mc.rect.centerx, 
            "mc.rect.centery != mediator._mc.rect.centery")
        self.assertIs(mediator_mc_rect, mc.rect, "mc.rect is not mediator._mc.rect")

    def test_mc_equality(self):
        
        screen = pg.Surface((500, 500))
        ai_settings = Settings()
        mediator = Mediator()
        mediator.add(screen=screen, ai_settings=ai_settings, 
        screen_rect = screen.get_rect())
        mc = MainCharacter(mediator, 'S')
        mediator.add(mc=mc)
        mediator_mc = mediator.get_value('mc')
        self.assertIs(mc, mediator_mc, 'mc is not mediator._mc')

    def test_mc_rect_changing_pos(self):

        screen = pg.Surface((500, 500))
        ai_settings = Settings()
        mediator = Mediator()
        mediator.add(screen=screen, ai_settings=ai_settings, 
        screen_rect = screen.get_rect())
        mc = MainCharacter(mediator, 'S')
        frl = mc.frl
        frames = mc.frames
        del mc
        mc_fist = Fist(mediator)
        mediator.add(mc_fist=mc_fist)
        for i in range(frames):
            mc_fist.change_position(frl[i], frl[i])
            mediator_mc_fist: Fist = mediator.get_value('mc_fist')
            self.assertEqual(mc_fist.rect.centerx, mediator_mc_fist.rect.centery)
            self.assertEqual(mc_fist.rect.centery, mediator_mc_fist.rect.centery)

    def test_colliding_rects(self):

        screen = pg.Surface((500, 500))
        ai_settings = Settings()
        mediator = Mediator()
        mediator.add(screen=screen, ai_settings=ai_settings, 
        screen_rect = screen.get_rect())

        fist = Fist(mediator)
        mediator.add(fist=fist)

        sprite = Container()
        self.assertFalse(pg.sprite.collide_rect(fist, sprite))
        
        mediator_fist: Fist = mediator.get_value('fist')
        self.assertFalse(pg.sprite.collide_rect(mediator_fist, sprite))

        fist.change_position(sprite.rect.left, sprite.rect.top)
        self.assertTrue(pg.sprite.collide_rect(fist, sprite))
        self.assertTrue(pg.sprite.collide_rect(mediator_fist, sprite))


if __name__ == '__main__':
    pg.init()
    pg.display.set_mode((500, 500))
    unittest.main()