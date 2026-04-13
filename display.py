"""
Display Manager mit pygame
Minimalistisches Interface für Abfahrtszeiten - Zweispalten-Layout
"""
import pygame
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

# Konstanten für Layout
HEADER_HEIGHT = 40
LEGEND_HEIGHT = 25
BADGE_SIZE = 45
ICON_SIZE = 20
TARGET_FPS = 5  # Frames pro Sekunde
SCROLL_SPEED = 3  # Pixel pro Frame (angepasst für 5 FPS)
SCROLL_PAUSE_FRAMES = 15  # 3 Sekunden bei 5 FPS
BLINK_INTERVAL = 0.5  # Sekunden
WIFI_ANIMATION_SPEED = 1  # Frames pro Animation-Frame (angepasst für 5 FPS)


class ScrollingText:
    """
    Klasse für horizontal scrollenden Text
    
    Scrollt automatisch wenn der Text breiter als max_width ist.
    Nach jedem Durchlauf gibt es eine Pause.
    """
    def __init__(self, text: str, font: pygame.font.Font, max_width: int, color: Tuple[int, int, int]):
        self.text = text
        self.font = font
        self.max_width = max_width
        self.color = color
        self.surface = font.render(text, True, color)
        self.text_width = self.surface.get_width()
        self.offset = 0
        self.needs_scroll = self.text_width > max_width
        self.scroll_speed = SCROLL_SPEED
        self.pause_frames = SCROLL_PAUSE_FRAMES
        self.pause_counter = self.pause_frames
        self.scroll_offset_float = 0.0  # Float für sanfteres Scrolling
        
    def update(self):
        """Aktualisiert die Scroll-Position für den nächsten Frame"""
        if not self.needs_scroll:
            return
            
        if self.pause_counter > 0:
            self.pause_counter -= 1
            return
        
        # Sanftes Scrolling mit Float-Präzision
        self.scroll_offset_float += self.scroll_speed
        self.offset = int(self.scroll_offset_float)
        
        # Am Ende angekommen? Zurücksetzen mit Pause
        if self.offset > self.text_width - self.max_width + 20:
            self.offset = 0
            self.scroll_offset_float = 0.0
            self.pause_counter = self.pause_frames
    
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """
        Zeichnet den Text an der angegebenen Position
        
        Args:
            screen: pygame Surface zum Zeichnen
            x, y: Position (obere linke Ecke)
        """
        if not self.needs_scroll:
            screen.blit(self.surface, (x, y))
        else:
            # Clipping für Scroll-Effekt
            clip_rect = pygame.Rect(x, y, self.max_width, self.surface.get_height())
            screen.set_clip(clip_rect)
            screen.blit(self.surface, (x - self.offset, y))
            screen.set_clip(None)


