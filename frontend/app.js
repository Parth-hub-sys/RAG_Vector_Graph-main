/* ─── State ─── */
const API = '';  // same-origin

let useWebSearch = false;

/* ─── DOM refs ─── */
const sidebar       = document.getElementById('sidebar');
const menuBtn       = document.getElementById('menuBtn');
const sidebarClose  = document.getElementById('sidebarClose');
const themeBtn      = document.getElementById('themeBtn');
const iconMoon      = document.getElementById('iconMoon');
const iconSun       = document.getElementById('iconSun');
const dropZone      = document.getElementById('dropZone');
const uploadBtn     = document.getElementById('uploadBtn');
const fileInput     = document.getElementById('fileInput');
const uploadStatus  = document.getElementById('uploadStatus');
const webToggle     = document.getElementById('webSearchToggle');
const modeBadges    = document.getElementById('modeBadges');
const clearBtn      = document.getElementById('clearBtn');
const messages      = document.getElementById('messages');
const welcomeState  = document.getElementById('welcomeState');
const queryInput    = document.getElementById('queryInput');
const charCount     = document.getElementById('charCount');
const sendBtn       = document.getElementById('sendBtn');
const webPill       = document.getElementById('webPill');

/* ─── Theme ─── */
(function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
    if (theme === 'dark') {
        iconMoon.style.display = '';
        iconSun.style.display = 'none';
    } else {
        iconMoon.style.display = 'none';
        iconSun.style.display = '';
    }
}

themeBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
});

/* ─── Sidebar ─── */
menuBtn.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
sidebarClose.addEventListener('click', () => sidebar.classList.add('collapsed'));

/* ─── Web Search Toggle ─── */
webToggle.addEventListener('change', () => {
    useWebSearch = webToggle.checked;
    webPill.classList.toggle('visible', useWebSearch);

    const webBadge = modeBadges.querySelector('.badge-web');
    if (useWebSearch) {
        if (!webBadge) {
            const b = document.createElement('span');
            b.className = 'badge badge-web';
            b.textContent = 'Web';
            modeBadges.appendChild(b);
        }
    } else if (webBadge) {
        webBadge.remove();
    }
});

/* ─── File Upload ─── */
uploadBtn.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('click', (e) => {
    if (e.target !== uploadBtn) fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) uploadFile(fileInput.files[0]);
    fileInput.value = '';
});

async function uploadFile(file) {
    const allowed = ['.pdf', '.txt', '.docx'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
        setUploadStatus('error', `Unsupported type "${ext}". Use PDF, TXT, or DOCX.`);
        return;
    }

    setUploadStatus('loading', `Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`${API}/upload`, { method: 'POST', body: formData });
        const data = await res.json();

        if (!res.ok) {
            setUploadStatus('error', data.detail || 'Upload failed.');
            return;
        }

        if (data.status === 'skipped') {
            setUploadStatus('skipped', `"${data.filename}" already ingested.`);
        } else {
            setUploadStatus('success',
                `"${data.filename}" ingested — ${data.chunks_stored} chunks, ${data.graph_relationships} relations.`
            );
        }
    } catch (err) {
        setUploadStatus('error', 'Network error. Is the server running?');
    }
}

function setUploadStatus(type, msg) {
    uploadStatus.className = 'upload-status';
    uploadStatus.classList.add(`status-${type}`);
    const icons = { loading: '⏳', success: '✓', skipped: '⚠', error: '✗' };
    uploadStatus.textContent = `${icons[type]} ${msg}`;
}

/* ─── Chat Input ─── */
queryInput.addEventListener('input', () => {
    const len = queryInput.value.length;
    charCount.textContent = `${len} / 2000`;
    charCount.className = 'char-count' + (len > 1800 ? ' warn' : '') + (len >= 2000 ? ' limit' : '');
    sendBtn.disabled = len === 0 || len > 2000;

    queryInput.style.height = 'auto';
    queryInput.style.height = Math.min(queryInput.scrollHeight, 150) + 'px';
});

queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        if (!sendBtn.disabled) sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

/* ─── Clear Chat ─── */
clearBtn.addEventListener('click', () => {
    messages.innerHTML = '';
    messages.appendChild(welcomeState);
    welcomeState.style.display = '';
});

/* ─── Send Message ─── */
async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    welcomeState.style.display = 'none';

    appendUserMessage(query);

    queryInput.value = '';
    queryInput.style.height = 'auto';
    charCount.textContent = '0 / 2000';
    sendBtn.disabled = true;

    const loadingEl = appendLoading();

    try {
        const res = await fetch(`${API}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, use_web_search: useWebSearch }),
        });

        const data = await res.json();
        loadingEl.remove();

        if (!res.ok) {
            appendError(data.detail || 'Server error.');
            return;
        }

        appendAIResponse(data.response, data.used_web_search);
    } catch (err) {
        loadingEl.remove();
        appendError('Network error. Is the server running?');
    }

    scrollToBottom();
}

