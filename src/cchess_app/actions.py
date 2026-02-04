from datetime import datetime

import tkinter as tk
from tkinter import filedialog, END
from tkinter.filedialog import asksaveasfile

from .ai import AIEngine
from .dependencies import AI_AVAILABLE, Iccs2move, Position, Search
from .pieces import init_board
from .state import SIDE, get_app
from .utils import BoardGeometry


def baiqi_button_click() -> None:
    app = get_app()
    cfg = app.config.board
    state = app.state
    state.baiqi_mode = True
    rcount = 0
    bcount = 0
    bx, by = ((cfg.width_square_number // 2 + 2) * cfg.square_width) * -1, cfg.height_square_number // 2 * cfg.square_width
    rx, ry = ((cfg.width_square_number // 2 + 1) * cfg.square_width), cfg.height_square_number // 2 * cfg.square_width
    for i in range(0, cfg.height_square_number + 1):
        for j in range(0, cfg.width_square_number + 1):
            if state.board[i][j].name != "empty":
                if state.board[i][j].side == SIDE.BLACK:
                    state.board[i][j].clear()
                    state.board[i][j].set_pos(bx + bcount % 2 * cfg.square_width, by - bcount // 2 * cfg.square_width)
                    state.board[i][j].show()
                    bcount = bcount + 1
                if state.board[i][j].side == SIDE.RED:
                    state.board[i][j].clear()
                    state.board[i][j].set_pos(rx + rcount % 2 * cfg.square_width, ry - rcount // 2 * cfg.square_width)
                    state.board[i][j].show()
                    rcount = rcount + 1


def kaishi_button_click() -> None:
    app = get_app()
    cfg = app.config.board
    state = app.state
    state.baiqi_mode = False
    for r in range(cfg.height_square_number + 1):
        for c in range(cfg.width_square_number + 1):
            rr, cc = state.board[r][c].r, state.board[r][c].c
            if not (0 <= rr <= cfg.height_square_number and 0 <= cc <= cfg.width_square_number):
                state.board[r][c].name = "empty"
                state.board[r][c].side = SIDE.NONE
                x, y = BoardGeometry.index_to_pos(r, c)
                state.board[r][c].set_pos(x, y)
                state.board[r][c].clear()
            state.board[r][c].clicked = False


def save_button_click() -> None:
    app = get_app()
    history = app.state.history
    ftypes = [('棋谱文件', '*.txt')]
    f = asksaveasfile(initialfile="棋谱.txt", defaultextension=".txt", filetypes=ftypes)
    if f is None:
        return
    f.close()
    f1 = open(f.name, "w", encoding="utf-8")
    i = 0
    if len(history.moves) > 0:
        for m in history.moves:
            if not i % 2:
                l = (str(i // 2 + 1) + "." + history.moves[i])
                print(l)
                f1.write(l)
            else:
                l = (" " + history.moves[i] + "\n")
                print(l)
                f1.write(l)
            i = i + 1
    f1.flush()
    f1.close()


def dapu_move(move: str, direction: str):
    app = get_app()
    cfg = app.config.board
    state = app.state

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

    if s in cfg.labels:
        side = SIDE.RED
        step = cfg.labels.index(e) - cfg.labels.index(s)
        column = cfg.width_square_number - cfg.labels.index(s)
        ystep1 = cfg.labels.index(e) + 1
    else:
        side = SIDE.BLACK
        step = int(e) - int(s)
        column = int(s) - 1
        ystep1 = int(e)
    ystep = 0
    if abs(step) == 1:
        ystep = 2
    if abs(step) == 2:
        ystep = 1

    count = 0
    potential_qizi = []
    for q in BoardGeometry.board_column(column):
        if q.caption == cap and q.side == side:
            count = count + 1
            potential_qizi.append(q)

    if count == 2:
        print("two qizi on the same col")

    gotox, gotoy = 0, 0

    def get_goto(cell, action):
        if action == "平":
            if side == SIDE.RED:
                gotox, gotoy = cell.x - step * cfg.square_width, cell.y
            if side == SIDE.BLACK:
                gotox, gotoy = cell.x + step * cfg.square_width, cell.y
        elif action == "进" or action == "退":
            scalar = 1
            if action == "退":
                scalar = -1
            if cell.caption == "马":
                if side == SIDE.RED:
                    gotox, gotoy = cell.x - step * cfg.square_width, cell.y + scalar * ystep * cfg.square_width
                if side == SIDE.BLACK:
                    gotox, gotoy = cell.x + step * cfg.square_width, cell.y - scalar * ystep * cfg.square_width
            elif cell.caption == "象" or cell.caption == "相" or cell.caption == "士" or cell.caption == "仕":
                if side == SIDE.RED:
                    gotox, gotoy = cell.x - step * cfg.square_width, cell.y + scalar * abs(step) * cfg.square_width
                if side == SIDE.BLACK:
                    gotox, gotoy = cell.x + step * cfg.square_width, cell.y - scalar * abs(step) * cfg.square_width
            else:
                if side == SIDE.RED:
                    gotox, gotoy = cell.x, cell.y + scalar * ystep1 * cfg.square_width
                if side == SIDE.BLACK:
                    gotox, gotoy = cell.x, cell.y - scalar * ystep1 * cfg.square_width
        return gotox, gotoy

    try:
        for row in state.board:
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
                            max = cfg.height_square_number + 2
                            for q1 in potential_qizi:
                                if q1.r > min:
                                    min = q1.r
                                    big = q1
                                if q1.r < max:
                                    max = q1.r
                                    small = q1
                            if (qh == "前" and cell.side == SIDE.RED) or (qh == "后" and cell.side == SIDE.BLACK):
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


def highlight_label() -> None:
    app = get_app()
    ui = app.ui
    history = app.state.history
    if ui.listbox is None or ui.listbox1 is None:
        return
    ui.listbox.selection_clear(0, END)
    ui.listbox1.selection_clear(0, END)
    if len(history.moves) > 0 and history.moves_index > 0:
        ui.listbox.selection_set(history.moves_index - 1, history.moves_index - 1)
        ui.listbox.see(history.moves_index - 1)
        ui.listbox1.selection_set(history.moves_index - 1, history.moves_index - 1)
        ui.listbox1.see(history.moves_index - 1)


def click_label(event, mov: str, dapu: bool, i: int) -> None:
    app = get_app()
    state = app.state
    history = state.history
    print("clicked ", mov, dapu, i)
    if dapu:
        reset()
        dupu(state.pu_path)
        history.dapu_moves_index = i
        ii = 0
        while ii != history.dapu_moves_index:
            move = history.dapu_moves[ii]
            dapu_move(move, "jin")
            ii = ii + 1
        highlight_label()


def dapu_onselect(event) -> None:
    app = get_app()
    state = app.state
    history = state.history
    ui = app.ui
    if ui.listbox is None or ui.listbox1 is None:
        return
    if not event.widget.curselection():
        return

    selection = event.widget.curselection()

    if selection:
        reset()
        dupu(state.pu_path)
        ui.listbox1.delete(0, END)
        index = selection[0]
        data = event.widget.get(index)
        print(index, data)
        ii = 0
        while ii != index + 1:
            move = history.dapu_moves[ii]
            dapu_move(move, "jin")
            ii = ii + 1
        history.moves_index = ii
        history.dapu_moves_index = ii
        ui.listbox.activate(index)
        ui.listbox.selection_set(index, index)
        ui.listbox.see(index)
        ui.listbox1.activate(index)
        ui.listbox1.selection_set(index, index)
        ui.listbox1.see(index)


def display_moves(dapu: bool, mov: str) -> None:
    app = get_app()
    history = app.state.history
    ui = app.ui
    if ui.listbox is None or ui.listbox1 is None:
        return

    if dapu:
        i = len(history.dapu_moves) - 1
        t = history.dapu_moves[i]
    else:
        i = len(history.moves) - 1
        if ui.save_button is not None:
            ui.save_button.lift()
        t = history.moves[i]
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
        ui.listbox1.insert(END, t1)
        if ui.frame2 is not None:
            ui.frame2.lift()
        ui.listbox.insert(END, t1)
        if ui.frame1 is not None:
            ui.frame1.lift()
        ui.listbox1.selection_set(END)
        ui.listbox1.see(END)
        ui.listbox.selection_set(END)
        ui.listbox.see(END)
        ui.listbox.selection_clear(0, END)
        ui.listbox1.selection_clear(0, END)
    else:
        ui.listbox1.selection_clear(0, END)
        ui.listbox1.insert(END, t1)
        ui.listbox1.selection_set(END)
        ui.listbox1.see(END)
        if ui.frame2 is not None:
            ui.frame2.lift()


def clear_widgets() -> None:
    app = get_app()
    history = app.state.history
    ui = app.ui

    history.clear()
    if ui.listbox is not None:
        ui.listbox.delete(0, END)
    if ui.listbox1 is not None:
        ui.listbox1.delete(0, END)
    if ui.frame1 is not None:
        ui.frame1.lower()
    if ui.frame2 is not None:
        ui.frame2.lower()


def reset() -> None:
    app = get_app()
    state = app.state
    ui = app.ui
    for row in state.board:
        for cell in row:
            if cell.turtle is not None:
                cell.clear()
    init_board()
    clear_widgets()
    if ui.draw_prev_pos is not None:
        ui.draw_prev_pos.clear()
    if ui.invalid_move is not None:
        ui.invalid_move.clear()
    if ui.save_button is not None:
        ui.save_button.lower()


def dupu(path: str) -> None:
    app = get_app()
    state = app.state
    history = state.history
    if path != "":
        reset()
        print(path)
        lines = open(path.strip(), encoding="utf-8")
        for line in lines:
            m = line.strip().split(".")[1].split(" ")
            if len(m) == 2:
                history.dapu_moves.append(m[0])
                display_moves(True, m[0])
                history.dapu_moves.append(m[1])
                display_moves(True, m[1])
            else:
                history.dapu_moves.append(m[0])
                display_moves(True, m[0])
        history.dapu_moves_index = 0
    for row in state.board:
        for cell in row:
            cell.dapu_move = True


def _rebuild_dapu_lists(saved_moves: list[str]) -> None:
    app = get_app()
    history = app.state.history
    if not saved_moves:
        return
    history.dapu_moves = []
    for move in saved_moves:
        history.dapu_moves.append(move)
        display_moves(True, move)
    history.dapu_moves_index = 0


def click_move(x: float, y: float) -> None:
    app = get_app()
    cfg = app.config.board
    state = app.state
    history = state.history
    ui = app.ui
    ai_state = state.ai_state

    print(datetime.now())

    if ui.hitboxes.ai.contains(x, y):
        if not AI_AVAILABLE:
            tk.messagebox.showinfo(
                "AI unavailable",
                "Install numpy to enable the AI opponent.",
            )
            return
        reset()
        state.ai_enabled = True
        ai_state.pos = Position()
        ai_state.pos.fromFen("rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1")
        ai_state.search = Search(ai_state.pos, 16)
        msg_box = tk.messagebox.askquestion('选择', '选红方吗？（取消将选择黑方', icon='warning')
        if msg_box == 'yes':
            pass
        else:
            tk.messagebox.showinfo('返回', '电脑执红先行')
            AIEngine.make_move()
            return

    if ui.hitboxes.reset.contains(x, y):
        reset()
        state.ai_enabled = False
        return

    if ui.hitboxes.read.contains(x, y):
        ftypes = [('棋谱文件', '*.txt')]
        dlg = filedialog.Open(filetypes=ftypes)
        state.pu_path = dlg.show()
        dupu(state.pu_path)

    if ui.hitboxes.forward.contains(x, y):
        if history.dapu_moves_index == len(history.dapu_moves):
            return
        move = history.dapu_moves[history.dapu_moves_index]
        print(move, history.dapu_moves_index)
        dapu_move(move, "jin")
        history.dapu_moves_index = history.dapu_moves_index + 1

    if ui.hitboxes.back.contains(x, y):
        if history.dapu_moves:
            if history.dapu_moves_index == 0:
                return
            target_index = history.dapu_moves_index - 1
            saved_dapu = history.dapu_moves.copy()
            reset()
            _rebuild_dapu_lists(saved_dapu)
            for idx in range(target_index):
                move = saved_dapu[idx]
                dapu_move(move, "jin")
                history.dapu_moves_index = history.dapu_moves_index + 1
            highlight_label()
            return
        if history.moves_index == 0:
            return

        if len(history.moves) > 0 and ui.listbox1 is not None:
            selection = ui.listbox1.curselection()
            if not selection:
                return
            history.moves_index = selection[0] - 1
            items = ui.listbox1.get(0, END)
            items = list(
                map(lambda e: str(e).split(".")[1].strip() if len(str(e).split(".")) == 2 else str(e).split(".")[
                    0].strip(), items))
            history.moves_index = len(items)

            if state.ai_enabled:
                i = history.moves_index - 2
            else:
                i = history.moves_index - 1
            ii = 0
            reset()
            while ii != i:
                move = items[ii]
                dapu_move(move, "jin")
                ii = ii + 1
            history.moves_index = ii

            highlight_label()
            if state.ai_enabled and ai_state.pos is not None:
                ai_state.pos.undoMakeMove()
                ai_state.pos.undoMakeMove()

    if ui.hitboxes.start.contains(x, y):
        reset()
        dupu(state.pu_path)

    if ui.hitboxes.end.contains(x, y):
        steps = len(history.dapu_moves)
        print(steps)
        while history.dapu_moves_index != steps:
            move = history.dapu_moves[history.dapu_moves_index]
            dapu_move(move, "jin")
            history.dapu_moves_index = history.dapu_moves_index + 1
        print(history.dapu_moves_index)

    highlight_label()

    if state.baiqi_mode:
        try:
            for r in range(cfg.height_square_number + 1):
                for c in range(cfg.width_square_number + 1):
                    qx, qy = BoardGeometry.index_to_pos(r, c)
                    rr, cc = state.board[r][c].r, state.board[r][c].c
                    if not (0 <= rr <= cfg.height_square_number and 0 <= cc <= cfg.width_square_number) and \
                            BoardGeometry.dist(state.board[r][c].x, state.board[r][c].y, x, y) <= cfg.qizi_size / 2:
                        BoardGeometry.reset_qizi_click()
                        state.board[r][c].clicked = True
                        raise StopIteration
                    elif BoardGeometry.dist(x, y, qx, qy) <= cfg.qizi_size / 2:
                        qizi = BoardGeometry.find_qizi_clicked()
                        if qizi is not None:
                            qizi.clear()
                            qizi.set_pos(qx, qy)
                            qizi.show()
                            raise StopIteration
        except StopIteration:
            pass

    else:
        qizi = None
        rr = cc = rr1 = cc1 = 0
        try:
            for row in state.board:
                for cell in row:
                    if BoardGeometry.dist(cell.x, cell.y, x, y) <= cfg.qizi_size / 2:
                        if cell.name != "empty":
                            qizi = BoardGeometry.find_qizi_clicked()
                            if qizi is not None and qizi.side != cell.side:
                                rr, cc = qizi.r, qizi.c
                                qizi.move(cell.x, cell.y)
                                rr1, cc1 = qizi.r, qizi.c
                            else:
                                BoardGeometry.reset_qizi_click()
                                cell.clicked = True
                            raise StopIteration
                        else:
                            qizi = BoardGeometry.find_qizi_clicked()
                            if qizi is not None and qizi.name != "empty":
                                rr, cc = qizi.r, qizi.c
                                qizi.move(cell.x, cell.y)
                                rr1, cc1 = qizi.r, qizi.c
                                raise StopIteration
        except StopIteration:
            if qizi is not None and state.ai_enabled:
                user_step = cfg.col_labels[cc] + str(cfg.height_square_number - rr) + "-" + \
                            cfg.col_labels[cc1] + str(cfg.height_square_number - rr1)
                user_move = Iccs2move(user_step)
                ai_state.pos.makeMove(user_move)
                winner = ai_state.pos.winner()
                if winner is not None:
                    if winner == 0:
                        tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
                    elif winner == 1:
                        tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
                    elif winner == 2:
                        tk.messagebox.showinfo('返回', '和棋！行棋结束')
                else:
                    AIEngine.make_move()


class MoveListUI:
    @staticmethod
    def display_moves(dapu: bool, mov: str) -> None:
        return display_moves(dapu, mov)

    @staticmethod
    def highlight_label() -> None:
        return highlight_label()

    @staticmethod
    def click_label(event, mov: str, dapu: bool, i: int) -> None:
        return click_label(event, mov, dapu, i)

    @staticmethod
    def dapu_onselect(event) -> None:
        return dapu_onselect(event)


class GameActions:
    @staticmethod
    def baiqi_button_click() -> None:
        return baiqi_button_click()

    @staticmethod
    def kaishi_button_click() -> None:
        return kaishi_button_click()

    @staticmethod
    def save_button_click() -> None:
        return save_button_click()

    @staticmethod
    def dapu_move(move: str, direction: str):
        return dapu_move(move, direction)

    @staticmethod
    def clear_widgets() -> None:
        return clear_widgets()

    @staticmethod
    def reset() -> None:
        return reset()

    @staticmethod
    def dupu(path: str) -> None:
        return dupu(path)

    @staticmethod
    def click_move(x: float, y: float) -> None:
        return click_move(x, y)
