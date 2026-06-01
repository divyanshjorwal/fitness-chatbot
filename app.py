from flask import Flask, request, jsonify, render_template_string
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "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"))

system_prompt = """You are a fitness assistant. Format every response like this:
- Use clear section headings in CAPS (e.g. UPPER BODY, LOWER BODY)
- Use bullet points with a dash for each exercise
- Add a blank line between each section
- Keep each point concise: Exercise name — what it works — sets x reps
- Never use ** or any markdown symbols
- End with a short TIP section"""

messages = [
    {"role": "system", "content": system_prompt}
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aria — Your AI Assistant</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #f4f3f0;
    --surface: rgba(255,255,255,0.72);
    --text: #1a1916;
    --muted: #7a7872;
    --border: rgba(0,0,0,0.08);
    --blob1: #5b6af5;
    --blob2: #c97ef5;
    --blob3: #f5a87e;
    --user-bubble: #1a1916;
    --ai-bubble: rgba(255,255,255,0.85);
  }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  .blobs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
  .blob { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.45; animation: drift 18s ease-in-out infinite; }
  .blob-1 { width: 480px; height: 480px; background: var(--blob1); top: -120px; right: -80px; animation-delay: 0s; }
  .blob-2 { width: 360px; height: 360px; background: var(--blob2); top: 60px; right: 120px; animation-delay: -6s; }
  .blob-3 { width: 300px; height: 300px; background: var(--blob3); top: -60px; right: 280px; animation-delay: -12s; }
  @keyframes drift {
    0%, 100% { transform: translate(0,0) scale(1); }
    33% { transform: translate(-20px,30px) scale(1.05); }
    66% { transform: translate(15px,-20px) scale(0.95); }
  }
  nav {
    position: relative; z-index: 10;
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 36px;
    border-bottom: 1px solid var(--border);
    background: rgba(244,243,240,0.6);
    backdrop-filter: blur(12px);
  }
  .nav-logo {
    font-family: 'DM Serif Display', serif; font-size: 20px;
    letter-spacing: -0.3px; color: var(--text);
    display: flex; align-items: center; gap: 8px;
  }
  .logo-dot {
    width: 8px; height: 8px; background: var(--blob1);
    border-radius: 50%; animation: pulse 2.5s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }
  .nav-links { display: flex; gap: 28px; list-style: none; font-size: 14px; color: var(--muted); }
  .nav-links a { text-decoration: none; color: inherit; transition: color 0.2s; }
  .nav-links a:hover { color: var(--text); }
  .nav-btn {
    background: var(--text); color: #f4f3f0; border: none;
    padding: 8px 20px; border-radius: 100px;
    font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 500;
    cursor: pointer; transition: opacity 0.2s;
  }
  .nav-btn:hover { opacity: 0.8; }
  .main {
    position: relative; z-index: 5; flex: 1;
    display: flex; flex-direction: column;
    max-width: 780px; width: 100%; margin: 0 auto;
    padding: 0 20px; overflow: hidden;
  }
  .welcome {
    flex: 1; display: flex; flex-direction: column;
    justify-content: flex-end; padding-bottom: 20px; transition: opacity 0.5s;
  }
  .welcome-text {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(36px, 5vw, 54px);
    line-height: 1.1; letter-spacing: -1px;
    color: var(--text); margin-bottom: 14px;
  }
  .welcome-sub {
    font-size: 15px; color: var(--muted); font-weight: 300;
    margin-bottom: 28px; max-width: 460px; line-height: 1.6;
  }
  .welcome-chips { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
  .chip {
    background: var(--ai-bubble); border: 1px solid var(--border);
    border-radius: 100px; padding: 9px 18px; font-size: 13px;
    color: var(--muted); cursor: pointer; transition: all 0.2s;
    backdrop-filter: blur(8px); font-family: 'DM Sans', sans-serif;
  }
  .chip:hover { background: rgba(255,255,255,0.95); color: var(--text); border-color: rgba(0,0,0,0.15); transform: translateY(-1px); }
  #chat-messages {
    flex: 1; overflow-y: auto; padding: 20px 0 16px;
    display: none; flex-direction: column; gap: 16px;
    scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.1) transparent;
  }
  #chat-messages.visible { display: flex; }
  .msg { display: flex; gap: 10px; animation: msgIn 0.3s cubic-bezier(0.22,1,0.36,1); }
  @keyframes msgIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .msg.user { flex-direction: row-reverse; }
  .msg-avatar {
    width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 500; margin-top: 4px;
  }
  .msg.user .msg-avatar { background: var(--text); color: #f4f3f0; }
  .msg.ai .msg-avatar { background: linear-gradient(135deg, var(--blob1), var(--blob2)); color: white; font-size: 12px; }
  .msg-bubble {
    white-space: pre-wrap;
    max-width: 72%; padding: 12px 16px; border-radius: 18px;
    font-size: 14.5px; line-height: 1.65; backdrop-filter: blur(8px);
  }
  .msg.user .msg-bubble { background: var(--user-bubble); color: #f4f3f0; border-bottom-right-radius: 4px; }
  .msg.ai .msg-bubble { background: var(--ai-bubble); color: var(--text); border: 1px solid var(--border); border-bottom-left-radius: 4px; }
  .typing-indicator { display: flex; align-items: center; gap: 10px; animation: msgIn 0.3s cubic-bezier(0.22,1,0.36,1); }
  .typing-dots {
    background: var(--ai-bubble); border: 1px solid var(--border);
    border-radius: 18px; border-bottom-left-radius: 4px;
    padding: 14px 18px; display: flex; gap: 5px; align-items: center;
  }
  .dot { width: 6px; height: 6px; background: var(--muted); border-radius: 50%; animation: bounce 1.2s ease-in-out infinite; }
  .dot:nth-child(2) { animation-delay: 0.15s; }
  .dot:nth-child(3) { animation-delay: 0.3s; }
  @keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-5px); opacity: 1; }
  }
  .input-bar { padding: 16px 0 24px; }
  .input-wrap {
    display: flex; align-items: flex-end; gap: 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 24px; padding: 10px 10px 10px 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .input-wrap:focus-within { border-color: rgba(0,0,0,0.18); box-shadow: 0 4px 28px rgba(0,0,0,0.1); }
  #user-input {
    flex: 1; border: none; background: transparent;
    font-family: 'DM Sans', sans-serif; font-size: 14.5px; color: var(--text);
    resize: none; outline: none; min-height: 24px; max-height: 140px;
    line-height: 1.6; padding: 2px 0;
  }
  #user-input::placeholder { color: var(--muted); }
  #send-btn {
    width: 38px; height: 38px; border-radius: 50%;
    background: var(--text); border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: all 0.2s;
  }
  #send-btn:hover { transform: scale(1.05); opacity: 0.85; }
  #send-btn:active { transform: scale(0.95); }
  #send-btn svg { width: 16px; height: 16px; stroke: #f4f3f0; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .input-hint { text-align: center; font-size: 11.5px; color: var(--muted); margin-top: 10px; }
