import json
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex("#F2F5FA")


class BPTrackerApp(App):

    def build(self):
        self.title = "BP Tracker"
        self.readings = self.load_readings()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10)
        )

        header = Label(
            text="[b]BP TRACKER[/b]\nOffline Blood Pressure Log",
            markup=True,
            font_size=22,
            color=get_color_from_hex("#17365D"),
            size_hint_y=None,
            height=dp(75)
        )
        root.add_widget(header)

        form = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180)
        )

        self.sys_input = self.make_input("e.g. 120")
        self.dia_input = self.make_input("e.g. 80")
        self.pulse_input = self.make_input("e.g. 72")

        fields = [
            ("Systolic (mmHg)", self.sys_input),
            ("Diastolic (mmHg)", self.dia_input),
            ("Pulse (BPM)", self.pulse_input),
        ]

        for title, widget in fields:
            form.add_widget(Label(
                text=title,
                color=get_color_from_hex("#24364B"),
                font_size=15
            ))
            form.add_widget(widget)

        root.add_widget(form)

        self.status_label = Label(
            text="Enter your blood pressure reading",
            color=get_color_from_hex("#334155"),
            size_hint_y=None,
            height=dp(45),
            font_size=14
        )
        root.add_widget(self.status_label)

        save_btn = Button(
            text="SAVE READING",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=get_color_from_hex("#1769AA"),
            color=(1, 1, 1, 1),
            font_size=18,
            bold=True
        )
        save_btn.bind(on_press=self.save_reading)
        root.add_widget(save_btn)

        root.add_widget(Label(
            text="[b]SAVED READINGS[/b]",
            markup=True,
            color=get_color_from_hex("#17365D"),
            size_hint_y=None,
            height=dp(35),
            font_size=18
        ))

        scroll = ScrollView()
        self.history_box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(4),
            size_hint_y=None
        )
        self.history_box.bind(
            minimum_height=self.history_box.setter("height")
        )

        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        self.refresh_history()
        return root

    def make_input(self, hint):
        return TextInput(
            hint_text=hint,
            input_filter="int",
            multiline=False,
            font_size=18,
            size_hint_y=None,
            height=dp(48),
            padding=dp(10)
        )

    def classify_bp(self, systolic, diastolic):
        if systolic >= 180 or diastolic >= 120:
            return "Very High - Crisis Range"
        if systolic >= 140 or diastolic >= 90:
            return "High Blood Pressure - Stage 2"
        if systolic >= 130 or diastolic >= 80:
            return "High Blood Pressure - Stage 1"
        if systolic >= 120 and diastolic < 80:
            return "Elevated"
        return "Normal Range"

    def save_reading(self, instance):
        try:
            systolic = int(self.sys_input.text.strip())
            diastolic = int(self.dia_input.text.strip())

            pulse_text = self.pulse_input.text.strip()
            pulse = int(pulse_text) if pulse_text else None

        except ValueError:
            self.status_label.text = "Please enter valid numbers."
            return

        if not (50 <= systolic <= 300):
            self.status_label.text = "Invalid systolic value."
            return

        if not (30 <= diastolic <= 200):
            self.status_label.text = "Invalid diastolic value."
            return

        if pulse is not None and not (30 <= pulse <= 220):
            self.status_label.text = "Invalid pulse value."
            return

        category = self.classify_bp(systolic, diastolic)

        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "systolic": systolic,
            "diastolic": diastolic,
            "pulse": pulse,
            "category": category
        }

        self.readings.insert(0, entry)
        self.write_readings()

        self.sys_input.text = ""
        self.dia_input.text = ""
        self.pulse_input.text = ""

        self.status_label.text = "Saved: " + category
        self.refresh_history()

    def load_readings(self):
        path = os.path.join(self.user_data_dir, "bp_readings.json")

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data if isinstance(data, list) else []
            except (ValueError, OSError):
                return []

        return []

    def write_readings(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        path = os.path.join(self.user_data_dir, "bp_readings.json")

        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.readings, file, indent=2)

    def refresh_history(self):
        self.history_box.clear_widgets()

        if not self.readings:
            self.history_box.add_widget(Label(
                text="No readings saved yet.",
                size_hint_y=None,
                height=dp(50),
                color=get_color_from_hex("#64748B")
            ))
            return

        for item in self.readings:
            pulse = item.get("pulse")
            pulse_text = f" | Pulse: {pulse} BPM" if pulse else ""

            text = (
                f"{item.get('time', '')}\n"
                f"{item.get('systolic', '')}/"
                f"{item.get('diastolic', '')} mmHg"
                f"{pulse_text}\n"
                f"{item.get('category', '')}"
            )

            card = BoxLayout(
                orientation="vertical",
                padding=dp(10),
                size_hint_y=None,
                height=dp(100)
            )

            card.add_widget(Label(
                text=text,
                halign="left",
                valign="middle",
                color=get_color_from_hex("#17365D"),
                font_size=14,
                text_size=(Window.width - dp(65), None)
            ))

            self.history_box.add_widget(card)


if __name__ == "__main__":
    BPTrackerApp().run()
