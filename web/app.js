// The search: on submit the greeting steps aside, the composer slides up to the top of the screen and
// the results appear under it. The answer comes from POST /api/search (f1rag serve).

const page = document.getElementById('page');
const form = document.getElementById('search');
const input = document.getElementById('q');
const send = form.querySelector('.send');
const results = document.getElementById('results');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');

const esc = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const anchor = id => 'c-' + id.replace(/\./g, '-');
const CLAUSE_ID = /\b(?:App)?B\d+(?:\.\d+)*(?:-part\d+)?/g;

// ------------------------------------------------------------------ the slide up
// FLIP: measure the composer, switch the layout, then animate it from where it was (transform only).
function enterResults() {
  if (page.classList.contains('is-results')) return;
  const before = form.getBoundingClientRect().top;
  page.classList.add('is-results');
  window.scrollTo(0, 0);
  if (reduced.matches) return;
  const after = form.getBoundingClientRect().top;
  form.animate(
    [{ transform: `translateY(${before - after}px)` }, { transform: 'none' }],
    { duration: 640, easing: 'cubic-bezier(.22,1,.36,1)' },
  );
}

function leaveResults() {
  page.classList.remove('is-results');
  results.hidden = true;
  results.innerHTML = '';
}

// ------------------------------------------------------------------ rendering
// A small Markdown subset: paragraphs, - and 1. lists, **bold**, `code`, and clause citations as links.
function inline(text) {
  return esc(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/[[【]([^\]】]*)[\]】]/g, (whole, inside) => {
      const ids = inside.match(CLAUSE_ID);
      if (!ids) return whole;
      return ids.map(id => `<a class="cite" href="#${anchor(id)}">${id}</a>`).join(' ');
    });
}

function markdown(text) {
  const out = [];
  let list = null;
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    const item = line.match(/^(?:[-*•]|\d+[.)])\s+(.*)$/);
    if (item) {
      const tag = /^\d/.test(line) ? 'ol' : 'ul';
      if (list !== tag) { if (list) out.push(`</${list}>`); out.push(`<${tag}>`); list = tag; }
      out.push(`<li>${inline(item[1])}</li>`);
      continue;
    }
    if (list) { out.push(`</${list}>`); list = null; }
    if (line) out.push(`<p>${inline(line.replace(/^#+\s*/, ''))}</p>`);
  }
  if (list) out.push(`</${list}>`);
  return out.join('');
}

// The PDF's line breaks are layout, not meaning: join the lines, keeping a break before each list item (a., ii., 3.).
function tidy(text) {
  return text.split('\n').map(l => l.trim()).filter(Boolean)
    .reduce((out, line) => /^(?:[a-z]|[ivx]+|\d+)[.)]\s/.test(line) || !out ? out + (out ? '\n' : '') + line : out + ' ' + line, '');
}

// Article titles come in capitals from the PDF ("B1 ORGANISATION OF A COMPETITION"): set them in sentence case.
function crumb(text) {
  return text.split(' > ').map(part => part === part.toUpperCase()
    ? part.replace(/^(\S+) (.)(.*)$/, (m, id, first, rest) => `${id} ${first}${rest.toLowerCase()}`).replace(/\((\w+)\)$/, m => m.toUpperCase())
    : part).join(' › ');
}

function clauseCard(c, tag) {
  const long = c.text.length > 420;
  return `<article class="clause${long ? ' is-long' : ''}" id="${anchor(c.id)}" tabindex="-1">
    <div class="clause__top"><p class="clause__id">${esc(c.id)}</p>${tag ? `<p class="clause__tag">${tag}</p>` : ''}</div>
    <p class="clause__crumb">${esc(crumb(c.breadcrumb))}${c.title ? ' › ' + esc(c.title) : ''}</p>
    <p class="clause__text">${esc(tidy(c.text) || c.title)}</p>
    ${long ? '<button class="clause__more" type="button" aria-expanded="false">Show the full clause</button>' : ''}
  </article>`;
}

