from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from turtle import Turtle
import tkinter as tk
from tkinter import Frame, Listbox, Scrollbar

from .config import AppConfig
from .dependencies import sr


class SIDE(Enum):
    RED = "red"
    BLACK = "black"
    NONE = None


CHESS_NAMES = ("empty", "shuai", "shi", "xiang", "ju", "ma", "pao", "zhu")
chess_names = CHESS_NAMES


@dataclass
class MoveHistory:
    moves: list[str] = field(default_factory=list)
    dapu_moves: list[str] = field(default_factory=list)
    moves_index: int = 0
    dapu_moves_index: int = 0

    def clear(self) -> None:
        self.moves.clear()
        self.dapu_moves.clear()
        self.moves_index = 0
        self.dapu_moves_index = 0


@dataclass
class AIState:
    pos: Optional[object] = None
    search: Optional[object] = None


def _create_recognizer() -> Optional[object]:
    if sr is None:
        return None
    return sr.Recognizer()


@dataclass
class VoiceState:
    recognizer: Optional[object] = field(default_factory=_create_recognizer)
    pending_move: Optional[str] = None


@dataclass
class HitBox:
    x1: float = 0.0
    y1: float = 0.0
    x2: float = 0.0
    y2: float = 0.0

    def contains(self, x: float, y: float) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 >= y >= self.y2


@dataclass
class ButtonHitBoxes:
    read: HitBox = field(default_factory=HitBox)
    forward: HitBox = field(default_factory=HitBox)
    back: HitBox = field(default_factory=HitBox)
    reset: HitBox = field(default_factory=HitBox)
    start: HitBox = field(default_factory=HitBox)
    end: HitBox = field(default_factory=HitBox)
    ai: HitBox = field(default_factory=HitBox)


@dataclass
class UIState:
    invalid_move: Optional[Turtle] = None
    draw_prev_pos: Optional[Turtle] = None
    save_button: Optional[tk.Button] = None
    changzi_button: Optional[tk.Button] = None
    changzi_confirm_button: Optional[tk.Button] = None
    baiqi_button: Optional[tk.Button] = None
    kaishi_button: Optional[tk.Button] = None
    frame1: Optional[Frame] = None
    frame2: Optional[Frame] = None
    listbox: Optional[Listbox] = None
    listbox1: Optional[Listbox] = None
    scrollbar: Optional[Scrollbar] = None
    scrollbar1: Optional[Scrollbar] = None
    hitboxes: ButtonHitBoxes = field(default_factory=ButtonHitBoxes)


@dataclass
class GameState:
    config: AppConfig
    board: list[list[Optional[object]]] = field(init=False)
    history: MoveHistory = field(default_factory=MoveHistory)
    baiqi_mode: bool = False
    ai_enabled: bool = False
    pu_path: str = ""
    ai_state: AIState = field(default_factory=AIState)
    voice_state: VoiceState = field(default_factory=VoiceState)

    def __post_init__(self) -> None:
        rows = self.config.board.board_rows
        cols = self.config.board.board_cols
        self.board = [[None] * cols for _ in range(rows)]


class CChessApp:
    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or AppConfig()
        self.state = GameState(self.config)
        self.ui = UIState()

    def run(self) -> None:
        from turtle import onscreenclick

        from .actions import GameActions
        from .pieces import init_board
        from .ui_board import draw_board, draw_dapu
        from .ui_controls import setup_controls, setup_move_lists

        draw_board()
        setup_controls()
        setup_move_lists()
        init_board()
        draw_dapu()
        onscreenclick(GameActions.click_move)


_APP: Optional[CChessApp] = None


def get_app() -> CChessApp:
    global _APP
    if _APP is None:
        _APP = CChessApp()
    return _APP
