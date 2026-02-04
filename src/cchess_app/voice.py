from .ai import AIEngine
from .state import get_app


class VoiceInput:
    @staticmethod
    def listen_move():
        import tkinter as tk

        from .dependencies import PYAUDIO_AVAILABLE, SOUNDDEVICE_AVAILABLE, sd, sr
        if sr is None:
            tk.messagebox.showinfo(
                "Voice input unavailable",
                "Install SpeechRecognition to enable voice input.",
            )
            return
        app = get_app()
        state = app.state
        ui = app.ui

        if ui.invalid_move is not None:
            ui.invalid_move.clear()
            ui.invalid_move.write("请唱棋例如，马二进三", align="center", font=('Arial', 20, 'bold'))
            ui.invalid_move.screen.update()
        if PYAUDIO_AVAILABLE:
            try:
                with sr.Microphone() as source:
                    state.voice_state.recognizer.adjust_for_ambient_noise(source)
                    the_audio = state.voice_state.recognizer.listen(source)
            except AttributeError:
                tk.messagebox.showinfo(
                    "Voice input unavailable",
                    "Install PyAudio to enable microphone input.",
                )
                return
        elif SOUNDDEVICE_AVAILABLE:
            if ui.invalid_move is not None:
                ui.invalid_move.clear()
                ui.invalid_move.write("录音中…", align="center", font=('Arial', 20, 'bold'))
                ui.invalid_move.screen.update()
            samplerate = 16000
            duration = 4.0
            try:
                recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
                sd.wait()
                the_audio = sr.AudioData(recording.tobytes(), samplerate, 2)
            except Exception:
                tk.messagebox.showinfo(
                    "Voice input unavailable",
                    "Microphone recording failed. Check device permissions.",
                )
                return
        else:
            tk.messagebox.showinfo(
                "Voice input unavailable",
                "Install sounddevice or PyAudio to enable microphone input.",
            )
            return
        try:
            text = state.voice_state.recognizer.recognize_google(the_audio, language='zh-CN')
            text = text.strip() if text is not None else ""
            if not text:
                state.voice_state.pending_move = None
                tk.messagebox.showinfo(
                    "Voice input",
                    "No move recognized. Please try 唱棋 again.",
                )
                return
            state.voice_state.pending_move = text
            if ui.invalid_move is not None:
                ui.invalid_move.clear()
                ui.invalid_move.write(state.voice_state.pending_move, align="center", font=('Arial', 20, 'bold'))
                ui.invalid_move.screen.update()
        except sr.UnknownValueError:
            state.voice_state.pending_move = None
            tk.messagebox.showinfo(
                "Voice input",
                "Could not understand audio. Please try 唱棋 again.",
            )

    @staticmethod
    def confirm_move():
        import tkinter as tk

        from .actions import GameActions
        from .dependencies import Iccs2move, sr
        if sr is None:
            tk.messagebox.showinfo(
                "Voice input unavailable",
                "Install SpeechRecognition to enable voice input.",
            )
            return
        app = get_app()
        cfg = app.config.board
        state = app.state

        pending_move = state.voice_state.pending_move
        if not pending_move:
            tk.messagebox.showinfo(
                "Voice input",
                "No pending move. Please use 唱棋 first.",
            )
            return

        r, c, r1, c1 = GameActions.dapu_move(pending_move, "jin")

        if state.ai_enabled:
            user_step = cfg.col_labels[c] + str(r) + "-" + cfg.col_labels[c1] + str(r1)
            user_move = Iccs2move(user_step)
            state.ai_state.pos.makeMove(user_move)
            winner = state.ai_state.pos.winner()
            if winner is not None:
                if winner == 0:
                    tk.messagebox.showinfo('返回', '红方胜利！行棋结束')
                elif winner == 1:
                    tk.messagebox.showinfo('返回', '黑方胜利！行棋结束')
                elif winner == 2:
                    tk.messagebox.showinfo('返回', '和棋！行棋结束')
            else:
                AIEngine.make_move()
