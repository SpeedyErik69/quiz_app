import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER
import asyncio
import random
import sys
from toga.colors import RED

QUIZ_DATEN = {
    "Technik": [
        {"frage": "Was bedeutet CPU?", "antworten": ["Central Processing Unit", "Computer Personal Unit", "Control Program Utility", "Central Power Unit"], "korrekt": 0},
        {"frage": "Welche Firma entwickelte das erste iPhone?", "antworten": ["Apple", "Samsung", "Nokia", "Microsoft"], "korrekt": 0},
        {"frage": "Was ist ein GPU?", "antworten": ["Grafikprozessor", "Speicherchip", "Netzwerkkarte", "Betriebssystem"], "korrekt": 0},
        {"frage": "Welches Betriebssystem nutzt den Linux-Kernel?", "antworten": ["Ubuntu", "Windows", "macOS", "MS-DOS"], "korrekt": 0},
        {"frage": "Wer gilt als Erfinder des WWW?", "antworten": ["Tim Berners-Lee", "Bill Gates", "Steve Jobs", "Linus Torvalds"], "korrekt": 0},
    ],
    "Musik": [
        {"frage": "Wer wird 'King of Pop' genannt?", "antworten": ["Michael Jackson", "Elvis Presley", "Justin Bieber", "Freddie Mercury"], "korrekt": 0},
        {"frage": "Welche Band sang 'Hey Jude'?", "antworten": ["The Beatles", "The Rolling Stones", "Queen", "ABBA"], "korrekt": 0},
        {"frage": "Welches Instrument hat 88 Tasten?", "antworten": ["Klavier", "Gitarre", "Geige", "Trommel"], "korrekt": 0},
        {"frage": "Wer sang 'Shape of You'?", "antworten": ["Ed Sheeran", "Shawn Mendes", "Bruno Mars", "Adele"], "korrekt": 0},
        {"frage": "Welches Land gewann den ESC 2010 mit Lena?", "antworten": ["Deutschland", "Frankreich", "England", "Schweden"], "korrekt": 0},
    ],
    "Sport": [
        {"frage": "Wie viele Spieler hat eine Fußballmannschaft auf dem Feld?", "antworten": ["11", "9", "10", "12"], "korrekt": 0},
        {"frage": "In welcher Sportart gibt es ein Slam Dunk?", "antworten": ["Basketball", "Volleyball", "Handball", "Tennis"], "korrekt": 0},
        {"frage": "Wie viele Ringe hat das Olympische Symbol?", "antworten": ["5", "4", "6", "7"], "korrekt": 0},
        {"frage": "Wer ist bekannt als 'GOAT' im Fußball?", "antworten": ["Lionel Messi", "Cristiano Ronaldo", "Pelé", "Maradona"], "korrekt": 0},
        {"frage": "In welcher Sportart gibt es einen Homerun?", "antworten": ["Baseball", "Cricket", "Hockey", "Rugby"], "korrekt": 0},
    ],
}

class QuizApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name, size=(600, 800))
        self.show_startseite()

    def show_startseite(self):
        box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=40))
        box.add(toga.Label("Willkommen zur Quiz-App", style=Pack(padding=20, font_size=28)))
        for kategorie in QUIZ_DATEN.keys():
            btn = toga.Button(
                kategorie,
                on_press=lambda w, k=kategorie: self.start_quiz(k),
                style=Pack(padding=10, width=300, font_size=18)
            )
            box.add(btn)
        self.main_window.content = box
        self.main_window.show()

    def start_quiz(self, kategorie):
        self.kategorie = kategorie
        self.fragen = random.sample(QUIZ_DATEN[kategorie], len(QUIZ_DATEN[kategorie]))
        self.frage_index = 0
        self.punkte = 0
        self.remaining_time = 40
        self.show_frage()

    def show_frage(self):
        if self.frage_index >= len(self.fragen):
            self.show_ergebnis()
            return
        frage = self.fragen[self.frage_index]

        antworten = frage["antworten"][:]
        random.shuffle(antworten)
        self.antworten = antworten
        self.korrekte_antwort = frage["antworten"][frage["korrekt"]]

        self.quiz_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=30))
        self.frage_label = toga.Label(frage["frage"], style=Pack(padding=20, font_size=22))
        self.quiz_box.add(self.frage_label)
        self.feedback_label = toga.Label("", style=Pack(padding=10, font_size=18))
        self.quiz_box.add(self.feedback_label)
        self.antwort_buttons = []
        for antwort in antworten:
            btn = toga.Button(
                antwort,
                on_press=lambda w, a=antwort: self.check_antwort(a),
                style=Pack(padding=8, width=300, font_size=16)
            )
            self.quiz_box.add(btn)
            self.antwort_buttons.append(btn)
        self.timer_label = toga.Label(f"Zeit: {self.remaining_time}", style=Pack(padding=15, font_size=18))
        self.quiz_box.add(self.timer_label)
        pause_btn = toga.Button("Pause", on_press=self.pause_quiz, style=Pack(padding=10, width=200, font_size=16))
        self.quiz_box.add(pause_btn)
        self.next_btn = toga.Button("Weiter", on_press=self.naechste_frage, style=Pack(padding=10, width=200, font_size=16))
        self.next_btn.enabled = False
        self.quiz_box.add(self.next_btn)
        self.main_window.content = self.quiz_box
        self.start_timer()

    def start_timer(self):
        if hasattr(self, "timer_task") and self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.ensure_future(self.run_timer())

    async def run_timer(self):
        while self.remaining_time > 0:
            self.timer_label.text = f"Zeit: {self.remaining_time}"
            await asyncio.sleep(1)
            self.remaining_time -= 1
        self.check_antwort(None)

    def check_antwort(self, antwort):
        if self.timer_task:
            self.timer_task.cancel()
        for btn in self.antwort_buttons:
            btn.enabled = False
        if antwort == self.korrekte_antwort:
            self.punkte += 1
            self.feedback_label.text = "✅ Richtig!"
        else:
            if antwort is None:
                self.feedback_label.text = f"⏰ Zeit abgelaufen! Richtige Antwort: {self.korrekte_antwort}"
            else:
                self.feedback_label.text = f"❌ Falsch! Richtige Antwort: {self.korrekte_antwort}"
        self.next_btn.enabled = True

    def naechste_frage(self, widget):
        self.frage_index += 1
        self.remaining_time = 40
        self.show_frage()

    def pause_quiz(self, widget):
        if self.timer_task:
            self.timer_task.cancel()
        self.paused_content = self.main_window.content
        box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=40))
        box.add(toga.Label("Pause", style=Pack(padding=20, font_size=24)))
        fortsetzen_btn = toga.Button("Fortsetzen", on_press=self.fortsetzen_quiz, style=Pack(padding=10, width=250, font_size=18))
        hauptmenue_btn = toga.Button("Hauptmenü", on_press=lambda w: self.show_startseite(), style=Pack(padding=10, width=250, font_size=18))
        neu_btn = toga.Button("Neu starten", on_press=lambda w: self.start_quiz(self.kategorie), style=Pack(padding=10, width=250, font_size=18))
        box.add(fortsetzen_btn)
        box.add(hauptmenue_btn)
        box.add(neu_btn)
        # Beenden-Button mit rotem Power-Symbol
        self.add_beenden_button(box)
        self.main_window.content = box

    def add_beenden_button(self, container):
        btn_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=20))
        btn = toga.Button("⏻", on_press=lambda w: sys.exit(0),
                          style=Pack(background_color=RED, color='white', font_size=48, padding=10, width=100, height=100))
        btn_box.add(btn)
        label = toga.Label("Spiel Beenden", style=Pack(padding_top=10, font_size=18, alignment=CENTER))
        btn_box.add(label)
        container.add(btn_box)

    def fortsetzen_quiz(self, widget):
        self.main_window.content = self.paused_content
        self.start_timer()

    def show_ergebnis(self):
        box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=40))
        ergebnis_text = f"Ergebnis: {self.punkte} von {len(self.fragen)} richtig."
        ergebnis_label = toga.Label(ergebnis_text, style=Pack(padding=20, font_size=26, width=500), alignment=CENTER)
        box.add(ergebnis_label)
        hauptmenue_btn = toga.Button("Zurück zum Hauptmenü", on_press=lambda w: self.show_startseite(),
                                     style=Pack(padding=15, width=300, font_size=20))
        neu_btn = toga.Button("Quiz erneut starten", on_press=lambda w: self.start_quiz(self.kategorie),
                             style=Pack(padding=15, width=300, font_size=20))
        box.add(hauptmenue_btn)
        box.add(neu_btn)
        # Beenden-Button auf Ergebnis-Bildschirm
        self.add_beenden_button(box)
        self.main_window.content = box

def main():
    return QuizApp()