</style>
</head>
<body>

<div class="blobs">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>
</div>

<nav>
  <div class="nav-logo"><div class="logo-dot"></div>Aria</div>
  <ul class="nav-links">
    <li><a href="#">Capabilities</a></li>
    <li><a href="#">About</a></li>
  </ul>
  <button class="nav-btn" id="new-chat-btn">New chat</button>
</nav>

<div class="main">
  <div class="welcome" id="welcome">
    <div class="welcome-text">Ask me<br><em>anything.</em></div>
    <p class="welcome-sub">Your fitness AI assistant, ready to help with workouts, nutrition, and more.</p>
    <div class="welcome-chips">
      <button class="chip" onclick="fillInput('Best exercises to build muscle at home')">Home workouts</button>
      <button class="chip" onclick="fillInput('How much protein do I need per day?')">Protein intake</button>
      <button class="chip" onclick="fillInput('How to lose belly fat effectively?')">Lose belly fat</button>
      <button class="chip" onclick="fillInput('Create a 5 day workout plan for me')">Workout plan</button>
    </div>
  </div>

  <div id="chat-messages"></div>

  <div class="input-bar">
    <div class="input-wrap">
      <textarea id="user-input" placeholder="Ask anything about fitness…" rows="1"></textarea>
      <button id="send-btn" aria-label="Send">
        <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </div>
    <p class="input-hint">Press Enter to send · Shift+Enter for new line</p>
  </div>
</div>

<script>
  const input = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const messagesEl = document.getElementById('chat-messages');
  const welcome = document.getElementById('welcome');
  let chatStarted = false;

  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 140) + 'px';
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
  sendBtn.addEventListener('click', sendMessage);

  function fillInput(text) {
    input.value = text;
    input.focus();
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 140) + 'px';
  }

  function startChat() {
    if (!chatStarted) {
      welcome.style.opacity = '0';
      setTimeout(() => { welcome.style.display = 'none'; }, 300);
      messagesEl.classList.add('visible');
      chatStarted = true;
    }
  }

  function appendMsg(role, text) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = role === 'user' ? 'You' : 'AI';
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = text;
    div.appendChild(avatar);
    div.appendChild(bubble);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typing';
    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.style.cssText = 'background:linear-gradient(135deg,#5b6af5,#c97ef5);color:white;';
    avatar.textContent = 'AI';
    const dots = document.createElement('div');
    dots.className = 'typing-dots';
    dots.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    div.appendChild(avatar);
    div.appendChild(dots);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById('typing');
    if (t) t.remove();
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    startChat();
    input.value = '';
    input.style.height = 'auto';
    appendMsg('user', text);
    showTyping();
    sendBtn.disabled = true;
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      removeTyping();
      appendMsg('ai', data.response || 'Sorry, no response received.');
    } catch (err) {
      removeTyping();
      appendMsg('ai', 'Connection error. Make sure the server is running.');
    }
    sendBtn.disabled = false;
    input.focus();
  }

  document.getElementById('new-chat-btn').addEventListener('click', () => {
    messagesEl.innerHTML = '';
    messagesEl.classList.remove('visible');
    welcome.style.display = 'flex';
    welcome.style.opacity = '1';
    chatStarted = false;
    fetch('/reset', { method: 'POST' });
  });
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    messages.append({"role": "user", "content": user_message})
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    reply = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return jsonify({"response": reply})


@app.route("/reset", methods=["POST"])
def reset():
    global messages
    messages = [{"role": "system", "content": system_prompt}]
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
