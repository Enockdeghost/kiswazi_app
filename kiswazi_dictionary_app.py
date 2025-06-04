import sys
import json
import sqlite3
import random
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
from gtts import gTTS
import pygame
import tempfile
import os

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('dictionary.db')
        self.create_tables()
        self.populate_sample_data()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Words table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                definition TEXT,
                part_of_speech TEXT,
                pronunciation TEXT,
                etymology TEXT,
                example TEXT,
                synonyms TEXT,
                antonyms TEXT
            )
        ''')
        
        # Search history kwa database
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY,
                word TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bookmarks///////////
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Custom word lists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_lists (
                id INTEGER PRIMARY KEY,
                list_name TEXT,
                words TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def populate_sample_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
        if cursor.fetchone()[0] == 0:
            sample_words = [
                ("hello", "A greeting used when meeting someone", "interjection", "/həˈloʊ/", "From Old English", "Hello, how are you?", "hi,greetings", "goodbye"),
                ("computer", "An electronic device for processing data", "noun", "/kəmˈpjuːtər/", "From Latin computare", "I use my computer daily", "machine,device", ""),
                ("beautiful", "Pleasing to the senses or mind", "adjective", "/ˈbjuːtɪfəl/", "From beauty + -ful", "The sunset is beautiful", "pretty,gorgeous", "ugly,hideous"),
                ("run", "To move at a speed faster than walking", "verb", "/rʌn/", "From Old English", "I run every morning", "jog,sprint", "walk,crawl"),
                ("wisdom", "The quality of having experience and good judgment", "noun", "/ˈwɪzdəm/", "From Old English", "Age brings wisdom", "knowledge,insight", "ignorance,foolishness")
            ]
            
            cursor.executemany('''
                INSERT INTO words (word, definition, part_of_speech, pronunciation, etymology, example, synonyms, antonyms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_words)
            self.conn.commit()

