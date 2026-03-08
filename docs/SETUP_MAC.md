# Setup Guide for Mac Users

**Introduction to AI Agents - Local Setup**
*By Nisarg Kadam | Senior AI Engineer*

This guide will walk you through everything from scratch — even if you've never coded before.

---

## Step 1: Install VS Code (Your Code Editor)

1. Open your browser and go to: https://code.visualstudio.com/
2. Click the big blue **"Download for Mac"** button
   - If you have a newer Mac (2020 or later) — pick **Apple Silicon**
   - If you have an older Mac — pick **Intel Chip**
   - Not sure? Click the Apple logo (top-left of screen) → "About This Mac" → check if it says "Apple M1/M2/M3" or "Intel"
3. Open the downloaded `.zip` file — it will extract to **Visual Studio Code.app**
4. Drag it into your **Applications** folder
5. Open it from Applications (or Spotlight: press `Cmd + Space`, type "Visual Studio Code")

### Enable the `code` command (so you can open projects from Terminal):
1. In VS Code, press `Cmd + Shift + P`
2. Type: **"Shell Command: Install 'code' command in PATH"**
3. Click on it — done!

---

## Step 2: Install Python

Mac comes with an old version of Python. We need the latest one.

1. Open your browser and go to: https://www.python.org/downloads/
2. Click the big yellow **"Download Python 3.x.x"** button
3. Open the downloaded `.pkg` file
4. Follow the installer — click **Continue** → **Agree** → **Install**
5. Enter your Mac password when asked
6. Click **Close** when done

### Verify Python is installed:
1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
2. Type this and press Enter:
   ```
   python3 --version
   ```
3. You should see something like `Python 3.11.9` — that means it worked!

> **Important:** On Mac, always use `python3` and `pip3` (not `python` and `pip`).

---

## Step 3: Install Git

Most Macs come with Git pre-installed. Let's check:

1. Open Terminal
2. Type:
   ```
   git --version
   ```
3. If you see a version number like `git version 2.x.x` — you're all set! Skip to Step 4.
4. If it asks you to install "Command Line Developer Tools" — click **Install** and wait.

---

## Step 4: Get Your OpenAI API Key

You need an API key to use the AI models. Think of it as a password that lets the app talk to OpenAI.

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click **"Create new secret key"**
4. Give it a name like "AI Agent Demo"
5. **Copy the key immediately** — you won't be able to see it again!
6. Paste it somewhere safe (like a Notes app) for now

> **Note:** OpenAI charges a small amount per API call. For this demo, it costs only a few cents per question.

---

## Step 5: Download the Project from GitHub

1. Open Terminal (`Cmd + Space` → type "Terminal" → Enter)
2. Navigate to where you want to save the project. For example, your Desktop:
   ```
   cd ~/Desktop
   ```
3. Download (clone) the project:
   ```
   git clone https://github.com/NisargKadam/introduction_to_aiagent.git
   ```
4. Go into the project folder:
   ```
   cd introduction_to_aiagent
   ```

---

## Step 6: Open the Project in VS Code

While still in Terminal (inside the project folder), type:
```
code .
```
This opens the entire project in VS Code.

---

## Step 7: Set Up the Project

### Option A: Use the Setup Script (Easiest)

1. In VS Code, press `` Ctrl + ` `` (backtick key, next to the 1 key) to open the built-in terminal
2. Type:
   ```
   bash setup.sh
   ```
3. The script will:
   - Create a virtual environment
   - Install all required packages
   - Create a `.env` file for you

### Option B: Manual Setup (If the script doesn't work)

1. Open the terminal in VS Code (`` Ctrl + ` ``)
2. Create a virtual environment:
   ```
   python3 -m venv .venv
   ```
3. Activate it:
   ```
   source .venv/bin/activate
   ```
   You should see `(.venv)` appear at the start of your command line.
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create your config file:
   ```
   cp .env.example .env
   ```

---

## Step 8: Add Your API Key

1. In VS Code, look at the left sidebar (file explorer)
2. Click on the file called **`.env`**
   - If you don't see it, click the gear icon in the file explorer and enable "Show Hidden Files"
3. Find the line that says:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Replace `sk-your-key-here` with the API key you copied in Step 4
5. Save the file (`Cmd + S`)

---

## Step 9: Run the App!

1. Make sure your virtual environment is active (you see `(.venv)` in the terminal)
   - If not, type: `source .venv/bin/activate`
2. Start the server:
   ```
   python app.py
   ```
3. You should see:
   ```
   === Introduction to AI Agents ===
   Pattern: Sequential (ReAct)
   Model: gpt-4o-mini
   Open http://localhost:8000 in your browser
   ```
4. Open your browser and go to: **http://localhost:8000**
5. That's it! You're running the AI Agent Demo!

---

## How to Use the App

1. **Choose a Pattern** — Use the dropdown at the top to switch between:
   - Sequential (ReAct) — step-by-step reasoning
   - Branching (Router) — routes to a specialist
   - Parallel (Fan-out/Fan-in) — 3 analysts run at once
   - Loop (Reflexion) — draft, critique, revise

2. **Choose a Model** — Pick from different OpenAI models

3. **Ask a Question** — Type in the input box or click an example question

4. **Watch the Graph** — Nodes light up in real-time as the AI processes your question

---

## How to Stop the App

- Go back to the terminal in VS Code
- Press `Ctrl + C` to stop the server

## How to Start Again Later

1. Open the project folder in VS Code
2. Open the terminal (`` Ctrl + ` ``)
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Run the server:
   ```
   python app.py
   ```
5. Open http://localhost:8000 in your browser

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python3: command not found` | Reinstall Python from python.org |
| `git: command not found` | Run `xcode-select --install` in Terminal |
| `ModuleNotFoundError` | Make sure you activated the venv: `source .venv/bin/activate` |
| `openai.AuthenticationError` | Check your API key in the `.env` file |
| Page won't load in browser | Make sure the server is running (you see "Uvicorn running" in terminal) |
| `pip` errors during install | Try: `python3 -m pip install --upgrade pip` then retry |
| `permission denied` on setup.sh | Run: `chmod +x setup.sh` then retry |
| Can't see `.env` file in VS Code | It's hidden by default — use `Cmd + Shift + .` in Finder, or open it from terminal: `code .env` |

---

*Need help? Reach out to Nisarg Kadam on [LinkedIn](https://www.linkedin.com/in/nisargkadam/)*