/* ─── Message Renderers ─── */
function appendUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'msg-user';
    div.innerHTML = `<div class="msg-user-bubble">${escapeHtml(text)}</div>`;
    messages.appendChild(div);
    scrollToBottom();
}

function appendLoading() {
    const div = document.createElement('div');
    div.className = 'msg-loading';
    div.innerHTML = `<div class="spinner"></div><span>Thinking...</span>`;
    messages.appendChild(div);
    scrollToBottom();
    return div;
}

function appendError(msg) {
    const div = document.createElement('div');
    div.className = 'msg-ai';
    div.innerHTML = `
        <div class="response-card">
            <div class="response-section" style="background:var(--error-bg)">
                <span style="color:var(--error);font-size:13px">✗ ${escapeHtml(msg)}</span>
            </div>
        </div>`;
    messages.appendChild(div);
    scrollToBottom();
}

function appendAIResponse(rawText, usedWeb) {
    const parsed = parseResponse(rawText);
    const div = document.createElement('div');
    div.className = 'msg-ai';

    let html = '<div class="response-card">';

    // Document Summary
    html += buildSection(
        'icon-doc', '📄', 'Document Summary',
        parsed.documentSummary,
        'response-text',
        true
    );

    // Graph Relations
    html += buildGraphSection(parsed.graphRelations);

    // Web Search Summary
    if (usedWeb && parsed.webSummary) {
        html += buildSection(
            'icon-web', '🌐', 'Web Search Summary',
            parsed.webSummary,
            'response-text',
            true
        );
    }

    // Final Answer
    html += `
        <div class="response-section final-answer-section">
            <div class="response-section-header">
                <div class="response-section-icon icon-ans">✦</div>
                <span class="response-section-title">Final Answer</span>
            </div>
            <div class="final-answer-text">${escapeHtml(parsed.finalAnswer || rawText)}</div>
        </div>`;

    // Sources
    if (parsed.sources) {
        html += buildSources(parsed.sources);
    }

    html += '</div>';
    div.innerHTML = html;

    // Collapsible sections
    div.querySelectorAll('.response-section-header[data-collapsible]').forEach(header => {
        const body = header.nextElementSibling;
        const arrow = header.querySelector('.collapse-arrow');
        header.addEventListener('click', () => {
            body.classList.toggle('hidden');
            arrow.classList.toggle('open');
        });
    });

    messages.appendChild(div);
    scrollToBottom();
}

function buildSection(iconClass, emoji, title, content, textClass, collapsible) {
    const isAbsent = !content || content.toLowerCase().startsWith('no ') || content.toLowerCase().includes('not available');
    const displayContent = content || 'Not available.';
    const collapsed = isAbsent ? 'hidden' : '';
    const arrowClass = isAbsent ? '' : 'open';

    if (collapsible) {
        return `
            <div class="response-section">
                <div class="response-section-header" data-collapsible>
                    <div class="response-section-icon ${iconClass}">${emoji}</div>
                    <span class="response-section-title">${title}</span>
                    <span class="collapse-arrow ${arrowClass}">▲</span>
                </div>
                <div class="collapsible-body ${collapsed}">
                    <div class="${textClass} ${isAbsent ? 'muted' : ''}">${escapeHtml(displayContent)}</div>
                </div>
            </div>`;
    }
    return `
        <div class="response-section">
            <div class="response-section-header">
                <div class="response-section-icon ${iconClass}">${emoji}</div>
                <span class="response-section-title">${title}</span>
            </div>
            <div class="${textClass} ${isAbsent ? 'muted' : ''}">${escapeHtml(displayContent)}</div>
        </div>`;
}

