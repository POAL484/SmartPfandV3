import pygame as pg
import keyboard as kb
import mouse
import pyautogui as pag
from enum import Enum
import math
import time
import json
import datetime as dt

def is_collision(x, y, width, height, mx, my, offset):
    if mx > x - offset and mx < x + width + offset and my > y - offset and my < y + height + offset: return True
    return False

class EventState:
    def __init__(self):
        self.mouseX = pag.position()[0]
        self.mouseY = pag.position()[1]
        self.pressed = mouse.is_pressed()

class Anchor(Enum):
    LEFT = 10
    CENTER = 11
    RIGHT = 12

class StorageMode(Enum):
    NOT_SET = 31
    OFFLINE = 32
    ONLINE = 33

class Text:
    def __init__(self, root: pg.Surface, eventstate: EventState,
                 x: int, y: int, text: str, size: int, color: tuple, font: str, anchor: Anchor, bold: bool = False, italic: bool = False):
        sfont = pg.font.SysFont(font, size, bold, italic)
        render = sfont.render(text, True, color)
        match anchor:
            case Anchor.LEFT:
                root.blit(render, (x, y))
            case Anchor.CENTER:
                root.blit(render, (x-(sfont.size(text)[0]/2), y-(sfont.size(text)[1]/2)))
            case Anchor.RIGHT:
                root.blit(render, (x-sfont.size(text)[0], y-sfont.size(text)[1]))

class Button:
    def __init__(self, root: pg.Surface, eventstate: EventState, x: int, y: int, width: int, height: int, func: callable, color: tuple, anchor: Anchor):
        surf = pg.Surface((width, height))
        surf.fill(color)
        match anchor:
            case Anchor.LEFT: pass
            case Anchor.CENTER:
                x -= width // 2
                y -= height // 2
            case Anchor.RIGHT:
                x -= width
                y -= height
        root.blit(
            surf,
            pg.Rect((x, y, width, height))
        )
        if is_collision(x, y, width, height, eventstate.mouseX, eventstate.mouseY, 30) and eventstate.pressed: func()

class SinGraf:
    def __init__(self, root: pg.Surface, eventstate: EventState,
                 ycenter: int, height: int, color: tuple, kx: float, speed: float):
        for i in range(root.get_width()):
            y = int((ycenter * math.sin((i-(time.time()*speed))*kx))+root.get_height()-height)
            surf = pg.Surface((1, height+y))
            surf.fill(color)
            root.blit(
                surf,
                pg.Rect((i, y, 1, height+y))
            )

class Bank:
    @classmethod
    def calcPoint(self, x: int, y: int, angle: int):
        R = math.sqrt(x**2 + y**2)
        stAngle = math.degrees(math.asin(x/R))
        return (R*math.sin(math.radians(stAngle+angle)), R*math.cos(math.radians(stAngle-angle)))


    def __init__(self, root: pg.Surface, eventstate: EventState,
                 xcenter: int, ycenter: int, ksize: float, xcolor: int, rotate: int):
        pg.draw.polygon(root, (180+xcolor, 180+xcolor, 180+xcolor), [
            [xcenter-(self.calcPoint(25, 70, rotate)[0]*ksize), ycenter-(self.calcPoint(25, 70, rotate)[1]*ksize)],
            [xcenter-(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter-(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter-(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(25, 70, rotate)[0]*ksize), ycenter-(self.calcPoint(25, 70, rotate)[1]*ksize)]])
        pg.draw.polygon(root, (140+xcolor, 140+xcolor, 140+xcolor), [
            [xcenter-(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter-(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter-(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter+(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter+(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter-(self.calcPoint(40, 55, rotate)[1]*ksize)]
        ])
        pg.draw.polygon(root, (180+xcolor, 180+xcolor, 180+xcolor), [
            [xcenter-(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter+(self.calcPoint(40, 55, rotate)[1]*ksize)],
            [xcenter-(self.calcPoint(25, 70, rotate)[0]*ksize), ycenter+(self.calcPoint(25, 70, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(25, 70, rotate)[0]*ksize), ycenter+(self.calcPoint(25, 70, rotate)[1]*ksize)],
            [xcenter+(self.calcPoint(40, 55, rotate)[0]*ksize), ycenter+(self.calcPoint(40, 55, rotate)[1]*ksize)]
        ])
        

class Logger:
    def __init__(self):
        self.logs = []
        with open("logs.txt", 'w') as saveLogs:
            saveLogs.close()

    def __call__(self, data: str):
        datatime = dt.datetime.now().strftime("%H:%M:%S ") + data
        self.logs.append(datatime)
        with open("logs.txt", "a") as saveLogs:
            saveLogs.write("\n" + datatime)
            saveLogs.close()