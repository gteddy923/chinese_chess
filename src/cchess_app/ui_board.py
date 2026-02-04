from enum import Enum

import tkinter as tk
from turtle import Screen, Turtle, penup, goto, setheading, pendown, forward, right, tracer, title, bgcolor, color, \
    hideturtle, write, update, pd, clone

from .actions import GameActions
from .state import HitBox, get_app


class DRAW_DIAGNAL(Enum):
    LEFT = 1
    RIGHT = 2
    NONE = 3


class DRAW_DECO(Enum):
    LEFT = 1
    RIGHT = 2
    BOTH = 3
    NONE = 4


def _ensure_ui_turtles() -> None:
    app = get_app()
    cfg = app.config.board
    ui = app.ui
    if ui.invalid_move is None:
        ui.invalid_move = Turtle()
        ui.invalid_move.hideturtle()
        ui.invalid_move.penup()
        ui.invalid_move.goto(0, cfg.square_width * (cfg.height_square_number // 2 + 2))
    if ui.draw_prev_pos is None:
        ui.draw_prev_pos = Turtle()
        ui.draw_prev_pos.hideturtle()


def draw_board() -> None:
    app = get_app()
    cfg = app.config.board
    ui = app.ui

    def draw_deco_top_left(x, y, distance):
        penup()
        goto(x - distance, y + distance)
        p = clone()
        p.hideturtle()
        pendown()
        goto(x - distance * 2, y + distance)
        p.pendown()
        p.goto(x - distance, y + distance * 2)

    def draw_deco_top_right(x, y, distance):
        penup()
        goto(x + distance, y + distance)
        p = clone()
        p.hideturtle()
        pendown()
        goto(x + distance * 2, y + distance)
        p.pendown()
        p.goto(x + distance, y + distance * 2)

    def draw_deco_down_left(x, y, distance):
        penup()
        goto(x - distance, y - distance)
        p = clone()
        p.hideturtle()
        pendown()
        goto(x - distance * 2, y - distance)
        p.pendown()
        p.goto(x - distance, y - distance * 2)

    def draw_deco_down_right(x, y, distance):
        penup()
        goto(x + distance, y - distance)
        p = clone()
        p.hideturtle()
        pendown()
        goto(x + distance * 2, y - distance)
        p.pendown()
        p.goto(x + distance, y - distance * 2)

    def draw_deco(x, y, distance, draw_deco):
        if draw_deco == DRAW_DECO.BOTH:
            draw_deco_top_left(x, y, distance)
            draw_deco_top_right(x, y, distance)
            draw_deco_down_left(x, y, distance)
            draw_deco_down_right(x, y, distance)
        if draw_deco == DRAW_DECO.LEFT:
            draw_deco_top_left(x, y, distance)
            draw_deco_down_left(x, y, distance)
        if draw_deco == DRAW_DECO.RIGHT:
            draw_deco_top_right(x, y, distance)
            draw_deco_down_right(x, y, distance)

    def draw_square(x, y, width, draw_diagnal_direction):
        penup()
        goto(x, y)
        setheading(0)
        pendown()
        forward(width)
        right(90)
        forward(width)
        right(90)
        forward(width)
        right(90)
        forward(width)
        if draw_diagnal_direction == DRAW_DIAGNAL.LEFT:
            penup()
            goto(x, y)
            pendown()
            goto(x + width, y - width)
            penup()
        if draw_diagnal_direction == DRAW_DIAGNAL.RIGHT:
            penup()
            goto(x + width, y)
            pendown()
            goto(x, y - width)
            penup()

    Screen().setup(cfg.square_width * cfg.width_square_number + (cfg.pu_button_width + 10) * 3 * 2,
                   cfg.square_width * (cfg.width_square_number + 5))
    tracer(0, 0)
    title("象棋")
    bgcolor("cyan")
    color("black")
    hideturtle()

    for i in range(cfg.width_square_number):
        for j in range(cfg.height_square_number):
            draw_diagnal = DRAW_DIAGNAL.NONE
            if (i == 3 and (j == 0 or j == 7)) or (i == 4 and (j == 1 or j == 8)):
                draw_diagnal = DRAW_DIAGNAL.LEFT
            if (i == 3 and (j == 1 or j == 8)) or (i == 4 and (j == 0 or j == 7)):
                draw_diagnal = DRAW_DIAGNAL.RIGHT
            if j == cfg.height_square_number // 2:
                continue
            draw_square(cfg.startx + i * cfg.square_width, cfg.starty - j * cfg.square_width,
                        cfg.square_width, draw_diagnal)
            if i == 0 and (j == 3 or j == 6):
                draw_deco(cfg.startx + i * cfg.square_width, cfg.starty - j * cfg.square_width,
                          cfg.deco_distance, DRAW_DECO.RIGHT)
            if i == 7 and (j == 3 or j == 6):
                draw_deco(cfg.startx + (i + 1) * cfg.square_width, cfg.starty - j * cfg.square_width,
                          cfg.deco_distance, DRAW_DECO.LEFT)
            if ((i == 1 and (j == 2 or j == 7)) or (i == 2 and (j == 3 or j == 6)) or (
                    i == 4 and (j == 3 or j == 6)) or (i == 6 and (j == 3 or j == 6)) or (
                    i == 7 and (j == 2 or j == 7))):
                draw_deco(cfg.startx + i * cfg.square_width, cfg.starty - j * cfg.square_width,
                          cfg.deco_distance, DRAW_DECO.BOTH)

    penup()
    goto(cfg.startx, cfg.starty - cfg.height_square_number // 2 * cfg.square_width)
    pd()
    goto(cfg.startx, cfg.starty - cfg.height_square_number // 2 * cfg.square_width - cfg.square_width)
    penup()
    goto(cfg.startx + cfg.width_square_number * cfg.square_width, cfg.starty - cfg.height_square_number // 2 * cfg.square_width)
    pd()
    goto(cfg.startx + cfg.width_square_number * cfg.square_width,
         cfg.starty - cfg.height_square_number // 2 * cfg.square_width - cfg.square_width)

    penup()
    p = clone()
    p.hideturtle()
    p.penup()
    for i in range(cfg.width_square_number + 1):
        goto(cfg.startx + i * cfg.square_width,
             cfg.starty - (cfg.height_square_number + 1) * cfg.square_width + int(0.2 * cfg.square_width))
        write(cfg.labels[8 - i])
        p.goto(cfg.startx + i * cfg.square_width, cfg.starty + int(0.4 * cfg.square_width))
        p.write(i + 1)

    texts = ['楚', '河', '汉', '界']
    for i in range(4):
        multi = (i + 1.5)
        if i >= 2:
            multi = multi + 2
        goto(cfg.startx + multi * cfg.square_width, cfg.starty - 5 * cfg.square_width)
        write(texts[i], align="center", font=('Arial', 30, 'bold'))
    update()

    if ui.save_button is None:
        ui.save_button = tk.Button(Screen().getcanvas().master, text="保  存", command=GameActions.save_button_click)
        Screen().getcanvas().create_window((cfg.startx + (cfg.width_square_number + 2) * cfg.square_width) * -1,
                                           cfg.pu_button_height * cfg.pu_button_group / -4 - cfg.pu_button_height * 1,
                                           window=ui.save_button)
    ui.save_button.lower()

    _ensure_ui_turtles()


def draw_dapu() -> None:
    app = get_app()
    cfg = app.config.board
    ui = app.ui

    def draw_button(x, y, width, height, text):
        penup()
        goto(x, y)
        setheading(0)
        pendown()
        forward(width)
        right(90)
        forward(height)
        right(90)
        forward(width)
        right(90)
        forward(height)
        penup()
        goto(x + width / 2, y - height / 2 - 10)
        write(text, align="center", font=('Arial', 10, 'bold'))

    p = 1.1

    a1, b1, w, h = cfg.startx, cfg.starty - (cfg.height_square_number + 1) * cfg.square_width, \
        cfg.square_width * p, cfg.square_width * 0.6
    draw_button(a1, b1, w, h, "读   谱")
    ui.hitboxes.read = HitBox(a1, b1, a1 + w, b1 - h)

    n = (cfg.square_width * cfg.width_square_number - 7 * cfg.square_width * p) / 6

    a2, b2 = cfg.startx + cfg.square_width * p + n, b1
    draw_button(a2, b2, w, h, "前进>>")
    ui.hitboxes.forward = HitBox(a2, b2, a2 + w, b2 - h)

    a3, b3 = cfg.startx + cfg.square_width * p * 2 + 2 * n, b1
    draw_button(a3, b3, w, h, "<<后退")
    ui.hitboxes.back = HitBox(a3, b3, a3 + w, b3 - h)

    a5, b5 = cfg.startx + cfg.square_width * p * 3 + 3 * n, b1
    draw_button(a5, b5, w, h, "开   局")
    ui.hitboxes.start = HitBox(a5, b5, a5 + w, b5 - h)

    a6, b6 = cfg.startx + cfg.square_width * p * 4 + 4 * n, b1
    draw_button(a6, b6, w, h, "终   局")
    ui.hitboxes.end = HitBox(a6, b6, a6 + w, b6 - h)

    a4, b4 = cfg.startx + cfg.square_width * p * 5 + 5 * n, b1
    draw_button(a4, b4, w, h, "重   置")
    ui.hitboxes.reset = HitBox(a4, b4, a4 + w, b4 - h)

    a7, b7 = cfg.startx + cfg.square_width * p * 6 + 6 * n, b1
    draw_button(a7, b7, w, h, "人机对战")
    ui.hitboxes.ai = HitBox(a7, b7, a7 + w, b7 - h)
