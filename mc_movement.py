import mc_animation as an
import pygame



def going_right(mc):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        вправо'''
        for enemy in mc.mediator.get_collection('enemies'):
            if mc.rect.right in range(enemy.rect.left - 10, enemy.rect.left + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if mc.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        
        mc.centerx += mc.speed
        an.going_right_animation(mc)

def going_left(mc):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение 
        влево'''
        for enemy in mc.mediator.get_collection('enemies'):
            if mc.rect.left in range(enemy.rect.right - 10, enemy.rect.right + 10):
                # Если персонаж расположен намного ниже врага, то он может пройти
                if mc.rect.centery in range(
                enemy.rect.bottom - enemy.rect.height, 
                enemy.rect.bottom - int(enemy.rect.height/3)):
                    return
        mc.centerx -= mc.speed
        an.going_left_animation(mc)

def going_down(mc):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вниз'''
        for enemy in mc.mediator.get_collection('enemies'):
            if mc.rect.bottom in range(enemy.rect.top - 10, enemy.rect.top + 10):
                if mc.rect.centerx in range(
                enemy.rect.left, enemy.rect.left + enemy.rect.width):               
                    return
        mc.centery += mc.speed
        an.going_down_animation(mc)

def going_up(mc):
        '''Если персонаж ни с кем не столкнулся из врагов, он делает движение
        вверх'''
        for enemy in mc.mediator.get_collection('enemies'):
            if mc.rect.top in range(enemy.rect.bottom - 10, enemy.rect.bottom + 10):
                if mc.rect.centerx in range(
                enemy.rect.left, enemy.rect.left + enemy.rect.width):                
                    return
        mc.centery -= mc.speed
        an.going_up_animation(mc)