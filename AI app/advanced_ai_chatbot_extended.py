"""
Advanced AI Chatbot — Extended Edition

What's new in this file:
- Full Flask web UI (single-file) so you can chat from your browser.
- KB folder loader: load many .txt files from a directory into the knowledge base.
- Admin endpoints to add docs at runtime (JSON POST) and rebuild the KB.
- Multi-turn context tracking: simple per-user conversation history and slot-like memory.
- Same foundation as before: TF-IDF retrieval + intent classifier (TF-IDF + LogisticRegression).

How to run:
1. Create a virtualenv and install requirements:
   pip install flask numpy scikit-learn nltk

2. Download NLTK data (one-time):
   python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('stopwords')"

3. Prepare a KB folder (optional): create a folder `kb_docs/` and drop plain `.txt` files in it. Each file becomes a knowledge doc.

4. Run the app:
   python advanced_ai_chatbot_extended.py

5. Open your browser at http://127.0.0.1:5000

Notes & next steps:
- This demo keeps everything in local files (no external AI APIs). It's a working staging prototype — not production hardened.
- If you'd like, I can add a small neural encoder replacement (PyTorch) next — that'll require a bit more setup but gives better semantic matching.

"""

from flask import Flask, request, jsonify, render_template_string
import os
import re
import pickle
import random
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------------------
# Configuration
# ---------------------------
MODEL_DIR = 'model_store'
KB_FOLDER = 'kb_docs'
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(KB_FOLDER, exist_ok=True)

# ---------------------------
# Minimal demo intents and built-in KB (used if KB folder is empty)
# ---------------------------
INTENTS = {
    "greeting": {
        "examples": ["hello", "hi", "hey", "good morning", "what's up"],
        "responses": ["Hello! How can I help you today?", "Hey — what's on your mind?"]
    },
    "goodbye": {
        "examples": ["bye", "goodbye", "see you"],
        "responses": ["Goodbye! Take care.", "See you later — stay brilliant."]
    },
    "thanks": {
        "examples": ["thanks", "thank you"],
        "responses": ["You're welcome!", "Anytime — happy to help."]
    },
    "kb_query": {
        "examples": ["what is tfidf", "explain tf-idf", "how does your memory work"],
        "responses": ["I'll check my knowledge base for that."]
    },
}

BUILTIN_KB = [
    {"id": "kb_builtin_1", "title": "TF-IDF explanation", "text": "TF-IDF stands for Term Frequency - Inverse Document Frequency. It helps measure how important a word is to a document in a corpus."},
    {"id": "kb_builtin_2", "title": "Tokenization and Lemmatization", "text": "Tokenization splits text into words; lemmatization reduces words to their dictionary base form."},
]

# ---------------------------
# NLTK setup
# ---------------------------
try:
    _ = stopwords.words('english')
except Exception:
    try:
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('stopwords')
    except Exception:
        pass

STOP_WORDS = set(stopwords.words('english')) if 'stopwords' in nltk.corpus.__dict__ else set()
LEMMATIZER = WordNetLemmatizer()

import re

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS]
    tokens = [LEMMATIZER.lemmatize(t) for t in tokens]
    return " ".join(tokens)

