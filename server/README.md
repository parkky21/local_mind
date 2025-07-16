# 🧠 Local Mind

<div align="center">
  <img src="https://img.shields.io/badge/Frontend-Next.js-000?logo=nextdotjs&logoColor=white&style=flat-square">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/RAG-LlamaIndex-blueviolet?style=flat-square">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square">
</div>

---

## 🏗️ Project Structure

```

local-mind/
├── client/       # Next.js React frontend (chat UI, file upload, etc)
├── server/       # FastAPI backend, LLM, RAG, and web search agents
│   ├── app/
│   │   ├── config.py
│   │   ├── utils.py
│   │   ├── rag.py
│   │   ├── research.py
│   │   └── main.py
│   ├── data/           # Your uploaded/managed documents
│   ├── store\_rag/      # Local vector store index
│   └── requirements.txt
├── README.md

````

---

## ✨ What is Local Mind?

**Local Mind** is your own personal, private, full-stack AI workspace.

- **Upload files, chat with your own knowledge base**
- **Research with live web search** (and get real, cited answers)
- **All locally, all private** — powered by FastAPI and Next.js

---

## 🖥️ Client (Next.js)

- **Beautiful chat interface**
- **File upload and management**
- **Live streaming answers from LLM**
- **Web search results shown in real time**

> The client talks to the FastAPI backend via simple HTTP endpoints.

---

## ⚡️ Server (FastAPI, LlamaIndex, LangChain, LLM)

- **Runs your local LLM (Llama.cpp)**
- **Retrieval-Augmented Generation on your uploaded files**
- **Web research agent for up-to-date answers**
- **Automatic file watching and index updating**
- **API endpoints for chat, file management, research**

---

## 🛠️ Use Cases

- **Personal Knowledge Base:** Chat with your notes, manuals, or code docs.
- **Research Copilot:** Get the best web and local insights, cited and summarized.
- **Secure Team Docs:** Host on LAN, share within your org—no data ever leaves.
- **Developer Assistant:** Index your codebase docs, get instant answers.
- **Academic Summaries:** Ask questions to your PDFs or web research.

---

## 🚀 Quick Start

### 1️⃣ Clone the repo

```sh
git clone https://github.com/yourusername/local-mind.git
cd local-mind
````

### 2️⃣ Setup the Server

```sh
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Place your Llama.cpp GGUF model in this folder (e.g. jan-nano-128k-Q5_K_M.gguf)
python -m app.main
# or
uvicorn app.main:app --reload
```

* The server runs at [http://localhost:8000](http://localhost:8000)
* Interactive API: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3️⃣ Setup the Client

```sh
cd ../client
npm install
npm run dev
```

* The client runs at [http://localhost:3000](http://localhost:3000)

---

## 🌐 How it Works

1. **Upload** your files (PDF, TXT, etc) via the web UI.
2. **Chat** with your knowledge base. Get answers instantly.
3. **Ask web questions:** The agent pulls the latest info and cites real URLs.
4. **All private:** Your files and chats never leave your device.

---

## 📖 API Reference

The FastAPI backend exposes endpoints such as:

* `POST /rag/upload/` — Upload documents
* `GET /rag/files/` — List uploaded files
* `DELETE /rag/delete/{filename}` — Delete documents
* `GET /rag/stream` — Chat with your files (RAG)
* `GET /research/stream` — Research agent (web search)
* `GET /health` — Health check

See [http://localhost:8000/docs](http://localhost:8000/docs) for full details.

---

## 💡 Why Local Mind?

* 🛡️ **Privacy First:** 100% local, no data leaves your computer.
* 🧠 **Multi-source AI:** Mixes your files and the web.
* ⚡ **Lightning Fast:** No cloud lag, no rate limits.
* 🧩 **Composable:** Easy to extend or add your own tools.

---

## 📸 Demo

<details>
<summary>Click to expand</summary>

![Local Mind Chat Screenshot](assets/screenshot1.png)

</details>

---

## 🤝 Contributing

Pull requests, issues, and suggestions are always welcome!

* Want to add more LLM models? New RAG features? Better UI? Jump in!

---
