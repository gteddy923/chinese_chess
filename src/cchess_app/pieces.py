from math import sin, cos, radians
from turtle import Turtle

from .state import CHESS_NAMES, SIDE, get_app
from .utils import BoardGeometry


def _display_moves(pu):
    # Local import avoids circular dependency at import time.
    from .actions import display_moves

    display_moves(False, pu)


class chess:
    caption = ""
    side = None
    r = 0
    c = 0
    clicked = False

    def __init__(self, name, turtle, x, y):
        if name not in CHESS_NAMES:
            raise Exception("name is not valid ", name)
        self.name = name
        self.turtle = turtle
        self.x = x
        self.y = y
        self.r, self.c = BoardGeometry.pos_to_index(x, y)
        if turtle is not None:
            turtle.hideturtle()
            turtle.penup()
            turtle.setposition(x, y)  # print(turtle.position())

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.r, self.c = BoardGeometry.pos_to_index(x, y)

    def move(self, x, y):
        app = get_app()
        cfg = app.config.board
        state = app.state
        ui = app.ui

        if self.check_move(x, y):
            rr = self.r
            cc = self.c
            xx = self.x
            yy = self.y
            temp = state.board[rr][cc]
            self.clear()
            self.x = x
            self.y = y
            self.r, self.c = BoardGeometry.pos_to_index(x, y)
            self.jipu(rr, cc, self.r, self.c)
            eat = False
            if state.board[self.r][self.c].name != "empty":
                eat = True
                state.board[self.r][self.c].clear()
            self.clicked = False
            self.show()
            print(self.side.value + self.caption + " moved to " + str(self.r) + "," + str(self.c))
            if eat:
                state.board[rr][cc] = chess("empty", None, xx, yy)
            else:
                state.board[rr][cc] = state.board[self.r][self.c]
                state.board[rr][cc].set_pos(xx, yy)
            state.board[self.r][self.c] = temp

            # ??
            if ui.draw_prev_pos is not None:
                ui.draw_prev_pos.clear()
                ui.draw_prev_pos.penup()
                ui.draw_prev_pos.goto(xx, yy)
                ui.draw_prev_pos.pendown()
                ui.draw_prev_pos.dot(10, "white")

                ui.draw_prev_pos.pensize(4)
                ui.draw_prev_pos.penup()
                ui.draw_prev_pos.goto(self.x + cfg.qizi_size / 2, y)
                ui.draw_prev_pos.pendown()
                ui.draw_prev_pos.color("yellow")
                for i in range(1, 400):
                    ui.draw_prev_pos.goto(cfg.qizi_size / 2 * cos(radians(i)) + x,
                                          cfg.qizi_size / 2 * sin(radians(i)) + y)

        else:
            BoardGeometry.reset_qizi_click()
            raise Exception("invalid move!")

    def jipu(self, r, c, r1, c1):
        app = get_app()
        cfg = app.config.board
        state = app.state

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
            s = cfg.labels[cfg.width_square_number - c]
        else:
            s = str(c + 1)
        if c == c1:
            if self.side == SIDE.RED:
                e = cfg.labels[abs(r - r1) - 1]
            else:
                e = str(abs(r - r1))
        else:
            if self.side == SIDE.RED:
                e = cfg.labels[cfg.width_square_number - c1]
            else:
                e = c1 + 1

        qh = ""
        if len([z for z in BoardGeometry.board_column(c) if z.name == self.name and z.side == self.side]) == 2:
            rn = [z for z in BoardGeometry.board_column(c) if z.name == self.name and z.r != r][0]
            if rn.r > r:
                qh = "?"
            else:
                qh = "?"
        pu = qh + cap + str(s) + action + str(e)
        print(pu)
        state.history.moves.append(pu)
        state.history.moves_index = state.history.moves_index + 1
        print(state.history.moves_index, state.history.moves)
        _display_moves(pu)

    def check_move(self, x, y) -> bool:
        app = get_app()
        cfg = app.config.board
        state = app.state
        ui = app.ui

        nr, nc = BoardGeometry.pos_to_index(x, y)
        can_move = True

        if state.board[nr][nc].side == self.side:
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

        # ?
        if self.name == "xiang":
            if (self.side == SIDE.RED and nr < 5) or (self.side == SIDE.BLACK and nr > 4):
                can_move = False
                reason = "象/相不能过河"
            elif not (abs(nr - self.r) == 2 and abs(nc - self.c) == 2):
                can_move = False
                reason = "象/相只能走田"
            elif state.board[int((nr + self.r) / 2)][int((nc + self.c) / 2)].name != "empty":
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
            elif nc == self.c and jumapao_road_block(BoardGeometry.board_column(nc), self.r, nr):
                can_move = False
            elif nr == self.r and jumapao_road_block(state.board[nr], self.c, nc):
                can_move = False
            return can_move

        # ?
        if self.name == "ju":
            can_move = check_ju_pao()
            if not can_move:
                reason = "车路上有其它子"
        # ?
        if self.name == "ma":
            if not ((abs(nc - self.c), abs(nr - self.r)) == (1, 2) or (abs(nc - self.c), abs(nr - self.r)) == (2, 1)):
                can_move = False
                reason = "马只能走日"
            elif abs(nc - self.c) == 2 and jumapao_road_block(state.board[self.r], self.c, nc):
                can_move = False
                reason = "马被撇腿"
            elif abs(nr - self.r) == 2 and jumapao_road_block(BoardGeometry.board_column(self.c), self.r, nr):
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

        # ?
        if self.name == "pao":
            if not (nc == self.c or nr == self.r):
                can_move = False
                reason = "炮只能走平或者直"
            elif state.board[nr][nc].name == "empty":
                can_move = check_ju_pao()
                reason = "炮路上有其它子"
            elif state.board[nr][nc].name != "empty" and state.board[nr][nc].side != self.side:
                if nc == self.c and not pao_da_ge_san(BoardGeometry.board_column(nc), self.r, nr):
                    reason = "炮打隔三"
                    can_move = False
                elif nr == self.r and not pao_da_ge_san(state.board[nr], self.c, nc):
                    reason = "炮打隔三"
                    can_move = False
        # ?
        if self.name == "zhu":
            if (self.side == SIDE.RED and nr > self.r) or (self.side == SIDE.BLACK and nr < self.r):
                can_move = False
                reason = "卒/兵不能后退"
            elif ((self.side == SIDE.RED and self.r > 4) or (self.side == SIDE.BLACK and nr < 5)) and abs(nc - self.c) == 1:
                can_move = False
                reason = "卒/兵不能后退"
            elif abs(nr - self.r) not in (1, 0) or abs(nc - self.c) not in (1, 0):
                reason = "卒/兵只能前进或平移一步"
                can_move = False

        if ui.invalid_move is not None:
            ui.invalid_move.clear()
        if not can_move:
            if ui.invalid_move is not None:
                ui.invalid_move.write("错误:" + reason, align="center", font=('Arial', 20, 'bold'))

        return can_move

    def show(self):
        app = get_app()
        cfg = app.config.board

        self.turtle.goto(self.x, self.y)
        self.turtle.dot(cfg.qizi_size, self.side.value)
        self.turtle.goto(self.x, self.y - 10)
        self.turtle.color("white")
        self.turtle.write(self.caption, align="center", font=('Arial', int(cfg.square_width * 0.2), 'bold'))

    def clear(self):
        self.turtle.clear()

    def to_string(self):
        if self.name != "empty":
            return "[" + self.side.value + self.caption + "," + str(self.clicked) + ",(" + str(self.r) + "," + str(
                self.c) + ")]"
        else:
            return "empty"


