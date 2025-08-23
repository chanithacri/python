# chatbot_app.py
"""
Advanced AI Chatbot — corrected & web UI (Enter sends)

Features:
- Flask web UI (Enter key sends message)
- TF-IDF retrieval + intent classifier (sklearn)
- SQLite persistence with WAL journal mode
- Optional PyTorch autoencoder for semantic embeddings (if torch installed)
- Resilient NLTK preprocessing (falls back if corpora missing)
- Safety checks (profanity, PII basic)
- Robust logging and defensive try/excepts

Run:
1) Install dependencies:
   pip install flask numpy scikit-learn nltk
   Optional (for encoder): pip install torch

2) NLTK one-time downloads (recommended):
   python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('stopwords')"

3) Run:
   python chatbot_app.py

4) Open: http://127.0.0.1:5000
"""
import os
import re
import sqlite3
import json
import time
import logging
import random
import tempfile
from typing import List, Dict, Any, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Optional PyTorch encoder
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from flask import Flask, request, jsonify, render_template_string

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("chatbot")

# ---------------------------
# Config paths
# ---------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "chatbot_data.sqlite3")
MODEL_DIR = os.path.join(BASE_DIR, "model_store")
KB_FOLDER = os.path.join(BASE_DIR, "kb_docs")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(KB_FOLDER, exist_ok=True)

# ---------------------------
# Safety filters (simple)
# ---------------------------
PROFANITY = {"damn", "shit", "fuck"}
PII_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}")
PII_PHONE_RE = re.compile(r"(?:\+?\d{1,3})?[\s\-\.\(]?(?:\d{2,4})[\s\-\.\)]?\d{3,4}[\s\-\.\)]?\d{3,4}")

def safety_check(text: str) -> Dict[str, Any]:
    reasons = []
    low = text.lower()
    toks = set(re.findall(r"\w+", low))
    if PROFANITY.intersection(toks):
        reasons.append("profanity")
    if PII_EMAIL_RE.search(text) or PII_PHONE_RE.search(text):
        reasons.append("pii")
    if len(text) > 5000:
        reasons.append("too_long")
    if any(ord(c) < 9 for c in text):
        reasons.append("bad_chars")
    return {"ok": len(reasons) == 0, "reasons": reasons}

# ---------------------------
# Resilient NLTK initialization
# ---------------------------
_NLTK_IMPORTED = True
try:
    _ = stopwords.words('english')
except Exception:
    try:
        nltk.download('stopwords')
        _ = stopwords.words('english')
    except Exception:
        logger.warning("NLTK stopwords not available; continuing without stopwords.")
        _NLTK_IMPORTED = False

LEMMATIZER = None
if _NLTK_IMPORTED:
    try:
        LEMMATIZER = WordNetLemmatizer()
        # ensure punkt
        try:
            _ = nltk.word_tokenize("test")
        except Exception:
            nltk.download('punkt')
    except Exception:
        logger.warning("NLTK lemmatizer/tokenizer not fully available; falling back to simple tokenization.")
        _NLTK_IMPORTED = False
else:
    logger.info("NLTK not usable; falling back to regex tokenization and no lemmatization.")

STOP_WORDS = set()
if _NLTK_IMPORTED:
    try:
        STOP_WORDS = set(stopwords.words('english'))
    except Exception:
        STOP_WORDS = set()

def _tokenize(text: str) -> List[str]:
    if _NLTK_IMPORTED:
        try:
            return nltk.word_tokenize(text)
        except Exception:
            pass
    return re.findall(r"\w+", text)

def preprocess_text(text: str) -> str:
    if not text:
        return ""
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    try:
        toks = _tokenize(s)
    except Exception:
        toks = re.findall(r"\w+", s)
    if STOP_WORDS:
        toks = [t for t in toks if t not in STOP_WORDS]
    if LEMMATIZER is not None:
        try:
            toks = [LEMMATIZER.lemmatize(t) for t in toks]
        except Exception:
            logger.debug("Lemmatization failed; continuing without it.")
    return " ".join(toks)

