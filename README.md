# 🐞 AI Bug Assistant

🚀 **Live App:** https://bug-assistant.streamlit.app/

An intelligent AI-powered debugging assistant that analyzes error logs and code snippets to identify bugs, explain root causes, and suggest actionable fixes instantly.

---

## ✨ Features

* 🔍 Analyze error logs and source code
* 🧠 AI-generated root cause explanations
* 🛠 Suggested fixes and improvements
* ⚡ Fast inference using Groq API
* 💻 Local support via Ollama (offline mode)
* 🌐 Fully deployed using Streamlit Cloud
* 📥 Downloadable analysis report

---

## 🏗️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Models:**

  * ☁️ Cloud: `llama-3.3-70b-versatile` (Groq API)
  * 💻 Local: `llama3` (Ollama)
* **APIs:** Groq API
* **Deployment:** Streamlit Cloud
* **Other:** Requests, dotenv

---

## ⚙️ How It Works

1. User inputs:

   * Error logs
   * Code snippet
   * Optional context

2. The system:

   * Cleans and structures input
   * Builds an AI prompt

3. Routing:

   * **Local environment → Ollama**
   * **Cloud deployment → Groq API**

4. Output:

   * Root cause
   * Explanation
   * Suggested fix

---

## 🚀 Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/bug-assistant.git
cd bug-assistant
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

### 4️⃣ Run Application

```bash
streamlit run app.py
```

---

## 🧠 Optional: Local AI (Ollama Mode)

1️⃣ Install Ollama
2️⃣ Run model:

```bash
ollama run llama3
```

3️⃣ Set environment variable:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
```

(Windows PowerShell)

```powershell
setx OLLAMA_BASE_URL "http://localhost:11434"
```

---

## 🔐 Environment Variables

| Variable         | Description           |
| ---------------- | --------------------- |
| GROQ_API_KEY     | Required for cloud AI |
| OLLAMA_BASE_URL  | Optional (local mode) |
| OLLAMA_MODEL     | Optional              |
| OLLAMA_TIMEOUT_S | Optional              |

---

## 🌍 Deployment

Deployed using **Streamlit Cloud**:

1. Push code to GitHub
2. Connect repository on Streamlit
3. Add secrets:

```toml
GROQ_API_KEY="your_api_key"
```

4. Deploy 🚀

---


## 💡 Future Improvements

* 📋 Copy-to-clipboard fixes
* 🧾 Structured output sections (Root Cause / Fix / Code)
* 🧪 Auto test case generation
* 📊 Bug severity detection
* 💬 Chat-based debugging interface
* 🔁 Multi-turn debugging

---

## 🧠 Key Learnings

* Hybrid AI architecture (Local + Cloud)
* API error handling & fallback design
* Deployment constraints (local vs cloud models)
* Secure API key management
* Real-world debugging workflows

---

## 👨‍💻 Author

**Souhardee Sen**

---

## ⭐ Support

If you found this useful:

⭐ Star the repo
🔁 Share with others
🚀 Build on top of it

---

## 📌 Project Status

✅ Fully Functional
✅ Deployed
✅ Production-ready (with hybrid AI support)
