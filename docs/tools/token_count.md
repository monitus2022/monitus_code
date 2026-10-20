# Token Counter

Estimate prompt tokens locally in your browser.

<style>
/* Token Counter - Material for MkDocs Dynamic Styling */
.tc-container {
  background-color: var(--md-code-bg-color);
  border: 1px solid var(--md-default-fg-color--lightest);
  padding: 20px;
  border-radius: 8px;
  margin: 1.5em 0;
}

.tc-textarea {
  width: 100%;
  height: 220px;
  padding: 14px;
  background-color: var(--md-default-bg-color);
  color: var(--md-typeset-color);
  font-family: var(--md-code-font-family, monospace);
  font-size: 0.85em;
  line-height: 1.5;
  border-radius: 6px;
  border: 1px solid var(--md-default-fg-color--lightest);
  outline: none;
  box-sizing: border-box;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.tc-textarea::placeholder {
  color: var(--md-default-fg-color--light);
}

.tc-textarea:focus {
  border-color: var(--md-primary-fg-color);
  box-shadow: 0 0 0 3px var(--md-accent-fg-color--transparent, rgba(233, 30, 99, 0.15));
}

.tc-metrics {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.tc-card {
  background-color: var(--md-default-bg-color);
  border: 1px solid var(--md-default-fg-color--lightest);
  padding: 16px;
  border-radius: 6px;
  flex: 1;
  text-align: center;
}

.tc-number {
  font-size: 1.8em;
  font-weight: 700;
  color: var(--md-primary-fg-color); /* Automatically uses Pink from your mkdocs.yml */
  margin-top: 4px;
}

.tc-label {
  font-size: 0.75em;
  color: var(--md-default-fg-color--light);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
<div class="tc-container">
  <textarea id="inputText" class="tc-textarea" placeholder="Paste your prompt, code, or context here..."></textarea>
  <div class="tc-metrics">
    <div class="tc-card">
      <div class="tc-label">Tokens (o200k)</div>
      <div id="tokenCount" class="tc-number">0</div>
    </div>
    <div class="tc-card">
      <div class="tc-label">Words</div>
      <div id="wordCount" class="tc-number">0</div>
    </div>
    <div class="tc-card">
      <div class="tc-label">Characters</div>
      <div id="charCount" class="tc-number">0</div>
    </div>
  </div>
</div>

<script type="module">
  import { getEncoding } from "https://cdn.jsdelivr.net/npm/js-tiktoken@1.0.21/+esm";

  const encoder = getEncoding("o200k_base");
  const textarea = document.getElementById("inputText");
  const tokenCountEl = document.getElementById("tokenCount");
  const wordCountEl = document.getElementById("wordCount");
  const charCountEl = document.getElementById("charCount");

  textarea.addEventListener("input", () => {
    const text = textarea.value;
    if (!text) {
      tokenCountEl.textContent = "0";
      wordCountEl.textContent = "0";
      charCountEl.textContent = "0";
      return;
    }
    const tokens = encoder.encode(text);
    tokenCountEl.textContent = tokens.length.toLocaleString();
    charCountEl.textContent = text.length.toLocaleString();
    wordCountEl.textContent = text.trim().split(/\s+/).filter(Boolean).length.toLocaleString();
  });
</script>