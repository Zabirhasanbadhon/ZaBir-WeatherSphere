import tkinter as tk
from tkinter import messagebox
import threading
import requests

from datetime import datetime
from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageTk,
    ImageOps,
    ImageEnhance,
)


# ============================================================
# ZABIR WEATHERSPHERE
# Modern Transparent Glass Weather Dashboard
# Python + Tkinter + Pillow + Open-Meteo API
# ============================================================

# ======================== CONFIGURATION =====================

APP_NAME = "ZaBir🌦️WeatherSphere"

BACKGROUND_IMAGE_PATH = r"D:\My Projects\Weather\Clouds.jpg"

DEFAULT_CITY = "Dhaka"
DEFAULT_COUNTRY = "Bangladesh"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

MIN_WIDTH = 1000
MIN_HEIGHT = 700

REFRESH_INTERVAL = 10 * 60 * 1000

WEATHER_API = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"


# ======================== COLORS ============================

WHITE = "#FFFFFF"
TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT = "#E5EAF2"

BACKGROUND_DARKNESS = 0.82

GLASS_OPACITY = 0.0
DETAIL_CARD_OPACITY = 0.0
ACTIVE_CARD_OPACITY = 0.0

GLASS_BORDER = ""

CURRENT_CARD_OPACITY = 0.13
CURRENT_CARD_RADIUS = 28
CURRENT_CARD_ACCENT = "#DCEAFF"
CURRENT_CARD_SEPARATOR = "#C8D7EB"

SEARCH_TEXT_COLOR = "#FFFFFF"
SEARCH_PLACEHOLDER_COLOR = "#C5D0E0"
SEARCH_BUTTON_HOVER_COLOR = "#BBD7FF"
SEARCH_FIELD_OPACITY = 0.12  # transparency of search field glass

SUGGESTION_BACKGROUND = "#26364D"
SUGGESTION_FOREGROUND = "#FFFFFF"
SUGGESTION_SELECTED_BACKGROUND = "#526D92"


# ======================== WEATHER CODES =====================

WEATHER_ICONS = {
    0: "☀", 1: "🌤", 2: "⛅", 3: "☁",
    45: "🌫", 48: "🌫",
    51: "🌦", 53: "🌦", 55: "🌧",
    56: "🌧", 57: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    66: "🌧", 67: "🌧",
    71: "🌨", 73: "🌨", 75: "❄", 77: "❄",
    80: "🌦", 81: "🌧", 82: "🌧",
    85: "🌨", 86: "❄",
    95: "⛈", 96: "⛈", 99: "⛈",
}

WEATHER_DESCRIPTIONS = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Freezing Drizzle",
    57: "Heavy Freezing Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Rain Showers",
    81: "Moderate Rain Showers",
    82: "Heavy Rain Showers",
    85: "Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail",
    99: "Heavy Thunderstorm",
}


def weather_icon(code):
    return WEATHER_ICONS.get(int(code), "🌡")


def weather_description(code):
    return WEATHER_DESCRIPTIONS.get(int(code), "Weather Unavailable")


# ============================================================
# FALLBACK BACKGROUND
# ============================================================

def create_fallback_background(width=1600, height=1000):
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    top = (130, 115, 125)
    middle = (93, 112, 139)
    bottom = (17, 29, 53)

    for y in range(height):
        t = y / max(1, height - 1)

        if t < 0.5:
            p = t / 0.5
            start, end = top, middle
        else:
            p = (t - 0.5) / 0.5
            start, end = middle, bottom

        color = tuple(
            int(start[i] * (1 - p) + end[i] * p)
            for i in range(3)
        )
        draw.line((0, y, width, y), fill=color)

    return image


# ============================================================
# MAIN APPLICATION
# ============================================================