# ---------------------------
# Chatbot core with multi-turn context and KB loader
# ---------------------------
class AdvancedChatbot:
    def __init__(self, model_dir: str = MODEL_DIR):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.intent_clf: Optional[Pipeline] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.kb_docs: List[Dict[str, Any]] = []
        self.kb_matrix: Optional[np.ndarray] = None
        self.user_memory_path = os.path.join(self.model_dir, 'user_memory.pkl')
        self.user_memory: Dict[str, Dict[str, Any]] = self._load_memory()
        # load built-in KB by default, then try loading folder
        self.build_kb(BUILTIN_KB)
        self.load_kb_from_folder(KB_FOLDER)
        self.train_intent_classifier(INTENTS)

    # -----------------
    # Memory & context
    # -----------------
    def _load_memory(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.user_memory_path):
            try:
                with open(self.user_memory_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return {}
        return {}

    def _save_memory(self):
        with open(self.user_memory_path, 'wb') as f:
            pickle.dump(self.user_memory, f)

    def remember(self, user_id: str, key: str, value: Any):
        self.user_memory.setdefault(user_id, {})[key] = value
        self._save_memory()

    def recall(self, user_id: str, key: str) -> Optional[Any]:
        return self.user_memory.get(user_id, {}).get(key)

    def push_history(self, user_id: str, role: str, text: str, max_len: int = 8):
        hist = self.user_memory.setdefault(user_id, {}).setdefault('history', [])
        hist.append({'role': role, 'text': text})
        # trim to last max_len entries
        if len(hist) > max_len:
            hist = hist[-max_len:]
        self.user_memory[user_id]['history'] = hist
        self._save_memory()

    def get_history(self, user_id: str) -> List[Dict[str,str]]:
        return self.user_memory.get(user_id, {}).get('history', [])

    # -----------------
    # KB load & retrieval
    # -----------------
    def build_kb(self, docs: List[Dict[str, str]]):
        self.kb_docs = docs
        texts = [preprocess_text(d['text']) for d in docs]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        if texts:
            self.kb_matrix = self.vectorizer.fit_transform(texts)
        else:
            self.kb_matrix = None

    def kb_retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.vectorizer is None or self.kb_matrix is None:
            return []
        q = preprocess_text(query)
        qv = self.vectorizer.transform([q])
        sims = (self.kb_matrix @ qv.T).toarray().ravel()
        idxs = np.argsort(-sims)[:top_k]
        results = []
        for i in idxs:
            score = float(sims[i])
            results.append({
                'id': self.kb_docs[i]['id'],
                'title': self.kb_docs[i]['title'],
                'text': self.kb_docs[i]['text'],
                'score': score,
            })
        return results

    def load_kb_from_folder(self, folder: str):
        # load all .txt files as docs; filename (without ext) becomes id/title
        files = [f for f in os.listdir(folder) if f.lower().endswith('.txt')]
        if not files:
            return
        docs = []
        for fname in files:
            path = os.path.join(folder, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                docs.append({'id': fname, 'title': os.path.splitext(fname)[0], 'text': text})
            except Exception:
                continue
        # merge with existing kb_docs (builtin) by appending and rebuilding
        self.kb_docs.extend(docs)
        texts = [preprocess_text(d['text']) for d in self.kb_docs]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.kb_matrix = self.vectorizer.fit_transform(texts)
        print(f"Loaded {len(docs)} docs from {folder} (total KB docs: {len(self.kb_docs)})")

    # -----------------
    # Intent classifier
    # -----------------
    def train_intent_classifier(self, intents: Dict[str, Dict[str, Any]]):
        X = []
        y = []
        for intent, payload in intents.items():
            for ex in payload.get('examples', []):
                X.append(preprocess_text(ex))
                y.append(intent)
        if not X:
            return
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
            ("clf", LogisticRegression(max_iter=300))
        ])
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pipe.fit(X_train, y_train)
        acc = pipe.score(X_test, y_test) if X_test else 1.0
        print(f"Intent classifier trained (test acc ~ {acc:.2f})")
        self.intent_clf = pipe

    def predict_intent(self, text: str) -> Dict[str, Any]:
        if self.intent_clf is None:
            return {'intent': 'unknown', 'confidence': 0.0}
        x = preprocess_text(text)
        probs = self.intent_clf.predict_proba([x])[0]
        classes = self.intent_clf.named_steps['clf'].classes_
        idx = int(np.argmax(probs))
        return {'intent': classes[idx], 'confidence': float(probs[idx])}

    # -----------------
    # Response pipeline with multi-turn awareness
    # -----------------
    def respond(self, user_input: str, user_id: str = 'default_user') -> str:
        if not user_input.strip():
            return "Say something — even a tiny word counts."
        # store user message
        self.push_history(user_id, 'user', user_input)

        # rule: remember name
        m = re.search(r"remember (?:that )?(?:my )?name is ([A-Za-z0-9_\- ]{1,60})", user_input, re.I)
        if m:
            name = m.group(1).strip()
            self.remember(user_id, 'name', name)
            return f"Got it — I'll remember your name is {name}."

        pred = self.predict_intent(user_input)
        intent = pred.get('intent', 'unknown')
        conf = pred.get('confidence', 0.0)

        # if low confidence => KB retrieval
        if intent == 'kb_query' or conf < 0.6:
            hits = self.kb_retrieve(user_input, top_k=2)
            if hits:
                top = hits[0]
                snippet = top['text']
                if len(snippet) > 500:
                    snippet = snippet[:500] + '...'
                reply = f"I found this in my knowledge base — {top['title']} (score {top['score']:.2f}):\n{snippet}"
                self.push_history(user_id, 'bot', reply)
                return reply

        # check for simple follow-up intents using conversation history
        history = self.get_history(user_id)
        # e.g., if last user asked "tell me about X" and now asks "more details" -> use KB
        if history and re.search(r"more detail|more info|tell me more|expand", user_input, re.I):
            # attempt to find last KB result in history
            for item in reversed(history):
                if item['role'] == 'bot' and 'knowledge base' in item['text'].lower():
                    # re-run retrieval with same query (simple heuristic)
                    q = history[-2]['text'] if len(history) >= 2 else user_input
                    hits = self.kb_retrieve(q, top_k=2)
                    if hits:
                        text = hits[0]['text']
                        self.push_history(user_id, 'bot', text)
                        return text

        # template responses
        if intent in INTENTS and conf >= 0.6:
            resp = random.choice(INTENTS[intent]['responses'])
            name = self.recall(user_id, 'name')
            if name and '{name}' in resp:
                resp = resp.replace('{name}', name)
            self.push_history(user_id, 'bot', resp)
            return resp

        # small-talk heuristic
        if re.search(r"how are you|how's it going", user_input, re.I):
            resp = random.choice(["I'm running smooth today.", "Optimized and metaphorically caffeinated."])
            self.push_history(user_id, 'bot', resp)
            return resp

        # fallback
        resp = "I don't have a crisp answer for that. Try rephrasing or add relevant docs to my KB."
        self.push_history(user_id, 'bot', resp)
        return resp

    # -----------------
    # Admin utilities
    # -----------------
    def add_kb_doc(self, doc: Dict[str, str]):
        # doc must contain id, title, text
        self.kb_docs.append(doc)
        # rebuild vectorizer/matrix
        texts = [preprocess_text(d['text']) for d in self.kb_docs]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.kb_matrix = self.vectorizer.fit_transform(texts)

    def save(self):
        # save intent clf and memory
        if self.intent_clf is not None:
            with open(os.path.join(self.model_dir, 'intent_clf.pkl'), 'wb') as f:
                pickle.dump(self.intent_clf, f)
        with open(self.user_memory_path, 'wb') as f:
            pickle.dump(self.user_memory, f)


