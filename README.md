# 🧠 Local Mind

<div align="center">
  <img src="https://img.shields.io/badge/Frontend-Next.js-000?logo=nextdotjs&logoColor=white&style=flat-square">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&style=flat-square">
  <img src="https://img.shields.io/badge/RAG-LlamaIndex-blueviolet?style=flat-square">
  <img src="https://img.shields.io/badge/LLM-Jan--nano-brightgreen?style=flat-square">
  <img src="https://img.shields.io/badge/WebSearch-Tavily-blue?style=flat-square">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square">
</div>

---

## 🧑‍💻 Requirements

- **Tavily Search API Key:**  
  Local Mind uses [Tavily Search](https://app.tavily.com/home) to fetch live web results for its research agent.  
  - **Get your free Tavily API key here:** [https://app.tavily.com/home](https://app.tavily.com/home)
  - Add your key to your `.env` file as:
    ```
    TAVILY_API_KEY=your-key-here
    ```
  - This is required for web research to function!

- **Local LLM Model:**  
  Local Mind runs a quantized [Jan-nano](https://huggingface.co/Menlo/Jan-nano) model on your machine, so all your data stays private.

  - **What is Jan-nano?**  
    Jan-nano is a highly efficient, open-source LLM by [Menlo](https://huggingface.co/Menlo/Jan-nano), specifically designed for running on local CPUs and resource-limited hardware, making it perfect for private, local AI.
    - Trained on high-quality English datasets.
    - Optimized for speed and context length.
    - Well-suited for chat, question answering, and code.

  - **Quantized Model Downloads:**  
    Local Mind supports quantized GGUF versions for best performance on your system.
    - Choose a quantized file (`*.gguf`) from [this list](https://huggingface.co/Menlo/Jan-nano-gguf/tree/main).
    - Download the version that matches your hardware and put it in your `server/model/` or the main server directory.

    | Model Variant | RAM Required | File Size | Download Link |
    |--------------|-------------|-----------|--------------|
    | Q4, Q5, Q6   | Varies      | ~1-2GB    | [Choose here](https://huggingface.co/Menlo/Jan-nano-gguf/tree/main) |

---

## 🚀 Quick Start

> **You need both a Tavily API key and a quantized Jan-nano GGUF model file!**

1. **Get your [Tavily API Key](https://app.tavily.com/home)**  
   and add it to `server/.env`:
```

TAVILY\_API\_KEY=your-key-here

```

2. **Download a quantized Jan-nano model:**  
[Pick from Jan-nano GGUF releases](https://huggingface.co/Menlo/Jan-nano-gguf/tree/main)  
and put your chosen `.gguf` file in `server/model/`.

3. **Follow previous setup for server and client...**

---

## 🧠 About Jan-nano

- **Jan-nano** is a state-of-the-art, efficient LLM built for privacy, low resource usage, and versatility.
- [Model card & benchmarks](https://huggingface.co/Menlo/Jan-nano)
- [Quantized downloads & sizes](https://huggingface.co/Menlo/Jan-nano-gguf/tree/main)
- Pick Q4 for low RAM, Q5/Q6 for best quality if you have more resources.

---

## 🕸️ About Tavily Search

- Tavily is a fast, privacy-friendly web search API for AI research agents.
- Get your API key at [https://app.tavily.com/home](https://app.tavily.com/home).
- Enables Local Mind to find and cite up-to-date answers beyond your files.

---

*See the rest of the README above for setup, API, and use cases!*


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
