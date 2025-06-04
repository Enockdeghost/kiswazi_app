import sys
import json
import sqlite3
import requests
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# API Configuration
OXFORD_API_URL = "https://od-api-sandbox.oxforddictionaries.com/api/v2"
APP_ID = "730af7fe"
APP_KEY = "7a410ccafe9572534dbd9f502daef133"

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('dictionary.db')
        self.create_tables()
        self.populate_sample_data()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                definition TEXT,
                part_of_speech TEXT,
                pronunciation TEXT,
                example TEXT,
                synonyms TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY,
                word TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def populate_sample_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
     
class OxfordAPIManager:
    @staticmethod
    def search_word(word):
        """Search word using API"""
        try:
            headers = {
                'app_id': APP_ID,
                'app_key': APP_KEY,
                'Accept': 'application/json'
            }
            
            # Clean the word input
            clean_word = word.lower().strip()
            
            # Try different endpoints
            endpoints = [
                f"{OXFORD_API_URL}/entries/en-us/{clean_word}",
                f"{OXFORD_API_URL}/entries/en-gb/{clean_word}",
                f"{OXFORD_API_URL}/entries/en/{clean_word}"
            ]
            
            for url in endpoints:
                print(f"Trying URL: {url}")
                response = requests.get(url, headers=headers, timeout=15)
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("API Response received successfully")
                        return OxfordAPIManager.parse_oxford_response(data, clean_word)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue
                elif response.status_code == 404:
                    print(f"Word '{clean_word}' not found in this endpoint")
                    continue
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    continue
            
            return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    @staticmethod
    def parse_oxford_response(data, word):
        """Parse Oxford API response into simplified format"""
        try:
            print("Parsing Oxford API response...")
            
            if 'results' not in data or not data['results']:
                print("No results in API response")
                return None
            
            result = data['results'][0]
            
            if 'lexicalEntries' not in result or not result['lexicalEntries']:
                print("No lexical entries found")
                return None
            
            lexical_entries = result['lexicalEntries'][0]
            
            # Get basic info
            actual_word = result.get('word', word)
            part_of_speech = ""
            
            if 'lexicalCategory' in lexical_entries:
                part_of_speech = lexical_entries['lexicalCategory'].get('text', '')
            
            # Get pronunciation
            pronunciation = ""
            if 'pronunciations' in lexical_entries:
                for pron in lexical_entries['pronunciations']:
                    if 'phoneticSpelling' in pron:
                        pronunciation = f"/{pron['phoneticSpelling']}/"
                        break
            elif 'pronunciations' in result:
                for pron in result['pronunciations']:
                    if 'phoneticSpelling' in pron:
                        pronunciation = f"/{pron['phoneticSpelling']}/"
                        break
            
            # Get definitions and examples
            definition = ""
            example = ""
            synonyms = ""
            
            if 'entries' in lexical_entries and lexical_entries['entries']:
                entries = lexical_entries['entries'][0]
                
                if 'senses' in entries and entries['senses']:
                    senses = entries['senses'][0]
                    
                    # Get definition
                    if 'definitions' in senses and senses['definitions']:
                        definition = senses['definitions'][0]
                    
                    # Get example
                    if 'examples' in senses and senses['examples']:
                        example = senses['examples'][0].get('text', '')
                    
                    # Get synonyms
                    if 'synonyms' in senses and senses['synonyms']:
                        syn_list = [syn.get('text', '') for syn in senses['synonyms'][:5] if 'text' in syn]
                        synonyms = ", ".join(syn_list)
            
            result_dict = {
                'word': actual_word,
                'definition': definition or "Definition not available",
                'part_of_speech': part_of_speech,
                'pronunciation': pronunciation,
                'example': example,
                'synonyms': synonyms
            }
            
            print(f"Successfully parsed word: {actual_word}")
            return result_dict
            
        except Exception as e:
            print(f"Error parsing Oxford response: {e}")
            import traceback
            traceback.print_exc()
            return None