# ---------------------------
# Flask app + simple browser UI
# ---------------------------
app = Flask(__name__)
bot = AdvancedChatbot()

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Advanced AI Chatbot — Demo</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; }
    #chat { border: 1px solid #ddd; padding: 12px; height: 60vh; overflow-y: auto; background: #fafafa; }
    .msg { margin: 8px 0; }
    .user { text-align: right; }
    .bot { text-align: left; }
    .bubble { display: inline-block; padding: 8px 12px; border-radius: 12px; max-width: 75%; }
    .user .bubble { background: #e6f7ff; }
    .bot .bubble { background: #fff; border: 1px solid #eee; }
    #controls { margin-top: 10px; display:flex; gap:8px; }
    input[type=text] { flex: 1; padding: 8px; }
    button { padding: 8px 12px; }
  </style>
</head>
<body>
  <h1>Advanced AI Chatbot — Demo</h1>
  <div id="chat"></div>
  <div id="controls">
    <input id="message" type="text" placeholder="Say something" />
    <button onclick="send()">Send</button>
  </div>
  <script>
    const userId = 'web_user_1';
    function addMessage(role, text){
      const chat = document.getElementById('chat');
      const d = document.createElement('div'); d.className = 'msg ' + role;
      const b = document.createElement('div'); b.className = 'bubble'; b.textContent = text;
      d.appendChild(b); chat.appendChild(d); chat.scrollTop = chat.scrollHeight;
    }
    async function send(){
      const inp = document.getElementById('message');
      const text = inp.value.trim(); if(!text) return;
      addMessage('user', text); inp.value = '';
      const res = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({user_id: userId, message: text}) });
      const j = await res.json(); addMessage('bot', j.reply);
    }
    // welcome message
    addMessage('bot', 'Hi — try asking me about TF-IDF or upload .txt docs into the kb_docs/ folder and ask about them.');
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(force=True)
    user_id = data.get('user_id', 'web_user_1')
    msg = data.get('message', '')
    reply = bot.respond(msg, user_id=user_id)
    return jsonify({'reply': reply})

@app.route('/api/admin/add_doc', methods=['POST'])
def api_add_doc():
    # Accept JSON {id, title, text}
    data = request.get_json(force=True)
    if not data or not all(k in data for k in ('id', 'title', 'text')):
        return jsonify({'ok': False, 'error': 'Missing id/title/text'}), 400
    bot.add_kb_doc({'id': data['id'], 'title': data['title'], 'text': data['text']})
    return jsonify({'ok': True, 'msg': 'Doc added'})

@app.route('/api/admin/list_kb', methods=['GET'])
def api_list_kb():
    return jsonify({'docs': [{'id': d['id'], 'title': d['title']} for d in bot.kb_docs]})

@app.route('/api/admin/upload_file', methods=['POST'])
def api_upload_file():
    # Accept file upload (multipart/form-data), save into KB folder and rebuild KB
    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'No file'}), 400
    f = request.files['file']
    filename = f.filename
    if not filename.lower().endswith('.txt'):
        return jsonify({'ok': False, 'error': 'Only .txt allowed'}), 400
    path = os.path.join(KB_FOLDER, filename)
    f.save(path)
    bot.load_kb_from_folder(KB_FOLDER)
    return jsonify({'ok': True, 'msg': f'Saved {filename}'})

@app.route('/admin', methods=['GET'])
def admin_page():
    # Minimal admin UI for listing and adding docs
    docs_html = '<ul>' + ''.join([f"<li>{d['id']} — {d['title']}</li>" for d in bot.kb_docs]) + '</ul>'
    return f"<h2>KB docs</h2>{docs_html}<p>Use POST /api/admin/add_doc to add docs or upload .txt to /api/admin/upload_file</p>"

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        bot.save()
