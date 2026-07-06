/* ===== ОТКРЫТКА (otkrytka) — app.js (buildless vanilla JS) ===== */
'use strict';

// ─── i18n ──────────────────────────────────────────────────────────────────
const STR = {
  en: {
    // Landing
    hero_eyebrow: "No accounts, no downloads",
    hero_title: "A group card, together",
    hero_sub: "Gather warm words and photos for someone dear. One link, no signup.",
    create_title_label: "The occasion",
    create_title_ph: "Happy birthday, Anna!",
    recipient_label: "Who is it for?",
    recipient_ph: "Anna",
    cover_label: "Pick a cover",
    create_btn: "Start a card",
    or_label: "or",
    join_label: "Have a link already?",
    join_ph: "Card code",
    join_go: "Open",
    preview_label: "A quick look",
    preview_hint: "Everyone drops in a wish. The nicest ones get pinned to the top.",
    feat_free: "No login, ever",
    feat_photo: "Words, photos and GIFs",
    feat_live: "Fills up live",
    preview_w1: "Wishing you the warmest year. We love you!",
    preview_w2: "Thank you for always being there.",
    preview_w3: "Here is to new adventures together.",
    preview_n1: "Mom",
    preview_n2: "Kirill",
    preview_n3: "The team",

    // Landing: sample assembled card + how it works
    sample_label: "This is what you gift",
    ex_title: "Happy birthday, Masha!",
    ex_for: "For Masha",
    ex_n1: "Anya",
    ex_w1: "Happy birthday! 🎉",
    ex_n2: "Boris",
    ex_w2: "Grow up big, I hug you!",
    ex_n3: "Gleb",
    ex_w3: "May all your wishes come true ✨",
    ex_n4: "Dasha",
    ex_w4: "Love you 💛",
    how_label: "How it works",
    how1: "Create a card",
    how2: "Share the link",
    how3: "Deliver it",
    form_lead: "Ready? Make yours",

    // Header / board
    doc_title: "Otkrytka · Warm words, together",
    brand: "Otkrytka",
    home_link: "Home",
    share_label: "Share:",
    share_tg: "Telegram",
    share_wa: "WhatsApp",
    share_vk: "VK",
    copy_link: "Copy link",
    copy_done: "Copied!",
    qr_btn: "QR",
    qr_title: "Scan to open the card",
    you_are: "You:",
    set_name: "Set your name",
    change_name: "Change",
    for_word: "For",
    add_wish_btn: "Add a wish",
    empty_title: "No wishes yet",
    empty_hint: "Be the first to add warm words, a photo or a GIF.",
    pin_action: "Pin",
    unpin_action: "Unpin",
    delete_action: "Remove",
    pinned_flag: "Pinned",
    lock_btn: "Close the card",
    locked_banner: "The card is closed and ready to deliver.",
    deliver_btn: "Deliver",
    delete_board: "Delete this card",
    board_deleted: "Card deleted.",
    undo_btn: "Undo",
    wishes_count: "{n} wishes",

    // Add-wish modal
    add_modal_title: "Add your wish",
    name_label: "Your name",
    name_ph: "Your name…",
    text_label: "Your words",
    text_ph: "Write something warm…",
    photo_label: "Photo (optional)",
    drop_hint: "Drop a photo here or tap to choose",
    gif_label: "GIF link (optional)",
    gif_ph: "https://…/hug.gif",
    gif_hint: "Paste a direct link to a GIF or image.",
    remove_photo: "Remove photo",
    send_wish: "Add to the card",
    cancel_btn: "Cancel",
    uploading: "Adding…",
    err_need_something: "Add some words, a photo or a GIF.",

    // Name modal
    name_modal_title: "What's your name for this card?",
    name_save: "Save",

    // Created modal
    created_title: "Your card is ready!",
    created_sub: "Share the guest link so everyone can add a wish.",
    created_share_label: "Guest link (add wishes)",
    created_manage_label: "Your private organizer link",
    created_manage_hint: "Bookmark this. It lets only you pin, close and deliver the card.",
    created_go: "Open the card",

    // Delivery
    deliver_intro: "For you,",
    back_to_board: "Back to the card",

    // Status / live / errors
    ws_live: "Live",
    ws_reconnecting: "Reconnecting…",
    loading: "Loading…",
    err_not_found: "Card not found.",
    err_generic: "Something went wrong.",
    confirm_delete_board: "Delete this card for everyone?",
    confirm_delete_card: "Remove this wish?",
  },
  ru: {
    // Landing
    hero_eyebrow: "Без аккаунтов и установок",
    hero_title: "Открытка вскладчину",
    hero_sub: "Соберите тёплые слова и фото для того, кто дорог. Одна ссылка, без регистрации.",
    create_title_label: "Повод",
    create_title_ph: "С днём рождения, Аня!",
    recipient_label: "Кому открытка?",
    recipient_ph: "Аня",
    cover_label: "Выберите обложку",
    create_btn: "Создать открытку",
    or_label: "или",
    join_label: "Уже есть ссылка?",
    join_ph: "Код открытки",
    join_go: "Открыть",
    preview_label: "Как это выглядит",
    preview_hint: "Каждый добавляет пожелание. Самые тёплые закрепляются наверху.",
    feat_free: "Никаких логинов",
    feat_photo: "Слова, фото и GIF",
    feat_live: "Наполняется вживую",
    preview_w1: "Пусть год будет самым тёплым. Любим тебя!",
    preview_w2: "Спасибо, что ты всегда рядом.",
    preview_w3: "За новые приключения вместе.",
    preview_n1: "Мама",
    preview_n2: "Кирилл",
    preview_n3: "Команда",

    // Landing: sample assembled card + how it works
    sample_label: "Вот что вы дарите",
    ex_title: "С днём рождения, Маша!",
    ex_for: "Для Маши",
    ex_n1: "Аня",
    ex_w1: "С днём рождения! 🎉",
    ex_n2: "Борис",
    ex_w2: "Расти большой, обнимаю!",
    ex_n3: "Глеб",
    ex_w3: "Пусть всё сбудется ✨",
    ex_n4: "Даша",
    ex_w4: "Люблю тебя 💛",
    how_label: "Как это работает",
    how1: "Создай открытку",
    how2: "Поделись ссылкой",
    how3: "Подари",
    form_lead: "Готовы? Соберите свою",

    // Header / board
    doc_title: "Открытка · Тёплые слова вскладчину",
    brand: "Открытка",
    home_link: "На главную",
    share_label: "Поделиться:",
    share_tg: "Telegram",
    share_wa: "WhatsApp",
    share_vk: "VK",
    copy_link: "Копировать ссылку",
    copy_done: "Скопировано!",
    qr_btn: "QR",
    qr_title: "Отсканируйте, чтобы открыть",
    you_are: "Вы:",
    set_name: "Укажите имя",
    change_name: "Изменить",
    for_word: "Кому:",
    add_wish_btn: "Добавить пожелание",
    empty_title: "Пока нет пожеланий",
    empty_hint: "Добавьте первым тёплые слова, фото или GIF.",
    pin_action: "Закрепить",
    unpin_action: "Открепить",
    delete_action: "Убрать",
    pinned_flag: "Закреплено",
    lock_btn: "Закрыть открытку",
    locked_banner: "Открытка закрыта и готова к вручению.",
    deliver_btn: "Подарить",
    delete_board: "Удалить открытку",
    board_deleted: "Открытка удалена.",
    undo_btn: "Отменить",
    wishes_count: "{n} пожеланий",

    // Add-wish modal
    add_modal_title: "Ваше пожелание",
    name_label: "Ваше имя",
    name_ph: "Ваше имя…",
    text_label: "Ваши слова",
    text_ph: "Напишите что-то тёплое…",
    photo_label: "Фото (по желанию)",
    drop_hint: "Перетащите фото сюда или нажмите, чтобы выбрать",
    gif_label: "Ссылка на GIF (по желанию)",
    gif_ph: "https://…/hug.gif",
    gif_hint: "Вставьте прямую ссылку на GIF или картинку.",
    remove_photo: "Убрать фото",
    send_wish: "Добавить в открытку",
    cancel_btn: "Отмена",
    uploading: "Добавляем…",
    err_need_something: "Добавьте слова, фото или GIF.",

    // Name modal
    name_modal_title: "Как вас зовут в этой открытке?",
    name_save: "Сохранить",

    // Created modal
    created_title: "Открытка готова!",
    created_sub: "Поделитесь гостевой ссылкой, чтобы каждый добавил пожелание.",
    created_share_label: "Гостевая ссылка (добавить пожелание)",
    created_manage_label: "Ваша личная ссылка организатора",
    created_manage_hint: "Сохраните её. Только вы сможете закреплять, закрывать и вручать открытку.",
    created_go: "Открыть открытку",

    // Delivery
    deliver_intro: "Для тебя,",
    back_to_board: "Вернуться к открытке",

    // Status / live / errors
    ws_live: "Вживую",
    ws_reconnecting: "Переподключение…",
    loading: "Загрузка…",
    err_not_found: "Открытка не найдена.",
    err_generic: "Что-то пошло не так.",
    confirm_delete_board: "Удалить открытку для всех?",
    confirm_delete_card: "Убрать это пожелание?",
  },
};