function buildGraphSection(relations) {
    const isAbsent = !relations || relations.length === 0 ||
        (relations.length === 1 && relations[0].toLowerCase().includes('not available'));

    let innerHtml;
    if (isAbsent) {
        innerHtml = `<div class="response-text muted">No graph relations available.</div>`;
    } else {
        const items = relations.map(r => {
            // Render "A → relation → B" with styled parts
            const parts = r.split('→').map(p => p.trim());
            if (parts.length === 3) {
                return `<div class="relation-item">
                    <span class="rel-subject">${escapeHtml(parts[0])}</span>
                    <span class="rel-arrow">→</span>
                    <span class="rel-predicate">${escapeHtml(parts[1])}</span>
                    <span class="rel-arrow">→</span>
                    <span class="rel-object">${escapeHtml(parts[2])}</span>
                </div>`;
            }
            return `<div class="relation-item">${escapeHtml(r)}</div>`;
        }).join('');
        innerHtml = `<div class="graph-relations">${items}</div>`;
    }

    const arrowClass = isAbsent ? '' : 'open';
    const collapsed = isAbsent ? 'hidden' : '';

    return `
        <div class="response-section">
            <div class="response-section-header" data-collapsible>
                <div class="response-section-icon icon-graph">◈</div>
                <span class="response-section-title">Graph Relations</span>
                <span class="collapse-arrow ${arrowClass}">▲</span>
            </div>
            <div class="collapsible-body ${collapsed}">${innerHtml}</div>
        </div>`;
}

function buildSources(sourcesText) {
    const parts = sourcesText.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
    const badges = parts.map(s => {
        if (s === 'VECTOR') return `<span class="badge badge-vector">Vector</span>`;
        if (s === 'GRAPH')  return `<span class="badge badge-graph">Graph</span>`;
        if (s === 'WEB')    return `<span class="badge badge-web">Web</span>`;
        return `<span class="badge" style="background:var(--surface-3)">${escapeHtml(s)}</span>`;
    }).join('');
    return `
        <div class="sources-section">
            <span class="sources-label">Sources:</span>
            <div class="sources-badges">${badges}</div>
        </div>`;
}

/* ─── Response Parser ─── */
function parseResponse(text) {
    const result = {
        documentSummary: null,
        graphRelations: null,
        webSummary: null,
        finalAnswer: null,
        sources: null,
    };

    const extract = (startLabel, stopLabels) => {
        const escapedStart = startLabel.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const escapedStops = stopLabels.map(l => l.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
        const stopGroup = escapedStops.length ? `(?=${escapedStops.join('|')}:|$)` : '';
        const rx = new RegExp(`${escapedStart}:\\s*([\\s\\S]*?)\\s*${stopGroup}`, 'i');
        const m = text.match(rx);
        return m ? m[1].trim() : null;
    };

    result.documentSummary = extract('Document Summary', ['Graph Relations', 'Web Search Summary', 'Final Answer', 'Sources']);
    const graphRaw = extract('Graph Relations', ['Web Search Summary', 'Final Answer', 'Sources']);
    if (graphRaw) {
        result.graphRelations = graphRaw.split('\n').map(l => l.trim()).filter(Boolean);
    }
    result.webSummary = extract('Web Search Summary', ['Final Answer', 'Sources']);
    result.finalAnswer = extract('Final Answer', ['Sources']);
    result.sources = extract('Sources', []);

    return result;
}

/* ─── Helpers ─── */
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        messages.scrollTop = messages.scrollHeight;
    });
}