def init_board():
    app = get_app()
    cfg = app.config.board
    state = app.state

    for r in range(10):
        for c in range(9):
            qizi = None
            if (r == 0 or r == 9) and (c == 0 or c == 8):
                qizi = chess("ju", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                qizi.caption = "车"
            if (r == 0 or r == 9) and (c == 1 or c == 7):
                qizi = chess("ma", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                qizi.caption = "马"
            if (r == 0 or r == 9) and (c == 2 or c == 6):
                qizi = chess("xiang", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                if r == 0:
                    qizi.caption = "象"
                else:
                    qizi.caption = "相"
            if (r == 0 or r == 9) and (c == 3 or c == 5):
                qizi = chess("shi", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                if r == 0:
                    qizi.caption = "士"
                else:
                    qizi.caption = "仕"
            if (r == 0 or r == 9) and (c == 4):
                qizi = chess("shuai", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                if r == 0:
                    qizi.caption = "将"
                else:
                    qizi.caption = "帅"

            if (r == 2 or r == 7) and (c == 1 or c == 7):
                qizi = chess("pao", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
                qizi.caption = "炮"
                if r == 2:
                    qizi.side = SIDE.BLACK
                else:
                    qizi.side = SIDE.RED

            if (r == 3 or r == 6) and (c == 0 or c == 2 or c == 4 or c == 6 or c == 8):
                qizi = chess("zhu", Turtle(), cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)
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
                qizi = chess("empty", None, cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width)

            state.board[r][c] = qizi
            if state.board[r][c].name != 'empty':
                state.board[r][c].show()
