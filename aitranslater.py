import tkinter as tk
import sys 
import threading
import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
import customtkinter as ctk
import speech_recognition as sr
from gtts import gTTS

# Configure application styling and dark environment presets
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

HISTORY_FILE = "translation_history.json"

# Sabhi supporting languages ki standard list jo bina library ke chalegi
LANGUAGES = {
    "auto": "Auto Detect", "en": "English", "hi": "Hindi", "es": "Spanish", 
    "fr": "French", "de": "German", "ar": "Arabic", "ur": "Urdu", 
    "mr": "Marathi", "bn": "Bengali", "te": "Telugu", "ta": "Tamil"
}

class ProfessionalAITranslator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Core Engines initialization
        self.recognizer = sr.Recognizer()
        
        # Window Canvas Configurations
        self.title("AI Translator (Professional)")
        self.geometry("950x680")
        self.resizable(False, False)

        # Map structures
        self.lang_display_to_code = {name: code for code, name in LANGUAGES.items() if code != "auto"}
        self.lang_options = ["Auto Detect"] + sorted(list(self.lang_display_to_code.keys()))
        
        # UI Assembly & Lifecycle state restoration
        self.setup_ui_architecture()
        self.hydrate_history_stream()

    def setup_ui_architecture(self):
        """Builds structural panels and layout grids using CustomTkinter layers"""
        self.header_label = ctk.CTkLabel(
            self, text="AI TRANSLATOR PRO", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.header_label.pack(pady=(20, 10))

        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=25, pady=10)

        self.processing_hub = ctk.CTkFrame(self.workspace_canvas, fg_color="#1e1e24", corner_radius=12)
        self.processing_hub.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self.sidebar_history = ctk.CTkFrame(self.workspace_canvas, width=300, fg_color="#141419", corner_radius=12)
        self.sidebar_history.pack(side="right", fill="both", padx=(12, 0))
        self.sidebar_history.pack_propagate(False)

        self.assemble_processing_hub()
        self.assemble_sidebar_history()

    def assemble_processing_hub(self):
        self.route_row = ctk.CTkFrame(self.processing_hub, fg_color="transparent")
        self.route_row.pack(fill="x", padx=20, pady=(20, 10))

        self.src_lang_menu = ctk.CTkComboBox(self.route_row, values=self.lang_options, width=200, state="readonly")
        self.src_lang_menu.set("Auto Detect")
        self.src_lang_menu.pack(side="left", padx=(0, 10))

        self.swap_direction_btn = ctk.CTkButton(
            self.route_row, text="⇄", width=45, font=ctk.CTkFont(size=16), 
            fg_color="#2c2c35", hover_color="#3a3a45", command=self.swap_locales
        )
        self.swap_direction_btn.pack(side="left")

        self.dest_lang_menu = ctk.CTkComboBox(self.route_row, values=sorted(list(self.lang_display_to_code.keys())), width=200, state="readonly")
        self.dest_lang_menu.set("Hindi")
        self.dest_lang_menu.pack(side="left", padx=(10, 0))

        self.src_title = ctk.CTkLabel(self.processing_hub, text="Source Document / Text Entry", font=ctk.CTkFont(size=13, weight="bold"))
        self.src_title.pack(anchor="w", padx=22, pady=(15, 2))

        self.text_intake_field = ctk.CTkTextbox(self.processing_hub, height=150, font=ctk.CTkFont(size=15), fg_color="#141419", border_color="#2c2c35", border_width=1,spacing3=5)
        self.text_intake_field.pack(fill="x", padx=20, pady=5)

        self.commands_row = ctk.CTkFrame(self.processing_hub, fg_color="transparent")
        self.commands_row.pack(fill="x", padx=20, pady=10)

        self.execute_btn = ctk.CTkButton(
            self.commands_row, text="Translate", width=140, font=ctk.CTkFont(weight="bold"),
            fg_color="#1a73e8", hover_color="#155cb4", command=self.dispatch_translation
        )
        self.execute_btn.pack(side="left")

        self.mic_stream_btn = ctk.CTkButton(
            self.commands_row, text="🎙 Record Speech", width=130, 
            fg_color="#2b2b36", hover_color="#3d3d4c", command=self.dispatch_voice_capture
        )
        self.mic_stream_btn.pack(side="left", padx=10)

        self.app_status_monitor = ctk.CTkLabel(self.commands_row, text="Engine Idle", text_color="#7e7e8c", font=ctk.CTkFont(size=12))
        self.app_status_monitor.pack(side="left", padx=10)

        self.dest_title = ctk.CTkLabel(self.processing_hub, text="Translated Interpretation", font=ctk.CTkFont(size=13, weight="bold"))
        self.dest_title.pack(anchor="w", padx=22, pady=(15, 2))

        self.text_output_field = ctk.CTkTextbox(self.processing_hub, height=150, font=ctk.CTkFont(size=15), fg_color="#141419", border_color="#2c2c35", border_width=1,spacing3=5)
        self.text_output_field.pack(fill="x", padx=20, pady=5)
        self.text_output_field.configure(state="disabled")

        self.utilities_row = ctk.CTkFrame(self.processing_hub, fg_color="transparent")
        self.utilities_row.pack(fill="x", padx=20, pady=(10, 20))

        self.clipboard_btn = ctk.CTkButton(
            self.utilities_row, text="📋 Copy Raw Output", width=150, 
            fg_color="#0f9d58", hover_color="#0b7b43", command=self.commit_to_clipboard
        )
        self.clipboard_btn.pack(side="left", padx=(0, 10))

        self.tts_playback_btn = ctk.CTkButton(
            self.utilities_row, text="🔊 Listen Out loud", width=140, 
            fg_color="#8ab4f8", text_color="#121214", hover_color="#669df6", command=self.dispatch_tts_audio
        )
        self.tts_playback_btn.pack(side="left")

    def assemble_sidebar_history(self):
        self.hist_header = ctk.CTkLabel(self.sidebar_history, text="Translation History", font=ctk.CTkFont(size=14, weight="bold"))
        self.hist_header.pack(pady=(15, 5))

        self.history_stream_box = ctk.CTkTextbox(
            self.sidebar_history, font=ctk.CTkFont(size=13, family="Courier" if os.name == "nt" else "Monospace"), 
            fg_color="#0b0b0d", border_width=0,spacing3=4
        )
        self.history_stream_box.pack(fill="both", expand=True, padx=12, pady=10)
        self.history_stream_box.configure(state="disabled")

        self.flush_history_btn = ctk.CTkButton(
            self.sidebar_history, text="Clear Data Logs", fg_color="#d93025", hover_color="#b3241b", 
            command=self.purge_history_cache
        )
        self.flush_history_btn.pack(fill="x", padx=12, pady=15)

    def swap_locales(self):
        source_selection = self.src_lang_menu.get()
        destination_selection = self.dest_lang_menu.get()
        if source_selection != "Auto Detect":
            self.src_lang_menu.set(destination_selection)
            self.dest_lang_menu.set(source_selection)

    def print_status_update(self, text_signal):
        self.app_status_monitor.configure(text=text_signal)

    def dispatch_translation(self):
        threading.Thread(target=self.worker_thread_translate, daemon=True).start()

    def worker_thread_translate(self):
        self.print_status_update("Querying Translation APIs...")
        raw_input_payload = self.text_intake_field.get("1.0", tk.END).strip()
        
        if not raw_input_payload:
            self.print_status_update("Aborted: Empty payload source")
            return

        selected_src = self.src_lang_menu.get()
        selected_dest = self.dest_lang_menu.get()

        iso_src = 'auto' if selected_src == "Auto Detect" else self.lang_display_to_code[selected_src]
        iso_dest = self.lang_display_to_code[selected_dest]

        try:
            # High Stability Web Translation URL API Execution
            api_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={iso_src}&tl={iso_dest}&dt=t&q=" + urllib.parse.quote(raw_input_payload)
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req) as response:
                response_payload = json.loads(response.read().decode())
                
            translated_text = "".join([part[0] for part in response_payload[0] if part[0]])
            detected_shortcut = response_payload[2] if len(response_payload) > 2 else "en"

            self.text_output_field.configure(state="normal")
            self.text_output_field.delete("1.0", tk.END)
            self.text_output_field.insert("1.0", translated_text)
            self.text_output_field.configure(state="disabled")
            
            self.print_status_update("Success")

            # Source name handling
            source_full_name = LANGUAGES.get(detected_shortcut, "English").title() if selected_src == "Auto Detect" else selected_src

            self.push_transaction_to_history(
                raw_input_payload, translated_text, source_full_name, selected_dest
            )
        except Exception:
            self.print_status_update("Fault: Web Translation API failure")

    def dispatch_voice_capture(self):
        threading.Thread(target=self.worker_thread_voice_capture, daemon=True).start()

    def worker_thread_voice_capture(self):
        self.print_status_update("Opening Audio Channels...")
        selected_src = self.src_lang_menu.get()
        audio_iso_target = 'en-US' if selected_src == "Auto Detect" else self.lang_display_to_code[selected_src]

        with sr.Microphone() as environmental_mic:
            self.recognizer.adjust_for_ambient_noise(environmental_mic, duration=0.8)
            try:
                self.print_status_update("Listening... Talk now")
                captured_audio_buffer = self.recognizer.listen(environmental_mic, timeout=4.5, phrase_time_limit=10)
                self.print_status_update("Processing Speech Arrays...")
                
                parsed_speech_string = self.recognizer.recognize_google(captured_audio_buffer, language=audio_iso_target)
                
                self.text_intake_field.delete("1.0", tk.END)
                self.text_intake_field.insert("1.0", parsed_speech_string)
                self.print_status_update("Speech Imported")
                
                self.worker_thread_translate()
            except sr.WaitTimeoutError:
                self.print_status_update("Error: Connection Timeout")
            except sr.UnknownValueError:
                self.print_status_update("Error: Unresolvable audio signature")
            except Exception:
                self.print_status_update("Error: Internal voice matrix fault")

    def dispatch_tts_audio(self):
        threading.Thread(target=self.worker_thread_tts, daemon=True).start()

    def worker_thread_tts(self):
        target_payload = self.text_output_field.get("1.0", tk.END).strip()
        if not target_payload:
            self.print_status_update("Aborted: Empty output channel")
            return
        
        self.print_status_update("Rendering Audio Frame...")
        selected_dest_label = self.dest_lang_menu.get()
        audio_iso_code = self.lang_display_to_code[selected_dest_label]
        
        try:
            tts_engine = gTTS(text=target_payload, lang=audio_iso_code)
            temporary_cache_path = "runtime_playback.mp3"
            tts_engine.save(temporary_cache_path)
            self.print_status_update("Streaming Audio Core...")
            
            if os.name == 'posix':  
                os.system(f"afplay {temporary_cache_path}" if "darwin" in sys.platform else f"mpg123 {temporary_cache_path}")
            else:  # Windows
                if hasattr(os, 'startfile'):
                    os.startfile(temporary_cache_path)
                else:
                    os.system(f"start {temporary_cache_path}")
                
            self.print_status_update("Playback Completed")
        except Exception:
            self.print_status_update("Fault: Audio pipeline broke")

    def commit_to_clipboard(self):
        payload = self.text_output_field.get("1.0", tk.END).strip()
        if payload:
            self.clipboard_clear()
            self.clipboard_append(payload)
            self.print_status_update("Copied into Clipboard Matrix!")

    def hydrate_history_stream(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as storage_pointer:
                    active_history_payload = json.load(storage_pointer)
                self.history_stream_box.configure(state="normal")
                for entry in reversed(active_history_payload):
                    formatted_block = f"⏳ [{entry['time']}] ({entry['src']} ➔ {entry['dest']})\n📥 {entry['input']}\n📤 {entry['output']}\n{'-'*35}\n"
                    self.history_stream_box.insert(tk.END, formatted_block)
                self.history_stream_box.configure(state="disabled")
            except Exception:
                pass

    def push_transaction_to_history(self, intake, outtake, source_label, dest_label):
        current_time_stamp = datetime.now().strftime("%H:%M:%S")
        record_dictionary = {
            "time": current_time_stamp, 
            "src": source_label, 
            "dest": dest_label, 
            "input": intake, 
            "output": outtake
        }
        
        historical_array = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as storage_pointer:
                    historical_array = json.load(storage_pointer)
            except Exception: 
                pass
            
        historical_array.append(record_dictionary)
        historical_array = historical_array[-40:]

        with open(HISTORY_FILE, "w") as storage_pointer:
            json.dump(historical_array, storage_pointer, indent=4)

        self.history_stream_box.configure(state="normal")
        formatted_block = f"⏳ [{current_time_stamp}] ({source_label} ➔ {dest_label})\n📥 {intake}\n📤 {outtake}\n{'-'*35}\n"
        self.history_stream_box.insert("1.0", formatted_block)
        self.history_stream_box.configure(state="disabled")

    def purge_history_cache(self):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self.history_stream_box.configure(state="normal")
        self.history_stream_box.delete("1.0", tk.END)
        self.history_stream_box.configure(state="disabled")
        self.print_status_update("Cache Cleared Successfully")

if __name__ == "__main__":
    app = ProfessionalAITranslator()
    app.mainloop()