# 📚 极客智能单词突击系统

A modern, full-stack intelligent vocabulary learning application designed for CET-6 preparation, featuring dynamic
Spaced Repetition (SM-2), DeepSeek AI integration, and a highly polished UI.

## ✨ Core Features

* **🧠 Dynamic Spaced Repetition**: Granular interval scheduling (minute/hour/day level) based on the optimized SM-2
  algorithm.
* **🤖 AI Tutor Integration**: Powered by LLM DeepSeek for contextual word analysis, mnemonic generation, and semantic
  classification.
* **✍️ Multi-Mode Practice**: Supports classic flashcards, reverse dictation , and definition challenge.
* **⚡ Modern Tech Stack**: B/S architecture ensuring high performance and separation of concerns.

## 🛠️ Tech Stack

* **Frontend**: Vue 3, Vite, Axios, Marked.js (for AI markdown rendering).
* **Backend**: Python, FastAPI, SQLAlchemy.
* **Database**: SQLite.
* **External APIs**: Free Dictionary API, DeepSeek API.

## 🚀 Quick Start

### 1. Clone the repository

\`\`\`bash
git clone https://github.com/YourUsername/geek-vocab-system.git
cd geek-vocab-system
\`\`\`

### 2. Backend Setup

\`\`\`bash

# Create virtual environment and install dependencies

python -m venv .venv
source .venv/Scripts/activate # Windows
pip install fastapi uvicorn sqlalchemy deep-translator openai httpx

# Start the server

uvicorn backend.main:app --reload
\`\`\`

### 3. Frontend Setup

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## 📌 Architecture Overview

The system follows a strict Frontend-Backend separation model. The FastAPI backend serves as the brain, handling
algorithm scheduling and AI prompting, while the Vue3 frontend provides a seamless, SPA (Single Page Application)
experience with real-time markdown rendering for AI interactions.
