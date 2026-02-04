from math import sqrt

from .state import get_app


class BoardGeometry:
    @staticmethod
    def pos_to_index(x, y):
        cfg = get_app().config.board
        return int((cfg.starty - y) / cfg.square_width), int((x - cfg.startx) / cfg.square_width)

    @staticmethod
    def index_to_pos(r, c):
        cfg = get_app().config.board
        return cfg.startx + c * cfg.square_width, cfg.starty - r * cfg.square_width

    @staticmethod
    def column(matrix, i):
        return [row[i] for row in matrix]

    @staticmethod
    def dist(x, y, x1, y1):
        return sqrt((x - x1) ** 2 + (y - y1) ** 2)

    @staticmethod
    def board_column(col):
        return BoardGeometry.column(get_app().state.board, col)

    @staticmethod
    def reset_qizi_click():
        for row in get_app().state.board:
            for cell in row:
                cell.clicked = False

    @staticmethod
    def find_qizi_clicked():
        for row in get_app().state.board:
            for cell in row:
                if cell.clicked:
                    return cell
        return None
