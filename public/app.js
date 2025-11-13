async function loadProvider() {
  try {
    const res = await fetch('/health');
    const data = await res.json();
    document.getElementById('provider').textContent = `Provider: ${data.provider}`;
  } catch (e) {
    document.getElementById('provider').textContent = 'Provider: unavailable';
  }
}

function showResult(data) {
  const r = document.getElementById('result');
  const sentiment = data.sentiment ? `${data.sentiment.label} (${data.sentiment.score})` : 'n/a';
  const keyphrases = data.keyphrases ? data.keyphrases.join(', ') : 'n/a';
  const summary = data.summary || 'n/a';
  const meta = `provider=${data.meta.provider} elapsed=${data.meta.elapsed_ms}ms`;
  r.textContent = `Sentiment: ${sentiment}\nKeyphrases: ${keyphrases}\nSummary: ${summary}\nMeta: ${meta}`;
}

async function analyze() {
  const text = document.getElementById('text').value;
  const payload = {
    text,
    options: {
      sentiment: document.getElementById('opt-sent').checked,
      keyphrases: document.getElementById('opt-key').checked,
      summary: document.getElementById('opt-sum').checked,
    },
  };
  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      document.getElementById('result').textContent = `Error: ${res.status} ${JSON.stringify(err)}`;
      return;
    }
    const data = await res.json();
    showResult(data);
  } catch (e) {
    document.getElementById('result').textContent = 'Network error';
  }
}

document.getElementById('analyze').addEventListener('click', analyze);
loadProvider();