class WeatherSphere:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.configure(bg="#17253A")

        self.session = requests.Session()

        # Location
        self.current_city = DEFAULT_CITY
        self.current_country = DEFAULT_COUNTRY
        self.latitude = None
        self.longitude = None

        # Weather data
        self.weather_data = None
        self.hourly_offset = 0

        # Background
        self.background_original = None
        self.background_rendered = None
        self.background_photo = None
        self.glass_images = []

        # Search state
        self.search_text = ""            # canvas-based text buffer
        self.suggestions = []
        self.search_after_id = None
        self.search_request_id = 0
        self.weather_request_id = 0
        self.search_has_focus = False
        self.search_placeholder = "Search city..."
        self.search_placeholder_active = True
        self.search_entry = None          # kept as a hidden binding sink
        self.search_entry_window = None
        self.search_field_image = None    # glass image for input field
        self.search_button = None
        self.suggestion_window = None
        self.suggestion_list = None
        self.search_cursor_visible = True
        self.search_cursor_after_id = None
        self.search_text_item = None
        self.search_cursor_item = None
        self.search_field_id = None

        # Hourly navigation
        self.previous_arrow = None
        self.next_arrow = None
        self.previous_arrow_hitbox = None
        self.next_arrow_hitbox = None

        # Fonts
        self.font_brand = ("Segoe UI", 18, "bold")
        self.font_title = ("Segoe UI", 30, "bold")
        self.font_location = ("Segoe UI", 14)
        self.font_temperature = ("Segoe UI", 55, "bold")
        self.font_description = ("Segoe UI", 17, "bold")
        self.font_section = ("Segoe UI", 19, "bold")
        self.font_label = ("Segoe UI", 11)
        self.font_search = ("Segoe UI", 12)

        # Main canvas
        self.canvas = tk.Canvas(
            self.root,
            bg="#17253A",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.load_background(BACKGROUND_IMAGE_PATH, redraw=False)
        self.create_search_controls()

        self.canvas.bind("<Configure>", self.on_resize)

        self.root.after(300, self.load_default_weather)
        self.root.after(REFRESH_INTERVAL, self.auto_refresh)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ========================================================
    # BACKGROUND
    # ========================================================

    def load_background(self, path, redraw=True):
        try:
            if path and Path(path).is_file():
                with Image.open(path) as source:
                    source = ImageOps.exif_transpose(source)
                    source = source.convert("RGB")
                    source.load()
                    self.background_original = source.copy()
            else:
                self.background_original = create_fallback_background()
                if path:
                    print("Background image not found. Using fallback background.")
        except (OSError, ValueError) as error:
            print("Background error:", error)
            self.background_original = create_fallback_background()

        if redraw and hasattr(self, "canvas"):
            self.redraw_background()
            self.draw_dashboard()

    def redraw_background(self):
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())

        if self.background_original is None:
            self.background_original = create_fallback_background()

        image = ImageOps.fit(
            self.background_original,
            (width, height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        image = ImageEnhance.Brightness(image).enhance(BACKGROUND_DARKNESS)

        overlay = Image.new("RGBA", (width, height), (10, 18, 35, 30))
        self.background_rendered = Image.alpha_composite(
            image.convert("RGBA"),
            overlay,
        )
        self.background_photo = ImageTk.PhotoImage(self.background_rendered)

        self.canvas.delete("background")
        self.canvas.create_image(
            0, 0,
            image=self.background_photo,
            anchor="nw",
            tags="background",
        )
        self.canvas.tag_lower("background")

    # ========================================================
    # GLASS CARD
    # ========================================================

    def draw_glass_card(
        self,
        x1,
        y1,
        x2,
        y2,
        radius=18,
        opacity=GLASS_OPACITY,
        border=False,
    ):
        if self.background_rendered is None:
            return None

        canvas_width = self.background_rendered.width
        canvas_height = self.background_rendered.height

        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(canvas_width, int(x2))
        y2 = min(canvas_height, int(y2))

        if x2 <= x1 or y2 <= y1:
            return None

        width = x2 - x1
        height = y2 - y1
        background_crop = self.background_rendered.crop((x1, y1, x2, y2))
        tint = Image.new("RGBA", (width, height), (210, 225, 245, 255))

        opacity = max(0.0, min(1.0, opacity))
        glass = Image.blend(background_crop.convert("RGBA"), tint, opacity)

        mask = Image.new("L", (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=min(radius, width // 2, height // 2),
            fill=255,
        )
        glass.putalpha(mask)

        photo = ImageTk.PhotoImage(glass)
        self.glass_images.append(photo)

        image_id = self.canvas.create_image(
            x1, y1,
            image=photo,
            anchor="nw",
            tags="dynamic",
        )

        if border:
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=GLASS_BORDER or SECONDARY_TEXT,
                width=1,
                tags="dynamic",
            )

        return image_id

    # ========================================================
    # SEARCH CONTROLS  (FULLY TRANSPARENT)
    # --------------------------------------------------------
    # Instead of an opaque tk.Entry widget we draw the search
    # field on the canvas using the same glass blending as the
    # weather cards, so the background image shows through.
    # Keyboard input is captured by a hidden 1x1 Entry that is
    # always kept focused but never visible.
    #
    # FIX: To make the hidden Entry actually receive keyboard
    # focus on all platforms, we now (a) place it INSIDE the
    # canvas at a valid coordinate instead of off-screen,
    # (b) bind a root-level <KeyPress> fallback, and (c) use
    # focus_force() rather than focus_set().
    # ========================================================

    def create_search_controls(self):
        # --- hidden keyboard sink ---------------------------------
        self.search_entry = tk.Entry(
            self.canvas,
            font=self.font_search,
            bg="#17253A",
            fg=SEARCH_TEXT_COLOR,
            insertbackground=WHITE,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )

        # FIX: place the entry at a real (mapped) coordinate inside
        # the canvas. An off-screen 1x1 window at (-50,-50) is
        # *unmapped* on Windows, which makes focus_set() silently
        # fail. We keep it at the search field position but layered
        # underneath the glass so it is visually hidden.
        self.search_entry_window = self.canvas.create_window(
            40, 26,
            window=self.search_entry,
            width=1,
            height=1,
            anchor="nw",
            tags=("controls", "search_input"),
        )

        self.search_entry.bind("<FocusIn>", self.on_search_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_entry_focus_out)
        self.search_entry.bind("<Return>", self.on_search_enter)
        self.search_entry.bind("<Down>", self.focus_suggestions)
        self.search_entry.bind("<Escape>", self.on_search_escape)
        self.search_entry.bind("<KeyPress>", self.on_search_key_press)
        self.search_entry.bind("<BackSpace>", self.on_search_backspace)
        self.search_entry.bind("<Control-a>", self.on_search_select_all)
        self.search_entry.bind("<Control-A>", self.on_search_select_all)

        # --- Search button (canvas text) --------------------------
        self.search_button = self.canvas.create_text(
            360, 45,
            text="Search  →",
            font=("Segoe UI", 10, "bold"),
            fill=WHITE,
            anchor="center",
            tags=("controls", "search_button"),
        )

        self.canvas.tag_bind("search_button", "<Button-1>", self.on_search_button_click)
        self.canvas.tag_bind("search_button", "<Enter>", self.on_search_button_enter)
        self.canvas.tag_bind("search_button", "<Leave>", self.on_search_button_leave)

        # --- Clicking the glass field focuses the hidden entry ----
        self.canvas.tag_bind("search_field", "<Button-1>", self.on_search_field_click)

        # --- Suggestion listbox (always a real widget) -----------
        self.suggestion_list = tk.Listbox(
            self.root,
            font=("Segoe UI", 10),
            bg=SUGGESTION_BACKGROUND,
            fg=SUGGESTION_FOREGROUND,
            selectbackground=SUGGESTION_SELECTED_BACKGROUND,
            selectforeground=WHITE,
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#60738D",
            highlightcolor="#60738D",
            selectborderwidth=0,
            exportselection=False,
        )

        self.suggestion_list.bind("<ButtonRelease-1>", self.on_suggestion_select)
        self.suggestion_list.bind("<Return>", self.on_suggestion_enter)
        self.suggestion_list.bind("<Up>", self.on_suggestion_up)
        self.suggestion_list.bind("<Down>", self.on_suggestion_down)
        self.suggestion_list.bind("<Escape>", self.return_to_search)

        self.suggestion_window = self.canvas.create_window(
            40, 68,
            window=self.suggestion_list,
            width=360,
            height=0,
            anchor="nw",
            tags=("controls", "suggestions"),
        )
        self.canvas.itemconfigure(self.suggestion_window, state="hidden")

        # initial placeholder text
        self.search_text = ""
        self.search_placeholder_active = True
        self.search_has_focus = False

        # FIX: Root-level <KeyPress> fallback so typing works even
        # when the hidden Entry loses focus (resize, arrow clicks,
        # refresh, etc.). And force-focus the entry after startup.
        self.root.bind("<KeyPress>", self.on_global_key_press, add="+")
        self.canvas.bind("<Button-1>", self.on_global_click_focus, add="+")

        # schedule cursor blink
        self.schedule_cursor_blink()

    # ========================================================
    # GLOBAL FOCUS / KEY FALLBACK  (FIX)
    # ========================================================

    def on_global_click_focus(self, event=None):
        """Re-focus the hidden entry after any click on the canvas."""
        try:
            if self.root.focus_get() is not self.search_entry:
                # Don't steal focus from the suggestion listbox
                if self.root.focus_get() is self.suggestion_list:
                    return None
                self.search_entry.focus_force()
        except (tk.TclError, KeyError):
            pass
        return None

    def on_global_key_press(self, event=None):
        """
        Root-level key handler fallback. Only acts when the hidden
        entry does NOT already have focus (otherwise the entry's
        own binding handles the key and we'd double-type).
        """
        if event is None:
            return None

        try:
            focused = self.root.focus_get()
        except (tk.TclError, KeyError):
            focused = None

        # Entry has focus -> its own binding handles this key.
        if focused is self.search_entry:
            return None
        # Listbox has focus -> let it handle keys.
        if focused is self.suggestion_list:
            return None

        keysym = event.keysym
        char = event.char

        if char and char.isprintable():
            self.search_has_focus = True
            self.search_placeholder_active = False
            self.search_text += char
            self.redraw_search_field()
            self.on_search_change()
            return "break"

        if keysym == "BackSpace":
            return self.on_search_backspace()

        if keysym in ("Return", "KP_Enter"):
            return self.on_search_enter()

        if keysym == "Escape":
            return self.on_search_escape()

        if keysym == "Down":
            return self.focus_suggestions()

        return None

    # ========================================================
    # DRAW SEARCH FIELD (glass, transparent)
    # ========================================================

    def draw_search_field(self):
        """Draw the transparent glass search input on the canvas."""
        if self.background_rendered is None:
            return

        x1, y1 = 40, 26
        x2, y2 = 300, 64

        # glass image
        image_id = self.draw_glass_card(
            x1, y1, x2, y2,
            radius=10,
            opacity=SEARCH_FIELD_OPACITY,
            border=False,
        )
        if image_id is not None:
            self.canvas.itemconfigure(image_id, tags=("dynamic", "search_field"))
            # keep it behind the text/cursor
            self.canvas.tag_lower(image_id)
            self.search_field_id = image_id

        # text / placeholder
        text = self.search_text
        if self.search_placeholder_active or not text:
            display_text = self.search_placeholder
            text_color = SEARCH_PLACEHOLDER_COLOR
        else:
            display_text = text
            text_color = SEARCH_TEXT_COLOR

        # truncate text if too wide
        display_text = self._fit_search_text(display_text, 240)

        self.search_text_item = self.canvas.create_text(
            x1 + 14, (y1 + y2) / 2,
            text=display_text,
            font=self.font_search,
            fill=text_color,
            anchor="w",
            tags=("dynamic", "search_text"),
        )

        # cursor
        if self.search_has_focus and self.search_cursor_visible and not self.search_placeholder_active:
            bbox = self.canvas.bbox(self.search_text_item)
            cursor_x = (bbox[2] + 2) if bbox else x1 + 14
            cursor_x = min(cursor_x, x2 - 10)
            self.search_cursor_item = self.canvas.create_line(
                cursor_x, y1 + 12,
                cursor_x, y2 - 12,
                fill=WHITE,
                width=1,
                tags=("dynamic", "search_cursor"),
            )
        else:
            self.search_cursor_item = None

    def _fit_search_text(self, text, max_width_px):
        """Trim text from the left so it fits inside the field."""
        if not text:
            return text
        # rough char-width estimate for Segoe UI 11
        approx_char_w = 7
        max_chars = max(1, max_width_px // approx_char_w)
        if len(text) <= max_chars:
            return text
        return "…" + text[-(max_chars - 1):]

    # ========================================================
    # SEARCH FOCUS / PLACEHOLDER
    # ========================================================

    def on_search_entry_focus_in(self, event=None):
        self.search_has_focus = True
        if self.search_placeholder_active:
            self.search_placeholder_active = False
            self.search_text = ""
            self.search_entry.delete(0, tk.END)
        self.redraw_search_field()

    def on_search_entry_focus_out(self, event=None):
        # Only lose focus if the click is really outside our controls
        self.root.after(10, self._check_search_focus_out)

    def _check_search_focus_out(self):
        try:
            focused = self.root.focus_get()
        except (tk.TclError, KeyError):
            focused = None

        if focused is self.search_entry:
            return
        if focused is self.suggestion_list:
            return

        # FIX: If we still have text, don't drop the focus state
        # (this preserves the cursor and lets typing continue).
        self.search_has_focus = bool(self.search_text.strip())
        if not self.search_text.strip():
            self.search_placeholder_active = True
            self.search_text = ""
        self.redraw_search_field()

        # FIX: Give focus back so typing keeps working.
        try:
            self.search_entry.focus_force()
        except tk.TclError:
            pass

    def on_search_field_click(self, event=None):
        self.search_entry.focus_force()   # FIX: force, not set
        self.search_has_focus = True
        if self.search_placeholder_active:
            self.search_placeholder_active = False
            self.search_text = ""
            self.search_entry.delete(0, tk.END)
        self.redraw_search_field()
        return "break"

    def redraw_search_field(self):
        """Delete previous search text/cursor and redraw."""
        self.canvas.delete("search_text")
        self.canvas.delete("search_cursor")
        self.draw_search_field()
        self.canvas.tag_raise("controls")

    # ========================================================
    # HIDDEN ENTRY KEY HANDLING
    # ========================================================

    def on_search_key_press(self, event=None):
        # Ignore special keys handled elsewhere
        if event is None:
            return
        keysym = event.keysym
        if keysym in (
            "Return", "KP_Enter", "Escape", "Down", "Up",
            "Left", "Right", "Home", "End", "Tab",
            "BackSpace", "Delete",
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R", "Caps_Lock",
        ):
            return
        char = event.char
        if char and char.isprintable():
            self.search_text += char
            self.search_placeholder_active = False
            self.redraw_search_field()
            self.on_search_change()
        return "break"

    def on_search_backspace(self, event=None):
        if self.search_placeholder_active:
            return "break"
        if self.search_text:
            self.search_text = self.search_text[:-1]
            self.redraw_search_field()
            if not self.search_text:
                self.search_placeholder_active = True
                self.hide_suggestions()
            else:
                self.on_search_change()
        return "break"

    def on_search_select_all(self, event=None):
        # Not implementing full selection; just keep cursor at end
        return "break"

    def on_search_variable_change(self, *args):
        # legacy hook — no longer used with canvas input
        pass

    def update_search_display(self):
        self.redraw_search_field()

    def on_search_escape(self, event=None):
        self.hide_suggestions()
        return "break"

    # ========================================================
    # CURSOR BLINK
    # ========================================================

    def schedule_cursor_blink(self):
        self.search_cursor_visible = not self.search_cursor_visible
        if self.search_has_focus and not self.search_placeholder_active:
            try:
                self.redraw_search_field()
            except tk.TclError:
                return
        try:
            self.search_cursor_after_id = self.root.after(530, self.schedule_cursor_blink)
        except tk.TclError:
            self.search_cursor_after_id = None

    # ========================================================
    # SEARCH BUTTON EVENTS
    # ========================================================

    def on_search_button_click(self, event=None):
        self.search_entry.focus_force()   # FIX: force
        if self.search_placeholder_active or not self.search_text.strip():
            return "break"
        self.search_city()
        return "break"

    def on_search_button_enter(self, event=None):
        self.canvas.configure(cursor="hand2")
        self.canvas.itemconfigure(self.search_button, fill=SEARCH_BUTTON_HOVER_COLOR)

    def on_search_button_leave(self, event=None):
        self.canvas.configure(cursor="")
        self.canvas.itemconfigure(self.search_button, fill=WHITE)

    # ========================================================
    # RESPONSIVE LAYOUT
    # ========================================================

    def on_resize(self, event=None):
        if self.canvas.winfo_width() < 2:
            return
        self.redraw_background()
        self.position_controls()
        self.draw_dashboard()

    def position_controls(self):
        # FIX: keep the sink mapped inside the canvas (behind the
        # glass) instead of off-screen, so it can accept focus.
        self.canvas.coords(self.search_entry_window, 40, 26)
        self.canvas.itemconfigure(self.search_entry_window, width=1, height=1)
        self.canvas.tag_lower(self.search_entry_window)
        self.canvas.coords(self.search_button, 360, 45)
        self.canvas.coords(self.suggestion_window, 40, 68)
        self.canvas.tag_raise("controls")

    # ========================================================
    # DRAWING HELPERS
    # ========================================================

    def draw_text(
        self,
        x,
        y,
        text,
        font,
        color=WHITE,
        anchor="nw",
    ):
        return self.canvas.create_text(
            x, y,
            text=str(text),
            font=font,
            fill=color,
            anchor=anchor,
            tags="dynamic",
        )

    def draw_rounded_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        radius=15,
        fill="#34445A",
    ):
        radius = min(
            radius,
            max(0, int((x2 - x1) / 2)),
            max(0, int((y2 - y1) / 2)),
        )

        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]

        return self.canvas.create_polygon(
            points,
            smooth=True,
            fill=fill,
            outline="",
            tags="dynamic",
        )

    # ========================================================
    # MAIN DASHBOARD
    # ========================================================

    def draw_dashboard(self):
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("dynamic")
        self.glass_images.clear()

        self.previous_arrow = None
        self.next_arrow = None
        self.previous_arrow_hitbox = None
        self.next_arrow_hitbox = None
        self.search_field_id = None
        self.search_text_item = None
        self.search_cursor_item = None

        width = max(MIN_WIDTH, self.canvas.winfo_width())
        height = max(MIN_HEIGHT, self.canvas.winfo_height())

        # re-draw transparent search field on top of background
        self.draw_search_field()

        self.draw_text(
            40, 82,
            "ZaBir",
            self.font_brand,
            "#55E6A5",
        )

        self.draw_text(
            105, 82,
            "🌥️",
            ("Segoe UI Emoji", 18),
            WHITE,
        )

        self.draw_text(
            140, 82,
            "WeatherSphere",
            self.font_brand,
            WHITE,
        )

        details_x = width - 240 - 40
        self.draw_text(
            details_x, 82,
            datetime.now().strftime("%A, %d %B %Y"),
            ("Segoe UI", 11),
            SECONDARY_TEXT,
        )

        self.draw_current_weather()
        self.draw_weather_details(width)
        self.draw_hourly_forecast(width, height)

        self.draw_text(
            40, height - 15,
            "Weather data provided by Open-Meteo",
            ("Segoe UI", 9),
            SECONDARY_TEXT,
            anchor="sw",
        )

        self.draw_text(
            width - 40, height - 15,
            "LIVE WEATHER  •  AUTO REFRESH",
            ("Segoe UI", 9, "bold"),
            SECONDARY_TEXT,
            anchor="se",
        )

        # keep search UI on top
        self.canvas.tag_raise("search_field")
        self.canvas.tag_raise("search_text")
        self.canvas.tag_raise("search_cursor")
        self.canvas.tag_raise("controls")
        for tag in (
            "previous_hours_hitbox",
            "next_hours_hitbox",
            "previous_hours",
            "next_hours",
        ):
            self.canvas.tag_raise(tag)
        self.canvas.tag_raise("controls")

        # FIX: after every redraw, re-assert focus on the hidden
        # entry so the user can keep typing.
        try:
            self.search_entry.focus_force()
        except tk.TclError:
            pass

    # ========================================================
    # CURRENT WEATHER
    # ========================================================

    def draw_current_weather(self):
        if not self.weather_data:
            return

        current = self.weather_data.get("current", {})
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        x = 48
        y = 150
        right = width - 400
        available_width = max(0, right - x)

        city = self.current_city or "Unknown City"
        country = self.current_country or ""

        temperature = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        code = current.get("weather_code", 0)

        description = weather_description(code)
        icon = weather_icon(code)

        self.draw_text(
            x, y, city,
            ("Segoe UI", 30, "bold"),
            "#FFFFFF",
            anchor="nw",
        )

        self.draw_text(
            x, y + 48, country,
            ("Segoe UI", 13),
            "#B8C7D9",
            anchor="nw",
        )

        self.canvas.create_oval(
            x, y + 83, x + 7, y + 90,
            fill="#55E6A5",
            outline="",
            tags="dynamic",
        )

        self.draw_text(
            x + 16, y + 86,
            "Weather at a Glance",
            ("Segoe UI", 12, "bold"),
            "#55E6A5",
            anchor="w",
        )

        weather_y = y + 125

        self.draw_text(
            x, weather_y + 35, icon,
            ("Segoe UI Emoji", 48),
            "#FFFFFF",
            anchor="w",
        )

        temperature_text = (
            f"{round(temperature)}°"
            if isinstance(temperature, (int, float))
            else "--°"
        )

        self.draw_text(
            x + 95, weather_y + 35,
            temperature_text,
            ("Segoe UI", 52, "bold"),
            "#FFFFFF",
            anchor="w",
        )

        self.draw_text(
            x + 2, weather_y + 92,
            description,
            ("Segoe UI", 16, "bold"),
            "#E5EDF7",
            anchor="w",
        )

        feels_text = (
            f"Feels like {round(feels_like)}°"
            if isinstance(feels_like, (int, float))
            else "Feels like --°"
        )

        self.draw_text(
            x + 2, weather_y + 123,
            feels_text,
            ("Segoe UI", 12),
            "#B8C7D9",
            anchor="w",
        )

        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        pressure = current.get("pressure_msl")

        summary_y = weather_y + 165

        wind_text = (
            f"{wind:g} km/h"
            if isinstance(wind, (int, float))
            else "-- km/h"
        )
        pressure_text = (
            f"{pressure:.0f} hPa"
            if isinstance(pressure, (int, float))
            else "-- hPa"
        )
        humidity_text = (
            f"{humidity}%"
            if isinstance(humidity, (int, float))
            else "--%"
        )

        columns = [
            ("HUMIDITY", humidity_text),
            ("WIND", wind_text),
            ("PRESSURE", pressure_text),
        ]

        if available_width >= 500:
            column_gap = min(190, available_width // 3)

            for index, (label, value) in enumerate(columns):
                column_x = x + index * column_gap

                self.draw_text(
                    column_x, summary_y,
                    label,
                    ("Segoe UI", 9, "bold"),
                    "#C8D9F0",
                    anchor="nw",
                )

                self.draw_text(
                    column_x, summary_y + 25,
                    value,
                    ("Segoe UI", 16, "bold"),
                    "#FFFFFF",
                    anchor="nw",
                )
        else:
            for index, (label, value) in enumerate(columns):
                self.draw_text(
                    x, summary_y + index * 30,
                    f"{label.title()}  {value}",
                    ("Segoe UI", 11, "bold"),
                    "#FFFFFF",
                    anchor="nw",
                )

        observation_time = current.get("time")

        if observation_time:
            try:
                parsed_time = datetime.fromisoformat(
                    observation_time.replace("Z", "+00:00")
                )
                time_text = parsed_time.strftime("%I:%M %p").lstrip("0")
            except (ValueError, AttributeError):
                time_text = str(observation_time)
        else:
            time_text = datetime.now().strftime("%I:%M %p").lstrip("0")

        observation_y = height - 100

        if observation_y > summary_y + 65:
            self.draw_text(
                x, observation_y,
                "LAST OBSERVATION",
                ("Segoe UI", 9, "bold"),
                "#C8D9F0",
                anchor="nw",
            )

            self.draw_text(
                x, observation_y + 23,
                time_text,
                ("Segoe UI", 12),
                "#FFFFFF",
                anchor="nw",
            )

    # ========================================================
    # WEATHER DETAILS
    # ========================================================

    def draw_weather_details(self, width):
        if not self.weather_data:
            return

        current = self.weather_data.get("current", {})
        humidity = current.get("relative_humidity_2m")
        pressure = current.get("pressure_msl")
        wind = current.get("wind_speed_10m")

        hourly = self.weather_data.get("hourly", {})
        times = hourly.get("time", [])
        rain_values = hourly.get("precipitation_probability", [])
        rain_probability = 0

        if times and rain_values:
            now = datetime.now().replace(minute=0, second=0, microsecond=0)
            try:
                index = min(
                    range(len(times)),
                    key=lambda i: abs(
                        (datetime.fromisoformat(times[i]) - now).total_seconds()
                    ),
                )
                if index < len(rain_values):
                    rain_probability = rain_values[index] or 0
            except (ValueError, TypeError):
                pass

        def display_number(value, fmt, suffix=""):
            if isinstance(value, (int, float)):
                return format(value, fmt) + suffix
            return "--" + suffix

        card_width = 240
        x = width - card_width - 40
        y = 148

        self.draw_text(
            x, y,
            "WEATHER DETAILS",
            self.font_brand,
            SECONDARY_TEXT,
        )

        details = [
            ("≋", "Humidity", display_number(humidity, ".0f", "%"), "Relative moisture"),
            ("◉", "Air Pressure", display_number(pressure, ".0f", " hPa"), "Sea-level pressure"),
            ("☂", "Chance of Rain", f"{rain_probability}%", "Hourly forecast"),
            ("≈", "Wind Speed", display_number(wind, ".1f", " km/h"), "Surface wind"),
        ]

        card_y = y + 28
        card_height = 88
        gap = 12

        for icon, label, value, subtitle in details:
            self.draw_glass_card(
                x, card_y,
                x + card_width, card_y + card_height,
                radius=14,
                opacity=DETAIL_CARD_OPACITY,
                border=False,
            )

            self.draw_text(
                x + 16, card_y + 15,
                icon,
                ("Segoe UI", 22, "bold"),
                WHITE,
            )

            self.draw_text(
                x + 53, card_y + 12,
                label,
                ("Segoe UI", 10),
                SECONDARY_TEXT,
            )

            self.draw_text(
                x + 53, card_y + 32,
                value,
                ("Segoe UI", 18, "bold"),
                WHITE,
            )

            self.draw_text(
                x + 53, card_y + 63,
                subtitle,
                ("Segoe UI", 9),
                SECONDARY_TEXT,
            )

            card_y += card_height + gap

    # ========================================================
    # HOURLY FORECAST
    # ========================================================

    def draw_hourly_forecast(self, width, height):
        section_y = height - 330

        self.draw_text(
            40, section_y - 48,
            "Hourly Forecast",
            ("Segoe UI", 19, "bold"),
            WHITE,
        )

        self.draw_text(
            40, section_y - 17,
            "Weather conditions throughout the day",
            ("Segoe UI", 10),
            SECONDARY_TEXT,
        )

        button_y = section_y - 42
        previous_x = width - 86
        next_x = width - 42
        arrow_y = button_y + 18

        self.previous_arrow_hitbox = self.canvas.create_text(
            previous_x, arrow_y,
            text="     ",
            font=("Segoe UI", 30),
            fill="",
            anchor="center",
            tags=("dynamic", "previous_hours_hitbox"),
        )

        self.next_arrow_hitbox = self.canvas.create_text(
            next_x, arrow_y,
            text="     ",
            font=("Segoe UI", 30),
            fill="",
            anchor="center",
            tags=("dynamic", "next_hours_hitbox"),
        )

        self.previous_arrow = self.canvas.create_text(
            previous_x, arrow_y,
            text="‹",
            font=("Segoe UI", 30),
            fill=WHITE,
            anchor="center",
            tags=("dynamic", "previous_hours"),
        )

        self.next_arrow = self.canvas.create_text(
            next_x, arrow_y,
            text="›",
            font=("Segoe UI", 30),
            fill=WHITE,
            anchor="center",
            tags=("dynamic", "next_hours"),
        )

        self.canvas.tag_bind(
            "previous_hours",
            "<Button-1>",
            lambda event: self.change_hourly_page(-1),
        )
        self.canvas.tag_bind(
            "next_hours",
            "<Button-1>",
            lambda event: self.change_hourly_page(1),
        )
        self.canvas.tag_bind(
            "previous_hours_hitbox",
            "<Button-1>",
            lambda event: self.change_hourly_page(-1),
        )
        self.canvas.tag_bind(
            "next_hours_hitbox",
            "<Button-1>",
            lambda event: self.change_hourly_page(1),
        )
        self.canvas.tag_bind(
            "previous_hours",
            "<Enter>",
            lambda event: self.set_arrow_hover(self.previous_arrow, True),
        )
        self.canvas.tag_bind(
            "previous_hours",
            "<Leave>",
            lambda event: self.set_arrow_hover(self.previous_arrow, False),
        )
        self.canvas.tag_bind(
            "next_hours",
            "<Enter>",
            lambda event: self.set_arrow_hover(self.next_arrow, True),
        )
        self.canvas.tag_bind(
            "next_hours",
            "<Leave>",
            lambda event: self.set_arrow_hover(self.next_arrow, False),
        )

        if not self.weather_data:
            self.draw_text(
                40, section_y + 50,
                "Loading hourly forecast...",
                ("Segoe UI", 11),
                WHITE,
            )
            return

        hourly = self.weather_data.get("hourly", {})
        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        codes = hourly.get("weather_code", [])
        probabilities = hourly.get("precipitation_probability", [])
        apparent = hourly.get("apparent_temperature", [])

        if not times:
            return

        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        try:
            base_index = min(
                range(len(times)),
                key=lambda i: abs(
                    (datetime.fromisoformat(times[i]) - now).total_seconds()
                ),
            )
        except (ValueError, TypeError):
            base_index = 0

        start_index = max(
            0,
            min(base_index + self.hourly_offset, len(times) - 1),
        )

        left = 40
        right = width - 40
        available_width = right - left

        number_of_cards = max(4, min(8, int(available_width // 135)))
        gap = 12
        card_width = (
            available_width - gap * (number_of_cards - 1)
        ) / number_of_cards

        card_top = section_y + 22
        card_bottom = height - 39
        card_height = card_bottom - card_top

        for i in range(number_of_cards):
            index = start_index + i

            if index >= len(times):
                break
            if index >= len(temperatures) or index >= len(codes):
                break

            x1 = left + i * (card_width + gap)
            x2 = x1 + card_width
            y1 = card_top
            y2 = card_bottom

            opacity = ACTIVE_CARD_OPACITY if i == 0 else GLASS_OPACITY

            self.draw_glass_card(
                x1, y1, x2, y2,
                radius=18,
                opacity=opacity,
                border=False,
            )

            if i == 0:
                self.canvas.create_line(
                    x1 + 18, y1 + 4,
                    x2 - 18, y1 + 4,
                    fill=WHITE,
                    width=3,
                    capstyle="round",
                    tags="dynamic",
                )

            dt = datetime.fromisoformat(times[index])
            hour_label = dt.strftime("%I:%M %p").lstrip("0")
            temperature = round(temperatures[index])
            code = int(codes[index])
            rain = probabilities[index] if index < len(probabilities) else 0
            feels = round(apparent[index]) if index < len(apparent) else temperature

            self.draw_text(
                (x1 + x2) / 2, y1 + 23,
                "NOW" if i == 0 else hour_label,
                ("Segoe UI", 10, "bold"),
                WHITE,
                anchor="center",
            )

            self.draw_text(
                (x1 + x2) / 2, y1 + 72,
                weather_icon(code),
                ("Segoe UI Emoji", 30),
                WHITE,
                anchor="center",
            )

            self.draw_text(
                (x1 + x2) / 2, y1 + 119,
                f"{temperature}°",
                ("Segoe UI", 25, "bold"),
                WHITE,
                anchor="center",
            )

            description = weather_description(code)
            if len(description) > 17:
                description = description[:15] + "…"

            self.draw_text(
                (x1 + x2) / 2, y1 + 153,
                description,
                ("Segoe UI", 9),
                SECONDARY_TEXT,
                anchor="center",
            )

            divider_y = y1 + 178
            if divider_y < y2 - 48:
                self.canvas.create_line(
                    x1 + 14, divider_y,
                    x2 - 14, divider_y,
                    fill=GLASS_BORDER or SECONDARY_TEXT,
                    width=1,
                    tags="dynamic",
                )

            if divider_y + 28 < y2 - 10:
                self.draw_text(
                    (x1 + x2) / 2, divider_y + 18,
                    f"☂  {rain}%",
                    ("Segoe UI", 10, "bold"),
                    WHITE,
                    anchor="center",
                )

            if card_height > 245:
                self.draw_text(
                    (x1 + x2) / 2, y2 - 19,
                    f"Feels {feels}°",
                    ("Segoe UI", 9),
                    SECONDARY_TEXT,
                    anchor="center",
                )

        for tag in (
            "previous_hours_hitbox",
            "next_hours_hitbox",
            "previous_hours",
            "next_hours",
        ):
            self.canvas.tag_raise(tag)

    # ========================================================
    # HOURLY ARROW HOVER
    # ========================================================

    def set_arrow_hover(self, item, hovered):
        if item is None:
            return

        try:
            self.canvas.itemconfigure(
                item,
                fill=SEARCH_BUTTON_HOVER_COLOR if hovered else WHITE,
            )
            self.canvas.configure(cursor="hand2" if hovered else "")
        except tk.TclError:
            pass

    # ========================================================
    # HOURLY NAVIGATION
    # ========================================================

    def change_hourly_page(self, direction):
        if not self.weather_data:
            return

        times = self.weather_data.get("hourly", {}).get("time", [])
        if not times:
            return

        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        try:
            base_index = min(
                range(len(times)),
                key=lambda i: abs(
                    (datetime.fromisoformat(times[i]) - now).total_seconds()
                ),
            )
        except (ValueError, TypeError):
            base_index = 0

        width = self.canvas.winfo_width()
        number_of_cards = max(4, min(8, int((width - 80) // 135)))
        max_offset = max(0, len(times) - base_index - number_of_cards)

        self.hourly_offset += direction * number_of_cards
        self.hourly_offset = max(0, min(self.hourly_offset, max_offset))

        self.draw_dashboard()

    # ========================================================
    # WEATHER API
    # ========================================================

    def fetch_weather(self, latitude, longitude):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "is_day,"
                "precipitation,"
                "weather_code,"
                "pressure_msl,"
                "wind_speed_10m"
            ),
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation_probability,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "forecast_days": 2,
            "timezone": "auto",
            "wind_speed_unit": "kmh",
            "temperature_unit": "celsius",
        }

        response = self.session.get(
            WEATHER_API,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    # ========================================================
    # SEARCH INPUT CHANGES
    # ========================================================

    def on_search_change(self, event=None):
        self.search_request_id += 1

        if self.search_after_id:
            try:
                self.root.after_cancel(self.search_after_id)
            except tk.TclError:
                pass
            self.search_after_id = None

        query = self.search_text.strip()

        if len(query) < 2:
            self.suggestions = []
            self.hide_suggestions()
            return

        request_id = self.search_request_id
        self.search_after_id = self.root.after(
            300,
            lambda q=query, rid=request_id: self.fetch_city_suggestions(q, rid),
        )

    # ========================================================
    # FETCH CITY SUGGESTIONS
    # ========================================================

    def fetch_city_suggestions(self, query, request_id=None):
        if request_id is None:
            self.search_request_id += 1
            request_id = self.search_request_id

        def worker():
            try:
                response = requests.get(
                    GEOCODING_API,
                    params={
                        "name": query,
                        "count": 10,
                        "language": "en",
                        "format": "json",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                cities = []

                for item in results:
                    if "latitude" not in item or "longitude" not in item:
                        continue

                    name = item.get("name", "Unknown")
                    country = item.get("country", "")
                    admin = item.get("admin1", "")
                    parts = [name]

                    if admin and admin.casefold() != name.casefold():
                        parts.append(admin)
                    if country:
                        parts.append(country)

                    cities.append({
                        "name": name,
                        "country": country,
                        "latitude": item["latitude"],
                        "longitude": item["longitude"],
                        "label": ", ".join(parts),
                    })

                self.root.after(
                    0,
                    lambda c=cities, q=query, rid=request_id:
                        self.show_suggestions(c, q, rid),
                )

            except (requests.RequestException, ValueError, TypeError):
                try:
                    self.root.after(
                        0,
                        lambda q=query, rid=request_id:
                            self.handle_suggestion_error(q, rid),
                    )
                except tk.TclError:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    # ========================================================
    # AUTOCOMPLETE ERROR HANDLING
    # ========================================================

    def handle_suggestion_error(self, query, request_id):
        if request_id != self.search_request_id:
            return
        if self.search_text.strip() != query:
            return

        self.suggestions = []
        self.hide_suggestions()
        print("Unable to retrieve city suggestions. Check the internet connection.")

    # ========================================================
    # DISPLAY SUGGESTIONS
    # ========================================================

    def show_suggestions(self, cities, query, request_id):
        if request_id != self.search_request_id:
            return
        if self.search_text.strip() != query:
            return

        self.suggestions = cities
        self.suggestion_list.delete(0, tk.END)

        for city in cities:
            self.suggestion_list.insert(tk.END, city["label"])

        if not cities:
            self.hide_suggestions()
            return

        count = min(5, len(cities))
        self.suggestion_list.configure(height=count)
        self.canvas.itemconfigure(
            self.suggestion_window,
            state="normal",
            height=count * 28,
            width=360,
        )
        self.canvas.tag_raise("controls")

    # ========================================================
    # HIDE SUGGESTIONS
    # ========================================================

    def hide_suggestions(self, event=None):
        if self.suggestion_window is not None:
            self.canvas.itemconfigure(
                self.suggestion_window,
                state="hidden",
                height=0,
            )
        return "break"

    # ========================================================
    # KEYBOARD NAVIGATION
    # ========================================================

    def focus_suggestions(self, event=None):
        if not self.suggestions:
            return "break"

        self.suggestion_list.focus_set()
        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_list.selection_set(0)
        self.suggestion_list.activate(0)
        self.suggestion_list.see(0)
        return "break"

    def on_suggestion_down(self, event=None):
        if not self.suggestions:
            return "break"

        selection = self.suggestion_list.curselection()
        index = selection[0] if selection else -1
        index = min(index + 1, len(self.suggestions) - 1)

        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_list.selection_set(index)
        self.suggestion_list.activate(index)
        self.suggestion_list.see(index)
        return "break"

    def on_suggestion_up(self, event=None):
        if not self.suggestions:
            return "break"

        selection = self.suggestion_list.curselection()
        index = selection[0] if selection else 0
        index = max(0, index - 1)

        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_list.selection_set(index)
        self.suggestion_list.activate(index)
        self.suggestion_list.see(index)
        return "break"

    def return_to_search(self, event=None):
        self.search_entry.focus_force()   # FIX: force
        return "break"

    # ========================================================
    # SELECT CITY SUGGESTION
    # ========================================================

    def on_suggestion_select(self, event=None):
        selection = self.suggestion_list.curselection()
        if not selection:
            return "break"

        index = selection[0]
        if index >= len(self.suggestions):
            return "break"

        city = self.suggestions[index]
        self.search_request_id += 1

        if self.search_after_id:
            try:
                self.root.after_cancel(self.search_after_id)
            except tk.TclError:
                pass
            self.search_after_id = None

        self.search_text = city["label"]
        self.search_placeholder_active = False
        self.hide_suggestions()
        self.search_entry.focus_force()   # FIX: force
        self.redraw_search_field()
        self.load_selected_city(city)
        return "break"

    def on_suggestion_enter(self, event=None):
        return self.on_suggestion_select(event)

    # ========================================================
    # ENTER KEY
    # ========================================================

    def on_search_enter(self, event=None):
        self.search_city()
        return "break"

    # ========================================================
    # SEARCH CITY
    # ========================================================

    def search_city(self):
        query = self.search_text.strip()

        if (
            not query
            or self.search_placeholder_active
            or query == self.search_placeholder
        ):
            return

        if self.search_after_id:
            try:
                self.root.after_cancel(self.search_after_id)
            except tk.TclError:
                pass
            self.search_after_id = None

        self.search_request_id += 1
        request_id = self.search_request_id

        for city in self.suggestions:
            if city["label"].casefold() == query.casefold():
                self.hide_suggestions()
                self.load_selected_city(city, request_id)
                return

        self.hide_suggestions()
        self.search_placeholder_active = False

        def worker():
            try:
                response = requests.get(
                    GEOCODING_API,
                    params={
                        "name": query,
                        "count": 10,
                        "language": "en",
                        "format": "json",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                results = response.json().get("results", [])

                if not results:
                    self.root.after(
                        0,
                        lambda: self.show_search_error(
                            "City Not Found",
                            f"No city matching '{query}' was found.",
                            request_id,
                        ),
                    )
                    return

                selected = next(
                    (
                        item for item in results
                        if item.get("name", "").casefold() == query.casefold()
                    ),
                    results[0],
                )

                if "latitude" not in selected or "longitude" not in selected:
                    raise ValueError("The location response did not include coordinates.")

                city = {
                    "name": selected.get("name", query),
                    "country": selected.get("country", ""),
                    "latitude": selected["latitude"],
                    "longitude": selected["longitude"],
                    "label": selected.get("name", query),
                }

                self.root.after(
                    0,
                    lambda: self.load_selected_city(city, request_id),
                )

            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                error_message = str(error)[:150]
                try:
                    self.root.after(
                        0,
                        lambda: self.show_search_error(
                            "Connection Error",
                            "Unable to search for the city.\n\n"
                            "Check your internet connection.\n\n"
                            + error_message,
                            request_id,
                        ),
                    )
                except tk.TclError:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    # ========================================================
    # SEARCH ERROR
    # ========================================================

    def show_search_error(self, title, message, request_id):
        if request_id != self.search_request_id:
            return
        self.show_error(title, message)

    # ========================================================
    # DEFAULT WEATHER
    # ========================================================

    def load_default_weather(self):
        # FIX: focus_force so the entry truly owns keyboard input
        try:
            self.search_entry.focus_force()
        except tk.TclError:
            pass
        self.search_text = DEFAULT_CITY
        self.search_placeholder_active = False
        self.redraw_search_field()
        self.search_city()

    # ========================================================
    # LOAD SELECTED CITY
    # ========================================================

    def load_selected_city(self, city, search_request_id=None):
        if (
            search_request_id is not None
            and search_request_id != self.search_request_id
        ):
            return

        self.current_city = city["name"]
        self.current_country = city.get("country", "")
        self.latitude = city["latitude"]
        self.longitude = city["longitude"]

        self.hourly_offset = 0
        self.weather_data = None
        self.draw_dashboard()

        self.weather_request_id += 1
        request_id = self.weather_request_id
        latitude = self.latitude
        longitude = self.longitude

        def worker():
            try:
                data = self.fetch_weather(latitude, longitude)
                self.root.after(
                    0,
                    lambda: self.on_weather_loaded(data, request_id),
                )
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                error_message = str(error)
                try:
                    self.root.after(
                        0,
                        lambda: self.on_weather_error(error_message, request_id),
                    )
                except tk.TclError:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    # ========================================================
    # WEATHER LOADED
    # ========================================================

    def on_weather_loaded(self, data, request_id):
        if request_id != self.weather_request_id:
            return
        self.weather_data = data
        self.draw_dashboard()

    # ========================================================
    # WEATHER ERROR
    # ========================================================

    def on_weather_error(self, error, request_id):
        if request_id != self.weather_request_id:
            return

        self.draw_dashboard()
        self.show_error(
            "Weather Error",
            "Unable to load weather information.\n\n"
            "Check your internet connection and try again.\n\n"
            + error[:180],
        )

    # ========================================================
    # AUTOMATIC WEATHER REFRESH
    # ========================================================

    def auto_refresh(self):
        if self.latitude is not None and self.longitude is not None:
            self.weather_request_id += 1
            request_id = self.weather_request_id
            latitude = self.latitude
            longitude = self.longitude

            def worker():
                try:
                    data = self.fetch_weather(latitude, longitude)
                    self.root.after(
                        0,
                        lambda: self.on_weather_loaded(data, request_id),
                    )
                except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                    print("Automatic refresh failed:", error)

            threading.Thread(target=worker, daemon=True).start()

        self.root.after(REFRESH_INTERVAL, self.auto_refresh)

    # ========================================================
    # ERROR DIALOG
    # ========================================================

    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self.root)

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def on_close(self):
        self.search_request_id += 1
        self.weather_request_id += 1

        if self.search_after_id:
            try:
                self.root.after_cancel(self.search_after_id)
            except tk.TclError:
                pass

        if self.search_cursor_after_id:
            try:
                self.root.after_cancel(self.search_cursor_after_id)
            except tk.TclError:
                pass

        self.session.close()
        self.root.destroy()

    # ========================================================
    # START APPLICATION
    # ========================================================

    def run(self):
        self.root.mainloop()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherSphere(root)
    app.run()