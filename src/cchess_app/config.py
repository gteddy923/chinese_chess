from dataclasses import dataclass, field


DEFAULT_LABELS = ("一", "二", "三", "四", "五", "六", "七", "八", "九")
DEFAULT_COL_LABELS = ("A", "B", "C", "D", "E", "F", "G", "H", "I")


@dataclass
class BoardConfig:
    square_width: int = 65
    width_square_number: int = 8
    height_square_number: int = 9
    deco_distance: int = 5
    pu_button_width: int = 65
    pu_button_height: int = 28
    pu_button_group: int = 50
    labels: tuple[str, ...] = field(default_factory=lambda: DEFAULT_LABELS)
    col_labels: tuple[str, ...] = field(default_factory=lambda: DEFAULT_COL_LABELS)

    @property
    def startx(self) -> float:
        return 0 - self.width_square_number / 2 * self.square_width

    @property
    def starty(self) -> float:
        return 0 + self.height_square_number / 2 * self.square_width

    @property
    def qizi_size(self) -> int:
        return int(self.square_width * 0.7)

    @property
    def board_rows(self) -> int:
        return self.height_square_number + 1

    @property
    def board_cols(self) -> int:
        return self.width_square_number + 1


@dataclass
class AIConfig:
    search_time_ms: int = 5000


@dataclass
class AppConfig:
    board: BoardConfig = field(default_factory=BoardConfig)
    ai: AIConfig = field(default_factory=AIConfig)