const COVERS = ['🎂', '🎉', '💐', '🌸', '❤️', '🎁', '✨', '🥳', '🌟', '🎈'];

// ─── State ─────────────────────────────────────────────────────────────────
const state = {
  lang: (() => {
    const s = localStorage.getItem('otkrytka_lang');
    if (s) return s;
    return (navigator.language || '').toLowerCase().startsWith('ru') ? 'ru' : 'en';
  })(),
  slug: '',
  board: null,
  seen: new Set(), // card ids already on screen (so only fresh ones animate)
};

// ─── WebSocket live-sync ─────────────────────────────────────────────────────
const ws = {
  socket: null,
  slug: null,
  retryTimer: null,
  retryDelay: 1000,
  debounceTimer: null,
  pendingRefresh: false,
  active: false,
};

function wsUrl(slug) {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${location.host}/api/v1/boards/${slug}/ws`;
}

/** True if the user is mid-action: modal open OR an input/textarea focused. */
function userIsBusy() {
  if (document.querySelector('.modal-overlay')) return true;
  const el = document.activeElement;
  if (!el) return false;
  const tag = el.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
}

/** Apply a deferred refresh, animating new cards and preserving scroll. */
async function applyObserverRefresh(slug) {
  try {
    const board = await api.get(`/api/v1/boards/${slug}`);
    state.board = board;
    const scrollY = window.scrollY;
    paintBoard(document.getElementById('app'), slug, { animateNew: true });
    window.scrollTo({ top: scrollY, behavior: 'instant' });
  } catch (_) {
    // WS refresh failure is non-fatal.
  }
}

function flushPendingRefresh() {
  if (ws.pendingRefresh && ws.slug && ws.slug === state.slug) {
    ws.pendingRefresh = false;
    applyObserverRefresh(ws.slug);
  }
}

function onChanged() {
  if (userIsBusy()) {
    ws.pendingRefresh = true;
    return;
  }
  applyObserverRefresh(ws.slug);
}

function setLivePip(status) {
  const pip = document.getElementById('live-pip');
  if (!pip) return;
  if (status === 'connected') {
    pip.className = 'live-pip live-pip--connected';
    pip.textContent = t('ws_live');
    pip.setAttribute('aria-label', t('ws_live'));
  } else if (status === 'reconnecting') {
    pip.className = 'live-pip live-pip--reconnecting';
    pip.textContent = t('ws_reconnecting');
    pip.setAttribute('aria-label', t('ws_reconnecting'));
  } else {
    pip.className = 'live-pip';
    pip.textContent = '';
  }
}

function wsConnect(slug) {
  wsClose();
  ws.active = true;
  ws.slug = slug;

  let sock;
  try {
    sock = new WebSocket(wsUrl(slug));
  } catch (_) {
    return; // browser/proxy without WS — degrade silently
  }
  ws.socket = sock;

  sock.addEventListener('open', () => {
    ws.retryDelay = 1000;
    setLivePip('connected');
  });
  sock.addEventListener('message', e => {
    let msg;
    try { msg = JSON.parse(e.data); } catch (_) { return; }
    if (msg.type === 'hello') return;
    if (msg.type === 'changed') {
      clearTimeout(ws.debounceTimer);
      ws.debounceTimer = setTimeout(onChanged, 300);
    }
  });
  sock.addEventListener('close', () => {
    if (!ws.active) return;
    setLivePip('reconnecting');
    scheduleReconnect(slug);
  });
  sock.addEventListener('error', () => {
    setLivePip('reconnecting');
  });
}

function scheduleReconnect(slug) {
  clearTimeout(ws.retryTimer);
  if (!ws.active) return;
  ws.retryTimer = setTimeout(() => {
    if (!ws.active) return;
    ws.retryDelay = Math.min(ws.retryDelay * 2, 15000);
    wsConnect(slug);
  }, ws.retryDelay);
}

function wsClose() {
  ws.active = false;
  clearTimeout(ws.retryTimer);
  clearTimeout(ws.debounceTimer);
  ws.pendingRefresh = false;
  if (ws.socket) {
    ws.socket.onclose = null;
    ws.socket.onerror = null;
    try { ws.socket.close(); } catch (_) {}
    ws.socket = null;
  }
  ws.slug = null;
  ws.retryDelay = 1000;
}

document.addEventListener('focusout', () => {
  setTimeout(() => { if (!userIsBusy()) flushPendingRefresh(); }, 80);
});
const _modalObserver = new MutationObserver(() => {
  if (!document.querySelector('.modal-overlay')) flushPendingRefresh();
});
_modalObserver.observe(document.body, { childList: true, subtree: false });

// ─── i18n helper ─────────────────────────────────────────────────────────────
function t(key, vars) {
  const dict = STR[state.lang] || STR.en;
  let s = dict[key] !== undefined ? dict[key] : (STR.en[key] !== undefined ? STR.en[key] : key);
  if (vars) s = s.replace(/\{(\w+)\}/g, (_, k) => (vars[k] !== undefined ? vars[k] : ''));
  return s;
}

// ─── API helpers ─────────────────────────────────────────────────────────────
async function apiCall(method, path, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  if (res.status === 204) return null;
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.detail || t('err_generic'));
  return json;
}

const api = {
  get: (p) => apiCall('GET', p),
  post: (p, b) => apiCall('POST', p, b),
  patch: (p, b) => apiCall('PATCH', p, b),
  del: (p, b) => apiCall('DELETE', p, b),
};

async function uploadImage(slug, blob, filename) {
  const fd = new FormData();
  fd.append('file', blob, filename);
  const res = await fetch(`/api/v1/boards/${slug}/upload`, { method: 'POST', body: fd });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.detail || t('err_generic'));
  return json.image_path;
}

// ─── Local storage helpers ───────────────────────────────────────────────────
function getMyName(slug) { return localStorage.getItem(`otkrytka_me_${slug}`) || ''; }
function setMyName(slug, name) { localStorage.setItem(`otkrytka_me_${slug}`, name); }
function getOrgToken(slug) { return localStorage.getItem(`otkrytka_org_${slug}`) || ''; }
function setOrgToken(slug, token) { localStorage.setItem(`otkrytka_org_${slug}`, token); }

// ─── XSS escape ──────────────────────────────────────────────────────────────
function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ─── Deterministic avatar gradient from a name ──────────────────────────────
function nameHue(name) {
  let h = 0;
  const s = String(name || '?');
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 360;
  return h;
}
function avatarStyle(name) {
  const h = nameHue(name);
  const c1 = `oklch(72% 0.14 ${h})`;
  const c2 = `oklch(64% 0.15 ${(h + 40) % 360})`;
  return `background:linear-gradient(135deg, ${c1}, ${c2})`;
}
function initial(name) {
  const s = String(name || '?').trim();
  return s ? s[0].toUpperCase() : '?';
}

// ─── Toast ───────────────────────────────────────────────────────────────────
function showToast(msg, duration = 3000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => {
    el.classList.add('out');
    setTimeout(() => el.remove(), 250);
  }, duration);
}

function showUndoToast(msg, actionLabel, onAction, duration = 8000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const el = document.createElement('div');
  el.className = 'toast';
  const text = document.createElement('span');
  text.textContent = msg;
  const btn = document.createElement('button');
  btn.className = 'toast-action';
  btn.textContent = actionLabel;
  let done = false;
  const dismiss = () => {
    if (done) return;
    done = true;
    el.classList.add('out');
    setTimeout(() => el.remove(), 250);
  };
  btn.addEventListener('click', async () => {
    if (done) return;
    done = true;
    el.remove();
    await onAction();
  });
  el.appendChild(text);
  el.appendChild(btn);
  document.body.appendChild(el);
  setTimeout(dismiss, duration);
}

// ─── Confetti — warm palette ─────────────────────────────────────────────────
let _confettiEl = null;
function getConfettiEl() {
  if (!_confettiEl) {
    _confettiEl = document.createElement('canvas');
    _confettiEl.id = 'confetti-canvas';
    document.body.appendChild(_confettiEl);
  }
  return _confettiEl;
}
function fireConfetti() {
  if (typeof confetti === 'undefined') return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const c = confetti.create(getConfettiEl(), { resize: true, useWorker: false });
  // Festive gift palette — rose, warm gold, lilac, mint
  const warm = ['#C93B57', '#E39A3D', '#F0C85A', '#C79AD6', '#7FCBB0'];
  c({ particleCount: 140, spread: 90, origin: { y: 0.5 }, colors: warm });
  setTimeout(() => c({ particleCount: 70, spread: 55, origin: { y: 0.6 }, startVelocity: 24, colors: warm }), 320);
}

// ─── Lang switcher ───────────────────────────────────────────────────────────
function mkLangSwitcher() {
  return `
    <div class="flex gap-1" role="group" aria-label="Language">
      <button class="lang-btn ${state.lang === 'ru' ? 'active' : ''}" data-lang="ru">RU</button>
      <button class="lang-btn ${state.lang === 'en' ? 'active' : ''}" data-lang="en">EN</button>
    </div>`;
}

// ─── Generic modal shell ─────────────────────────────────────────────────────
function openModal(innerHtml) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  const card = document.createElement('div');
  card.className = 'modal-card';
  card.innerHTML = innerHtml;
  overlay.appendChild(card);
  document.body.appendChild(overlay);
  const close = () => overlay.remove();
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', function onKey(e) {
    if (e.key === 'Escape') { close(); document.removeEventListener('keydown', onKey); }
  });
  return { overlay, card, close };
}

// ─── Name modal (ensureName gate before adding a card) ───────────────────────
let _nameModalOpen = false;

function showNameModal(slug, current) {
  _nameModalOpen = true;
  return new Promise(resolve => {
    const { overlay, card } = openModal(`
      <h2 class="modal-title">${esc(t('name_modal_title'))}</h2>
      <input class="kg-input" type="text" placeholder="${esc(t('name_ph'))}" maxlength="48" value="${esc(current || '')}" autocomplete="nickname">
      <div class="flex gap-2">
        <button class="flex-1 py-3 rounded-2xl border-2 font-body btn-press-sm" style="border-color:var(--sand-deep);color:var(--muted);font-weight:700" data-action="cancel">${esc(t('cancel_btn'))}</button>
        <button class="flex-1 py-3 rounded-2xl font-body btn-press" style="background:var(--coral-dark);color:var(--surface);font-weight:700" data-action="save">${esc(t('name_save'))}</button>
      </div>`);
    const input = card.querySelector('input');
    setTimeout(() => input.focus(), 30);
    const doSave = () => {
      const name = input.value.trim();
      if (!name) { input.focus(); return; }
      setMyName(slug, name);
      overlay.remove();
      _nameModalOpen = false;
      resolve(name);
    };
    const doCancel = () => { overlay.remove(); _nameModalOpen = false; resolve(null); };
    card.querySelector('[data-action="save"]').addEventListener('click', doSave);
    card.querySelector('[data-action="cancel"]').addEventListener('click', doCancel);
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') doSave();
      if (e.key === 'Escape') doCancel();
    });
    overlay.addEventListener('click', e => { if (e.target === overlay) doCancel(); });
  });
}

function ensureName(slug) {
  const existing = getMyName(slug);
  if (existing) return Promise.resolve(existing);
  if (_nameModalOpen) {
    return new Promise(resolve => {
      const poll = setInterval(() => {
        const n = getMyName(slug);
        if (n) { clearInterval(poll); resolve(n); }
      }, 200);
    });
  }
  return showNameModal(slug);
}

// ─── Client-side image resize (canvas, max ~1600px) ──────────────────────────
function resizeImage(file, maxDim = 1600) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      let { width, height } = img;
      if (Math.max(width, height) > maxDim) {
        const k = maxDim / Math.max(width, height);
        width = Math.round(width * k);
        height = Math.round(height * k);
      }
      const canvas = document.createElement('canvas');
      canvas.width = width; canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);
      const type = file.type === 'image/png' ? 'image/png' : 'image/jpeg';
      const ext = type === 'image/png' ? 'photo.png' : 'photo.jpg';
      canvas.toBlob(
        blob => (blob ? resolve({ blob, filename: ext }) : reject(new Error('encode failed'))),
        type,
        0.85,
      );
    };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('bad image')); };
    img.src = url;
  });
}

// ─── Routing ─────────────────────────────────────────────────────────────────
/** Parse `#/slug`, `#/slug/k/<token>`, `#/slug/deliver`. */
function parseRoute() {
  const raw = location.hash.replace(/^#\/?/, '').trim();
  if (!raw) return { view: 'landing' };
  const parts = raw.split('/');
  const slug = parts[0].toLowerCase();
  if (parts[1] === 'k' && parts[2]) return { view: 'manage', slug, token: parts[2] };
  if (parts[1] === 'deliver') return { view: 'deliver', slug };
  return { view: 'board', slug };
}
function goTo(hash) { location.hash = hash; }

async function render() {
  document.documentElement.lang = state.lang;
  document.title = t('doc_title'); // keep the browser tab title in sync with the UI language
  const route = parseRoute();
  const root = document.getElementById('app');

  if (route.view === 'manage') {
    // Adopt the organizer token for this browser, then drop it from the URL.
    setOrgToken(route.slug, route.token);
    location.replace(`${location.pathname}#/${route.slug}`);
    return;
  }
  if (route.view === 'landing') {
    state.slug = '';
    renderLanding(root);
  } else if (route.view === 'deliver') {
    state.slug = route.slug;
    await renderDeliver(root, route.slug);
  } else {
    state.slug = route.slug;
    await renderBoard(root, route.slug);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SCREEN 1 — Landing
// ═══════════════════════════════════════════════════════════════════════════
function renderLanding(root) {
  let cover = COVERS[0];
  root.innerHTML = `
    <nav style="position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:14px 5vw;background:oklch(98% 0.018 75 / 0.92);backdrop-filter:blur(12px);border-bottom:2px solid var(--sand-deep)">
      <a class="font-display" style="display:inline-flex;align-items:center;gap:8px;font-size:1.3rem;color:var(--ink);text-decoration:none;font-weight:900" href="#">
        <span>💌</span><span>${esc(t('brand'))}</span>
      </a>
      ${mkLangSwitcher()}
    </nav>

    <main class="hero-blobs" style="max-width:820px;margin:0 auto;padding:48px 6vw 80px">
      <div style="text-align:center;max-width:660px;margin:0 auto">
        <p class="hero-reveal-1 font-display" style="color:var(--coral);font-weight:800;letter-spacing:0.06em;text-transform:uppercase;font-size:0.8rem;margin-bottom:14px">${esc(t('hero_eyebrow'))}</p>
        <h1 class="hero-reveal-1 font-display" style="font-weight:900;font-size:clamp(2.2rem,6vw,3.4rem);line-height:1.05;color:var(--ink);letter-spacing:-0.02em">${esc(t('hero_title'))}</h1>
        <p class="hero-reveal-2" style="margin-top:16px;font-size:clamp(1.05rem,2.5vw,1.25rem);color:var(--muted)">${esc(t('hero_sub'))}</p>
      </div>

      <!-- The outcome: a sample assembled card, shown before the form -->
      <p class="hero-reveal-2 font-display" style="text-align:center;font-size:0.75rem;color:var(--gold-deep);font-weight:800;letter-spacing:0.08em;text-transform:uppercase;margin:30px auto 12px">${esc(t('sample_label'))}</p>
      <div class="hero-reveal-2 sample-card" style="margin:0 auto">
        <div class="sample-head">
          <span class="cover-badge">🎂</span>
          <div style="min-width:0">
            <p class="sample-for">🎀 ${esc(t('ex_for'))}</p>
            <p class="sample-title">${esc(t('ex_title'))}</p>
          </div>
        </div>
        <div class="masonry">
          ${[
            { n: t('ex_n1'), w: t('ex_w1'), pin: true },
            { n: t('ex_n2'), w: t('ex_w2'), pin: false },
            { n: t('ex_n3'), w: t('ex_w3'), pin: false },
            { n: t('ex_n4'), w: t('ex_w4'), pin: false },
          ].map(c => `
            <div class="wish ${c.pin ? 'pinned' : ''}">
              ${c.pin ? `<span class="pin-flag">📌 ${esc(t('pinned_flag'))}</span>` : ''}
              <div class="wish-author" style="margin-top:${c.pin ? '8px' : '0'}">
                <span class="wish-avatar" style="${avatarStyle(c.n)}">${esc(initial(c.n))}</span>${esc(c.n)}
              </div>
              <p class="wish-text">${esc(c.w)}</p>
            </div>`).join('')}
        </div>
        <p style="text-align:center;font-size:0.85rem;color:var(--muted);margin-top:14px">${esc(t('preview_hint'))}</p>
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:14px">
          <span class="tally-chip" style="background:var(--sand);color:var(--muted)">🔓 ${esc(t('feat_free'))}</span>
          <span class="tally-chip" style="background:var(--sand);color:var(--muted)">📷 ${esc(t('feat_photo'))}</span>
          <span class="tally-chip" style="background:var(--sand);color:var(--muted)">⚡ ${esc(t('feat_live'))}</span>
        </div>
      </div>

      <!-- How it works: collect wishes → share → gift -->
      <div class="hero-reveal-3" style="max-width:560px;margin:34px auto 0">
        <p class="font-display" style="text-align:center;font-size:0.75rem;color:var(--gold-deep);font-weight:800;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:16px">${esc(t('how_label'))}</p>
        <div class="how-steps">
          ${[
            { i: '✍️', n: '1', l: t('how1') },
            { i: '🔗', n: '2', l: t('how2') },
            { i: '🎁', n: '3', l: t('how3') },
          ].map(s => `
            <div class="how-step">
              <span class="step-icon">${s.i}<span class="step-num">${s.n}</span></span>
              <span class="step-label">${esc(s.l)}</span>
            </div>`).join('')}
        </div>
      </div>

      <!-- Create form, after the emotional hook -->
      <div class="hero-reveal-4 cozy-card" style="max-width:520px;margin:36px auto 0;padding:24px">
        <p class="font-display" style="text-align:center;font-weight:800;font-size:1.15rem;color:var(--ink);margin-bottom:16px">${esc(t('form_lead'))}</p>
        <label class="modal-label" style="display:block;margin-bottom:8px">${esc(t('create_title_label'))}</label>
        <input id="create-title" class="kg-input" type="text" maxlength="120" placeholder="${esc(t('create_title_ph'))}">
        <label class="modal-label" style="display:block;margin:14px 0 8px">${esc(t('recipient_label'))}</label>
        <input id="create-recipient" class="kg-input" type="text" maxlength="80" placeholder="${esc(t('recipient_ph'))}">
        <label class="modal-label" style="display:block;margin:14px 0 8px">${esc(t('cover_label'))}</label>
        <div class="cover-grid" id="cover-grid">
          ${COVERS.map((c, i) => `<button type="button" class="cover-chip ${i === 0 ? 'sel' : ''}" data-cover="${esc(c)}">${c}</button>`).join('')}
        </div>
        <button id="create-btn" class="cta-hero" style="width:100%;margin-top:18px">💌 ${esc(t('create_btn'))}</button>

        <div class="ornament-rule gold" style="margin:20px 0"><span>${esc(t('or_label'))}</span></div>
        <label class="modal-label" style="display:block;margin-bottom:8px">${esc(t('join_label'))}</label>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <input id="join-input" class="kg-input" style="flex:1;min-width:160px" type="text" maxlength="7" placeholder="${esc(t('join_ph'))}">
          <button id="join-btn" class="btn-soft btn-press-sm">${esc(t('join_go'))}</button>
        </div>
      </div>
    </main>`;

  root.querySelectorAll('[data-cover]').forEach(btn => {
    btn.addEventListener('click', () => {
      cover = btn.dataset.cover;
      root.querySelectorAll('.cover-chip').forEach(c => c.classList.remove('sel'));
      btn.classList.add('sel');
    });
  });

  const titleInput = root.querySelector('#create-title');
  const doCreate = async () => {
    const title = titleInput.value.trim();
    if (!title) { titleInput.focus(); return; }
    const recipient = root.querySelector('#create-recipient').value.trim() || null;
    try {
      const out = await api.post('/api/v1/boards', { title, recipient, cover });
      setOrgToken(out.slug, out.organizer_token);
      showCreatedModal(out.slug, out.organizer_token);
    } catch (e) { showToast(e.message); }
  };
  root.querySelector('#create-btn').addEventListener('click', doCreate);
  titleInput.addEventListener('keydown', e => { if (e.key === 'Enter') doCreate(); });

  const joinInput = root.querySelector('#join-input');
  const doJoin = () => {
    const slug = joinInput.value.trim().toLowerCase();
    if (slug) goTo(`#/${slug}`);
  };
  root.querySelector('#join-btn').addEventListener('click', doJoin);
  joinInput.addEventListener('keydown', e => { if (e.key === 'Enter') doJoin(); });
}

// ─── Created modal (organizer link shown once) ───────────────────────────────
function showCreatedModal(slug, token) {
  const shareUrl = `${location.origin}/#/${slug}`;
  const manageUrl = `${location.origin}/#/${slug}/k/${token}`;
  const { overlay, card } = openModal(`
    <h2 class="modal-title">🎉 ${esc(t('created_title'))}</h2>
    <p style="color:var(--muted)">${esc(t('created_sub'))}</p>
    <label class="modal-label">${esc(t('created_share_label'))}</label>
    <div style="display:flex;gap:8px">
      <input class="kg-input" style="flex:1" readonly value="${esc(shareUrl)}" data-field="share">
      <button class="btn-soft btn-press-sm" data-copy="${esc(shareUrl)}">🔗</button>
    </div>
    <label class="modal-label" style="margin-top:6px">${esc(t('created_manage_label'))}</label>
    <div style="display:flex;gap:8px">
      <input class="kg-input" style="flex:1" readonly value="${esc(manageUrl)}" data-field="manage">
      <button class="btn-soft btn-press-sm" data-copy="${esc(manageUrl)}">🔗</button>
    </div>
    <p style="font-size:0.82rem;color:var(--muted)">${esc(t('created_manage_hint'))}</p>
    <button class="cta-hero" style="width:100%" data-action="go">${esc(t('created_go'))}</button>`);
  card.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(btn.dataset.copy); showToast(t('copy_done'), 1400); } catch (_) {}
    });
  });
  card.querySelector('[data-action="go"]').addEventListener('click', () => {
    overlay.remove();
    goTo(`#/${slug}`);
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SCREEN 2 — Board
// ═══════════════════════════════════════════════════════════════════════════
async function renderBoard(root, slug) {
  root.innerHTML = `<div style="max-width:720px;margin:60px auto;text-align:center;color:var(--muted)" class="font-display">${esc(t('loading'))}</div>`;
  try {
    state.board = await api.get(`/api/v1/boards/${slug}`);
  } catch (e) {
    root.innerHTML = `
      <div style="max-width:520px;margin:80px auto;text-align:center;padding:0 6vw">
        <p class="font-display" style="font-size:1.2rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p>
        <button id="go-home" class="cta-hero" style="margin-top:20px">💌 ${esc(t('home_link'))}</button>
      </div>`;
    root.querySelector('#go-home').addEventListener('click', () => goTo(''));
    return;
  }
  state.seen = new Set(state.board.cards.map(c => c.id)); // no entrance anim on first paint
  paintBoard(root, slug, { animateNew: false });
  wsConnect(slug);
}

function wishHtml(c, isOrganizer, animate) {
  const media = c.image_path
    ? `<div class="wish-media"><img src="${esc(c.image_path)}" alt="" loading="lazy"></div>`
    : (c.gif_url ? `<div class="wish-media"><img src="${esc(c.gif_url)}" alt="" loading="lazy"></div>` : '');
  const tools = isOrganizer ? `
    <div class="wish-tools">
      <button class="wish-tool" data-pin="${c.id}">${c.pinned ? '📌 ' + esc(t('unpin_action')) : '📌 ' + esc(t('pin_action'))}</button>
      <button class="wish-tool" data-del-card="${c.id}">🗑 ${esc(t('delete_action'))}</button>
    </div>` : '';
  return `
    <div class="wish ${c.pinned ? 'pinned' : ''} ${animate ? 'enter' : ''}" data-card="${c.id}">
      ${c.pinned ? `<span class="pin-flag">📌 ${esc(t('pinned_flag'))}</span>` : ''}
      <div class="wish-author" style="margin-top:${c.pinned ? '8px' : '0'}">
        <span class="wish-avatar" style="${avatarStyle(c.author_name)}">${esc(initial(c.author_name))}</span>${esc(c.author_name)}
      </div>
      ${c.text ? `<p class="wish-text">${esc(c.text)}</p>` : ''}
      ${media}
      ${tools}
    </div>`;
}

function paintBoard(root, slug, opts = {}) {
  const animateNew = !!opts.animateNew;
  const b = state.board;
  const myName = getMyName(slug);
  const isOrganizer = !!getOrgToken(slug);
  const locked = b.locked;

  const cardsHtml = b.cards.length === 0
    ? `<div class="cozy-card" style="padding:32px;text-align:center;max-width:460px;margin:0 auto">
         <p class="font-display" style="font-weight:800;color:var(--ink);font-size:1.05rem">${esc(t('empty_title'))}</p>
         <p style="margin-top:8px;color:var(--muted)">${esc(t('empty_hint'))}</p>
       </div>`
    : `<div class="masonry">${b.cards.map(c => wishHtml(c, isOrganizer, animateNew && !state.seen.has(c.id))).join('')}</div>`;

  root.innerHTML = `
    <nav style="position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:12px 5vw;background:oklch(98% 0.018 75 / 0.92);backdrop-filter:blur(12px);border-bottom:2px solid var(--sand-deep)">
      <a class="font-display" style="display:inline-flex;align-items:center;gap:8px;font-size:0.95rem;color:var(--muted);text-decoration:none;font-weight:800" href="#">← ${esc(t('home_link'))}</a>
      <div style="display:flex;align-items:center;gap:10px">
        <span id="live-pip" class="live-pip"></span>
        ${mkLangSwitcher()}
      </div>
    </nav>

    <main style="max-width:1000px;margin:0 auto;padding:28px 6vw 100px">
      <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <span class="cover-badge">${esc(b.cover || '💌')}</span>
        <div style="flex:1;min-width:0">
          <h1 class="font-display title-clamp" style="font-weight:900;font-size:clamp(1.6rem,4vw,2.4rem);color:var(--ink);letter-spacing:-0.01em">${esc(b.title)}</h1>
          ${b.recipient ? `<p style="color:var(--muted);margin-top:2px;font-weight:600">${esc(t('for_word'))} <span style="color:var(--ink);font-weight:800">${esc(b.recipient)}</span></p>` : ''}
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:18px">
        <span class="font-display" style="font-size:0.8rem;color:var(--muted);font-weight:700;margin-right:2px">${esc(t('share_label'))}</span>
        <a class="share-btn" data-share="tg" target="_blank" rel="noopener">✈️ ${esc(t('share_tg'))}</a>
        <a class="share-btn" data-share="wa" target="_blank" rel="noopener">💬 ${esc(t('share_wa'))}</a>
        <a class="share-btn" data-share="vk" target="_blank" rel="noopener">🅥 ${esc(t('share_vk'))}</a>
        <button class="share-btn" data-copy-share="1">🔗 ${esc(t('copy_link'))}</button>
        <button class="share-btn" data-qr="1">▦ ${esc(t('qr_btn'))}</button>
      </div>

      <div style="display:flex;align-items:center;gap:8px;margin-top:12px;flex-wrap:wrap">
        <span class="font-display" style="font-size:0.85rem;color:var(--muted);font-weight:700">${esc(t('you_are'))}</span>
        ${myName ? `<span class="font-display" style="font-weight:800;color:var(--ink)">${esc(myName)}</span>` : ''}
        <button class="font-display" data-set-name="1" style="background:transparent;border:none;color:var(--coral);font-size:0.82rem;font-weight:800;cursor:pointer">${myName ? esc(t('change_name')) : esc(t('set_name'))}</button>
      </div>

      ${locked ? `
      <div class="locked-banner" style="margin-top:20px">
        <span style="font-size:1.4rem">🎀</span>
        <p class="font-display" style="font-weight:800;color:var(--ink)">${esc(t('locked_banner'))}</p>
      </div>` : `
      <div style="margin-top:22px">
        <button id="add-wish-btn" class="cta-hero" style="width:100%;max-width:340px">➕ ${esc(t('add_wish_btn'))}</button>
      </div>`}

      <div style="margin-top:26px">
        ${cardsHtml}
      </div>

      ${isOrganizer ? `
      <div style="margin-top:36px;display:flex;gap:10px;justify-content:center;flex-wrap:wrap">
        ${locked ? '' : `<button class="btn-soft btn-press-sm" data-lock="${b.id}">🔒 ${esc(t('lock_btn'))}</button>`}
        <button class="cta-hero" style="min-height:44px;padding:11px 20px" data-deliver="1">🎁 ${esc(t('deliver_btn'))}</button>
        <button class="font-display" data-del-board="${b.id}" style="background:transparent;border:none;color:var(--muted);font-size:0.8rem;font-weight:700;cursor:pointer">🗑 ${esc(t('delete_board'))}</button>
      </div>` : ''}
    </main>`;

  state.seen = new Set(b.cards.map(c => c.id));
  setLivePip(ws.socket && ws.socket.readyState === 1 ? 'connected' : 'reconnecting');
  wireBoard(root, slug);
}

function shareUrls(slug, recipient) {
  const url = `${location.origin}/#/${slug}`;
  const msg = recipient
    ? `${t('add_wish_btn')} · ${recipient}`
    : t('add_wish_btn');
  return {
    url,
    tg: `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(msg)}`,
    wa: `https://wa.me/?text=${encodeURIComponent(msg + ' ' + url)}`,
    vk: `https://vk.com/share.php?url=${encodeURIComponent(url)}`,
  };
}

function wireBoard(root, slug) {
  const b = state.board;
  const token = getOrgToken(slug);
  const su = shareUrls(slug, b.recipient);

  const tg = root.querySelector('[data-share="tg"]');
  const wa = root.querySelector('[data-share="wa"]');
  const vk = root.querySelector('[data-share="vk"]');
  if (tg) tg.href = su.tg;
  if (wa) wa.href = su.wa;
  if (vk) vk.href = su.vk;

  const copyBtn = root.querySelector('[data-copy-share]');
  if (copyBtn) copyBtn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(su.url); } catch (_) {}
    copyBtn.classList.add('copied');
    copyBtn.textContent = `✓ ${t('copy_done')}`;
    setTimeout(() => { copyBtn.classList.remove('copied'); copyBtn.innerHTML = `🔗 ${esc(t('copy_link'))}`; }, 1600);
  });

  const qrBtn = root.querySelector('[data-qr]');
  if (qrBtn) qrBtn.addEventListener('click', () => showQrModal(su.url));

  root.querySelectorAll('[data-set-name]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const name = await showNameModal(slug, getMyName(slug));
      if (name) paintBoard(root, slug);
    });
  });

  const addBtn = root.querySelector('#add-wish-btn');
  if (addBtn) addBtn.addEventListener('click', () => showAddWishModal(root, slug));

  root.querySelectorAll('[data-pin]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await api.post(`/api/v1/cards/${btn.dataset.pin}/pin`, { organizer_token: token });
        await refreshBoard(root, slug);
      } catch (e) { showToast(e.message); }
    });
  });

  root.querySelectorAll('[data-del-card]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm(t('confirm_delete_card'))) return;
      try {
        await api.del(`/api/v1/cards/${btn.dataset.delCard}`, { organizer_token: token });
        await refreshBoard(root, slug);
      } catch (e) { showToast(e.message); }
    });
  });

  root.querySelectorAll('[data-lock]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await api.patch(`/api/v1/boards/${btn.dataset.lock}/lock`, { organizer_token: token });
        await refreshBoard(root, slug);
      } catch (e) { showToast(e.message); }
    });
  });

  root.querySelectorAll('[data-deliver]').forEach(btn => {
    btn.addEventListener('click', () => goTo(`#/${slug}/deliver`));
  });

  root.querySelectorAll('[data-del-board]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm(t('confirm_delete_board'))) return;
      const boardId = btn.dataset.delBoard;
      try {
        await api.del(`/api/v1/boards/${boardId}`, { organizer_token: token });
        wsClose();
        goTo('');
        showUndoToast(t('board_deleted'), t('undo_btn'), async () => {
          try {
            await api.post(`/api/v1/boards/${boardId}/restore`, { organizer_token: token });
            goTo(`#/${slug}`);
          } catch (e) { showToast(e.message); }
        });
      } catch (e) { showToast(e.message); }
    });
  });
}