class WordCard(QWidget):
    def __init__(self, word_data, parent=None):
        super().__init__(parent)
        self.word_data = word_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Word header
        header_layout = QHBoxLayout()
        word_label = QLabel(self.word_data[1])  
        # docorator hh
        word_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(word_label)
        
        # Pronunciation
        if self.word_data[4]:  # pronunciation
            pron_label = QLabel(self.word_data[4])
            pron_label.setStyleSheet("font-size: 16px; color: #7f8c8d; font-style: italic;")
            header_layout.addWidget(pron_label)
        
        header_layout.addStretch()
        
        # Audio button
        audio_btn = QPushButton("🔊")
        audio_btn.setFixedSize(30, 30)
        audio_btn.clicked.connect(self.play_pronunciation)
        header_layout.addWidget(audio_btn)
        
        # Bookmark button
        bookmark_btn = QPushButton("⭐")
        bookmark_btn.setFixedSize(30, 30)
        bookmark_btn.clicked.connect(self.toggle_bookmark)
        header_layout.addWidget(bookmark_btn)
        
        layout.addLayout(header_layout)
        
        # Part of speech
        if self.word_data[3]:  # part_of_speech
            pos_label = QLabel(f"({self.word_data[3]})")
            pos_label.setStyleSheet("font-size: 14px; color: #3498db; font-weight: bold;")
            layout.addWidget(pos_label)
        
        # Definition
        def_label = QLabel(self.word_data[2])  # definition
        def_label.setWordWrap(True)
        def_label.setStyleSheet("font-size: 16px; color: #2c3e50; margin: 10px 0;")
        layout.addWidget(def_label)
        
        # Example
        if self.word_data[6]:  # example
            example_label = QLabel(f"Example: {self.word_data[6]}")
            example_label.setWordWrap(True)
            example_label.setStyleSheet("font-size: 14px; color: #7f8c8d; font-style: italic;")
            layout.addWidget(example_label)
        
        # Synonyms and Antonyms
        if self.word_data[7]:  # synonyms
            syn_label = QLabel(f"Synonyms: {self.word_data[7]}")
            syn_label.setWordWrap(True)
            syn_label.setStyleSheet("font-size: 14px; color: #27ae60;")
            layout.addWidget(syn_label)
        
        if self.word_data[8]:  # antonyms
            ant_label = QLabel(f"Antonyms: {self.word_data[8]}")
            ant_label.setWordWrap(True)
            ant_label.setStyleSheet("font-size: 14px; color: #e74c3c;")
            layout.addWidget(ant_label)
        
        # Etymology
        if self.word_data[5]:  # etymology
            etym_label = QLabel(f"Etymology: {self.word_data[5]}")
            etym_label.setWordWrap(True)
            etym_label.setStyleSheet("font-size: 12px; color: #95a5a6;")
            layout.addWidget(etym_label)
        
        self.setStyleSheet("""
            WordCard {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
    
    def play_pronunciation(self):
        try:
            word = self.word_data[1]
            tts = gTTS(text=word, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                pygame.mixer.init()
                pygame.mixer.music.load(temp_file.name)
                pygame.mixer.music.play()
        except Exception as e:
            QMessageBox.warning(self, "Audio Error", f"Could not play pronunciation: {str(e)}")
    
    def toggle_bookmark(self):
        # Toggle bookmark functionality
        pass

class kiswaziDictionary(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.load_settings()
        self.show_word_of_day()
    
    def init_ui(self):
        self.setWindowTitle("kiswazi Dictionary - Language Helper")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set kiswazi style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        self.create_header(main_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dictionary_tab()
        self.create_translator_tab()
        self.create_vocabulary_tab()
        self.create_grammar_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
    
    def create_header(self, layout):
        header_layout = QHBoxLayout()
        
        # Logo/Title
        title_label = QLabel("📚 kiswazi Dictionary")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a word...")
        self.search_input.setFixedWidth(300)
        self.search_input.returnPressed.connect(self.search_word)
        header_layout.addWidget(self.search_input)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_word)
        header_layout.addWidget(search_btn)
        
        # Dark mode toggle
        self.dark_mode_btn = QPushButton("🌙")
        self.dark_mode_btn.setFixedSize(40, 40)
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        header_layout.addWidget(self.dark_mode_btn)
        
        layout.addLayout(header_layout)
    
    def create_dictionary_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search results area
        self.results_scroll = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_scroll.setWidget(self.results_widget)
        self.results_scroll.setWidgetResizable(True)
        layout.addWidget(self.results_scroll)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        random_word_btn = QPushButton("Random Word")
        random_word_btn.clicked.connect(self.show_random_word)
        actions_layout.addWidget(random_word_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        actions_layout.addWidget(clear_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        self.tab_widget.addTab(tab, "Dictionary")
    
    def create_translator_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("From:"))
        self.from_lang = QComboBox()
        self.from_lang.addItems(["English", "Spanish", "French", "German", "Italian"])
        lang_layout.addWidget(self.from_lang)
        
        lang_layout.addWidget(QLabel("To:"))
        self.to_lang = QComboBox()
        self.to_lang.addItems(["Spanish", "English", "French", "German", "Italian"])
        lang_layout.addWidget(self.to_lang)
        
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Translation input
        self.translate_input = QTextEdit()
        self.translate_input.setPlaceholderText("Enter text to translate...")
        self.translate_input.setMaximumHeight(100)
        layout.addWidget(self.translate_input)
        
        # Translate button
        translate_btn = QPushButton("Translate")
        translate_btn.clicked.connect(self.translate_text)
        layout.addWidget(translate_btn)
        
        # Translation output
        self.translation_output = QTextEdit()
        self.translation_output.setReadOnly(True)
        layout.addWidget(self.translation_output)
        
        self.tab_widget.addTab(tab, "Translator")
    
    def create_vocabulary_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left panel - Word lists
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Word Lists"))
        
        self.word_lists = QListWidget()
        self.word_lists.addItems(["GRE Words", "TOEFL Words", "Academic Words", "Business Terms", "My Custom List"])
        left_layout.addWidget(self.word_lists)
        
        # Add new list button
        add_list_btn = QPushButton("Add New List")
        add_list_btn.clicked.connect(self.add_word_list)
        left_layout.addWidget(add_list_btn)
        
        layout.addWidget(left_panel)
        
        # Right panel - Flashcards
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Flashcard display
        self.flashcard = QFrame()
        self.flashcard.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #007bff;
                border-radius: 10px;
                min-height: 200px;
            }
        """)

        #error here
        flashcard_layout = QVBoxLayout(self.flashcard)
        
        self.flashcard_word = QLabel("Click 'Start Practice' to begin")
        self.flashcard_word.setAlignment(Qt.AlignCenter)
        self.flashcard_word.setStyleSheet("font-size: 24px; font-weight: bold;")
        flashcard_layout.addWidget(self.flashcard_word)
        
        self.flashcard_definition = QLabel("")
        self.flashcard_definition.setAlignment(Qt.AlignCenter)
        self.flashcard_definition.setWordWrap(True)
        self.flashcard_definition.setStyleSheet("font-size: 16px; color: #666;")
        flashcard_layout.addWidget(self.flashcard_definition)
        
        right_layout.addWidget(self.flashcard)
        
        # Flashcard controls
        controls_layout = QHBoxLayout()
        
        self.start_practice_btn = QPushButton("Start Practice")
        self.start_practice_btn.clicked.connect(self.start_flashcard_practice)
        controls_layout.addWidget(self.start_practice_btn)
        
        self.flip_btn = QPushButton("Flip Card")
        self.flip_btn.clicked.connect(self.flip_flashcard)
        self.flip_btn.setEnabled(False)
        controls_layout.addWidget(self.flip_btn)
        
        self.next_btn = QPushButton("Next Card")
        self.next_btn.clicked.connect(self.next_flashcard)
        self.next_btn.setEnabled(False)
        controls_layout.addWidget(self.next_btn)
        
        right_layout.addLayout(controls_layout)
        
        layout.addWidget(right_panel)
        
        self.tab_widget.addTab(tab, "Vocabulary")
    
    def create_grammar_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grammar checker input
        layout.addWidget(QLabel("Grammar Checker"))
        self.grammar_input = QTextEdit()
        self.grammar_input.setPlaceholderText("Enter your text to check grammar...")
        self.grammar_input.setMaximumHeight(100)
        layout.addWidget(self.grammar_input)
        
        # Check button
        check_btn = QPushButton("Check Grammar")
        check_btn.clicked.connect(self.check_grammar)
        layout.addWidget(check_btn)
        
        # Results
        self.grammar_results = QTextEdit()
        self.grammar_results.setReadOnly(True)
        layout.addWidget(self.grammar_results)
        
        # Grammar rules section
        layout.addWidget(QLabel("Grammar Rules"))
        self.grammar_rules = QTextBrowser()
        self.grammar_rules.setHtml("""
        <h3>Common Grammar Rules</h3>
        <ul>
            <li><b>Subject-Verb Agreement:</b> The subject and verb must agree in number</li>
            <li><b>Articles:</b> Use 'a' before consonant sounds, 'an' before vowel sounds</li>
            <li><b>Past Tense:</b> Regular verbs add -ed, irregular verbs have unique forms</li>
            <li><b>Prepositions:</b> In (enclosed spaces), On (surfaces), At (specific points)</li>
        </ul>
        """)
        layout.addWidget(self.grammar_rules)
        
        self.tab_widget.addTab(tab, "Grammar")
    
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_search_history)
        controls_layout.addWidget(refresh_btn)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_search_history)
        controls_layout.addWidget(clear_history_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # History list
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        # Bookmarks section
        layout.addWidget(QLabel("Bookmarks"))
        self.bookmarks_list = QListWidget()
        layout.addWidget(self.bookmarks_list)
        
        self.load_search_history()
        
        self.tab_widget.addTab(tab, "History")
    
    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        self.dark_mode_check = QCheckBox("Dark Mode")
        self.dark_mode_check.toggled.connect(self.toggle_dark_mode)
        appearance_layout.addWidget(self.dark_mode_check)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addWidget(self.font_size_spin)
        appearance_layout.addLayout(font_layout)
        
        layout.addWidget(appearance_group)
        
        # Language settings
        language_group = QGroupBox("Language Settings")
        language_layout = QVBoxLayout(language_group)
        
        self.pronunciation_check = QCheckBox("Enable Pronunciation")
        self.pronunciation_check.setChecked(True)
        language_layout.addWidget(self.pronunciation_check)
        
        self.auto_translate_check = QCheckBox("Auto-translate unknown words")
        language_layout.addWidget(self.auto_translate_check)
        
        layout.addWidget(language_group)
        
        # Data settings
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout(data_group)
        
        export_btn = QPushButton("Export Personal Data")
        export_btn.clicked.connect(self.export_data)
        data_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Personal Data")
        import_btn.clicked.connect(self.import_data)
        data_layout.addWidget(import_btn)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Settings")
    
    def search_word(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        # Add to search history
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO search_history (word) VALUES (?)", (query,))
        self.db.conn.commit()
        
        # Search in database
        cursor.execute("""
            SELECT * FROM words WHERE word LIKE ? OR definition LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        
        results = cursor.fetchall()
        
        # Clear previous results
        self.clear_results()
        
        if results:
            for word_data in results:
                word_card = WordCard(word_data)
                self.results_layout.addWidget(word_card)
            self.statusBar().showMessage(f"Found {len(results)} result(s)")
        else:
            no_results = QLabel(f"No results found for '{query}'")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 50px;")
            self.results_layout.addWidget(no_results)
            self.statusBar().showMessage("No results found")
        
        # Switch to dictionary tab
        self.tab_widget.setCurrentIndex(0)
    
    def clear_results(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def show_random_word(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            self.clear_results()
            word_card = WordCard(result)
            self.results_layout.addWidget(word_card)
            self.statusBar().showMessage("Random word displayed")
    
    def show_word_of_day(self):
        # Simple implementation - could be enhanced with actual word-of-day logic
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            word = result[1]
            definition = result[2]
            self.statusBar().showMessage(f"Word of the Day: {word} - {definition[:50]}...")
    
    def translate_text(self):
        text = self.translate_input.toPlainText()
        if not text:
            return
        
        # Simple mock translation (in real app, use Google Translate API or similar)
        self.translation_output.setText(f"[Translated] {text}")
        self.statusBar().showMessage("Text translated (mock)")
    
    def start_flashcard_practice(self):
        self.flashcard_words = []
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT word, definition FROM words ORDER BY RANDOM() LIMIT 10")
        self.flashcard_words = cursor.fetchall()
        
        if self.flashcard_words:
            self.current_flashcard_index = 0
            self.flashcard_showing_definition = False
            self.update_flashcard()
            self.flip_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
            self.start_practice_btn.setText("Restart Practice")
    
    def update_flashcard(self):
        if self.flashcard_words and self.current_flashcard_index < len(self.flashcard_words):
            word, definition = self.flashcard_words[self.current_flashcard_index]
            if self.flashcard_showing_definition:
                self.flashcard_word.setText(definition)
                self.flashcard_definition.setText("")
            else:
                self.flashcard_word.setText(word)
                self.flashcard_definition.setText("Click 'Flip Card' to see definition")
    
    def flip_flashcard(self):
        self.flashcard_showing_definition = not self.flashcard_showing_definition
        self.update_flashcard()
    
    def next_flashcard(self):
        self.current_flashcard_index += 1
        self.flashcard_showing_definition = False
        
        if self.current_flashcard_index >= len(self.flashcard_words):
            self.flashcard_word.setText("Practice Complete!")
            self.flashcard_definition.setText("Click 'Start Practice' to begin again")
            self.flip_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
        else:
            self.update_flashcard()
    
    def add_word_list(self):
        name, ok = QInputDialog.getText(self, 'New Word List', 'Enter list name:')
        if ok and name:
            self.word_lists.addItem(name)
            cursor = self.db.conn.cursor()
            cursor.execute("INSERT INTO word_lists (list_name, words) VALUES (?, ?)", (name, ""))
            self.db.conn.commit()
    
    def check_grammar(self):
        text = self.grammar_input.toPlainText()
        if not text:
            return
        
        # Simple grammar check (mock implementation)
        suggestions = []
        
        # Check for common mistakes
        if " dont " in text.lower():
            suggestions.append("Consider using 'don't' instead of 'dont'")
        if " cant " in text.lower():
            suggestions.append("Consider using 'can't' instead of 'cant'")
        if text.count('.') == 0 and len(text) > 10:
            suggestions.append("Consider adding punctuation")
        
        if suggestions:
            self.grammar_results.setText("Suggestions:\n" + "\n".join(f"• {s}" for s in suggestions))
        else:
            self.grammar_results.setText("No grammar issues detected!")
    
    def load_search_history(self):
        self.history_list.clear()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT word, timestamp FROM search_history ORDER BY timestamp DESC LIMIT 50")
        for word, timestamp in cursor.fetchall():
            self.history_list.addItem(f"{word} - {timestamp}")
    
    def clear_search_history(self):
        cursor = self.db.conn.cursor()
        cursor.execute("DELETE FROM search_history")
        self.db.conn.commit()
        self.load_search_history()
        self.statusBar().showMessage("Search history cleared")
    
    def toggle_dark_mode(self):
        # Toggle between light and dark themes
        if hasattr(self, 'dark_mode') and self.dark_mode:
            self.apply_light_theme()
            self.dark_mode = False
            self.dark_mode_btn.setText("🌙")
        else:
            self.apply_dark_theme()
            self.dark_mode = True
            self.dark_mode_btn.setText("☀️")
    
    def apply_dark_theme(self):
        dark_style = """
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #34495e;
                background-color: #34495e;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                border-bottom: 2px solid #3498db;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #7f8c8d;
                padding: 10px;
                border-radius: 6px;
            }
            QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                color: #ecf0f1;
            }
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
            }
            QScrollArea {
                background-color: #2c3e50;
            }
            QGroupBox {
                color: #ecf0f1;
                border: 2px solid #7f8c8d;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        self.setStyleSheet(dark_style)
    
    def apply_light_theme(self):
        light_style = """
            QMainWindow {
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        self.setStyleSheet(light_style)
    
    def export_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Export Data', 'dictionary_data.json', 'JSON Files (*.json)')
        if filename:
            try:
                data = {
                    'search_history': [],
                    'bookmarks': [],
                    'word_lists': []
                }
                
                cursor = self.db.conn.cursor()
                
                # Export search history
                cursor.execute("SELECT word, timestamp FROM search_history")
                data['search_history'] = [{'word': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
                
                # Export bookmarks
                cursor.execute("SELECT word, timestamp FROM bookmarks")
                data['bookmarks'] = [{'word': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
                
                # Export word lists
                cursor.execute("SELECT list_name, words, created_date FROM word_lists")
                data['word_lists'] = [{'name': row[0], 'words': row[1], 'created_date': row[2]} for row in cursor.fetchall()]
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                QMessageBox.information(self, "Export Complete", f"Data exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def import_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Import Data', '', 'JSON Files (*.json)')
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                cursor = self.db.conn.cursor()
                
                # Import search history
                for item in data.get('search_history', []):
                    cursor.execute("INSERT OR IGNORE INTO search_history (word, timestamp) VALUES (?, ?)",
                                 (item['word'], item['timestamp']))
                
                # Import bookmarks
                for item in data.get('bookmarks', []):
                    cursor.execute("INSERT OR IGNORE INTO bookmarks (word, timestamp) VALUES (?, ?)",
                                 (item['word'], item['timestamp']))
                
                # Import word lists
                for item in data.get('word_lists', []):
                    cursor.execute("INSERT OR IGNORE INTO word_lists (list_name, words, created_date) VALUES (?, ?, ?)",
                                 (item['name'], item['words'], item['created_date']))
                
                self.db.conn.commit()
                self.load_search_history()
                
                QMessageBox.information(self, "Import Complete", "Data imported successfully")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import data: {str(e)}")
    
    def load_settings(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        settings = dict(cursor.fetchall())
        
        # Apply saved settings
        if settings.get('dark_mode') == 'true':
            self.dark_mode = True
            self.apply_dark_theme()
            self.dark_mode_btn.setText("☀️")
            self.dark_mode_check.setChecked(True)
        else:
            self.dark_mode = False
    
    def save_settings(self):
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                      ('dark_mode', 'true' if self.dark_mode else 'false'))
        self.db.conn.commit()
    
    def closeEvent(self, event):
        self.save_settings()
        self.db.conn.close()
        event.accept()

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        
        # Create a simple splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor('#007bff'))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        font = QFont('Arial', 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📚 kiswazi Dictionary\n\nLoading...")
        painter.end()
        
        self.setPixmap(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("kiswazi Dictionary")
    app.setApplicationVersion("1.0")
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Process events to show splash
    app.processEvents()
    
    # Load main window
    window = kiswaziDictionary()
    
    # Close splash and show main window
    splash.finish(window)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()