# ---------------------------
# SQLite storage (with WAL)
# ---------------------------
class Storage:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        # ensure directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        # enable WAL and reasonable synchronous setting for better concurrency
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            logger.info("SQLite PRAGMA set: WAL + NORMAL synchronous")
        except Exception:
            logger.exception("Failed to set SQLite PRAGMA; continuing.")
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS kb_docs (
                id TEXT PRIMARY KEY,
                title TEXT,
                text TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                text TEXT,
                ts REAL
            )
        """)
        self.conn.commit()

    def add_kb_doc(self, doc_id: str, title: str, text: str):
        try:
            self.conn.execute("REPLACE INTO kb_docs (id, title, text) VALUES (?,?,?)", (doc_id, title, text))
            self.conn.commit()
        except Exception:
            logger.exception("add_kb_doc failed")

    def list_kb(self) -> List[Dict[str,str]]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, title FROM kb_docs")
        return [{"id": r[0], "title": r[1]} for r in cur.fetchall()]

    def get_all_kb_texts(self) -> List[Dict[str,str]]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, title, text FROM kb_docs")
        return [{"id": r[0], "title": r[1], "text": r[2]} for r in cur.fetchall()]

    def push_history(self, user_id: str, role: str, text: str):
        try:
            self.conn.execute("INSERT INTO history (user_id, role, text, ts) VALUES (?,?,?,?)",
                              (user_id, role, text, time.time()))
            self.conn.commit()
        except Exception:
            logger.exception("push_history failed")

    def get_history(self, user_id: str, limit: int = 20) -> List[Dict[str,Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT role, text, ts FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        return [{"role": r[0], "text": r[1], "ts": r[2]} for r in reversed(rows)]

storage = Storage()

# ---------------------------
# Retriever (TF-IDF) + optional Encoder
# ---------------------------
class Retriever:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.kb_matrix = None
        self.kb_docs = []
        self.encoder = None
        self.embeddings = None
        # build from storage initially
        self.build_from_storage()

    def build_from_storage(self):
        docs = storage.get_all_kb_texts()
        if not docs:
            self.kb_docs = []
            self.kb_matrix = None
            self.vectorizer = None
            return
        self.kb_docs = docs
        texts = [preprocess_text(d["text"]) for d in docs]
        try:
            self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
            self.kb_matrix = self.vectorizer.fit_transform(texts)
            logger.info(f"Built TF-IDF KB with {len(docs)} docs")
        except Exception:
            logger.exception("Failed building TF-IDF vectorizer")
            self.vectorizer = None
            self.kb_matrix = None

    def tfidf_retrieve(self, query: str, top_k: int = 3):
        if self.vectorizer is None or self.kb_matrix is None:
            return []
        q = preprocess_text(query)
        try:
            qv = self.vectorizer.transform([q])
            sims = (self.kb_matrix @ qv.T).toarray().ravel()
            idxs = np.argsort(-sims)[:top_k]
            res = []
            for i in idxs:
                res.append({
                    "id": self.kb_docs[i]["id"],
                    "title": self.kb_docs[i]["title"],
                    "text": self.kb_docs[i]["text"],
                    "score": float(sims[i])
                })
            return res
        except Exception:
            logger.exception("TF-IDF retrieval failed")
            return []

    # PyTorch autoencoder (dense embeddings)
    def init_encoder(self, input_dim: int, hidden_dim: int = 256, latent_dim: int = 128, device: str = "cpu"):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not installed")
        class Autoencoder(nn.Module):
            def __init__(self, input_dim, hidden_dim, latent_dim):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, latent_dim)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(latent_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, input_dim)
                    # NOTE: no final Sigmoid (we use raw MSE recon loss on float vectors)
                )
            def forward(self, x):
                z = self.encoder(x)
                xrec = self.decoder(z)
                return xrec

        self.encoder = Autoencoder(input_dim, hidden_dim, latent_dim)
        # device handling
        self.device = torch.device(device if torch.cuda.is_available() and device != "cpu" else "cpu")
        self.encoder.to(self.device)
        logger.info(f"Initialized encoder on device {self.device}")

    def train_encoder(self, epochs: int = 50, batch_size: int = 16, lr: float = 1e-3):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not installed")
        if self.kb_matrix is None:
            raise RuntimeError("TF-IDF KB not built")
        X = self.kb_matrix.toarray().astype(np.float32)
        input_dim = X.shape[1]
        if self.encoder is None:
            self.init_encoder(input_dim)
        ae = self.encoder
        opt = torch.optim.Adam(ae.parameters(), lr=lr)
        loss_fn = nn.MSELoss()
        ae.train()
        dataset = torch.utils.data.TensorDataset(torch.from_numpy(X))
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        for ep in range(epochs):
            total = 0.0
            count = 0
            for batch in loader:
                xb = batch[0].to(self.device).float()
                opt.zero_grad()
                xb_rec = ae(xb)
                loss = loss_fn(xb_rec, xb)
                loss.backward()
                opt.step()
                total += float(loss.item()) * xb.size(0)
                count += xb.size(0)
            avg = total / (count if count else 1)
            if ep % 10 == 0 or ep == epochs-1:
                logger.info(f"Encoder training epoch {ep}/{epochs} loss={avg:.6f}")
        # build embeddings in batches to conserve memory
        ae.eval()
        embeddings = []
        batch_size_emb = 128
        X_t = torch.from_numpy(X).to(self.device).float()
        with torch.no_grad():
            for i in range(0, X_t.size(0), batch_size_emb):
                chunk = X_t[i:i+batch_size_emb]
                z = ae.encoder(chunk)
                embeddings.append(z.cpu().numpy())
        self.embeddings = np.vstack(embeddings)
        logger.info("Trained encoder and built embeddings")

    def emb_retrieve(self, query: str, top_k: int = 3):
        if self.embeddings is None or self.vectorizer is None:
            return []
        q = preprocess_text(query)
        try:
            qv = self.vectorizer.transform([q]).toarray().astype(np.float32)
            # use encoder to get embedding (on same device as encoder)
            if not TORCH_AVAILABLE or self.encoder is None:
                return []
            with torch.no_grad():
                q_tensor = torch.from_numpy(qv).to(self.device).float()
                zq = self.encoder.encoder(q_tensor).cpu().numpy()
            sims = (self.embeddings @ zq.T).ravel()
            idxs = np.argsort(-sims)[:top_k]
            res = []
            for i in idxs:
                res.append({
                    "id": self.kb_docs[i]["id"],
                    "title": self.kb_docs[i]["title"],
                    "text": self.kb_docs[i]["text"],
                    "score": float(sims[i])
                })
            return res
        except Exception:
            logger.exception("Embedding retrieval failed")
            return []

retriever = Retriever()

# ---------------------------
# Intent model (TF-IDF + LogisticRegression)
# ---------------------------
INTENTS = {
    "greeting": {"examples": ["hello", "hi", "hey"], "responses": ["Hello!", "Hey there!"]},
    "goodbye": {"examples": ["bye", "goodbye"], "responses": ["Goodbye!", "See you!"]},
    "thanks": {"examples": ["thanks", "thank you"], "responses": ["You're welcome!", "Anytime"]},
    "kb_query": {"examples": ["what is tfidf", "explain tf-idf", "tell me about tokenization"], "responses": ["I'll look that up in KB."]},
}

class IntentModel:
    def __init__(self):
        self.pipe: Optional[Pipeline] = None

    def train(self, intents: Dict[str, Dict[str, Any]]):
        X = []
        y = []
        for intent, payload in intents.items():
            for ex in payload.get("examples", []):
                X.append(preprocess_text(ex))
                y.append(intent)
        if not X:
            logger.warning("No intent training data")
            return
        try:
            pipe = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
                ("clf", LogisticRegression(max_iter=300))
            ])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            pipe.fit(X_train, y_train)
            acc = pipe.score(X_test, y_test) if X_test else 1.0
            logger.info(f"Trained intent classifier (acc ~ {acc:.2f})")
            self.pipe = pipe
        except Exception:
            logger.exception("Intent training failed")
            self.pipe = None

    def predict(self, text: str) -> Dict[str, Any]:
        if self.pipe is None:
            return {"intent": "unknown", "confidence": 0.0}
        x = preprocess_text(text)
        try:
            probs = self.pipe.predict_proba([x])[0]
            classes = self.pipe.named_steps["clf"].classes_
            idx = int(np.argmax(probs))
            return {"intent": classes[idx], "confidence": float(probs[idx])}
        except Exception:
            logger.exception("Intent prediction failed")
            return {"intent": "unknown", "confidence": 0.0}

intent_model = IntentModel()
intent_model.train(INTENTS)

# ---------------------------
# Bot logic
# ---------------------------
class Bot:
    def __init__(self):
        self.retriever = retriever
        self.intent = intent_model

    def add_kb_file(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            doc_id = os.path.basename(filepath)
            title = os.path.splitext(doc_id)[0]
            storage.add_kb_doc(doc_id, title, text)
            self.retriever.build_from_storage()
            logger.info(f"Added KB file {doc_id}")
            return True
        except Exception:
            logger.exception("add_kb_file failed")
            return False

    def handle(self, user_id: str, message: str) -> str:
        s = safety_check(message)
        if not s["ok"]:
            logger.info(f"Message blocked for user={user_id} reasons={s['reasons']}")
            return f"I can't process that message (reasons: {', '.join(s['reasons'])})."
        storage.push_history(user_id, "user", message)
        intent = self.intent.predict(message)
        logger.info(f"Predicted intent for user={user_id}: {intent}")
        try:
            if intent["intent"] == "kb_query" or intent["confidence"] < 0.6:
                # prefer embeddings if available
                if retriever.embeddings is not None:
                    hits = retriever.emb_retrieve(message, top_k=3)
                else:
                    hits = retriever.tfidf_retrieve(message, top_k=3)
                if hits:
                    top = hits[0]
                    reply = f"Found in KB: {top['title']} (score {top['score']:.2f})\n{top['text'][:600]}"
                    storage.push_history(user_id, "bot", reply)
                    return reply
            # template responses
            name_match = re.search(r"remember (?:that )?(?:my )?name is ([A-Za-z0-9_ -]{1,60})", message, re.I)
            if name_match:
                name = name_match.group(1).strip()
                # store name in users table (simple)
                try:
                    storage.conn.execute("REPLACE INTO users (user_id, data) VALUES (?, ?)",
                                         (user_id, json.dumps({"name": name})))
                    storage.conn.commit()
                except Exception:
                    logger.exception("storing user name failed")
                resp = f"Got it — I'll remember your name is {name}."
                storage.push_history(user_id, "bot", resp)
                return resp
            intent_name = intent["intent"]
            if intent_name in INTENTS and intent["confidence"] >= 0.6:
                resp = random.choice(INTENTS[intent_name]["responses"])
                storage.push_history(user_id, "bot", resp)
                return resp
            if re.search(r"how are you|how's it going", message, re.I):
                resp = random.choice(["I'm running smooth today.", "Optimized and caffeinated (metaphorically)."])
                storage.push_history(user_id, "bot", resp)
                return resp
        except Exception:
            logger.exception("Error in bot logic")
        resp = "Sorry, I don't have a crisp answer. Try rephrasing or add docs to the KB."
        storage.push_history(user_id, "bot", resp)
        return resp

bot = Bot()

# ---------------------------
# Flask app & UI (Enter sends)
# ---------------------------
app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Advanced AI Chatbot</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; }
    #chat { border: 1px solid #ddd; padding: 12px; height: 60vh; overflow-y: auto; background: #fafafa; }
    .msg { margin: 8px 0; }
    .user { text-align: right; }
    .bot { text-align: left; }
    .bubble { display: inline-block; padding: 8px 12px; border-radius: 12px; max-width: 75%; white-space: pre-wrap; }
    .user .bubble { background: #e6f7ff; }
    .bot .bubble { background: #fff; border: 1px solid #eee; }
    #controls { margin-top: 10px; display:flex; gap:8px; }
    input[type=text] { flex: 1; padding: 8px; font-size: 1rem; }
    button { padding: 8px 12px; }
  </style>
</head>
<body>
  <h1>Advanced AI Chatbot</h1>
  <div id="chat"></div>
  <div id="controls">
    <input id="message" type="text" placeholder="Say something and press Enter" autocomplete="off" />
    <button id="sendBtn">Send</button>
  </div>

  <script>
    const userId = 'web_user_1';
    const chat = document.getElementById('chat');
    const input = document.getElementById('message');
    const sendBtn = document.getElementById('sendBtn');

    function addMessage(role, text) {
      const d = document.createElement('div');
      d.className = 'msg ' + role;
      const b = document.createElement('div');
      b.className = 'bubble';
      b.textContent = text;
      d.appendChild(b);
      chat.appendChild(d);
      chat.scrollTop = chat.scrollHeight;
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;
      addMessage('user', text);
      input.value = '';
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ user_id: userId, message: text })
        });
        const j = await res.json();
        if (j.ok) addMessage('bot', j.reply);
        else addMessage('bot', 'Error: ' + (j.error || 'unknown'));
      } catch (e) {
        addMessage('bot', 'Network error');
      }
    }

    // send on button
    sendBtn.addEventListener('click', sendMessage);

    // send on Enter (when input has focus)
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault(); // avoid form submit / newline
        sendMessage();
      }
    });

    // welcome
    addMessage('bot', 'Hi — try asking about TF-IDF or upload .txt files to kb_docs/ and ask about them.');
    input.focus();
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    user_id = data.get("user_id", "web_user_1")
    msg = data.get("message", "")
    try:
        reply = bot.handle(user_id, msg)
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        logger.exception("chat API error")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "no file"}), 400
    f = request.files["file"]
    if not f.filename.lower().endswith(".txt"):
        return jsonify({"ok": False, "error": "only .txt allowed"}), 400
    path = os.path.join(KB_FOLDER, f.filename)
    f.save(path)
    ok = bot.add_kb_file(path)
    return jsonify({"ok": ok})

@app.route("/api/admin/list_kb", methods=["GET"])
def api_list_kb():
    docs = storage.list_kb()
    return jsonify({"ok": True, "docs": docs})

@app.route("/api/admin/train_encoder", methods=["POST"])
def api_train_encoder():
    if not TORCH_AVAILABLE:
        return jsonify({"ok": False, "error": "PyTorch not installed"}), 400
    try:
        # train with conservative defaults; call asynchronously in prod
        retriever.train_encoder(epochs=30, batch_size=8, lr=1e-3)
        return jsonify({"ok": True})
    except Exception:
        logger.exception("train encoder failed")
        return jsonify({"ok": False, "error": "training failed"}), 500

# ---------------------------
# CLI helper: preload .txt files into DB on startup
# ---------------------------
def preload_kb_folder():
    for fname in os.listdir(KB_FOLDER):
        if fname.lower().endswith(".txt"):
            path = os.path.join(KB_FOLDER, fname)
            try:
                bot.add_kb_file(path)
            except Exception:
                logger.exception("preload add_kb_file failed for %s", fname)

if __name__ == "__main__":
    try:
        preload_kb_folder()
        retriever.build_from_storage()
        logger.info("Starting Flask app (debug disabled). Open http://127.0.0.1:5000")
        # NOTE: debug is False by default for safety; enable only during development intentionally
        app.run(host="127.0.0.1", port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down")
    except Exception:
        logger.exception("Fatal error in main")
