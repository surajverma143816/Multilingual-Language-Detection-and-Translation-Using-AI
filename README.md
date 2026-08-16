# 🤖 Multilingual Language Detection and Translation Using AI

A feature-rich, multi-threaded Desktop AI Translation Tool built with **Python** and **CustomTkinter**. 
It supports real-time text translation, speech recognition (Voice Input), text-to-speech audio playback, and local history tracking with a modern dark theme interface.

## 🛠 Tech Stack & Dependencies
* **Programming Language:** Python 3
* **GUI Framework:** `customtkinter`, `tkinter`
* **Translation Engine:** `googletrans`
* **Speech Recognition:** `SpeechRecognition` (via Microphone)
* **Text-To-Speech (TTS):** `gTTS`
* **Storage & Concurrency:** `json`, `threading`, `os`, `sys`, `datetime`

## ✨ Key Features
* 🌐 **Auto Language Detection & Mapping:** 
  Automatically detects the source language and maps short language codes to full display names (e.g., `en` ➔ `English`, `hi` ➔ `Hindi`).

* 🎙 **Live Voice Input (Speech-to-Text):** 
  Captures live speech using a microphone and automatically converts it into text for translation.

* 🔊 **Listen Out Loud (Text-to-Speech):** 
  Uses the `gTTS` engine to render translated text into natural audio playback.

* 📜 **Persistent Translation History:** 
  Automatically logs up to 40 recent translations with timestamps in a local `translation_history.json` file.

* ⚡ **Non-Blocking Multithreaded Engine:** 
  Runs API requests, speech recognition, and audio rendering on background threads to ensure a smooth, lag-free UI experience.

* 📋 **Clipboard Utility & Quick Actions:** 
  Includes a one-click copy button, language swapping functionality (`⇄`), and real-time engine status tracking.

## 📁 Repository Structure
* `aitranslater.py` — Main application source code containing UI logic and core features.
* `Presentation.pdf` — Project slide presentation deck.
* `REPORT 3.22.pdf` — Comprehensive academic project report and documentation.
* `translation_history.json` — Auto-generated local storage file for history logs.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/surajverma143816/Multilingual-Language-Detection-and-Translation-Using-AI.git]
   https://github.com/surajverma143816/Multilingual-Language-Detection-and-Translation-Using-AI.git