function renderLoading(question) {
  results.innerHTML = `
    <div class="results__grid">
      <div class="answer is-loading">
        <p class="label">Answer</p>
        <p class="answer__status" role="status">Searching 304 clauses and following the graph. This takes a few seconds.</p>
        <div class="skeleton" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
      </div>
      <div class="cited"><p class="label">Cited clauses</p><div class="clause skeleton-card" aria-hidden="true"></div></div>
    </div>`;
}

function renderError(question, message) {
  results.innerHTML = `
    <div class="answer answer--error">
      <p class="label">Answer</p>
      <p role="alert">The search didn’t run. ${esc(message)}</p>
    </div>`;
}

function render(data) {
  const cited = data.citations.map(c => clauseCard(c, '')).join('');
  const more = [
    ...data.retrieved.map(c => clauseCard(c, 'Vector search')),
    ...data.related.map(c => clauseCard(c, 'Through the graph')),
  ].join('');
  results.innerHTML = `
    <div class="results__grid">
      <div class="answer">
        <p class="label">Answer</p>
        ${data.answerable ? '' : '<p class="answer__note">Section B doesn’t answer this directly.</p>'}
        <div class="answer__body">${markdown(data.answer)}</div>
      </div>
      <div class="cited">
        <p class="label">Cited clauses <span class="muted">${data.citations.length}</span></p>
        ${cited || '<p class="muted">The answer cites no clause.</p>'}
      </div>
    </div>
    ${more ? `<div class="more"><p class="label">Also found <span class="muted">${data.retrieved.length + data.related.length} clauses the answer didn’t cite</span></p><div class="more__grid">${more}</div></div>` : ''}`;
}

// ------------------------------------------------------------------ the search
let current = null;

// The textarea grows with its text, up to its max-height.
function fit() {
  input.style.height = 'auto';
  input.style.height = input.scrollHeight + 'px';
  send.disabled = input.value.trim().length < 3;
}

async function search(question, push = true) {
  input.value = question;
  fit();
  if (push) history.pushState({ q: question }, '', '?q=' + encodeURIComponent(question));
  enterResults();
  results.hidden = false;
  renderLoading(question);

  current?.abort();
  const request = current = new AbortController();
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
      signal: request.signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(typeof body.detail === 'string' ? body.detail : `the server answered ${response.status}`);
    }
    render(await response.json());
  } catch (e) {
    if (e.name === 'AbortError') return;
    renderError(question, e.message === 'Failed to fetch' ? 'The server isn’t reachable: start it with f1rag serve and open the page from it.' : e.message);
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  const question = input.value.trim();
  if (question.length < 3) return;
  input.blur();
  search(question);
});

input.addEventListener('input', fit);
// Enter searches, Shift+Enter starts a new line (not while an input method is composing).
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});

// A citation in the answer moves the focus to its clause card; a long card opens in place.
results.addEventListener('click', event => {
  const more = event.target.closest('.clause__more');
  if (more) {
    const open = more.closest('.clause').classList.toggle('is-open');
    more.setAttribute('aria-expanded', String(open));
    more.textContent = open ? 'Show less' : 'Show the full clause';
    return;
  }
  const cite = event.target.closest('a.cite');
  if (cite) {
    const card = document.querySelector(cite.getAttribute('href'));
    if (!card) return;
    event.preventDefault();
    card.scrollIntoView({ block: 'center', behavior: reduced.matches ? 'auto' : 'smooth' });
    card.focus({ preventScroll: true });
  }
});

window.addEventListener('popstate', () => {
  const q = new URLSearchParams(location.search).get('q');
  if (q) search(q, false); else { current?.abort(); leaveResults(); input.value = ''; fit(); }
});

const start = new URLSearchParams(location.search).get('q');
if (start) search(start, false); else input.focus();
