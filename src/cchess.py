# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 08:05:34 2023

@author: gteddy
"""

from turtle import *
from enum import *
import math
from math import sin, cos, radians
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, Frame, Listbox, Scrollbar, SINGLE, RIGHT, BOTH, W, Y, N, S, END
from tkinter.filedialog import asksaveasfile
from XQlightPy.position import Position
from XQlightPy.search import Search
from XQlightPy.cchess import move2Iccs, Iccs2move
import speech_recognition as sr
from XQlightPy.play_against_ai import print_board as pb


class DRAW_DIAGNAL(Enum):
    LEFT = 1
    RIGHT = 2
    NONE = 3


pos = None
search = None
search_time_ms = 5000

changzi = sr.Recognizer()


class DRAW_DECO(Enum):
    LEFT = 1
    RIGHT = 2
    BOTH = 3
    NONE = 4


class SIDE(Enum):
    RED = "red"
    BLACK = "black"
    NONE = None


chess_names = ['empty', 'shuai', 'shi', 'xiang', 'ju', 'ma', 'pao', 'zhu']
square_width = 65
width_square_number = 8
height_square_number = 9
deco_distance = 5
pu_button_width = 65
startx = 0 - width_square_number / 2 * square_width
starty = 0 + height_square_number / 2 * square_width
board = [[None] * (width_square_number + 1) for i in range(height_square_number + 1)]
qizi_size = int(square_width * 0.7)
dapu_moves = []
dapu_moves_index = 0
moves = []
moves_index = 0
dapu_widgets = []
widgets = []

pu_button_height = 28
pu_button_group = 50

invalid_move = Turtle()
invalid_move.hideturtle()
invalid_move.penup()
invalid_move.goto(0, 0 + (square_width) * (height_square_number // 2 + 2))

changzi_move = None


def chagnzi_button_click():
    global changzi_move
    invalid_move.clear()
    invalid_move.write("请唱棋例如，马二进三", align="center", font=('Arial', 20, 'bold'))
    invalid_move.screen.update()
    with sr.Microphone() as source:
        changzi.adjust_for_ambient_noise(source)
        the_audio = changzi.listen(source)
    try:
        changzi_move = changzi.recognize_google(the_audio, language='zh-CN')
        invalid_move.clear()
        invalid_move.write(changzi_move, align="center", font=('Arial', 20, 'bold'))
        invalid_move.screen.update()
    except sr.UnknownValueError:
        print("Could not understand audio")


def changzi_confirm_button_click():
    global changzi_move

    ## more standardization to the converted text
    # if len(moves)%2:
    #     ##red
    #
    # else:
    #     ##black

    r, c, r1, c1 = dapu_move(changzi_move, "jin")

    if ai:
        user_step = col_label[c] + str(r) + "-" + col_label[c1] + str(r1)
        user_move = Iccs2move(user_step)
        pos.makeMove(user_move)
        winner = pos.winner()
        if winner is not None:
            if winner == 0:
                tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
            elif winner == 1:
                tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
            elif winner == 2:
                tk.messagebox.showinfo('返回', '和棋！行棋结束')
        else:
            zouzi()


baiqi = False


def baiqi_button_click():
    global baiqi
    baiqi = True
    rcount = 0
    bcount = 0
    bx, by = ((width_square_number // 2 + 2) * square_width) * -1, height_square_number // 2 * square_width
    rx, ry = ((width_square_number // 2 + 1) * square_width), height_square_number // 2 * square_width
    for i in range(0, height_square_number + 1):
        for j in range(0, width_square_number + 1):
            if board[i][j].name != "empty":
                if board[i][j].side == SIDE.BLACK:
                    board[i][j].clear()
                    # board[i][j].set_pos(bx,by)
                    board[i][j].set_pos(bx + bcount % 2 * square_width, by - bcount // 2 * square_width)
                    board[i][j].show()
                    bcount = bcount + 1
                if board[i][j].side == SIDE.RED:
                    board[i][j].clear()
                    # board[i][j].set_pos(rx,ry)
                    board[i][j].set_pos(rx + rcount % 2 * square_width, ry - rcount // 2 * square_width)
                    board[i][j].show()
                    rcount = rcount + 1


def kaishi_button_click():
    global baiqi
    baiqi = False
    for r in range(height_square_number + 1):
        for c in range(width_square_number + 1):
            rr, cc = board[r][c].r, board[r][c].c
            if not (0 <= rr <= height_square_number and 0 <= cc <= width_square_number):
                board[r][c].name = 'empty'
                board[r][c].side=SIDE.NONE
                x,y = index_to_pos(r,c)
                board[r][c].set_pos(x,y)
                board[r][c].clear()
            board[r][c].clicked = False


changzi_button = tk.Button(Screen().getcanvas().master, text="唱 棋", command=chagnzi_button_click)
Screen().getcanvas().create_window(square_width * -3, (-square_width) * (height_square_number // 2 + 2),
                                   window=changzi_button)

changzi_confirm_button = tk.Button(Screen().getcanvas().master, text="确 认", command=changzi_confirm_button_click)
Screen().getcanvas().create_window(square_width * -2.3, (-square_width) * (height_square_number // 2 + 2),
                                   window=changzi_confirm_button)

baiqi_button = tk.Button(Screen().getcanvas().master, text="摆 棋", command=baiqi_button_click)
Screen().getcanvas().create_window(square_width * -4.4, (-square_width) * (height_square_number // 2 + 2),
                                   window=baiqi_button)

kaishi_button = tk.Button(Screen().getcanvas().master, text="开 始", command=kaishi_button_click)
Screen().getcanvas().create_window(square_width * -3.7, (-square_width) * (height_square_number // 2 + 2),
                                   window=kaishi_button)

draw_prev_pos = Turtle()
draw_prev_pos.hideturtle()

save_button = None
pu_path = ""
ai = False

label = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
# cordinates for buttons
# 读谱
x1, y1, x2, y2 = 0, 0, 0, 0
# 前进
x3, y3, x4, y4 = 0, 0, 0, 0
# 后退
x5, y5, x6, y6 = 0, 0, 0, 0
# 重置
x7, y7, x8, y8 = 0, 0, 0, 0
# 开局
x9, y9, x10, y10 = 0, 0, 0, 0
# 终局
x11, y11, x12, y12 = 0, 0, 0, 0
# 人机对战
x13, y13, x14, y14 = 0, 0, 0, 0


def pos_to_index(x, y) -> tuple:
    return int((starty - y) / square_width), int((x - startx) / square_width)


def index_to_pos(r, c) -> tuple:
    return startx + c * square_width, starty - r * square_width


def column(matrix, i):
    return [row[i] for row in matrix]


class chess:
    caption = ""
    side = SIDE.NONE
    r = 0
    c = 0
    clicked = False

    def __init__(self, name, turtle, x, y):
        if name not in chess_names:
            raise Exception("name is not valid ", name)
        self.name = name
        self.turtle = turtle
        self.x = x
        self.y = y
        self.r, self.c = pos_to_index(x, y)
        if turtle is not None:
            turtle.hideturtle()
            turtle.penup()
            turtle.setposition(x, y)  # print(turtle.position())

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.r, self.c = pos_to_index(x, y)

    def move(self, x, y):
        if self.check_move(x, y):
            rr = self.r
            cc = self.c
            xx = self.x
            yy = self.y
            temp = board[rr][cc]
            self.clear()
            self.x = x
            self.y = y
            self.r, self.c = pos_to_index(x, y)
            self.jipu(rr, cc, self.r, self.c)
            eat = False
            if board[self.r][self.c].name != "empty":
                eat = True
                board[self.r][self.c].clear()
            self.clicked = False
            self.show()
            print(self.side.value + self.caption + " moved to " + str(self.r) + "," + str(self.c))
            if eat:
                board[rr][cc] = chess("empty", None, xx, yy)
            else:
                board[rr][cc] = board[self.r][self.c]
                board[rr][cc].set_pos(xx, yy)
            board[self.r][self.c] = temp

            # 记谱

            draw_prev_pos.clear()
            draw_prev_pos.penup()
            draw_prev_pos.goto(xx, yy)
            draw_prev_pos.pendown()
            draw_prev_pos.dot(10, "white")

            draw_prev_pos.pensize(4)
            draw_prev_pos.penup()
            draw_prev_pos.goto(self.x + qizi_size / 2, y)
            draw_prev_pos.pendown()
            draw_prev_pos.color("yellow")
            for i in range(1, 400):
                draw_prev_pos.goto(qizi_size / 2 * cos(radians(i)) + x, qizi_size / 2 * sin(radians(i)) + y)

        else:
            reset_qizi_click()
            raise Exception("invalid move!")

    def jipu(self, r, c, r1, c1):
        global moves_index
        cap = ""
        s = ""
        action = ""
        e = ""
        if (self.name, self.side) == ("shuai", SIDE.BLACK):
            cap = "将"
        if (self.name, self.side) == ("shuai", SIDE.RED):
            cap = "帅"
        if (self.name, self.side) == ("shi", SIDE.BLACK):
            cap = "士"
        if (self.name, self.side) == ("shi", SIDE.RED):
            cap = "仕"
        if (self.name, self.side) == ("xiang", SIDE.RED):
            cap = "相"
        if (self.name, self.side) == ("xiang", SIDE.BLACK):
            cap = "象"
        if (self.name, self.side) == ("zhu", SIDE.RED):
            cap = "兵"
        if (self.name, self.side) == ("zhu", SIDE.BLACK):
            cap = "卒"
        if self.name == "ju":
            cap = "车"
        if self.name == "ma":
            cap = "马"
        if self.name == "pao":
            cap = "炮"
        if r == r1:
            action = "平"
        else:
            if (self.side == SIDE.BLACK and r1 > r) or (self.side == SIDE.RED and r1 < r):
                action = "进"
            else:
                action = "退"
        if self.side == SIDE.RED:
            s = label[width_square_number - c]
        else:
            s = str(c + 1)
        if c == c1:
            if self.side == SIDE.RED:
                e = label[abs(r - r1) - 1]
            else:
                e = str(abs(r - r1))
        else:
            if self.side == SIDE.RED:
                e = label[width_square_number - c1]
            else:
                e = c1 + 1

        qh = ""
        if len([z for z in board_column(c) if z.name == self.name and z.side == self.side]) == 2:
            rn = [z for z in board_column(c) if z.name == self.name and z.r != r][0]
            if rn.r > r:
                qh = "后"
            else:
                qh = "前"
        pu = qh + cap + str(s) + action + str(e)
        print(pu)
        moves.append(pu)
        moves_index = moves_index + 1
        print(moves_index, moves)
        display_moves(False, pu)

    def check_move(self, x, y) -> bool:

        nr, nc = pos_to_index(x, y)
        can_move = True

        if board[nr][nc].side == self.side:
            return False

        # 将  士
        if self.name == "shuai" or self.name == "shi":
            if nc < 3 or nc > 5:
                can_move = False
                reason = "将/帅走出框"
            elif (self.side == SIDE.BLACK and nr > 2) or (self.side == SIDE.RED and nr < 7):
                can_move = False
                reason = "将/帅走出框"

            if self.name == "shuai":
                if abs(nr - self.r) not in (1, 0) or abs(nc - self.c) not in (1, 0):
                    can_move = False
                    reason = "将/帅走出框"
                elif abs(nr - self.r) == 1 and abs(nc - self.c) == 1:
                    can_move = False
                    reason = "将/帅走斜线"

            if self.name == "shi":
                if not (abs(nr - self.r) == 1 and abs(nc - self.c) == 1):
                    can_move = False
                    reason = "士/仕只能走斜线"

        # 相
        if self.name == "xiang":
            if (self.side == SIDE.RED and nr < 5) or (self.side == SIDE.BLACK and nr > 4):
                can_move = False
                reason = "象/相不能过河"
            elif not (abs(nr - self.r) == 2 and abs(nc - self.c) == 2):
                can_move = False
                reason = "象/相只能走田"
            elif board[int((nr + self.r) / 2)][int((nc + self.c) / 2)].name != "empty":
                can_move = False
                reason = "象/相撇腿"

        def jumapao_road_block(road, s, e):
            if s >= e:
                small = e
                big = s
            else:
                small = s
                big = e
            if big - small == 1:
                return False
            return any(cc.name != "empty" for cc in road[small + 1: big])

        def check_ju_pao():
            can_move = True
            if not (nc == self.c or nr == self.r):
                can_move = False
            elif nc == self.c and jumapao_road_block(board_column(nc), self.r, nr):
                can_move = False
            elif nr == self.r and jumapao_road_block(board[nr], self.c, nc):
                can_move = False
            return can_move

        # 车
        if self.name == "ju":
            can_move = check_ju_pao()
            if not can_move:
                reason = "车路上有其它子"
        # 马
        if self.name == "ma":
            if not ((abs(nc - self.c), abs(nr - self.r)) == (1, 2) or (abs(nc - self.c), abs(nr - self.r)) == (2, 1)):
                can_move = False
                reason = "马只能走日"
            elif abs(nc - self.c) == 2 and jumapao_road_block(board[self.r], self.c, nc):
                can_move = False
                reason = "马被撇腿"
            elif abs(nr - self.r) == 2 and jumapao_road_block(board_column(self.c), self.r, nr):
                can_move = False
                reason = "马被撇腿"

        def pao_da_ge_san(road, s, e):
            if s >= e:
                small = e
                big = s
            else:
                small = s
                big = e
            ct = 0
            for cc in road[small + 1: big]:
                if cc.name != "empty":
                    ct = ct + 1
            return ct == 1

        # 炮
        if self.name == "pao":
            if not (nc == self.c or nr == self.r):
                can_move = False
                reason = "炮只能走平或者直"
            elif board[nr][nc].name == "empty":
                can_move = check_ju_pao()
                reason = "炮路上有其它子"
            elif board[nr][nc].name != "empty" and board[nr][nc].side != self.side:
                if nc == self.c and not pao_da_ge_san(board_column(nc), self.r, nr):
                    reason = "炮打隔三"
                    can_move = False
                elif nr == self.r and not pao_da_ge_san(board[nr], self.c, nc):
                    reason = "炮打隔三"
                    can_move = False
        # 卒
        if self.name == "zhu":
            if (self.side == SIDE.RED and nr > self.r) or (self.side == SIDE.BLACK and nr < self.r):
                can_move = False
                reason = "卒/兵不能后退"
            elif ((self.side == SIDE.RED and self.r > 4) or (self.side == SIDE.BLACK and nr < 5)) and abs(
                    nc - self.c) == 1:
                can_move = False
                reason = "卒/兵只能前进"
            elif abs(nr - self.r) not in (1, 0) or abs(nc - self.c) not in (1, 0):
                reason = "卒/兵只能前进或平移一步"
                can_move = False

        # if len(moves) > 0:
        #     if len(moves[len(moves) - 1]) == 5:
        #         z = moves[len(moves) - 1][2]
        #     else:
        #         z = moves[len(moves) - 1][1]
        #     if (( z in label and self.side == SIDE.RED) or (z not in label and self.side == SIDE.BLACK)):
        #         can_move = False
        #         reason = "不能连续走子"

        invalid_move.clear()
        if not can_move:
            invalid_move.write("错误:" + reason, align="center", font=('Arial', 20, 'bold'))

        return can_move

    def show(self):
        self.turtle.goto(self.x, self.y)
        self.turtle.dot(qizi_size, self.side.value)
        self.turtle.goto(self.x, self.y - 10)
        self.turtle.color("white")
        self.turtle.write(self.caption, align="center", font=('Arial', int(square_width * 0.2), 'bold'))

    def clear(self):
        self.turtle.clear()

    def to_string(self):
        if self.name != "empty":
            return "[" + self.side.value + self.caption + "," + str(self.clicked) + ",(" + str(self.r) + "," + str(
                self.c) + ")]"
        else:
            return "empty"


def init_board():
    for r in range(10):
        for c in range(9):
            qizi = None
            if (r == 0 or r == 9) and (c == 0 or c == 8):
                qizi = chess("ju", Turtle(), startx + c * square_width, starty - r * square_width)
                qizi.caption = "车"
            if (r == 0 or r == 9) and (c == 1 or c == 7):
                qizi = chess("ma", Turtle(), startx + c * square_width, starty - r * square_width)
                qizi.caption = "马"
            if (r == 0 or r == 9) and (c == 2 or c == 6):
                qizi = chess("xiang", Turtle(), startx + c * square_width, starty - r * square_width)
                if r == 0:
                    qizi.caption = "象"
                else:
                    qizi.caption = "相"
            if (r == 0 or r == 9) and (c == 3 or c == 5):
                qizi = chess("shi", Turtle(), startx + c * square_width, starty - r * square_width)
                if r == 0:
                    qizi.caption = "士"
                else:
                    qizi.caption = "仕"
            if (r == 0 or r == 9) and (c == 4):
                qizi = chess("shuai", Turtle(), startx + c * square_width, starty - r * square_width)
                if r == 0:
                    qizi.caption = "将"
                else:
                    qizi.caption = "帅"

            if (r == 2 or r == 7) and (c == 1 or c == 7):
                qizi = chess("pao", Turtle(), startx + c * square_width, starty - r * square_width)
                qizi.caption = "炮"
                if r == 2:
                    qizi.side = SIDE.BLACK
                else:
                    qizi.side = SIDE.RED

            if (r == 3 or r == 6) and (c == 0 or c == 2 or c == 4 or c == 6 or c == 8):
                qizi = chess("zhu", Turtle(), startx + c * square_width, starty - r * square_width)
                if r == 3:
                    qizi.caption = "卒"
                else:
                    qizi.caption = "兵"
                if r == 3:
                    qizi.side = SIDE.BLACK
                else:
                    qizi.side = SIDE.RED

            if r == 0:
                qizi.side = SIDE.BLACK
            if r == 9:
                qizi.side = SIDE.RED

            if qizi is None:
                qizi = chess("empty", None, startx + c * square_width, starty - r * square_width)

            board[r][c] = qizi
            if board[r][c].name != 'empty':
                board[r][c].show()


def save_button_click():
    ftypes = [('棋谱文件', '*.txt')]
    f = asksaveasfile(initialfile="棋谱.txt", defaultextension=".txt", filetypes=ftypes)
    f.close()
    f1 = open(f.name, "w", encoding="utf-8")
    i = 0
    if len(moves) > 0:
        for m in moves:
            if not i % 2:
                l = (str(i // 2 + 1) + "." + moves[i])
                print(l)
                f1.write(l)
            else:
                l = (" " + moves[i] + "\n")
                print(l)
                f1.write(l)
            i = i + 1
    f1.flush()
    f1.close()


def draw_board():
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

    def draw_square(x, y, width, draw_diagnal_direction, draw_deco_direction):
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

    # draw the board
    Screen().setup(square_width * width_square_number + (pu_button_width + 10) * 3 * 2,
                   square_width * (width_square_number + 5))
    tracer(0, 0)
    title("象棋")
    bgcolor("cyan")
    color("black")
    hideturtle()
    for i in range(width_square_number):
        for j in range(height_square_number):
            draw_diagnal = DRAW_DIAGNAL.NONE
            if (i == 3 and (j == 0 or j == 7)) or (i == 4 and (j == 1 or j == 8)):
                draw_diagnal = DRAW_DIAGNAL.LEFT
            if (i == 3 and (j == 1 or j == 8)) or (i == 4 and (j == 0 or j == 7)):
                draw_diagnal = DRAW_DIAGNAL.RIGHT
            if j == height_square_number // 2:
                continue
            draw_square(startx + i * square_width, starty - j * square_width, square_width, draw_diagnal,
                        DRAW_DECO.NONE)
            if i == 0 and (j == 3 or j == 6):
                draw_deco(startx + i * square_width, starty - j * square_width, deco_distance, DRAW_DECO.RIGHT)
            if i == 7 and (j == 3 or j == 6):
                draw_deco(startx + (i + 1) * square_width, starty - j * square_width, deco_distance, DRAW_DECO.LEFT)
            if ((i == 1 and (j == 2 or j == 7)) or (i == 2 and (j == 3 or j == 6)) or (
                    i == 4 and (j == 3 or j == 6)) or (i == 6 and (j == 3 or j == 6)) or (
                    i == 7 and (j == 2 or j == 7))):
                draw_deco(startx + i * square_width, starty - j * square_width, deco_distance, DRAW_DECO.BOTH)
    # draw the board - connect the top and board halves of the board
    penup()
    goto(startx, starty - height_square_number // 2 * square_width)
    pd()
    goto(startx, starty - height_square_number // 2 * square_width - square_width)
    penup()
    goto(startx + width_square_number * square_width, starty - height_square_number // 2 * square_width)
    pd()
    goto(startx + width_square_number * square_width, starty - height_square_number // 2 * square_width - square_width)

    # write board numbers
    penup()
    p = clone()
    p.hideturtle()
    p.penup()
    for i in range(width_square_number + 1):
        goto(startx + i * square_width, starty - (height_square_number + 1) * square_width + int(0.2 * square_width))
        write(label[8 - i])
        p.goto(startx + i * square_width, starty + int(0.4 * square_width))
        p.write(i + 1)
    # for i in range(height_square_number):
    #     goto(startx - int(0.6 * square_width), starty - (i + 1) * square_width - 10)  # seems by default, turtle is 20*20 in size
    #     write(i + 1)
    #     goto(startx + 8 * square_width + int(0.6 * square_width), starty - i * square_width - 10)
    #     write(label[height_square_number - i - 1])

    # write boundaries texts
    texts = ['楚', '河', '汉', '界']
    for i in range(4):
        multi = (i + 1.5)
        if i >= 2:
            multi = multi + 2
        goto(startx + multi * square_width, starty - 5 * square_width)
        write(texts[i], align="center", font=('Arial', 30, 'bold'))
    update()

    global save_button
    save_button = tk.Button(Screen().getcanvas().master, text="保  存", command=save_button_click)
    Screen().getcanvas().create_window((startx + (width_square_number + 2) * square_width) * -1,
                                       pu_button_height * pu_button_group / -4 - pu_button_height * 1,
                                       window=save_button)
    save_button.lower()


def dist(x, y, x1, y1):
    return int(math.sqrt(abs(x1 - x) ** 2 + abs(y1 - y) ** 2))


def reset_qizi_click():
    for row in board:
        for cell in row:
            cell.clicked = False


def find_qizi_clicked():
    for row in board:
        for cell in row:
            if cell.clicked:
                return cell
    return None


def board_column(col):
    return [row[col] for row in board]


def dapu_move(move, direction):
    rr, cc, rr1, cc1 = 0, 0, 0, 0
    qh = None
    if len(move) == 5:
        qh = move[0]
        move = move[1:5]
    if direction == "jin":
        cap = move[0:1]
        s = move[1:2]
        action = move[2:3]
        e = move[3:4]
    if direction == "tui":
        cap = move[0:1]
        action = move[2:3]
        if action == "进":
            action = "退"
        elif action == "退":
            action = "进"
        if cap == "车" or cap == "炮":
            s = move[1:2]
            e = move[3: 4]
        else:
            s = move[3:4]
            e = move[1:2]

    side = SIDE.NONE
    step = 0
    column = 0

    if s in label:
        side = SIDE.RED
        step = label.index(e) - label.index(s)
        column = width_square_number - label.index(s)
        ystep1 = label.index(e) + 1
    else:
        side = SIDE.BLACK
        step = int(e) - int(s)
        column = int(s) - 1
        ystep1 = int(e)
    ystep = 0
    if abs(step) == 1:
        ystep = 2
    if (abs(step)) == 2:
        ystep = 1

    count = 0
    potential_qizi = []
    for q in board_column(column):
        if q.caption == cap and q.side == side:
            count = count + 1
            potential_qizi.append(q)

    if count == 2:
        print("two qizi on the same col")

    gotox, gotoy = 0, 0

    def get_goto(cell, action):
        if action == "平":
            if side == SIDE.RED:
                gotox, gotoy = cell.x - step * square_width, cell.y  # cell.move(cell.x - step * square_width, cell.y)
            if side == SIDE.BLACK:
                gotox, gotoy = cell.x + step * square_width, cell.y  # cell.move(cell.x + step * square_width, cell.y)
        elif action == "进" or action == "退":
            scalar = 1
            if action == "退":
                scalar = -1
            if cell.caption == "马":
                if side == SIDE.RED:
                    # cell.move(cell.x - step * square_width, cell.y + scalar * ystep * square_width)
                    gotox, gotoy = cell.x - step * square_width, cell.y + scalar * ystep * square_width
                if side == SIDE.BLACK:
                    # cell.move(cell.x + step * square_width, cell.y - scalar * ystep * square_width)
                    gotox, gotoy = cell.x + step * square_width, cell.y - scalar * ystep * square_width
            elif cell.caption == "象" or cell.caption == "相" or cell.caption == "士" or cell.caption == "仕":
                if side == SIDE.RED:
                    # cell.move(cell.x - step * square_width, cell.y + scalar * abs(step) * square_width)
                    gotox, gotoy = cell.x - step * square_width, cell.y + scalar * abs(step) * square_width
                if side == SIDE.BLACK:
                    # cell.move(cell.x + step * square_width, cell.y - scalar * abs(step) * square_width)
                    gotox, gotoy = cell.x + step * square_width, cell.y - scalar * abs(step) * square_width
            else:
                if side == SIDE.RED:
                    # cell.move(cell.x, cell.y + scalar * ystep1 * square_width)
                    gotox, gotoy = cell.x, cell.y + scalar * ystep1 * square_width
                if side == SIDE.BLACK:
                    # cell.move(cell.x, cell.y - scalar * ystep1 * square_width)
                    gotox, gotoy = cell.x, cell.y - scalar * ystep1 * square_width
        return gotox, gotoy

    try:
        for row in board:
            for cell in row:
                if cell.caption == cap and cell.side == side and cell.c == column:
                    gotox, gotoy = get_goto(cell, action)
                    try:
                        if direction == "tui":
                            cell.huiqi = True
                        if qh is None:
                            rr, cc = cell.r, cell.c
                            cell.move(gotox, gotoy)
                            rr1, cc1 = cell.r, cell.c
                        else:
                            min = 0
                            max = height_square_number + 2
                            for q1 in potential_qizi:
                                if q1.r > min:
                                    min = q1.r
                                    big = q1
                                if q1.r < max:
                                    max = q1.r
                                    small = q1
                            if (qh == "前" and cell.side == SIDE.RED) or (qh == "后" and cell.side == SIDE.BLACK):  # 找小
                                gotox, gotoy = get_goto(small, action)
                                rr, cc = small.r, small.c
                                small.move(gotox, gotoy)
                                rr1, cc1 = small.r, small.c
                            else:
                                gotox, gotoy = get_goto(big, action)
                                rr, cc = small.r, small.c
                                big.move(gotox, gotoy)
                                rr1, cc1 = small.r, small.c

                    except Exception:
                        print(cell.to_string(), " invalid move.")
                        if count == 2:
                            potential_qizi.remove(cell)

                            if potential_qizi[0] is not None:
                                if direction == "tui":
                                    cell.huiqi = True
                                gotox, gotoy = get_goto(potential_qizi[0], action)
                                rr, cc = potential_qizi[0].r, potential_qizi[0].c
                                potential_qizi[0].move(gotox, gotoy)
                                rr1, cc1 = potential_qizi[0].r, potential_qizi[0].c

                    raise StopIteration
    except StopIteration:
        pass
    return rr, cc, rr1, cc1


# def highlight_label():
#     if len(dapu_moves) > 0 and len(dapu_widgets) > 0 and dapu_moves_index > 0:
#         for i in range(len(dapu_widgets)):
#             if i == dapu_moves_index - 1:
#                 dapu_widgets[i].config(bg="green")
#             else:
#                 dapu_widgets[i].config(bg="white")

def highlight_label():
    listbox.selection_clear(0, END)
    listbox1.selection_clear(0, END)
    if len(moves) > 0 and moves_index > 0:
        listbox.selection_set(moves_index - 1, moves_index - 1)
        listbox.see(moves_index - 1)
        listbox1.selection_set(moves_index - 1, moves_index - 1)
        listbox1.see(moves_index - 1)


def click_label(event, mov, dapu, i):
    global dapu_moves_index
    print("clicked ", mov, dapu, i)
    if dapu:
        reset()
        dupu(pu_path)
        dapu_moves_index = i
        ii = 0
        while ii != dapu_moves_index:
            move = dapu_moves[ii]
            dapu_move(move, "jin")
            ii = ii + 1
        highlight_label()


mx, my = (startx + (
        width_square_number + 3) * square_width) * -1, pu_button_height * pu_button_group / -4  # starty * -1 - square_width * 3
pux, puy = startx + (
        width_square_number + 1.5) * square_width, pu_button_height * pu_button_group / -4  # starty * -1 - square_width * 3

frame1 = tk.Frame(Screen().getcanvas().master, height=height_square_number * square_width,
                  width=(width_square_number - 5) * square_width, bg='white')
scrollbar = tk.Scrollbar(frame1, orient="vertical")
listbox = tk.Listbox(frame1, activestyle='none', width=20, height=40, selectmode=SINGLE, exportselection=0)

frame2 = tk.Frame(Screen().getcanvas().master, height=height_square_number * square_width,
                  width=(width_square_number - 5) * square_width, bg='white')
scrollbar1 = tk.Scrollbar(frame2, orient="vertical")
listbox1 = tk.Listbox(frame2, activestyle='none', width=20, height=40, selectmode=SINGLE, exportselection=0)


def dapu_onselect(event):
    if not event.widget.curselection():
        return

    global moves_index, dapu_moves_index
    selection = event.widget.curselection()

    if selection:
        reset()
        dupu(pu_path)
        listbox1.delete(0, END)
        index = selection[0]
        data = event.widget.get(index)
        print(index, data)
        ii = 0
        while ii != index + 1:
            move = dapu_moves[ii]
            dapu_move(move, "jin")
            ii = ii + 1
        moves_index = ii
        dapu_moves_index = ii
        listbox.activate(index)
        listbox.selection_set(index, index)
        listbox.see(index)
        listbox1.activate(index)
        listbox1.selection_set(index, index)
        listbox1.see(index)


Screen().getcanvas().create_window((width_square_number - 2) * square_width, 0, window=frame1)
Screen().getcanvas().create_window(-1 * (width_square_number - 2) * square_width, 0, window=frame2)
frame1.rowconfigure(1, weight=1)
frame1.columnconfigure(1, weight=1)
listbox.grid(row=0, column=0, sticky=W)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky=W + N + S)
scrollbar.config(command=listbox.yview)
listbox.bind("<<ListboxSelect>>", dapu_onselect)
frame1.lower()

frame2.rowconfigure(1, weight=1)
frame2.columnconfigure(1, weight=1)
listbox1.grid(row=0, column=0, sticky=W)
listbox1.config(yscrollcommand=scrollbar1.set)
scrollbar1.grid(row=0, column=1, sticky=W + N + S)
scrollbar1.config(command=listbox1.yview)
frame2.lower()


def display_moves(dapu, mov):
    if dapu:
        i = len(dapu_moves) - 1
        t = dapu_moves[i]
    else:
        i = len(moves) - 1
        if save_button is not None:
            save_button.lift()
        t = moves[i]
    if i % 2 == 0:
        t1 = str((i + 1) // 2 + 1) + ". " + t
    else:
        if i <= 9:
            t1 = "    " + t
        elif i <= 99:
            t1 = "      " + t
        elif i <= 999:
            t1 = "        " + t

    if dapu:
        listbox1.insert(END, t1)
        frame2.lift()
        listbox.insert(END, t1)
        frame1.lift()
        listbox1.selection_set(END)
        listbox1.see(END)
        listbox.selection_set(END)
        listbox.see(END)
        listbox.selection_clear(0, END)
        listbox1.selection_clear(0, END)
    else:
        listbox1.selection_clear(0, END)
        listbox1.insert(END, t1)
        listbox1.selection_set(END)
        listbox1.see(END)
        frame2.lift()

    # def display_moves(dapu, mov):


#     if dapu:
#         i = len(dapu_widgets)
#         t = dapu_moves[i]
#         x, y = pux + i // pu_button_group * (pu_button_width * 2 + 40), puy + (i % pu_button_group) // 2 * (
#                 pu_button_height + 2)
#     else:
#         i = len(widgets)
#         t = mov
#         x, y = mx - i // pu_button_group * (pu_button_width * 2 + 40), my + (i % pu_button_group) // 2 * (
#                 pu_button_height + 2)
#
#     if i % 2 == 0:
#         t1 = str((i + 1) // 2 + 1) + ". " + t
#     else:
#         t1 = t
#
#     l = tk.Label(Screen().getcanvas().master, text=t1)
#
#     if i % 2 == 0:
#         Screen().getcanvas().create_window(x, y, height=pu_button_height, width=pu_button_width, window=l)
#     else:
#         Screen().getcanvas().create_window(x + pu_button_width + 10, y, height=pu_button_height, width=pu_button_width,
#                                            window=l)
#
#     if dapu:
#         dapu_widgets.append(l)
#         index = len(dapu_widgets)
#     else:
#         widgets.append(l)
#         index = len(widgets)
#
#     l.bind("<Button-1>", lambda event, m=t, d=dapu, i=index: click_label(event, m, d, i))
#
#     if len(widgets) > 0 and save_button is not None:
#         save_button.lift()


def clear_widgets():
    global dapu_moves_index
    global moves_index, ai
    for w in dapu_widgets:
        w.lower()
        w.destroy()
    dapu_widgets.clear()
    dapu_moves.clear()
    dapu_moves_index = 0

    moves.clear()
    moves_index = 0
    for w in widgets:
        w.lower()
        w.destroy()
    widgets.clear()
    listbox.delete(0, END)
    listbox1.delete(0, END)
    frame1.lower()
    frame2.lower()


def reset():
    for row in board:
        for cell in row:
            if cell.turtle is not None:
                cell.clear()
    init_board()
    clear_widgets()
    draw_prev_pos.clear()
    invalid_move.clear()
    if save_button is not None:
        save_button.lower()


def dupu(path):
    if path != '':
        reset()
        print(path)
        lines = open(path.strip(), encoding="utf-8")
        for line in lines:
            m = line.strip().split(".")[1].split(" ")
            if len(m) == 2:
                dapu_moves.append(m[0])
                display_moves(True, m[0])
                dapu_moves.append(m[1])
                display_moves(True, m[1])
            else:
                dapu_moves.append(m[0])
                display_moves(True, m[0])
    for row in board:
        for cell in row:
            cell.dapu_move = True


col_label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']


def zouzi():
    invalid_move.clear()
    invalid_move.write("电脑正在思考", align="center", font=('Arial', 20, 'bold'))
    invalid_move.screen.update()
    mov = search.searchMain(64, search_time_ms)
    invalid_move.clear()
    move = move2Iccs(mov)
    f = move.split("-")
    r, c = 9 - int(f[0][1]), col_label.index(f[0][0])
    r1, c1 = 9 - int(f[1][1]), col_label.index(f[1][0])
    print("zouzi:", r, c, r1, c1)
    board[r][c].move(board[r1][c1].x, board[r1][c1].y)
    pos.makeMove(mov)
    pb(pos)
    winner = pos.winner()
    if winner is not None:
        if winner == 0:
            tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
        elif winner == 1:
            tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
        elif winner == 2:
            tk.messagebox.showinfo('返回', '和棋！行棋结束')


def click_move(x, y):
    print(datetime.now())
    global dapu_moves_index
    global moves_index
    global pu_path
    global ai
    global pos
    global search

    ##人机对战
    if x13 <= x <= x14 and y13 >= y >= y14:
        reset()
        ai = True
        pos = Position()
        pos.fromFen("rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1")
        search = Search(pos, 16)
        msg_box = tk.messagebox.askquestion('选择', '选红方吗？（取消将选择黑方）', icon='warning')
        if msg_box == 'yes':
            pass
        else:
            tk.messagebox.showinfo('返回', '电脑执红先行')
            zouzi()
            return

    ##重置
    if x7 <= x <= x8 and y7 >= y >= y8:
        reset()
        ai = False
        return

    ##读谱
    if x1 <= x <= x2 and y1 >= y >= y2:
        # C:\Users\gtedd\OneDrive\Desktop\pu.txt
        # pu_path = Screen().textinput("棋谱路径", "请输入棋谱文件完整路径:")
        ftypes = [('棋谱文件', '*.txt')]
        dlg = filedialog.Open(filetypes=ftypes)
        pu_path = dlg.show()
        dupu(pu_path)

    ##前进
    if x3 <= x <= x4 and y3 >= y >= y4:
        if dapu_moves_index == len(dapu_moves):
            return
        move = dapu_moves[dapu_moves_index]
        print(move, dapu_moves_index)
        dapu_move(move, "jin")
        dapu_moves_index = dapu_moves_index + 1

    ##后退
    if x5 <= x <= x6 and y5 >= y >= y6:
        global moves
        if moves_index == 0:
            return

        if len(moves) > 0:
            moves_index = listbox1.curselection()[0] - 1
            items = listbox1.get(0, END)
            items = list(
                map(lambda e: str(e).split(".")[1].strip() if len(str(e).split(".")) == 2 else str(e).split(".")[
                    0].strip(), items))
            moves_index = len(items)

            if ai:
                i = moves_index - 2
            else:
                i = moves_index - 1
            ii = 0
            reset()
            while ii != i:
                move = items[ii]
                dapu_move(move, "jin")
                ii = ii + 1
            moves_index = ii

            highlight_label()
            if ai:
                pos.undoMakeMove()
                pos.undoMakeMove()

    ##开局
    if x9 <= x <= x10 and y9 >= y >= y10:
        reset()
        dupu(pu_path)

    ##终局
    if x11 <= x <= x12 and y11 >= y >= y12:
        steps = len(dapu_moves)
        print(steps)
        while dapu_moves_index != steps:
            move = dapu_moves[dapu_moves_index]
            dapu_move(move, "jin")
            dapu_moves_index = dapu_moves_index + 1
        print(dapu_moves_index)

    highlight_label()

    if baiqi:
        try:
            for r in range(height_square_number+1):
                for c in range(width_square_number+1):
                    qx,qy=index_to_pos(r,c)
                    rr,cc = board[r][c].r, board[r][c].c
                    if not ( 0<= rr <=height_square_number and 0<=cc<=width_square_number) and dist(board[r][c].x, board[r][c].y, x, y) <= qizi_size / 2:
                        reset_qizi_click()
                        board[r][c].clicked=True
                        raise StopIteration
                    elif dist(x,y, qx,qy) <=qizi_size/2:
                        qizi = find_qizi_clicked()
                        if qizi is not None:
                            qizi.clear()
                            qizi.set_pos(qx,qy)
                            qizi.show()
                            raise StopIteration
        except StopIteration:
            pass

    else:
        # 棋盘
        try:
            for row in board:
                for cell in row:
                    if dist(cell.x, cell.y, x, y) <= qizi_size / 2:
                        if cell.name != "empty":
                            qizi = find_qizi_clicked()
                            if qizi is not None and qizi.side != cell.side:
                                rr, cc = qizi.r, qizi.c
                                qizi.move(cell.x, cell.y)
                                rr1, cc1 = qizi.r, qizi.c
                            else:
                                reset_qizi_click()
                                cell.clicked = True
                            raise StopIteration
                        else:
                            qizi = find_qizi_clicked()
                            if qizi is not None and qizi.name != "empty":
                                rr, cc = qizi.r, qizi.c
                                qizi.move(cell.x, cell.y)
                                rr1, cc1 = qizi.r, qizi.c
                                raise StopIteration
        except StopIteration:
            if qizi is not None and ai:
                user_step = col_label[cc] + str(9 - rr) + "-" + col_label[cc1] + str(9 - rr1)
                user_move = Iccs2move(user_step)
                pos.makeMove(user_move)
                winner = pos.winner()
                if winner is not None:
                    if winner == 0:
                        tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
                    elif winner == 1:
                        tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
                    elif winner == 2:
                        tk.messagebox.showinfo('返回', '和棋！行棋结束')
                else:
                    zouzi()


def draw_dapu():
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

    a1, b1, w, h = startx, starty - (height_square_number + 1) * square_width, square_width * p, square_width * 0.6
    draw_button(a1, b1, w, h, "读   谱")
    global x1, y1, x2, y2
    x1, y1, x2, y2 = a1, b1, a1 + w, b1 - h

    n = (square_width * width_square_number - 7 * square_width * p) / 6

    a2, b2 = startx + square_width * p + n, b1
    draw_button(a2, b2, w, h, "前进>>")
    global x3, y3, x4, y4
    x3, y3, x4, y4 = a2, b2, a2 + w, b2 - h

    a3, b3 = startx + square_width * p * 2 + 2 * n, b1
    draw_button(a3, b3, w, h, "<<后退")
    global x5, y5, x6, y6
    x5, y5, x6, y6 = a3, b3, a3 + w, b3 - h

    a5, b5 = startx + square_width * p * 3 + 3 * n, b1
    draw_button(a5, b5, w, h, "开   局")
    global x9, y9, x10, y10
    x9, y9, x10, y10 = a5, b5, a5 + w, b5 - h

    a6, b6 = startx + square_width * p * 4 + 4 * n, b1
    draw_button(a6, b6, w, h, "终   局")
    global x11, y11, x12, y12
    x11, y11, x12, y12 = a6, b6, a6 + w, b6 - h

    a4, b4 = startx + square_width * p * 5 + 5 * n, b1
    draw_button(a4, b4, w, h, "重   置")
    global x7, y7, x8, y8
    x7, y7, x8, y8 = a4, b4, a4 + w, b4 - h

    a7, b7 = startx + square_width * p * 6 + 6 * n, b1
    draw_button(a7, b7, w, h, "人机对战")
    global x13, y13, x14, y14
    x13, y13, x14, y14 = a7, b7, a7 + w, b7 - h


def main():
    draw_board()
    init_board()
    draw_dapu()
    onscreenclick(click_move)


if __name__ == "__main__":
    main()
    mainloop()
