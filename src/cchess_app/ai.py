import tkinter as tk

from .dependencies import AI_AVAILABLE, move2Iccs, pb
from .state import get_app


class AIEngine:
    @staticmethod
    def make_move():
        if not AI_AVAILABLE:
            tk.messagebox.showinfo(
                "AI unavailable",
                "Install numpy to enable the AI opponent.",
            )
            return
        app = get_app()
        cfg = app.config.board
        ai_cfg = app.config.ai
        state = app.state
        ui = app.ui

        if ui.invalid_move is not None:
            ui.invalid_move.clear()
            ui.invalid_move.write("电脑正在思考", align="center", font=('Arial', 20, 'bold'))
            ui.invalid_move.screen.update()
        mov = state.ai_state.search.searchMain(64, ai_cfg.search_time_ms)
        if ui.invalid_move is not None:
            ui.invalid_move.clear()
        move = move2Iccs(mov)
        f = move.split("-")
        r, c = cfg.height_square_number - int(f[0][1]), cfg.col_labels.index(f[0][0])
        r1, c1 = cfg.height_square_number - int(f[1][1]), cfg.col_labels.index(f[1][0])
        print("zouzi:", r, c, r1, c1)
        state.board[r][c].move(state.board[r1][c1].x, state.board[r1][c1].y)
        state.ai_state.pos.makeMove(mov)
        pb(state.ai_state.pos)
        winner = state.ai_state.pos.winner()
        if winner is not None:
            if winner == 0:
                tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
            elif winner == 1:
                tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
            elif winner == 2:
                tk.messagebox.showinfo('返回', '和棋！行棋结束')
