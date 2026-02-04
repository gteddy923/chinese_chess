import tkinter as tk
from turtle import Screen
from tkinter import Listbox, Scrollbar, SINGLE, W, N, S

from .actions import GameActions, MoveListUI
from .state import get_app
from .voice import VoiceInput


def setup_controls() -> None:
    app = get_app()
    cfg = app.config.board
    ui = app.ui
    canvas = Screen().getcanvas()
    master = canvas.master

    if ui.changzi_button is None:
        ui.changzi_button = tk.Button(master, text="唱 棋", command=VoiceInput.listen_move)
        canvas.create_window(cfg.square_width * -3, (-cfg.square_width) * (cfg.height_square_number // 2 + 2),
                             window=ui.changzi_button)

    if ui.changzi_confirm_button is None:
        ui.changzi_confirm_button = tk.Button(master, text="确 认", command=VoiceInput.confirm_move)
        canvas.create_window(cfg.square_width * -2.3, (-cfg.square_width) * (cfg.height_square_number // 2 + 2),
                             window=ui.changzi_confirm_button)

    if ui.baiqi_button is None:
        ui.baiqi_button = tk.Button(master, text="摆 棋", command=GameActions.baiqi_button_click)
        canvas.create_window(cfg.square_width * -4.4, (-cfg.square_width) * (cfg.height_square_number // 2 + 2),
                             window=ui.baiqi_button)

    if ui.kaishi_button is None:
        ui.kaishi_button = tk.Button(master, text="开 始", command=GameActions.kaishi_button_click)
        canvas.create_window(cfg.square_width * -3.7, (-cfg.square_width) * (cfg.height_square_number // 2 + 2),
                             window=ui.kaishi_button)


def setup_move_lists() -> None:
    app = get_app()
    cfg = app.config.board
    ui = app.ui

    if ui.frame1 is not None and ui.frame2 is not None:
        return

    frame1 = tk.Frame(Screen().getcanvas().master, height=cfg.height_square_number * cfg.square_width,
                      width=(cfg.width_square_number - 5) * cfg.square_width, bg='white')
    scrollbar = tk.Scrollbar(frame1, orient="vertical")
    listbox = tk.Listbox(frame1, activestyle='none', width=20, height=40, selectmode=SINGLE, exportselection=0)

    frame2 = tk.Frame(Screen().getcanvas().master, height=cfg.height_square_number * cfg.square_width,
                      width=(cfg.width_square_number - 5) * cfg.square_width, bg='white')
    scrollbar1 = tk.Scrollbar(frame2, orient="vertical")
    listbox1 = tk.Listbox(frame2, activestyle='none', width=20, height=40, selectmode=SINGLE, exportselection=0)

    Screen().getcanvas().create_window((cfg.width_square_number - 2) * cfg.square_width, 0, window=frame1)
    Screen().getcanvas().create_window(-1 * (cfg.width_square_number - 2) * cfg.square_width, 0, window=frame2)

    frame1.rowconfigure(1, weight=1)
    frame1.columnconfigure(1, weight=1)
    listbox.grid(row=0, column=0, sticky=W)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky=W + N + S)
    scrollbar.config(command=listbox.yview)
    listbox.bind("<<ListboxSelect>>", MoveListUI.dapu_onselect)
    frame1.lower()

    frame2.rowconfigure(1, weight=1)
    frame2.columnconfigure(1, weight=1)
    listbox1.grid(row=0, column=0, sticky=W)
    listbox1.config(yscrollcommand=scrollbar1.set)
    scrollbar1.grid(row=0, column=1, sticky=W + N + S)
    scrollbar1.config(command=listbox1.yview)
    frame2.lower()

    ui.frame1 = frame1
    ui.frame2 = frame2
    ui.scrollbar = scrollbar
    ui.scrollbar1 = scrollbar1
    ui.listbox = listbox
    ui.listbox1 = listbox1