class WordCard(QWidget):
    def __init__(self, word_data, parent=None):
        super().__init__(parent)
        self.word_data = word_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Word header
        header_layout = QHBoxLayout()
        
        if isinstance(self.word_data, dict):
            word = self.word_data['word']
            definition = self.word_data['definition']
            part_of_speech = self.word_data.get('part_of_speech', '')
            pronunciation = self.word_data.get('pronunciation', '')
            example = self.word_data.get('example', '')
            synonyms = self.word_data.get('synonyms', '')
        else:
            # Database tuple format
            word = self.word_data[1]
            definition = self.word_data[2]
            part_of_speech = self.word_data[3] if len(self.word_data) > 3 else ''
            pronunciation = self.word_data[4] if len(self.word_data) > 4 else ''
            example = self.word_data[5] if len(self.word_data) > 5 else ''
            synonyms = self.word_data[6] if len(self.word_data) > 6 else ''
        
        word_label = QLabel(word)
        word_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(word_label)
        
        if pronunciation:
            pron_label = QLabel(pronunciation)
            pron_label.setStyleSheet("font-size: 16px; color: #7f8c8d; font-style: italic;")
            header_layout.addWidget(pron_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Part of speech
        if part_of_speech:
            pos_label = QLabel(f"({part_of_speech})")
            pos_label.setStyleSheet("font-size: 14px; color: #3498db; font-weight: bold;")
            layout.addWidget(pos_label)
        
        # Definition
        def_label = QLabel(definition)
        def_label.setWordWrap(True)
        def_label.setStyleSheet("font-size: 16px; color: #2c3e50; margin: 10px 0;")
        layout.addWidget(def_label)
        
        # Example
        if example:
            example_label = QLabel(f"Example: {example}")
            example_label.setWordWrap(True)
            example_label.setStyleSheet("font-size: 14px; color: #7f8c8d; font-style: italic;")
            layout.addWidget(example_label)
        
        # Synonyms
        if synonyms:
            syn_label = QLabel(f"Synonyms: {synonyms}")
            syn_label.setWordWrap(True)
            syn_label.setStyleSheet("font-size: 14px; color: #27ae60;")
            layout.addWidget(syn_label)
        
        self.setStyleSheet("""
            WordCard {
                background-color: white;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)

class KiswaziDictionary(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.show_random_word()
    
    def init_ui(self):
        self.setWindowTitle("Kiswazi Dictionary - Oxford Powered")
        self.setGeometry(100, 100, 1000, 700)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
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
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        self.create_header(main_layout)
        
        # Results area
        self.results_scroll = QScrollArea()
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_scroll.setWidget(self.results_widget)
        self.results_scroll.setWidgetResizable(True)
        main_layout.addWidget(self.results_scroll)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        random_word_btn = QPushButton("Random Word")
        random_word_btn.clicked.connect(self.show_random_word)
        actions_layout.addWidget(random_word_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        actions_layout.addWidget(clear_btn)
        
        history_btn = QPushButton("Search History")
        history_btn.clicked.connect(self.show_history)
        actions_layout.addWidget(history_btn)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        self.statusBar().showMessage("Ready - Powered by API")
    
    def create_header(self, layout):
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📚 Kiswazi Dictionary")
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
        
        # Test API connection button
        test_api_btn = QPushButton("Test API")
        test_api_btn.clicked.connect(self.test_api_connection)
        header_layout.addWidget(test_api_btn)
        
        layout.addLayout(header_layout)
    
    def test_api_connection(self):
        """Test the API connection"""
        self.statusBar().showMessage("Testing API connection...")
        
        # Test with a simple word
        test_word = "test"
        result = OxfordAPIManager.search_word(test_word)
        
        if result and result['definition'] != "Definition not available":
            QMessageBox.information(self, "API Test", 
                                  f"✓ API Connection Successful!\n\n"
                                  f"Test word: {result['word']}\n"
                                  f"Definition: {result['definition'][:100]}...")
            self.statusBar().showMessage("✓ API connection successful")
        else:
            QMessageBox.warning(self, "API Test", 
                              "✗ API Connection Failed!\n\n"
                              "Please check:\n"
                              "• Internet connection\n"
                              "• API credentials\n"
                              "• API rate limits")
            self.statusBar().showMessage("✗ API connection failed")
    
    def search_word(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.statusBar().showMessage("Searching...")
        self.clear_results()
        
        # Add to search history
        cursor = self.db.conn.cursor()
        cursor.execute("INSERT INTO search_history (word) VALUES (?)", (query,))
        self.db.conn.commit()
        
        # Try Oxford API first
        print(f"Searching for: {query}")
        oxford_result = OxfordAPIManager.search_word(query)
        
        if oxford_result and oxford_result['definition'] != "Definition not available":
            print("Oxford API result found")
            
            # Save to local database
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO words (word, definition, part_of_speech, pronunciation, example, synonyms)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    oxford_result['word'],
                    oxford_result['definition'],
                    oxford_result['part_of_speech'],
                    oxford_result['pronunciation'],
                    oxford_result['example'],
                    oxford_result['synonyms']
                ))
                self.db.conn.commit()
                print("Saved to local database")
            except Exception as e:
                print(f"Error saving to database: {e}")
            
            # Display result
            word_card = WordCard(oxford_result)
            self.results_layout.addWidget(word_card)
            self.statusBar().showMessage(f"✓ Found '{query}' from")
            
        else:
            print("Oxford API failed, searching local database...")
            
            # Fallback to local database
            cursor.execute("""
                SELECT * FROM words WHERE word LIKE ? OR definition LIKE ?
            """, (f"%{query}%", f"%{query}%"))
            
            results = cursor.fetchall()
            
            if results:
                for word_data in results:
                    word_card = WordCard(word_data)
                    self.results_layout.addWidget(word_card)
                self.statusBar().showMessage(f"Found {len(results)} result(s) from local database")
            else:
                # Show "not found" message with suggestions
                not_found_widget = QWidget()
                not_found_layout = QVBoxLayout(not_found_widget)
                
                no_results = QLabel(f"'{query}' not found")
                no_results.setAlignment(Qt.AlignCenter)
                no_results.setStyleSheet("font-size: 18px; color: #e74c3c; font-weight: bold; padding: 20px;")
                not_found_layout.addWidget(no_results)
                
                suggestions = QLabel("• Check spelling\n• Try simpler words\n• Use base form (e.g., 'run' instead of 'running')")
                suggestions.setAlignment(Qt.AlignCenter)
                suggestions.setStyleSheet("font-size: 14px; color: #7f8c8d;")
                not_found_layout.addWidget(suggestions)
                
                self.results_layout.addWidget(not_found_widget)
                self.statusBar().showMessage(f"'{query}' not found in or local database")
    
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
    
    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search History")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout(dialog)
        
        history_list = QListWidget()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT word, timestamp FROM search_history ORDER BY timestamp DESC LIMIT 50")
        for word, timestamp in cursor.fetchall():
            history_list.addItem(f"{word} - {timestamp}")
        
        layout.addWidget(history_list)
        
        # Clear history button
        clear_btn = QPushButton("Clear History")
        def clear_history():
            cursor.execute("DELETE FROM search_history")
            self.db.conn.commit()
            history_list.clear()
        clear_btn.clicked.connect(clear_history)
        layout.addWidget(clear_btn)
        
        dialog.exec_()
    
    def closeEvent(self, event):
        self.db.conn.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Kiswazi Dictionary")
    app.setApplicationVersion("2.0")
    
    window = KiswaziDictionary()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()