class DisplayManager:
    # Farben (minimalistisch)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (60, 60, 60)
    RED = (255, 80, 80)
    GREEN = (80, 255, 120)
    YELLOW = (255, 220, 80)
    BLUE = (100, 150, 255)
    ORANGE = (255, 165, 80)
    
    # Produkt-Farben (BVG-Style)
    PRODUCT_COLORS = {
        'subway': (0, 84, 159),      # U-Bahn Blau
        'suburban': (0, 131, 81),     # S-Bahn Grün
        'tram': (204, 0, 0),          # Tram Rot
        'bus': (153, 51, 153),        # Bus Lila
        'ferry': (0, 153, 204),       # Fähre Türkis
        'express': (204, 0, 0),       # Express Rot
        'regional': (204, 0, 0),      # Regional Rot
    }
    
    def __init__(self, width: int = 800, height: int = 480, fullscreen: bool = False, test_mode: bool = False):
        """
        Initialisiert das Display
        
        Args:
            width: Bildschirmbreite
            height: Bildschirmhöhe
            fullscreen: Vollbildmodus
            test_mode: Test-Modus aktiviert
        """
        pygame.init()
        
        self.width = width
        self.height = height
        self.test_mode = test_mode
        
        flags = pygame.FULLSCREEN | pygame.DOUBLEBUF if fullscreen else pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption('BVG Abfahrtsmonitor')
        
        # Schriften
        try:
            self.font_huge = pygame.font.SysFont('Liberation Sans', 64, bold=True)
            self.font_large = pygame.font.SysFont('Liberation Sans', 40, bold=True)
            self.font_medium = pygame.font.SysFont('Liberation Sans', 24)
            self.font_small = pygame.font.SysFont('Liberation Sans', 18)
            self.font_tiny = pygame.font.SysFont('Liberation Sans', 14)
        except:
            self.font_huge = pygame.font.Font(None, 64)
            self.font_large = pygame.font.Font(None, 40)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
        
        self.clock = pygame.time.Clock()
        
        # WiFi-Animation Setup
        self.wifi_frames = []
        self.wifi_icon_offline = None
        self.wifi_frame_index = 0
        self.wifi_animation_counter = 0
        self.wifi_animation_speed = WIFI_ANIMATION_SPEED
        self._load_wifi_icon()
        
        # Scrolling-Text Cache
        self.scrolling_texts = {}
        
        # Text-Rendering Cache (für statische Texte)
        self.text_cache = {}
        
        # Blink-State für "jetzt"-Abfahrten
        self.blink_state = True
        self.last_blink = time.time()
        
        # Online-Status
        self.is_live = True
        self.last_update_time = time.time()
    
    def _load_wifi_icon(self):
        """Lädt das WiFi-Icon mit pygame und generiert Reveal-Animation (unten nach oben)"""
        import os
        wifi_path = os.path.join(os.path.dirname(__file__), 'Wifi.png')

        try:
            wifi_image = pygame.image.load(wifi_path).convert_alpha()
            wifi_scaled = pygame.transform.smoothscale(wifi_image, (ICON_SIZE, ICON_SIZE))

            # Offline-Version (graues Icon)
            self.wifi_icon_offline = wifi_scaled.copy()
            self.wifi_icon_offline.fill((80, 80, 80), special_flags=pygame.BLEND_RGB_MULT)

            # Reveal-Animation: 8 Frames, progressiv von unten nach oben aufdeckend
            # Simuliert "Signal-Balken füllen sich auf"
            num_frames = 8
            self.wifi_frames = []
            for i in range(num_frames):
                frame = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
                reveal_height = max(1, int((i + 1) * ICON_SIZE / num_frames))
                reveal_y = ICON_SIZE - reveal_height
                frame.set_clip(pygame.Rect(0, reveal_y, ICON_SIZE, reveal_height))
                frame.blit(wifi_scaled, (0, 0))
                frame.set_clip(None)
                self.wifi_frames.append(frame)
        except Exception as e:
            logger.warning(f"WiFi-Icon konnte nicht geladen werden: {e}")
    
    def _render_text_cached(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int]) -> pygame.Surface:
        """
        Rendert Text mit Caching für bessere Performance
        
        Args:
            text: Zu rendernder Text
            font: Schriftart
            color: Textfarbe
            
        Returns:
            Gerenderte Text-Surface
        """
        cache_key = (text, id(font), color)
        if cache_key not in self.text_cache:
            self.text_cache[cache_key] = font.render(text, True, color)
        return self.text_cache[cache_key]
    
    def _get_product_icon(self, product: str) -> Tuple[str, Tuple[int, int, int]]:
        """
        Gibt Icon-Text und Farbe für Produkttyp zurück
        
        Returns:
            (icon_text, color)
        """
        product_map = {
            'subway': ('U-Bahn', self.PRODUCT_COLORS['subway']),
            'suburban': ('S-Bahn', self.PRODUCT_COLORS['suburban']),
            'tram': ('Tram', self.PRODUCT_COLORS['tram']),
            'bus': ('Bus', self.PRODUCT_COLORS['bus']),
            'ferry': ('Fähre', self.PRODUCT_COLORS['ferry']),
            'express': ('RBX', self.PRODUCT_COLORS['express']),
            'regional': ('RB', self.PRODUCT_COLORS['regional']),
        }
        return product_map.get(product, ('?', self.GRAY))
    
    def _draw_product_badge(self, screen: pygame.Surface, x: int, y: int, 
                           product: str, line: str, size: int = 50):
        """
        Zeichnet ein Produkt-Badge (Icon + Linie)
        
        Args:
            x, y: Position
            product: Produkttyp (subway, bus, etc.)
            line: Liniennummer
            size: Größe des Badges
        """
        icon_text, color = self._get_product_icon(product)
        
        # Badge-Hintergrund
        badge_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, color, badge_rect, border_radius=8)
        
        # Icon (oben im Badge)
        icon_surface = self.font_tiny.render(icon_text, True, self.WHITE)
        icon_rect = icon_surface.get_rect(centerx=x + size // 2, top=y + 4)
        screen.blit(icon_surface, icon_rect)
        
        # Liniennummer (unten im Badge)
        line_surface = self.font_medium.render(line, True, self.WHITE)
        line_rect = line_surface.get_rect(centerx=x + size // 2, bottom=y + size - 4)
        screen.blit(line_surface, line_rect)
    
    def _draw_disruption_banner(self, x: int, y: int, disruptions: List[Dict],
                                 max_width: int, station_index: int) -> int:
        """
        Zeichnet Störungsbanner für eine Station.
        
        Zeigt alle Störungen mit scrollendem Text bei langen Meldungen.
        Rotiert zwischen Störungen wenn mehrere vorhanden.
        
        Args:
            x, y: Position (obere linke Ecke)
            disruptions: Liste von Störungsdaten
            max_width: Verfügbare Breite
            station_index: Index der Station (für Scroll-Cache-Keys)
            
        Returns:
            Neue Y-Position nach dem Banner
        """
        if not disruptions:
            return y

        BANNER_HEIGHT = 22
        ICON_SIZE = 16
        TEXT_PADDING = 6
        MAX_DISRUPTIONS = 3  # Maximal angezeigte Störungen

        # Rotiere bei >MAX_DISRUPTIONS: zeige immer nur MAX_DISRUPTIONS, Auswahl wechselt
        visible = disruptions[:MAX_DISRUPTIONS]
        if len(disruptions) > MAX_DISRUPTIONS:
            cycle_period = 5  # Sekunden pro Rotation
            offset = int(time.time() / cycle_period) % len(disruptions)
            visible = [disruptions[(offset + i) % len(disruptions)] for i in range(MAX_DISRUPTIONS)]

        for idx, disruption in enumerate(visible):
            row_y = y + idx * (BANNER_HEIGHT + 2)
            summary = disruption.get('summary', 'Störung')
            dtype = disruption.get('type', 'warning')

            # Hintergrundfarbe je nach Typ
            bg_color = (60, 40, 0) if dtype == 'warning' else (40, 40, 20)
            banner_rect = pygame.Rect(x, row_y, max_width, BANNER_HEIGHT)
            pygame.draw.rect(self.screen, bg_color, banner_rect, border_radius=4)

            # "!" Icon
            icon_x = x + TEXT_PADDING
            icon_center_y = row_y + BANNER_HEIGHT // 2
            pygame.draw.circle(self.screen, self.ORANGE, (icon_x + ICON_SIZE // 2, icon_center_y), ICON_SIZE // 2)
            icon_text = self.font_tiny.render('!', True, self.WHITE)
            icon_rect = icon_text.get_rect(center=(icon_x + ICON_SIZE // 2, icon_center_y))
            self.screen.blit(icon_text, icon_rect)

            # Scrollender Störungstext
            text_x = icon_x + ICON_SIZE + TEXT_PADDING
            text_max_width = max_width - ICON_SIZE - TEXT_PADDING * 3
            scroll_key = f"disruption_{station_index}_{idx}_{summary[:20]}"

            if scroll_key not in self.scrolling_texts or self.scrolling_texts[scroll_key].text != summary:
                self.scrolling_texts[scroll_key] = ScrollingText(
                    summary, self.font_small, text_max_width, self.ORANGE
                )

            scroller = self.scrolling_texts[scroll_key]
            scroller.update()
            scroller.draw(self.screen, text_x, row_y + 3)

        total_height = len(visible) * (BANNER_HEIGHT + 2)

        # Hinweis wenn mehr Störungen vorhanden
        if len(disruptions) > MAX_DISRUPTIONS:
            hint_y = y + total_height
            count_text = self._render_text_cached(
                f'+{len(disruptions) - MAX_DISRUPTIONS} weitere', self.font_tiny, self.GRAY
            )
            self.screen.blit(count_text, (x + TEXT_PADDING, hint_y))
            total_height += 16

        return y + total_height + 4
    
    def _draw_legend(self):
        """Zeichnet die Farblegende am unteren Rand"""
        legend_y = self.height - 25
        
        # Trennlinie über der Legende
        pygame.draw.line(self.screen, self.DARK_GRAY, (0, legend_y - 5), (self.width, legend_y - 5), 1)
        
        # Legende-Items
        legend_items = [
            (self.GREEN, "🟢 >Fußweg"),
            (self.YELLOW, "🟡 =Fußweg"),
            (self.RED, "🔴 <Fußweg"),
            (self.ORANGE, "🟠 Störung"),
        ]
        
        # Berechne Abstände für Items
        item_width = (self.width - 220) // len(legend_items)  # Mehr Platz für Delay-Hinweis
        
        for i, (color, text) in enumerate(legend_items):
            x = i * item_width + 10
            
            # Farbiger Punkt
            pygame.draw.circle(self.screen, color, (x, legend_y + 7), 5)
            
            # Text (cached)
            legend_text = self._render_text_cached(text[2:], self.font_tiny, self.LIGHT_GRAY)
            self.screen.blit(legend_text, (x + 10, legend_y))
        
        # Delay-Hinweis rechts (erweitert für +/-)
        delay_hint = self._render_text_cached("Zeiten inkl. Delays (+/-)", self.font_tiny, self.GRAY)
        delay_x = self.width - delay_hint.get_width() - 10
        self.screen.blit(delay_hint, (delay_x, legend_y))
    
    def draw_departures(self, stations_data: List[Dict]):
        """
        Zeichnet Abfahrtszeiten im Zweispalten-Layout
        
        Args:
            stations_data: Liste von Stations-Daten mit Abfahrten
        """
        self.screen.fill(self.BLACK)
        
        # Blink-Update für "JETZT"
        current_time = time.time()
        if current_time - self.last_blink > 0.5:  # Alle 0.5 Sekunden
            self.blink_state = not self.blink_state
            self.last_blink = current_time
        
        # Header
        title = self._render_text_cached('BVG Abfahrten', self.font_small, self.LIGHT_GRAY)
        self.screen.blit(title, (20, 10))
        
        # Test-Modus Indikator (neben dem Titel)
        if self.test_mode:
            test_text = self._render_text_cached('testMode=ON', self.font_small, self.ORANGE)
            title_width = title.get_width()
            self.screen.blit(test_text, (30 + title_width, 10))
        
        # Uhrzeit und WiFi-Status Icon (oben rechts)
        now_str = datetime.now().strftime('%H:%M:%S')
        time_text = self.font_small.render(now_str, True, self.LIGHT_GRAY)
        time_width = time_text.get_width()
        
        # Aktualisierung vor X Sekunden (in 5s-Schritten, darunter)
        seconds_ago = int(time.time() - self.last_update_time)
        seconds_rounded = (seconds_ago // 5) * 5  # Runde auf 5er-Schritte
        update_text = self.font_tiny.render(f'vor {seconds_rounded}s', True, self.GRAY)
        update_width = update_text.get_width()
        
        # Zeit oben rechts
        self.screen.blit(time_text, (self.width - time_width - 10, 10))
        # Aktualisierung darunter (rechtsbündig, etwas höher damit nichts abgeschnitten wird)
        self.screen.blit(update_text, (self.width - update_width - 10, 26))  # Von 28 auf 26
        
        # WiFi-Icon Animation (links neben der Zeit)
        if self.wifi_frames:
            if self.is_live:
                # Animation abspielen
                self.wifi_animation_counter += 1
                if self.wifi_animation_counter >= self.wifi_animation_speed:
                    self.wifi_animation_counter = 0
                    self.wifi_frame_index = (self.wifi_frame_index + 1) % len(self.wifi_frames)
                icon = self.wifi_frames[self.wifi_frame_index]
            else:
                # Offline: statisches graues Icon
                icon = self.wifi_icon_offline
            
            icon_x = self.width - time_width - 35  # Links neben der Zeit
            if icon:
                self.screen.blit(icon, (icon_x, 10))
        
        # Trennlinie unter Header
        pygame.draw.line(self.screen, self.DARK_GRAY, (0, 40), (self.width, 40), 2)
        
        # Dynamisches Layout: 1 Spalte (volle Breite) oder 2 Spalten
        num_stations = len(stations_data)
        if num_stations == 1:
            # Eine Station: volle Breite nutzen
            column_width = self.width
            max_departures = 8  # Mehr Platz für Abfahrten
        else:
            # Mehrere Stationen: Zweispalten-Layout
            column_width = self.width // 2
            max_departures = 5
        
        for i, station in enumerate(stations_data[:2]):  # Max 2 Stationen
            # Spaltenposition
            x_offset = i * column_width
            y_offset = 50
            
            # Vertikale Trennlinie zwischen Spalten (nur bei 2 Stationen)
            if i == 1 and num_stations > 1:
                pygame.draw.line(self.screen, self.DARK_GRAY, 
                               (column_width, 40), (column_width, self.height), 2)
            
            # Station Header (kompakter)
            station_name = station['name']
            walking_time = station.get('walkingTime', 0)
            disruptions = station.get('disruptions', [])
            
            # Stationsname (länger - bis 40 Zeichen)
            station_short = station_name[:40] + '...' if len(station_name) > 40 else station_name
            header_text = self.font_medium.render(station_short, True, self.WHITE)
            self.screen.blit(header_text, (x_offset + 15, y_offset))
            
            # Fußweg-Info (klein und grau)
            walk_text = self.font_tiny.render(f'🚶 {walking_time} min', True, self.GRAY)
            self.screen.blit(walk_text, (x_offset + 15, y_offset + 28))
            
            # Störungsbanner (unter dem Namen)
            if disruptions:
                y_offset = self._draw_disruption_banner(
                    x_offset + 10, y_offset + 45,
                    disruptions, column_width - 20, i
                )
                y_offset += 15
            else:
                y_offset += 45
            
            # "Abfahrt in:" Label (rechtsbündig über den Zeitangaben, etwas nach links verschoben)
            abfahrt_label = self._render_text_cached('Abfahrt in:', self.font_tiny, self.GRAY)
            label_x = x_offset + column_width - 80  # Mehr nach links (vorher -65)
            self.screen.blit(abfahrt_label, (label_x, y_offset))
            y_offset += 18
            
            # Abfahrten (abhängig von Anzahl der Stationen)
            departures = station.get('departures', [])[:max_departures]
            
            if not departures:
                no_data = self._render_text_cached('Keine Abfahrten', self.font_small, self.GRAY)
                self.screen.blit(no_data, (x_offset + 20, y_offset))
            else:
                for dep in departures:
                    y_offset = self._draw_departure_compact(
                        dep, walking_time, x_offset + 10, y_offset, 
                        column_width - 20, f"station_{i}_dep_{dep['line']}_{dep['direction'][:10]}"
                    )
        
        # Farblegende am unteren Rand
        self._draw_legend()
        
        pygame.display.flip()
    
    def _draw_departure_compact(self, departure: Dict, walking_time: int, 
                               x: int, y: int, max_width: int, scroll_id: str) -> int:
        """
        Zeichnet eine einzelne Abfahrt (kompakt, zweispaltig)
        
        Args:
            departure: Abfahrtsdaten
            walking_time: Fußweg in Minuten
            x, y: Position
            max_width: Maximale Breite
            scroll_id: ID für Scrolling-Text Cache
            
        Returns:
            Neue Y-Position
        """
        line = departure['line']
        direction = departure['direction']
        minutes = departure['minutes']
        delay = departure.get('delay', 0)
        product = departure.get('product', 'bus')
        has_delay = delay > 0
        
        # Farbcodierung nach Fußweg (Fußweg = garantierte Schaffbarkeit)
        # Grün = Mehr Zeit als Fußweg (locker schaffbar)
        # Gelb = Genau Fußweg (auf den Punkt)
        # Rot = Weniger als Fußweg (zu knapp/zu spät)
        is_jetzt = False
        if minutes < walking_time:
            # Weniger als Fußweg - zu knapp!
            time_color = self.RED
            time_str = f"{minutes}'"
        elif minutes == walking_time:
            # Genau Fußweg - auf den Punkt!
            time_color = self.YELLOW
            time_str = f"{minutes}'"
        else:
            # Mehr als Fußweg - locker schaffbar!
            time_color = self.GREEN
            time_str = f"{minutes}'"
        
        # Spezialfall: "jetzt" für 0 Minuten
        if minutes == 0:
            time_color = self.RED if self.blink_state else self.DARK_GRAY
            time_str = "jetzt"
            is_jetzt = True
        
        # Produkt-Badge (links) - blinkt bei "jetzt"
        badge_size = 45
        if not is_jetzt or self.blink_state:
            self._draw_product_badge(self.screen, x, y, product, line, badge_size)
        
        # Richtung (scrollend wenn nötig) - blinkt bei "jetzt"
        direction_x = x + badge_size + 10
        direction_max_width = max_width - badge_size - 105  # Weniger Platz für bessere Trennung (vorher 80)
        
        # Scrolling-Text verwalten
        scroll_key = f"{scroll_id}_{direction}"
        if scroll_key not in self.scrolling_texts or self.scrolling_texts[scroll_key].text != direction:
            self.scrolling_texts[scroll_key] = ScrollingText(
                direction, self.font_small, direction_max_width, self.LIGHT_GRAY
            )
        
        scrolling_text = self.scrolling_texts[scroll_key]
        # Farbe immer aktualisieren: bei "jetzt" blinken, sonst normal
        if is_jetzt:
            scrolling_text.color = self.LIGHT_GRAY if self.blink_state else self.DARK_GRAY
        else:
            scrolling_text.color = self.LIGHT_GRAY
        scrolling_text.update()
        scrolling_text.draw(self.screen, direction_x, y + 5)
        
        # Zeit (rechts, groß und fett)
        time_text = self.font_large.render(time_str, True, time_color)
        time_width = time_text.get_width()
        self.screen.blit(time_text, (x + max_width - time_width - 5, y + 5))  # Weniger Abstand rechts
        
        # Verspätung/Verfrühung (klein daneben, falls vorhanden)
        if has_delay:
            delay_sign = '+' if delay > 0 else ''  # + bei Verspätung, - ist automatisch bei negativem delay
            delay_color = self.RED if delay > 0 else self.GREEN  # Rot bei Verspätung, Grün bei Verfrühung
            delay_text = self.font_small.render(f'({delay_sign}{delay})', True, delay_color)
            self.screen.blit(delay_text, (x + max_width - time_width - 5, y + 43))
        
        return y + 60
    
    def handle_events(self) -> bool:
        """
        Verarbeitet Events
        
        Returns:
            True wenn fortfahren, False zum Beenden
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
        return True
    
    def tick(self, fps: int = 5):
        """Limitiert FPS (erhöht für flüssiges Scrolling)"""
        self.clock.tick(fps)
    
    def quit(self):
        """Beendet pygame"""
        pygame.quit()
