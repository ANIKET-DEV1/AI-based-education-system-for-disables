# AI-Based Education System for Disabled Students (SunoPadho)

An AI-powered accessible learning platform built for students with learning disabilities. Uses AI to simplify complex text, generate quizzes, summarize PDFs, and provide an interactive tutor — all with voice support.

## Features

- **AI Tutor Chatbot** — Ask questions and get instant, simplified explanations
- **Magic Simplifier** — Paste complex text and get a simple version with visual keywords
- **PDF Summarizer** — Upload PDFs and get AI-powered summaries with bullet points
- **AI Quiz Generator** — Generate MCQ quizzes on any topic with difficulty levels
- **Document Converter** — Convert files between formats (PDF, PPT, Excel, CSV)
- **Activity Tracker** — Track learning progress and stats

## Accessibility Features

- **Hover-to-Listen (CC Mode)** — Hover over any element to hear it read aloud
- **Text-to-Speech** — Listen to page content via the speaker button
- **Font Size Controls** — Adjust text size (A+ / A-)
- **Theme Switching** — Dark, Light, and High-Contrast (colorblind-friendly) modes

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **AI Engine:** Groq API (Llama 3.3 70B)
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **PDF Processing:** PyPDF2

## Setup & Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ANIKET-DEV1/AI-based-education-system-for-disables.git
   cd AI-based-education-system-for-disables
   ```

2. **Create a `.env` file** with your credentials:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open in browser:** [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure

```
├── app.py                  # Flask app entry point
├── view.py                 # All routes (auth, pages, API)
├── models.py               # SQLite database layer
├── modules/
│   ├── ai_engine.py        # Groq AI functions (simplify, quiz, summarize)
│   └── video_engine.py     # Video generation module
├── templates/
│   ├── base.html           # Base layout with accessibility engine
│   ├── loginRegister.html  # Login & registration page
│   ├── dashboard.html      # Main dashboard
│   ├── chatbot.html        # AI tutor chatbot
│   ├── simplifier.html     # Text simplifier
│   ├── document.html       # PDF document reader/summarizer
│   ├── quiz.html           # AI quiz generator
│   ├── activity.html       # User activity & stats
│   ├── PDFSummarizer.html  # PDF summarizer (standalone)
│   └── documentConvert.html# File converter
├── requirements.txt
├── .env                    # Environment variables (not in repo)
└── .gitignore
```

## Team

**Null Pointers** — Built for Hackathon 2026