/** Refetch and repaint, animating any newly arrived cards. */
async function refreshBoard(root, slug) {
  try {
    state.board = await api.get(`/api/v1/boards/${slug}`);
    paintBoard(root, slug, { animateNew: true });
  } catch (e) {
    showToast(e.message);
  }
}

// ─── QR modal ────────────────────────────────────────────────────────────────
function showQrModal(url) {
  const { card } = openModal(`
    <h2 class="modal-title">${esc(t('qr_title'))}</h2>
    <div class="qr-box" id="qr-box"></div>
    <button class="btn-soft btn-press-sm" data-copy="${esc(url)}" style="width:100%">🔗 ${esc(t('copy_link'))}</button>`);
  const box = card.querySelector('#qr-box');
  if (typeof QRCode !== 'undefined') {
    try {
      new QRCode(box, { text: url, width: 220, height: 220, colorDark: '#33202b', colorLight: '#fdf6ee' });
    } catch (_) { box.textContent = url; }
  } else {
    box.innerHTML = `<span style="color:var(--muted);word-break:break-all">${esc(url)}</span>`;
  }
  card.querySelector('[data-copy]').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(url); showToast(t('copy_done'), 1400); } catch (_) {}
  });
}

// ─── Add-wish modal ──────────────────────────────────────────────────────────
function showAddWishModal(root, slug) {
  let picked = null; // { blob, filename }
  const preset = getMyName(slug);
  const { overlay, card } = openModal(`
    <h2 class="modal-title">💌 ${esc(t('add_modal_title'))}</h2>
    <div>
      <label class="modal-label">${esc(t('name_label'))}</label>
      <input class="kg-input" data-f="name" type="text" maxlength="48" placeholder="${esc(t('name_ph'))}" value="${esc(preset)}" autocomplete="nickname" style="margin-top:6px">
    </div>
    <div>
      <label class="modal-label">${esc(t('text_label'))}</label>
      <textarea class="kg-textarea" data-f="text" maxlength="2000" placeholder="${esc(t('text_ph'))}" style="margin-top:6px"></textarea>
    </div>
    <div>
      <label class="modal-label">${esc(t('photo_label'))}</label>
      <div class="drop-zone" data-f="drop" style="margin-top:6px">📷 ${esc(t('drop_hint'))}</div>
      <input type="file" accept="image/jpeg,image/png,image/webp" data-f="file" hidden>
      <div data-f="preview" style="margin-top:10px"></div>
    </div>
    <div>
      <label class="modal-label">${esc(t('gif_label'))}</label>
      <input class="kg-input" data-f="gif" type="url" maxlength="500" placeholder="${esc(t('gif_ph'))}" style="margin-top:6px">
      <p style="font-size:0.78rem;color:var(--muted);margin-top:4px">${esc(t('gif_hint'))}</p>
    </div>
    <div class="flex gap-2">
      <button class="flex-1 py-3 rounded-2xl border-2 font-body btn-press-sm" style="border-color:var(--sand-deep);color:var(--muted);font-weight:700" data-f="cancel">${esc(t('cancel_btn'))}</button>
      <button class="flex-1 py-3 rounded-2xl font-body btn-press" style="background:var(--coral-dark);color:var(--surface);font-weight:700" data-f="send">${esc(t('send_wish'))}</button>
    </div>`);

  const nameInput = card.querySelector('[data-f="name"]');
  const textInput = card.querySelector('[data-f="text"]');
  const gifInput = card.querySelector('[data-f="gif"]');
  const fileInput = card.querySelector('[data-f="file"]');
  const drop = card.querySelector('[data-f="drop"]');
  const preview = card.querySelector('[data-f="preview"]');
  const sendBtn = card.querySelector('[data-f="send"]');

  const showPreview = (blob) => {
    const url = URL.createObjectURL(blob);
    preview.innerHTML = `
      <div class="img-preview">
        <img src="${url}" alt="">
        <button class="img-remove" data-f="remove" aria-label="${esc(t('remove_photo'))}" title="${esc(t('remove_photo'))}">✕</button>
      </div>`;
    preview.querySelector('[data-f="remove"]').addEventListener('click', () => {
      picked = null; preview.innerHTML = ''; URL.revokeObjectURL(url);
    });
  };

  const handleFile = async (file) => {
    if (!file || !/^image\/(jpeg|png|webp)$/.test(file.type)) return;
    try {
      picked = await resizeImage(file);
      showPreview(picked.blob);
    } catch (_) { showToast(t('err_generic')); }
  };

  drop.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));
  ['dragover', 'dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('drag'); }));
  drop.addEventListener('drop', e => { if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });

  setTimeout(() => (preset ? textInput : nameInput).focus(), 30);

  card.querySelector('[data-f="cancel"]').addEventListener('click', () => overlay.remove());

  sendBtn.addEventListener('click', async () => {
    const name = nameInput.value.trim();
    if (!name) { nameInput.focus(); return; }
    const text = textInput.value.trim();
    const gif = gifInput.value.trim();
    if (!text && !gif && !picked) { showToast(t('err_need_something')); return; }
    sendBtn.disabled = true;
    sendBtn.textContent = t('uploading');
    try {
      setMyName(slug, name);
      let imagePath = null;
      if (picked) imagePath = await uploadImage(slug, picked.blob, picked.filename);
      await api.post(`/api/v1/boards/${slug}/cards`, {
        author_name: name,
        text: text || null,
        gif_url: gif || null,
        image_path: imagePath,
      });
      overlay.remove();
      await refreshBoard(root, slug);
    } catch (e) {
      showToast(e.message);
      sendBtn.disabled = false;
      sendBtn.textContent = t('send_wish');
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SCREEN 3 — Delivery (read-only, confetti)
// ═══════════════════════════════════════════════════════════════════════════
async function renderDeliver(root, slug) {
  root.innerHTML = `<div style="max-width:720px;margin:60px auto;text-align:center;color:var(--muted)" class="font-display">${esc(t('loading'))}</div>`;
  let b;
  try {
    b = await api.get(`/api/v1/boards/${slug}`);
  } catch (e) {
    root.innerHTML = `
      <div style="max-width:520px;margin:80px auto;text-align:center;padding:0 6vw">
        <p class="font-display" style="font-size:1.2rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p>
        <button id="go-home" class="cta-hero" style="margin-top:20px">💌 ${esc(t('home_link'))}</button>
      </div>`;
    root.querySelector('#go-home').addEventListener('click', () => goTo(''));
    return;
  }

  root.innerHTML = `
    <main class="hero-blobs" style="max-width:1000px;margin:0 auto;padding:40px 6vw 90px">
      <div style="text-align:center;max-width:640px;margin:0 auto">
        <div class="hero-reveal-1"><span class="cover-badge big">${esc(b.cover || '💌')}</span></div>
        ${b.recipient ? `<p class="hero-reveal-2 font-display" style="color:var(--coral);font-weight:800;margin-top:14px;font-size:1.05rem">${esc(t('deliver_intro'))} ${esc(b.recipient)}</p>` : ''}
        <h1 class="hero-reveal-2 font-display" style="font-weight:900;font-size:clamp(1.9rem,5vw,3rem);color:var(--ink);letter-spacing:-0.02em;margin-top:6px">${esc(b.title)}</h1>
        <p class="hero-reveal-3" style="color:var(--muted);margin-top:10px">${esc(t('wishes_count', { n: b.cards.length }))}</p>
      </div>

      <div class="hero-reveal-4" style="margin-top:32px">
        ${b.cards.length === 0
          ? `<p style="text-align:center;color:var(--muted)">${esc(t('empty_hint'))}</p>`
          : `<div class="masonry">${b.cards.map(c => wishHtml(c, false, false)).join('')}</div>`}
      </div>

      <div style="text-align:center;margin-top:36px">
        <a class="font-display" href="#/${esc(slug)}" style="color:var(--muted);font-weight:700;font-size:0.85rem;text-decoration:none">← ${esc(t('back_to_board'))}</a>
      </div>
    </main>`;

  fireConfetti();
}

// ─── Global lang toggle (delegated) ──────────────────────────────────────────
document.getElementById('app').addEventListener('click', e => {
  const btn = e.target.closest('[data-lang]');
  if (!btn) return;
  state.lang = btn.dataset.lang;
  localStorage.setItem('otkrytka_lang', state.lang);
  render();
});

// ─── Init ────────────────────────────────────────────────────────────────────
function init() {
  document.documentElement.lang = state.lang;
  render();
  window.addEventListener('hashchange', () => {
    wsClose();
    state.board = null;
    render();
  });
}

init();
