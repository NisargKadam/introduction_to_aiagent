# Setup Guide for Windows Users

**Introduction to AI Agents - Local Setup**
*By Nisarg Kadam | Senior AI Engineer*

This guide will walk you through everything from scratch — even if you've never coded before.

---

## Step 1: Install VS Code (Your Code Editor)

1. Open your browser and go to: https://code.visualstudio.com/
2. Click the big blue **"Download for Windows"** button
3. Once downloaded, double-click the installer file
4. During installation, **check all the boxes** especially:
   - ✅ "Add to PATH"
   - ✅ "Add Open with Code action"
5. Click **Install** and wait for it to finish
6. Click **Finish** — VS Code will open

---

## Step 2: Install Python

1. Open your browser and go to: https://www.python.org/downloads/
2. Click the big yellow **"Download Python 3.x.x"** button
3. Double-click the downloaded installer
4. **IMPORTANT:** On the first screen, check the box that says:
   - ✅ **"Add Python to PATH"** (this is at the bottom — don't miss it!)
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**

### Verify Python is installed:
1. Press `Windows + R` on your keyboard
2. Type `cmd` and press Enter (this opens Command Prompt)
3. Type this and press Enter:
   ```
   python --version
   ```
4. You should see something like `Python 3.11.9` — that means it worked!

---

## Step 3: Install Git

Git is a tool that lets you download code from GitHub.

1. Go to: https://git-scm.com/download/win
2. The download should start automatically
3. Double-click the installer
4. Keep clicking **Next** for all the default options (they're fine)
5. Click **Install**, then **Finish**

### Verify Git is installed:
1. Open Command Prompt again (`Windows + R` → type `cmd` → Enter)
2. Type this and press Enter:
   ```
   git --version
   ```
3. You should see something like `git version 2.x.x`

---

## Step 4: Get Your OpenAI API Key

You need an API key to use the AI models. Think of it as a password that lets the app talk to OpenAI.

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click **"Create new secret key"**
4. Give it a name like "AI Agent Demo"
5. **Copy the key immediately** — you won't be able to see it again!
6. Paste it somewhere safe (like a Notepad file) for now

> **Note:** OpenAI charges a small amount per API call. For this demo, it costs only a few cents per question.

---

## Step 5: Download the Project from GitHub

1. Open Command Prompt (`Windows + R` → type `cmd` → Enter)
2. Navigate to where you want to save the project. For example, your Desktop:
   ```
   cd Desktop
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

While still in Command Prompt (inside the project folder), type:
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
   setup.bat
   ```
3. The script will:
   - Create a virtual environment
   - Install all required packages
   - Create a `.env` file for you

### Option B: Manual Setup (If the script doesn't work)

1. Open the terminal in VS Code (`` Ctrl + ` ``)
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate it:
   ```
   .venv\Scripts\activate
   ```
   You should see `(.venv)` appear at the start of your command line.
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Create your config file:
   ```
   copy .env.example .env
   ```

---

## Step 8: Add Your API Key

1. In VS Code, look at the left sidebar (file explorer)
2. Click on the file called **`.env`**
3. Find the line that says:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
4. Replace `sk-your-key-here` with the API key you copied in Step 4
5. Save the file (`Ctrl + S`)

---

## Step 9: Run the App!

1. Make sure your virtual environment is active (you see `(.venv)` in the terminal)
   - If not, type: `.venv\Scripts\activate`
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
   .venv\Scripts\activate
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
| `python is not recognized` | Reinstall Python and make sure to check "Add to PATH" |
| `git is not recognized` | Reinstall Git and restart your Command Prompt |
| `ModuleNotFoundError` | Make sure you activated the venv: `.venv\Scripts\activate` |
| `openai.AuthenticationError` | Check your API key in the `.env` file |
| Page won't load in browser | Make sure the server is running (you see "Uvicorn running" in terminal) |
| `pip` errors during install | Try: `python -m pip install --upgrade pip` then retry |

---

*Need help? Reach out to Nisarg Kadam on [LinkedIn](https://www.linkedin.com/in/nisargkadam/)*
