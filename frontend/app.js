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
    embed_btn: "Embed",
    embed_open: "Open the card",
    embed_modal_title: "Embed this card",
    embed_hint: "Paste this into a blog, a tribute page or Notion. It stays read only and updates live.",
    embed_copy: "Copy embed code",
    embed_copied: "Embed code copied",
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
    unlock_btn: "Reopen card",
    locked_banner: "The card is closed and ready to deliver.",
    deliver_btn: "Deliver",
    delete_board: "Delete this card",
    board_deleted: "Card deleted.",
    undo_btn: "Undo",
    del_confirm_btn: "Delete",
    confirm_title: "Are you sure?",
    wishes_count_one: "{n} wish",
    wishes_count_other: "{n} wishes",

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
    download_pdf: "Print / Save as PDF",

    // Occasion preset / scheduled reveal / corp-brand
    occasion_label: "Card type",
    occasion_birthday: "Birthday",
    occasion_farewell: "Farewell",
    occasion_teacher: "For a teacher",
    occasion_retirement: "Retirement",
    occasion_thanks: "Thank you",
    reveal_at_label: "Reveal wishes at (optional)",
    reveal_hint: "Until then guests add wishes but cannot see them. You can reveal earlier.",
    reveal_btn: "Reveal wishes now",
    gated_title: "Wishes are hidden for now",
    gated_hint: "Add your wish — everything opens at the chosen moment.",
    gated_hidden: "hidden until reveal",
    brand_color_label: "Brand color (optional)",
    wish_prompt_farewell: "Write a wish for your departing colleague…",
    wish_prompt_teacher: "Write a thank-you to your teacher…",
    wish_prompt_retirement: "Wish them a happy retirement…",
    wish_prompt_thanks: "Write your words of thanks…",

    // Status / live / errors
    ws_live: "Live",
    ws_reconnecting: "Reconnecting…",
    loading: "Loading…",
    err_not_found: "Card not found.",
    err_generic: "Something went wrong.",
    confirm_delete_board: "Hide this card from everyone? You can restore it right after.",
    confirm_delete_card: "Remove this wish and its photo? You cannot undo this.",

    // Inline validation + upload feedback
    err_name_required: "Add your name first.",
    processing: "Processing…",
    err_img_type: "Only JPG, PNG or WEBP.",
    err_img_size: "That image is too large (max {n} MB).",
    img_alt: "Photo from {author}",
    img_preview_alt: "Photo preview",

    // Organizer-link recovery
    created_only_way: "Save this private link now. It is the ONLY way to manage this card. Lose it and you cannot pin, close or deliver.",
    copy_btn: "Copy",
    save_file: "Save as file",
    created_ack: "I saved my organizer link somewhere safe.",
    org_file_intro: "Your PRIVATE organizer link for the card \"{title}\". Keep it secret: anyone with this link can pin, close, deliver or delete the card. Bookmark it or store it in your password manager.",
    org_banner_text: "You are the only organizer. Save your private link so you never lose access.",
    org_banner_save: "Save link",
    import_link_cta: "I have an organizer link",
    import_title: "Restore organizer access",
    import_hint: "Paste your private organizer link (or its token) to manage its card on this device.",
    import_ph: "Paste the organizer link…",
    import_go: "Restore access",
    import_bad: "That does not look like a valid organizer link.",
    import_done: "Organizer access restored.",

    // Backend error codes -> localized inline messages
    err_codes: {
      author_required: "Please add your name.",
      board_full: "This card is full, so no more wishes can be added.",
      board_locked: "This card is closed and no longer accepts wishes.",
      board_not_found: "Card not found.",
      card_not_found: "That wish no longer exists.",
      content_required: "Add some words, a photo or a GIF.",
      gif_url_invalid: "That GIF link is not valid.",
      gif_url_not_image: "That link is not a direct image or GIF.",
      image_ref_invalid: "That image could not be attached.",
      image_too_large: "That image is too large.",
      image_unsupported_type: "Only JPG, PNG or WEBP images are allowed.",
      image_wrong_board: "That image belongs to a different card.",
      organizer_token_required: "Only the organizer can do that.",
      slug_unavailable: "That card code is taken. Please try again.",
      upload_limit: "Upload limit reached. Please try again later.",
      request_too_large: "That request is too large.",
    },
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
    embed_btn: "Встроить",
    embed_open: "Открыть открытку",
    embed_modal_title: "Встроить эту открытку",
    embed_hint: "Вставьте этот код в блог, страницу памяти или Notion. Открытка остаётся только для чтения и обновляется вживую.",
    embed_copy: "Копировать код",
    embed_copied: "Код скопирован",
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
    unlock_btn: "Открыть заново",
    locked_banner: "Открытка закрыта и готова к вручению.",
    deliver_btn: "Подарить",
    delete_board: "Удалить открытку",
    board_deleted: "Открытка удалена.",
    undo_btn: "Отменить",
    del_confirm_btn: "Удалить",
    confirm_title: "Вы уверены?",
    wishes_count_one: "{n} пожелание",
    wishes_count_few: "{n} пожелания",
    wishes_count_many: "{n} пожеланий",

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
    download_pdf: "Печать / Сохранить в PDF",

    // Повод / отложенное открытие / фирменный стиль
    occasion_label: "Тип открытки",
    occasion_birthday: "День рождения",
    occasion_farewell: "Проводы коллеги",
    occasion_teacher: "Учителю",
    occasion_retirement: "На пенсию",
    occasion_thanks: "Благодарность",
    reveal_at_label: "Открыть пожелания (по желанию)",
    reveal_hint: "До этого момента гости добавляют пожелания, но не видят их. Вы можете открыть раньше.",
    reveal_btn: "Открыть пожелания сейчас",
    gated_title: "Пожелания пока скрыты",
    gated_hint: "Добавьте своё пожелание — все откроются в назначенный момент.",
    gated_hidden: "скрыто до открытия",
    brand_color_label: "Цвет бренда (по желанию)",
    wish_prompt_farewell: "Напишите пожелание уходящему коллеге…",
    wish_prompt_teacher: "Напишите слова благодарности учителю…",
    wish_prompt_retirement: "Пожелайте счастливых лет на пенсии…",
    wish_prompt_thanks: "Напишите слова благодарности…",

    // Status / live / errors
    ws_live: "Вживую",
    ws_reconnecting: "Переподключение…",
    loading: "Загрузка…",
    err_not_found: "Открытка не найдена.",
    err_generic: "Что-то пошло не так.",
    confirm_delete_board: "Скрыть открытку от всех? Сразу после этого её можно вернуть.",
    confirm_delete_card: "Убрать это пожелание вместе с фото? Отменить это нельзя.",

    // Inline validation + upload feedback
    err_name_required: "Сначала укажите имя.",
    processing: "Обрабатываем…",
    err_img_type: "Только JPG, PNG или WEBP.",
    err_img_size: "Файл слишком большой (макс. {n} МБ).",
    img_alt: "Фото от {author}",
    img_preview_alt: "Предпросмотр фото",

    // Organizer-link recovery
    created_only_way: "Сохраните эту личную ссылку сейчас. Это единственный способ управлять открыткой. Без неё вы не сможете закреплять, закрывать и вручать.",
    copy_btn: "Копировать",
    save_file: "Сохранить файлом",
    created_ack: "Я сохранил(а) ссылку организатора в надёжном месте.",
    org_file_intro: "Ваша ЛИЧНАЯ ссылка организатора для открытки «{title}». Держите её в секрете: любой, у кого есть эта ссылка, сможет закреплять, закрывать, вручать и удалять открытку. Добавьте её в закладки или сохраните в менеджере паролей.",
    org_banner_text: "Вы единственный организатор. Сохраните личную ссылку, чтобы не потерять доступ.",
    org_banner_save: "Сохранить ссылку",
    import_link_cta: "У меня есть ссылка организатора",
    import_title: "Восстановить доступ организатора",
    import_hint: "Вставьте личную ссылку организатора (или её токен), чтобы управлять открыткой на этом устройстве.",
    import_ph: "Вставьте ссылку организатора…",
    import_go: "Восстановить доступ",
    import_bad: "Это не похоже на действительную ссылку организатора.",
    import_done: "Доступ организатора восстановлен.",

    // Backend error codes -> localized inline messages
    err_codes: {
      author_required: "Пожалуйста, укажите имя.",
      board_full: "Открытка заполнена, добавить пожелание больше нельзя.",
      board_locked: "Открытка закрыта и больше не принимает пожелания.",
      board_not_found: "Открытка не найдена.",
      card_not_found: "Этого пожелания больше нет.",
      content_required: "Добавьте слова, фото или GIF.",
      gif_url_invalid: "Ссылка на GIF недействительна.",
      gif_url_not_image: "Эта ссылка не ведёт на картинку или GIF.",
      image_ref_invalid: "Не удалось прикрепить это изображение.",
      image_too_large: "Изображение слишком большое.",
      image_unsupported_type: "Разрешены только изображения JPG, PNG или WEBP.",
      image_wrong_board: "Это изображение принадлежит другой открытке.",
      organizer_token_required: "Это может сделать только организатор.",
      slug_unavailable: "Такой код открытки занят. Попробуйте ещё раз.",
      upload_limit: "Достигнут лимит загрузок. Попробуйте позже.",
      request_too_large: "Слишком большой запрос.",
    },
  },
};

const MAX_UPLOAD_MB = 3; // matches backend max_upload_mb (config.py); checked on the POST-RESIZE bytes

const COVERS = ['🎂', '🎉', '💐', '🌸', '❤️', '🎁', '✨', '🥳', '🌟', '🎈'];

// Occasion presets — must mirror the backend Literal (schemas/board.py).
const OCCASIONS = ['birthday', 'farewell', 'teacher', 'retirement', 'thanks'];

/** Guest wish placeholder for the occasion; birthday/null keeps the original. */
function occasionWishPrompt(occasion) {
  const dict = STR[state.lang] || STR.en;
  const key = `wish_prompt_${occasion || 'birthday'}`;
  return dict[key] !== undefined ? t(key) : t('text_ph');
}

/** Only ever inject a strict #RRGGBB into a style attribute (defense in depth —
 *  the server already validates, but never trust a value flowing into markup). */
function safeHex(v) {
  return (typeof v === 'string' && /^#[0-9a-fA-F]{6}$/.test(v)) ? v : null;
}

/** Localized human-readable reveal moment for the gate banner. */
function fmtRevealAt(iso) {
  try {
    return new Date(iso).toLocaleString(state.lang === 'ru' ? 'ru-RU' : 'en-US',
      { dateStyle: 'medium', timeStyle: 'short' });
  } catch (_) { return iso; }
}

// ─── State ─────────────────────────────────────────────────────────────────
const state = {
  lang: (() => {
    let s = null;
    try { s = localStorage.getItem('otkrytka_lang'); } catch (_) {}
    if (s) return s;
    return (navigator.language || '').toLowerCase().startsWith('ru') ? 'ru' : 'en';
  })(),
  slug: '',
  board: null,
  embed: false, // read-only embedded card (/embed/{slug}); no organizer access
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
    const board = await fetchBoard(slug);
    state.board = board;
    const scrollY = window.scrollY;
    const paint = state.embed ? paintEmbed : paintBoard;
    paint(document.getElementById('app'), slug, { animateNew: true });
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

/** Grammatically correct "{n} wishes" for RU (one/few/many) and EN (one/other).
 *  RU uses the standard Slavic plural rule: 1/21/31 -> one (пожелание),
 *  2..4/22..24 -> few (пожелания), 0/5..20/25.. -> many (пожеланий). */
function pluralWishes(n) {
  n = Math.abs(Number(n) || 0);
  let key;
  if (state.lang === 'ru') {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) key = 'wishes_count_one';
    else if (mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)) key = 'wishes_count_few';
    else key = 'wishes_count_many';
  } else {
    key = n === 1 ? 'wishes_count_one' : 'wishes_count_other';
  }
  return t(key, { n });
}

// ─── API helpers ─────────────────────────────────────────────────────────────
/** Turn a FastAPI error body into a localized message. Handles the stable
 *  contract `{detail:{code,message}}`, a pydantic 422 `{detail:[...]}` list,
 *  a plain string detail, and a missing detail — never surfaces `[object
 *  Object]` or `undefined`. Returns { message, code }. */
function localizeApiError(json) {
  const d = json ? json.detail : undefined;
  if (d && typeof d === 'object' && !Array.isArray(d)) {
    if (d.code) {
      const table = (STR[state.lang] && STR[state.lang].err_codes) || {};
      const enTable = STR.en.err_codes || {};
      const msg = table[d.code] || enTable[d.code] || d.message || t('err_generic');
      return { message: msg, code: d.code };
    }
    return { message: (typeof d.message === 'string' && d.message) || t('err_generic'), code: null };
  }
  if (Array.isArray(d)) {
    const first = d[0];
    const msg = (first && typeof first.msg === 'string') ? first.msg : t('err_generic');
    return { message: msg, code: null };
  }
  if (typeof d === 'string' && d) return { message: d, code: null };
  return { message: t('err_generic'), code: null };
}

function apiError(json) {
  const { message, code } = localizeApiError(json);
  const err = new Error(message);
  err.code = code;
  return err;
}

async function apiCall(method, path, body, extraHeaders) {
  const opts = { method, headers: { ...(extraHeaders || {}) } };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  if (res.status === 204) return null;
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw apiError(json);
  return json;
}

const api = {
  get: (p) => apiCall('GET', p),
  post: (p, b) => apiCall('POST', p, b),
  patch: (p, b) => apiCall('PATCH', p, b),
  del: (p, b) => apiCall('DELETE', p, b),
};

/** GET a board, presenting the organizer token (when this device holds it) so a
 *  not-yet-revealed board's wishes are previewed. The token rides in a header,
 *  never the URL, so it stays out of server access logs. */
function fetchBoard(slug) {
  const token = getOrgToken(slug);
  return apiCall('GET', `/api/v1/boards/${slug}`, undefined,
    token ? { 'X-Organizer-Token': token } : undefined);
}

async function uploadImage(slug, blob, filename) {
  const fd = new FormData();
  fd.append('file', blob, filename);
  const res = await fetch(`/api/v1/boards/${slug}/upload`, { method: 'POST', body: fd });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw apiError(json);
  return json.image_path;
}

// ─── Local storage helpers (safe: private mode / disabled storage must not break) ─
function lsGet(key) {
  try { return localStorage.getItem(key); } catch (_) { return null; }
}
function lsSet(key, val) {
  try { localStorage.setItem(key, val); return true; } catch (_) { return false; }
}
function lsRemove(key) {
  try { localStorage.removeItem(key); } catch (_) {}
}

function getMyName(slug) { return lsGet(`otkrytka_me_${slug}`) || ''; }
function setMyName(slug, name) { lsSet(`otkrytka_me_${slug}`, name); }
function getOrgToken(slug) { return lsGet(`otkrytka_org_${slug}`) || ''; }
function setOrgToken(slug, token) { lsSet(`otkrytka_org_${slug}`, token); }

// Canonical origin — server injects window.__CANONICAL__ on /c/{slug} & /embed/{slug};
// fall back to the current origin for the bare hash routes and the static landing.
function canonicalOrigin() { return window.__CANONICAL__ || location.origin; }

function orgBannerDismissed(slug) { return lsGet(`otkrytka_orgbanner_${slug}`) === '1'; }
function dismissOrgBanner(slug) { lsSet(`otkrytka_orgbanner_${slug}`, '1'); }

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

// ─── Single-modal manager ────────────────────────────────────────────────────
// Invariant: at most ONE modal exists in the DOM at any moment. openModal() first
// tears down any live modal (and its Escape listener) before mounting a new one,
// so a second open can never stack a second .modal-card. Modal state is NEVER
// persisted, so a reload starts with no modal (see clearAllModals() in init()).
let _activeModal = null;
let _modalSeq = 0;

function clearAllModals() {
  // Capture + detach the active modal first, so settling its promise cannot
  // re-enter this teardown.
  const prev = _activeModal;
  _activeModal = null;
  if (prev && prev.onKey) document.removeEventListener('keydown', prev.onKey);
  // Settle the pending caller promise (resolve null) BEFORE ripping the DOM out,
  // so a 2nd openModal firing before the 1st settled never leaves an `await` hung.
  // The caller's resolver is idempotent, so a later real resolve still wins.
  if (prev && prev.onDismiss) { try { prev.onDismiss(); } catch (_) {} }
  // Defensive: remove every overlay in the DOM (guarantees .modal-card count 0),
  // not just the tracked one, in case anything ever slipped past the manager.
  document.querySelectorAll('.modal-overlay').forEach(o => o.remove());
}

function openModal(innerHtml, opts) {
  clearAllModals(); // enforce the single-modal invariant before mounting
  const onDismiss = (opts && opts.onDismiss) || null;
  const id = ++_modalSeq;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  const card = document.createElement('div');
  card.className = 'modal-card';
  card.innerHTML = innerHtml;
  overlay.appendChild(card);
  document.body.appendChild(overlay);
  // Identity-scoped close: only tears down if THIS modal is still the active one,
  // so a stale close() from an older caller can never nuke a newer modal.
  const close = () => { if (_activeModal && _activeModal.id === id) clearAllModals(); };
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  const onKey = e => { if (e.key === 'Escape') close(); };
  document.addEventListener('keydown', onKey);
  _activeModal = { id, overlay, card, close, onKey, onDismiss };
  return { overlay, card, close };
}

// ─── Confirm modal (styled replacement for native window.confirm) ────────────
// Resolves true if the user confirms, false on cancel / dismiss / Escape. Uses
// the same single-modal manager as every other dialog so all confirmations share
// one consistent, localized look instead of the browser's native confirm().
function showConfirmModal(message, opts) {
  const o = opts || {};
  const confirmLabel = o.confirmLabel || t('del_confirm_btn');
  return new Promise(resolve => {
    let settled = false;
    const finish = (val) => { if (!settled) { settled = true; resolve(val); } };
    const { card, close } = openModal(`
      <h2 class="modal-title">${esc(o.title || t('confirm_title'))}</h2>
      <p style="color:var(--muted);margin:0 0 4px;line-height:1.5">${esc(message)}</p>
      <div class="flex gap-2" style="margin-top:18px">
        <button class="flex-1 py-3 rounded-2xl border-2 font-body btn-press-sm" style="border-color:var(--sand-deep);color:var(--muted);font-weight:700" data-action="cancel">${esc(t('cancel_btn'))}</button>
        <button class="flex-1 py-3 rounded-2xl font-body btn-press" style="background:var(--coral-dark);color:var(--surface);font-weight:700" data-action="confirm">${esc(confirmLabel)}</button>
      </div>`, { onDismiss: () => finish(false) });
    const doConfirm = () => { finish(true); close(); };
    const doCancel = () => { finish(false); close(); };
    card.querySelector('[data-action="confirm"]').addEventListener('click', doConfirm);
    card.querySelector('[data-action="cancel"]').addEventListener('click', doCancel);
    setTimeout(() => { try { card.querySelector('[data-action="confirm"]').focus(); } catch (_) {} }, 30);
  });
}

// ─── Name modal (set/change the signer name for this card) ───────────────────
function showNameModal(slug, current) {
  return new Promise(resolve => {
    let settled = false;
    const finish = (val) => { if (!settled) { settled = true; resolve(val); } };
    const { card, close } = openModal(`
      <h2 class="modal-title">${esc(t('name_modal_title'))}</h2>
      <input class="kg-input" type="text" placeholder="${esc(t('name_ph'))}" maxlength="48" value="${esc(current || '')}" autocomplete="nickname">
      <p class="field-err" data-f="err" hidden></p>
      <div class="flex gap-2">
        <button class="flex-1 py-3 rounded-2xl border-2 font-body btn-press-sm" style="border-color:var(--sand-deep);color:var(--muted);font-weight:700" data-action="cancel">${esc(t('cancel_btn'))}</button>
        <button class="flex-1 py-3 rounded-2xl font-body btn-press" style="background:var(--coral-dark);color:var(--surface);font-weight:700" data-action="save">${esc(t('name_save'))}</button>
      </div>`, { onDismiss: () => finish(null) });
    const input = card.querySelector('input');
    const err = card.querySelector('[data-f="err"]');
    setTimeout(() => input.focus(), 30);
    const doSave = () => {
      const name = input.value.trim();
      if (!name) { showFieldError(err, input, t('err_name_required')); return; }
      setMyName(slug, name);
      finish(name); // resolve BEFORE teardown; the onDismiss finish(null) is then a no-op
      close();
    };
    const doCancel = () => { finish(null); close(); };
    card.querySelector('[data-action="save"]').addEventListener('click', doSave);
    card.querySelector('[data-action="cancel"]').addEventListener('click', doCancel);
    input.addEventListener('input', () => clearFieldError(err, input));
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') doSave();
      if (e.key === 'Escape') doCancel();
    });
  });
}

// ─── Inline field-error helpers (message shown next to the field, not a toast) ─
function showFieldError(errEl, fieldEl, msg) {
  if (errEl) { errEl.textContent = '⚠ ' + msg; errEl.hidden = false; }
  if (fieldEl) {
    fieldEl.classList.add('invalid');
    try { fieldEl.focus(); } catch (_) {}
  }
}
function clearFieldError(errEl, fieldEl) {
  if (errEl) { errEl.textContent = ''; errEl.hidden = true; }
  if (fieldEl) fieldEl.classList.remove('invalid');
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
/** Parse the route. The hash forms — `#/slug`, `#/slug/k/<token>`,
 *  `#/slug/deliver` — take precedence (organizer + deliver deep links keep
 *  working). Otherwise the real guest path `/c/{slug}` renders the board so a
 *  shared, crawler-visible link opens the card directly. */
function parseRoute() {
  const raw = location.hash.replace(/^#\/?/, '').trim();
  if (raw) {
    const parts = raw.split('/');
    const slug = parts[0].toLowerCase();
    if (parts[1] === 'k' && parts[2]) return { view: 'manage', slug, token: parts[2] };
    if (parts[1] === 'deliver') return { view: 'deliver', slug };
    return { view: 'board', slug };
  }
  const em = location.pathname.match(/^\/embed\/([a-z0-9]+)\/?$/i);
  if (em) return { view: 'embed', slug: em[1].toLowerCase() };
  const m = location.pathname.match(/^\/c\/([a-z0-9]+)\/?$/i);
  if (m) return { view: 'board', slug: m[1].toLowerCase() };
  // Root path -> home. Any OTHER non-root pathname that reached the SPA (served
  // index.html by the backend catch-all, e.g. /totally-bogus) is an unknown
  // route -> render the localized not-found instead of silently showing home.
  if (location.pathname === '/' || location.pathname === '') return { view: 'landing' };
  return { view: 'notfound' };
}
function goTo(hash) { location.hash = hash; }
/** Navigate to the landing at the real root, clearing any `/c/{slug}` path. */
function goHome() {
  wsClose();
  state.board = null;
  history.pushState(null, '', '/');
  render();
}

async function render() {
  document.documentElement.lang = state.lang;
  document.title = t('doc_title'); // keep the browser tab title in sync with the UI language
  const route = parseRoute();
  const root = document.getElementById('app');

  if (route.view === 'manage') {
    // Adopt the organizer token for this browser, then drop it from the URL.
    setOrgToken(route.slug, route.token);
    location.replace(`/#/${route.slug}`);
    return;
  }
  state.embed = route.view === 'embed';
  if (route.view === 'notfound') {
    state.slug = '';
    renderNotFound(root);
  } else if (route.view === 'landing') {
    state.slug = '';
    renderLanding(root);
  } else if (route.view === 'deliver') {
    state.slug = route.slug;
    await renderDeliver(root, route.slug);
  } else if (route.view === 'embed') {
    state.slug = route.slug;
    await renderEmbed(root, route.slug);
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
      <a class="font-display" style="display:inline-flex;align-items:center;gap:8px;font-size:1.3rem;color:var(--ink);text-decoration:none;font-weight:900" href="/" data-home="1">
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
        <label class="modal-label" style="display:block;margin:14px 0 8px">${esc(t('occasion_label'))}</label>
        <select id="create-occasion" class="kg-input">
          ${OCCASIONS.map(o => `<option value="${esc(o)}">${esc(t('occasion_' + o))}</option>`).join('')}
        </select>
        <label class="modal-label" style="display:block;margin:14px 0 8px">${esc(t('reveal_at_label'))}</label>
        <input id="create-reveal" class="kg-input" type="datetime-local">
        <p style="color:var(--muted);font-size:0.8rem;margin-top:6px">${esc(t('reveal_hint'))}</p>
        <label class="modal-label" style="display:block;margin:14px 0 8px">${esc(t('brand_color_label'))}</label>
        <div style="display:flex;align-items:center;gap:10px">
          <input id="brand-toggle" type="checkbox">
          <input id="create-brand" type="color" value="#c93b57" disabled style="width:46px;height:34px;border:none;background:transparent;cursor:pointer">
        </div>
        <button id="create-btn" class="cta-hero" style="width:100%;margin-top:18px">💌 ${esc(t('create_btn'))}</button>

        <div class="ornament-rule gold" style="margin:20px 0"><span>${esc(t('or_label'))}</span></div>
        <label class="modal-label" style="display:block;margin-bottom:8px">${esc(t('join_label'))}</label>
        <div style="display:flex;gap:10px;flex-wrap:wrap">
          <input id="join-input" class="kg-input" style="flex:1;min-width:160px" type="text" maxlength="7" placeholder="${esc(t('join_ph'))}">
          <button id="join-btn" class="btn-soft btn-press-sm">${esc(t('join_go'))}</button>
        </div>
        <div style="text-align:center;margin-top:16px">
          <button id="import-org" class="font-display" style="background:transparent;border:none;color:var(--gold-deep);font-weight:800;font-size:0.82rem;cursor:pointer;text-decoration:underline">🔑 ${esc(t('import_link_cta'))}</button>
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

  const brandToggle = root.querySelector('#brand-toggle');
  brandToggle.addEventListener('change', () => {
    root.querySelector('#create-brand').disabled = !brandToggle.checked;
  });

  const titleInput = root.querySelector('#create-title');
  const doCreate = async () => {
    const title = titleInput.value.trim();
    if (!title) { titleInput.focus(); return; }
    const recipient = root.querySelector('#create-recipient').value.trim() || null;
    const body = { title, recipient, cover };
    // Occasion 'birthday' is the default -> omit it so a plain card stays null
    // (backward-compatible). A datetime-local value is local time; convert to a
    // UTC ISO string so the server-side gate compares in one canonical zone.
    const occasion = root.querySelector('#create-occasion').value;
    if (occasion && occasion !== 'birthday') body.occasion = occasion;
    const revealRaw = root.querySelector('#create-reveal').value;
    if (revealRaw) body.reveal_at = new Date(revealRaw).toISOString();
    if (brandToggle.checked) body.brand_color = root.querySelector('#create-brand').value;
    try {
      const out = await api.post('/api/v1/boards', body);
      setOrgToken(out.slug, out.organizer_token);
      showCreatedModal(out.slug, out.organizer_token, title);
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

  root.querySelector('#import-org').addEventListener('click', () => showImportModal());
}

/** Build the private organizer (manage) URL. Kept as a hash route so the secret
 *  token never lands in a server request path, access log or crawler fetch. */
function manageUrlFor(slug, token) { return `${canonicalOrigin()}/#/${slug}/k/${token}`; }
/** Guest link = real path so crawlers unfurl the per-board preview. */
function guestUrlFor(slug) { return `${canonicalOrigin()}/c/${slug}`; }

/** Trigger a client-side download of the organizer link as a plain .txt file so
 *  the user can save it off-device (no backend involvement). */
function downloadOrganizerLink(slug, manageUrl, title) {
  const intro = t('org_file_intro', { title: title || slug });
  const body = `${intro}\n\n${manageUrl}\n`;
  try {
    const blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `otkrytka-organizer-${slug}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (_) { showToast(t('err_generic')); }
}

async function copyToClipboard(text) {
  try { await navigator.clipboard.writeText(text); showToast(t('copy_done'), 1400); return true; }
  catch (_) { return false; }
}

// ─── Created modal (organizer link surfaced + forced acknowledgment) ──────────
function showCreatedModal(slug, token, boardTitle) {
  const shareUrl = guestUrlFor(slug);
  const manageUrl = manageUrlFor(slug, token);
  const title = boardTitle || (state.board ? state.board.title : '');
  const { card, close } = openModal(`
    <h2 class="modal-title">🎉 ${esc(t('created_title'))}</h2>
    <p style="color:var(--muted)">${esc(t('created_sub'))}</p>
    <label class="modal-label">${esc(t('created_share_label'))}</label>
    <div style="display:flex;gap:8px">
      <input class="kg-input" style="flex:1" readonly value="${esc(shareUrl)}" data-field="share">
      <button class="btn-soft btn-press-sm" data-copy="${esc(shareUrl)}" aria-label="${esc(t('copy_link'))}" title="${esc(t('copy_link'))}">🔗</button>
    </div>

    <label class="modal-label" style="margin-top:6px">${esc(t('created_manage_label'))}</label>
    <div class="manage-callout"><span aria-hidden="true">🔑</span><span>${esc(t('created_only_way'))}</span></div>
    <div style="display:flex;gap:8px;margin-top:8px">
      <input class="kg-input" style="flex:1" readonly value="${esc(manageUrl)}" data-field="manage">
    </div>
    <div class="link-actions">
      <button class="org-mini-btn" data-copy="${esc(manageUrl)}">🔗 ${esc(t('copy_btn'))}</button>
      <button class="org-mini-btn" data-f="dl">💾 ${esc(t('save_file'))}</button>
      <button class="org-mini-btn" data-f="qr">▦ ${esc(t('qr_btn'))}</button>
    </div>
    <div class="qr-inline" data-f="qrbox" hidden></div>

    <label class="ack-row">
      <input type="checkbox" data-f="ack">
      <span>${esc(t('created_ack'))}</span>
    </label>
    <button class="cta-hero" style="width:100%" data-action="go" disabled>${esc(t('created_go'))}</button>`);

  card.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', () => copyToClipboard(btn.dataset.copy));
  });
  card.querySelector('[data-f="dl"]').addEventListener('click', () => downloadOrganizerLink(slug, manageUrl, title));

  const qrBox = card.querySelector('[data-f="qrbox"]');
  card.querySelector('[data-f="qr"]').addEventListener('click', () => {
    if (!qrBox.hidden) { qrBox.hidden = true; return; }
    if (!qrBox.dataset.rendered) {
      renderQrInto(qrBox, manageUrl, 180);
      qrBox.dataset.rendered = '1';
    }
    qrBox.hidden = false;
  });

  const ack = card.querySelector('[data-f="ack"]');
  const goBtn = card.querySelector('[data-action="go"]');
  ack.addEventListener('change', () => { goBtn.disabled = !ack.checked; });
  goBtn.addEventListener('click', () => {
    if (!ack.checked) return;
    close();
    goTo(`#/${slug}`);
  });
}

// ─── Import organizer link (restore access on a new device) ──────────────────
/** Extract {slug, token} from a pasted organizer link or a raw token. Accepts a
 *  full URL, a `#/slug/k/token` fragment, or (with a known slug) a bare token. */
function parseOrganizerLink(raw, knownSlug) {
  const s = String(raw || '').trim();
  if (!s) return null;
  const m = s.match(/#\/?([a-z0-9]+)\/k\/([^/\s#?]+)/i);
  if (m) return { slug: m[1].toLowerCase(), token: m[2] };
  if (knownSlug && /^[A-Za-z0-9._-]+$/.test(s)) return { slug: knownSlug.toLowerCase(), token: s };
  return null;
}

function showImportModal(knownSlug) {
  const { card, close } = openModal(`
    <h2 class="modal-title">🔑 ${esc(t('import_title'))}</h2>
    <p style="color:var(--muted);font-size:0.9rem">${esc(t('import_hint'))}</p>
    <textarea class="kg-textarea" data-f="link" placeholder="${esc(t('import_ph'))}" style="min-height:84px"></textarea>
    <p class="field-err" data-f="err" hidden></p>
    <div class="flex gap-2">
      <button class="flex-1 py-3 rounded-2xl border-2 font-body btn-press-sm" style="border-color:var(--sand-deep);color:var(--muted);font-weight:700" data-f="cancel">${esc(t('cancel_btn'))}</button>
      <button class="flex-1 py-3 rounded-2xl font-body btn-press" style="background:var(--coral-dark);color:var(--surface);font-weight:700" data-f="go">${esc(t('import_go'))}</button>
    </div>`);
  const input = card.querySelector('[data-f="link"]');
  const err = card.querySelector('[data-f="err"]');
  setTimeout(() => input.focus(), 30);
  input.addEventListener('input', () => clearFieldError(err, input));
  card.querySelector('[data-f="cancel"]').addEventListener('click', () => close());
  card.querySelector('[data-f="go"]').addEventListener('click', () => {
    const parsed = parseOrganizerLink(input.value, knownSlug);
    if (!parsed) { showFieldError(err, input, t('import_bad')); return; }
    // Same adoption path the hash `#/slug/k/token` route uses.
    setOrgToken(parsed.slug, parsed.token);
    close();
    showToast(t('import_done'), 2200);
    goTo(`#/${parsed.slug}`);
  });
}

/** Localized styled not-found for an unknown top-level path (e.g. /totally-bogus).
 *  Mirrors the board-not-found view: the same "Card not found" copy + Home CTA. */
function renderNotFound(root) {
  wsClose();
  state.board = null;
  root.innerHTML = `
    <div style="max-width:520px;margin:80px auto;text-align:center;padding:0 6vw">
      <p class="font-display" style="font-size:1.2rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p>
      <button id="go-home" class="cta-hero" style="margin-top:20px">💌 ${esc(t('home_link'))}</button>
    </div>`;
  root.querySelector('#go-home').addEventListener('click', () => goHome());
}

// ═══════════════════════════════════════════════════════════════════════════
// SCREEN 2 — Board
// ═══════════════════════════════════════════════════════════════════════════
async function renderBoard(root, slug) {
  root.innerHTML = `<div style="max-width:720px;margin:60px auto;text-align:center;color:var(--muted)" class="font-display">${esc(t('loading'))}</div>`;
  try {
    state.board = await fetchBoard(slug);
  } catch (e) {
    root.innerHTML = `
      <div style="max-width:520px;margin:80px auto;text-align:center;padding:0 6vw">
        <p class="font-display" style="font-size:1.2rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p>
        <button id="go-home" class="cta-hero" style="margin-top:20px">💌 ${esc(t('home_link'))}</button>
      </div>`;
    root.querySelector('#go-home').addEventListener('click', () => goHome());
    return;
  }
  state.seen = new Set(state.board.cards.map(c => c.id)); // no entrance anim on first paint
  paintBoard(root, slug, { animateNew: false });
  wsConnect(slug);
}

function wishHtml(c, isOrganizer, animate) {
  const alt = esc(t('img_alt', { author: c.author_name || '?' }));
  // Own uploads are same-origin; GIF/URL images are third-party, so add
  // referrerpolicy="no-referrer" to avoid leaking the card URL / visitor IP.
  const media = c.image_path
    ? `<div class="wish-media"><img src="${esc(c.image_path)}" alt="${alt}" loading="lazy"></div>`
    : (c.gif_url ? `<div class="wish-media"><img src="${esc(c.gif_url)}" alt="${alt}" loading="lazy" referrerpolicy="no-referrer"></div>` : '');
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
  // Reveal gate: the server withholds wishes from a guest until reveal. When
  // gated, the guest sees a placeholder (and the waiting count) instead of the
  // wishes; the organizer always previews them (token header on the fetch).
  const gatedForGuest = !b.revealed && !isOrganizer;
  const bc = safeHex(b.brand_color); // corp-brand accent, or null

  const cardsHtml = gatedForGuest
    ? `<div class="cozy-card" style="padding:32px;text-align:center;max-width:460px;margin:0 auto">
         <p class="font-display" style="font-weight:800;color:var(--ink);font-size:1.05rem">🔒 ${esc(t('gated_title'))}</p>
         <p style="margin-top:8px;color:var(--muted)">${esc(t('gated_hint'))}</p>
         ${b.card_count > 0 ? `<p style="margin-top:10px;color:var(--muted);font-weight:700">🎁 ${esc(pluralWishes(b.card_count))} · ${esc(t('gated_hidden'))}</p>` : ''}
       </div>`
    : (b.cards.length === 0
      ? `<div class="cozy-card" style="padding:32px;text-align:center;max-width:460px;margin:0 auto">
           <p class="font-display" style="font-weight:800;color:var(--ink);font-size:1.05rem">${esc(t('empty_title'))}</p>
           <p style="margin-top:8px;color:var(--muted)">${esc(t('empty_hint'))}</p>
         </div>`
      : `<div class="masonry">${b.cards.map(c => wishHtml(c, isOrganizer, animateNew && !state.seen.has(c.id))).join('')}</div>`);

  root.innerHTML = `
    <nav style="position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:12px 5vw;background:oklch(98% 0.018 75 / 0.92);backdrop-filter:blur(12px);border-bottom:2px solid var(--sand-deep)">
      <a class="font-display nav-back" style="font-size:0.95rem;color:var(--muted);text-decoration:none;font-weight:800" href="/" data-home="1" aria-label="${esc(t('home_link'))}"><span aria-hidden="true">←</span><span class="nav-label">${esc(t('home_link'))}</span></a>
      <div style="display:flex;align-items:center;gap:10px">
        <span id="live-pip" class="live-pip"></span>
        ${mkLangSwitcher()}
      </div>
    </nav>

    <main style="max-width:1000px;margin:0 auto;padding:28px 6vw 100px">
      <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
        <span class="cover-badge"${bc ? ` style="box-shadow:0 0 0 3px ${bc}"` : ''}>${esc(b.cover || '💌')}</span>
        <div style="flex:1;min-width:0">
          <h1 class="font-display title-clamp" style="font-weight:900;font-size:clamp(1.6rem,4vw,2.4rem);color:var(--ink);letter-spacing:-0.01em${bc ? `;border-bottom:3px solid ${bc};display:inline-block;padding-bottom:2px` : ''}">${esc(b.title)}</h1>
          ${b.recipient ? `<p style="color:var(--muted);margin-top:2px;font-weight:600">${esc(t('for_word'))} <span style="color:var(--ink);font-weight:800">${esc(b.recipient)}</span></p>` : ''}
        </div>
      </div>

      ${isOrganizer && !orgBannerDismissed(slug) ? `
      <div class="org-banner" data-f="orgbanner" style="margin-top:18px">
        <span aria-hidden="true" style="font-size:1.3rem">🔑</span>
        <p class="org-banner-text">${esc(t('org_banner_text'))}</p>
        <div class="org-banner-actions">
          <button class="org-mini-btn" data-f="org-copy">🔗 ${esc(t('org_banner_save'))}</button>
          <button class="org-mini-btn" data-f="org-qr">▦ ${esc(t('qr_btn'))}</button>
        </div>
        <button class="org-banner-close" data-f="org-dismiss" aria-label="${esc(t('cancel_btn'))}" title="${esc(t('cancel_btn'))}">✕</button>
      </div>` : ''}

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:18px">
        <span class="font-display" style="font-size:0.8rem;color:var(--muted);font-weight:700;margin-right:2px">${esc(t('share_label'))}</span>
        <a class="share-btn" data-share="tg" target="_blank" rel="noopener">✈️ ${esc(t('share_tg'))}</a>
        <a class="share-btn" data-share="wa" target="_blank" rel="noopener">💬 ${esc(t('share_wa'))}</a>
        <a class="share-btn" data-share="vk" target="_blank" rel="noopener">🅥 ${esc(t('share_vk'))}</a>
        <button class="share-btn" data-copy-share="1">🔗 ${esc(t('copy_link'))}</button>
        <button class="share-btn" data-qr="1">▦ ${esc(t('qr_btn'))}</button>
        <button class="share-btn" data-embed="1">⧉ ${esc(t('embed_btn'))}</button>
      </div>

      <div style="display:flex;align-items:center;gap:8px;margin-top:12px;flex-wrap:wrap">
        <span class="font-display" style="font-size:0.85rem;color:var(--muted);font-weight:700">${esc(t('you_are'))}</span>
        ${myName ? `<span class="font-display" style="font-weight:800;color:var(--ink)">${esc(myName)}</span>` : ''}
        <button class="font-display" data-set-name="1" style="background:transparent;border:none;color:var(--coral);font-size:0.82rem;font-weight:800;cursor:pointer">${myName ? esc(t('change_name')) : esc(t('set_name'))}</button>
      </div>

      ${!b.revealed ? `
      <div class="locked-banner" style="margin-top:20px">
        <span style="font-size:1.4rem">🔒</span>
        <p class="font-display" style="font-weight:800;color:var(--ink)">${esc(t('gated_title'))}${b.reveal_at ? ` · ${esc(fmtRevealAt(b.reveal_at))}` : ''}</p>
      </div>` : ''}

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
        ${locked
          ? `<button class="btn-soft btn-press-sm" data-unlock="${b.id}">🔓 ${esc(t('unlock_btn'))}</button>`
          : `<button class="btn-soft btn-press-sm" data-lock="${b.id}">🔒 ${esc(t('lock_btn'))}</button>`}
        ${!b.revealed ? `<button class="cta-hero" style="min-height:44px;padding:11px 20px" data-reveal="${b.id}">🔓 ${esc(t('reveal_btn'))}</button>` : ''}
        <button class="cta-hero" style="min-height:44px;padding:11px 20px" data-deliver="1">🎁 ${esc(t('deliver_btn'))}</button>
        <button class="font-display" data-del-board="${b.id}" style="background:transparent;border:none;color:var(--muted);font-size:0.8rem;font-weight:700;cursor:pointer">🗑 ${esc(t('delete_board'))}</button>
      </div>` : ''}
    </main>`;

  state.seen = new Set(b.cards.map(c => c.id));
  setLivePip(ws.socket && ws.socket.readyState === 1 ? 'connected' : 'reconnecting');
  wireBoard(root, slug);
}

function shareUrls(slug, recipient) {
  // Guest link is the real path /c/{slug} so crawlers (Telegram/WhatsApp/Slack)
  // can fetch it and unfurl the per-board card preview.
  const url = guestUrlFor(slug);
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

  // Organizer "save your link" banner — copy / QR of the private manage link, dismiss.
  if (token) {
    const manageUrl = manageUrlFor(slug, token);
    const orgCopy = root.querySelector('[data-f="org-copy"]');
    if (orgCopy) orgCopy.addEventListener('click', () => copyToClipboard(manageUrl));
    const orgQr = root.querySelector('[data-f="org-qr"]');
    if (orgQr) orgQr.addEventListener('click', () => showQrModal(manageUrl));
    const orgDismiss = root.querySelector('[data-f="org-dismiss"]');
    if (orgDismiss) orgDismiss.addEventListener('click', () => {
      dismissOrgBanner(slug);
      const banner = root.querySelector('[data-f="orgbanner"]');
      if (banner) banner.remove();
    });
  }

  const embedBtn = root.querySelector('[data-embed]');
  if (embedBtn) embedBtn.addEventListener('click', () => showEmbedModal(slug));

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
      if (!await showConfirmModal(t('confirm_delete_card'))) return;
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

  root.querySelectorAll('[data-reveal]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await api.patch(`/api/v1/boards/${btn.dataset.reveal}/reveal`, { organizer_token: token });
        await refreshBoard(root, slug);
      } catch (e) { showToast(e.message); }
    });
  });

  root.querySelectorAll('[data-unlock]').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await api.patch(`/api/v1/boards/${btn.dataset.unlock}/unlock`, { organizer_token: token });
        await refreshBoard(root, slug);
      } catch (e) { showToast(e.message); }
    });
  });

  root.querySelectorAll('[data-deliver]').forEach(btn => {
    btn.addEventListener('click', () => goTo(`#/${slug}/deliver`));
  });

  root.querySelectorAll('[data-del-board]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!await showConfirmModal(t('confirm_delete_board'))) return;
      const boardId = btn.dataset.delBoard;
      try {
        await api.del(`/api/v1/boards/${boardId}`, { organizer_token: token });
        wsClose();
        goHome();
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
    state.board = await fetchBoard(slug);
    paintBoard(root, slug, { animateNew: true });
  } catch (e) {
    showToast(e.message);
  }
}

// ─── QR rendering ────────────────────────────────────────────────────────────
/** Render a QR code for `url` into `box`, degrading to the plain URL text if the
 *  qrcode library failed to load (e.g. blocked CDN + SRI mismatch). */
function renderQrInto(box, url, size = 220) {
  if (typeof QRCode !== 'undefined') {
    try {
      new QRCode(box, { text: url, width: size, height: size, colorDark: '#33202b', colorLight: '#fdf6ee' });
      return;
    } catch (_) { /* fall through to text */ }
  }
  box.innerHTML = `<span style="color:var(--muted);word-break:break-all">${esc(url)}</span>`;
}

function showQrModal(url) {
  const { card } = openModal(`
    <h2 class="modal-title">${esc(t('qr_title'))}</h2>
    <div class="qr-box" id="qr-box"></div>
    <button class="btn-soft btn-press-sm" data-copy="${esc(url)}" style="width:100%">🔗 ${esc(t('copy_link'))}</button>`);
  renderQrInto(card.querySelector('#qr-box'), url, 220);
  card.querySelector('[data-copy]').addEventListener('click', () => copyToClipboard(url));
}

// ─── Embed modal (copy the iframe snippet) ───────────────────────────────────
function showEmbedModal(slug) {
  // Build the absolute src from the server-injected canonical origin when
  // present (so the snippet points at the real host even when the SPA is opened
  // on a bare hash route), else the current origin. The board title becomes the
  // iframe title="..." attribute; esc() keeps it a safe, single-escaped value.
  const canonical = canonicalOrigin();
  const title = state.board ? state.board.title : '';
  const src = `${canonical}/embed/${slug}`;
  const snippet =
    `<iframe src="${src}" width="100%" height="560" ` +
    `style="border:0;border-radius:16px" loading="lazy" title="${esc(title)}"></iframe>`;
  const { card } = openModal(`
    <h2 class="modal-title">⧉ ${esc(t('embed_modal_title'))}</h2>
    <p style="color:var(--muted);font-size:0.88rem">${esc(t('embed_hint'))}</p>
    <textarea class="kg-textarea" readonly data-f="code" style="margin-top:8px;min-height:120px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:0.78rem">${esc(snippet)}</textarea>
    <button class="cta-hero" style="width:100%" data-f="copy">🔗 ${esc(t('embed_copy'))}</button>`);
  const ta = card.querySelector('[data-f="code"]');
  card.querySelector('[data-f="copy"]').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(snippet); showToast(t('embed_copied'), 1600); }
    catch (_) { ta.focus(); ta.select(); }
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// SCREEN — Embedded card (read-only, no organizer access, live)
// ═══════════════════════════════════════════════════════════════════════════
async function renderEmbed(root, slug) {
  root.innerHTML = `<div style="max-width:720px;margin:48px auto;text-align:center;color:var(--muted)" class="font-display">${esc(t('loading'))}</div>`;
  try {
    state.board = await fetchBoard(slug);
  } catch (e) {
    root.innerHTML = `<div style="max-width:520px;margin:60px auto;text-align:center;padding:0 6vw"><p class="font-display" style="font-size:1.1rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p></div>`;
    return;
  }
  state.seen = new Set(state.board.cards.map(c => c.id)); // no entrance anim on first paint
  paintEmbed(root, slug, { animateNew: false });
  wsConnect(slug);
}

function paintEmbed(root, slug, opts = {}) {
  const animateNew = !!opts.animateNew;
  const b = state.board;
  const openUrl = `${canonicalOrigin()}/c/${slug}`;

  // Read-only: wishHtml(..., isOrganizer=false, ...) emits no pin/delete tools.
  const cardsHtml = b.cards.length === 0
    ? `<div class="cozy-card" style="padding:24px;text-align:center"><p style="color:var(--muted)">${esc(t('empty_hint'))}</p></div>`
    : `<div class="masonry">${b.cards.map(c => wishHtml(c, false, animateNew && !state.seen.has(c.id))).join('')}</div>`;

  root.innerHTML = `
    <main class="embed-wrap">
      <div class="embed-head">
        <span class="cover-badge">${esc(b.cover || '💌')}</span>
        <div style="flex:1;min-width:0">
          <h1 class="font-display title-clamp" style="font-weight:900;font-size:clamp(1.2rem,4vw,1.7rem);color:var(--ink);letter-spacing:-0.01em">${esc(b.title)}</h1>
          ${b.recipient ? `<p style="color:var(--muted);margin-top:2px;font-weight:600;font-size:0.9rem">${esc(t('for_word'))} <span style="color:var(--ink);font-weight:800">${esc(b.recipient)}</span></p>` : ''}
        </div>
        <span id="live-pip" class="live-pip"></span>
      </div>
      <div style="margin-top:16px">${cardsHtml}</div>
      <div class="embed-foot">
        <a href="${esc(openUrl)}" target="_blank" rel="noopener" class="font-display" style="color:var(--coral);font-weight:800;font-size:0.85rem;text-decoration:none">💌 ${esc(t('embed_open'))} ↗</a>
      </div>
    </main>`;

  state.seen = new Set(b.cards.map(c => c.id));
  setLivePip(ws.socket && ws.socket.readyState === 1 ? 'connected' : 'reconnecting');
}

// ─── Add-wish modal ──────────────────────────────────────────────────────────
function showAddWishModal(root, slug) {
  let picked = null; // { blob, filename }
  const preset = getMyName(slug);
  const { card, close } = openModal(`
    <h2 class="modal-title">💌 ${esc(t('add_modal_title'))}</h2>
    <div>
      <label class="modal-label">${esc(t('name_label'))}</label>
      <input class="kg-input" data-f="name" type="text" maxlength="48" placeholder="${esc(t('name_ph'))}" value="${esc(preset)}" autocomplete="nickname" style="margin-top:6px">
    </div>
    <div>
      <label class="modal-label">${esc(t('text_label'))}</label>
      <textarea class="kg-textarea" data-f="text" maxlength="2000" placeholder="${esc(occasionWishPrompt(state.board && state.board.occasion))}" style="margin-top:6px"></textarea>
    </div>
    <div>
      <label class="modal-label">${esc(t('photo_label'))}</label>
      <div class="drop-zone" data-f="drop" style="margin-top:6px">📷 ${esc(t('drop_hint'))}</div>
      <input type="file" accept="image/jpeg,image/png,image/webp" data-f="file" hidden>
      <p class="field-err" data-f="fileerr" hidden></p>
      <div data-f="preview" style="margin-top:10px"></div>
    </div>
    <div>
      <label class="modal-label">${esc(t('gif_label'))}</label>
      <input class="kg-input" data-f="gif" type="url" maxlength="500" placeholder="${esc(t('gif_ph'))}" style="margin-top:6px">
      <p style="font-size:0.78rem;color:var(--muted);margin-top:4px">${esc(t('gif_hint'))}</p>
    </div>
    <p class="field-err" data-f="err" hidden></p>
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
  const formErr = card.querySelector('[data-f="err"]');
  const fileErr = card.querySelector('[data-f="fileerr"]');
  const dropIdle = `📷 ${esc(t('drop_hint'))}`;

  const showPreview = (blob) => {
    const url = URL.createObjectURL(blob);
    preview.innerHTML = `
      <div class="img-preview">
        <img src="${url}" alt="${esc(t('img_preview_alt'))}">
        <button class="img-remove" data-f="remove" aria-label="${esc(t('remove_photo'))}" title="${esc(t('remove_photo'))}">✕</button>
      </div>`;
    preview.querySelector('[data-f="remove"]').addEventListener('click', () => {
      picked = null; preview.innerHTML = ''; URL.revokeObjectURL(url);
    });
    // The modal is tall; a fresh preview often lands below the fold — bring it in.
    try { preview.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } catch (_) {}
  };

  const handleFile = async (file) => {
    if (!file) return;
    clearFieldError(fileErr, drop);
    // Client-side pre-check (server also enforces image_unsupported_type / image_too_large).
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) {
      showFieldError(fileErr, drop, t('err_img_type'));
      return;
    }
    drop.classList.add('busy');
    drop.innerHTML = `<span class="mini-spin" aria-hidden="true"></span>${esc(t('processing'))}`;
    try {
      // Resize first, then size-check the ACTUAL bytes that will be uploaded
      // (the re-encoded blob), not the original file. A large original that
      // shrinks under the cap is accepted; the cap matches the backend so a
      // client-side pass can no longer be rejected by a server 413.
      const resized = await resizeImage(file);
      if (resized.blob.size > MAX_UPLOAD_MB * 1024 * 1024) {
        picked = null;
        showFieldError(fileErr, drop, t('err_img_size', { n: MAX_UPLOAD_MB }));
        return;
      }
      picked = resized;
      showPreview(picked.blob);
    } catch (_) {
      showFieldError(fileErr, drop, t('err_img_type'));
    } finally {
      drop.classList.remove('busy');
      drop.innerHTML = dropIdle;
    }
  };

  drop.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));
  ['dragover', 'dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('drag'); }));
  drop.addEventListener('drop', e => { if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });

  nameInput.addEventListener('input', () => clearFieldError(formErr, nameInput));
  textInput.addEventListener('input', () => clearFieldError(formErr, textInput));

  setTimeout(() => (preset ? textInput : nameInput).focus(), 30);

  card.querySelector('[data-f="cancel"]').addEventListener('click', () => close());

  sendBtn.addEventListener('click', async () => {
    clearFieldError(formErr, nameInput);
    clearFieldError(formErr, textInput);
    const name = nameInput.value.trim();
    if (!name) { showFieldError(formErr, nameInput, t('err_name_required')); return; }
    const text = textInput.value.trim();
    const gif = gifInput.value.trim();
    if (!text && !gif && !picked) { showFieldError(formErr, textInput, t('err_need_something')); return; }
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
      close();
      await refreshBoard(root, slug);
    } catch (e) {
      // Inline in the modal (not a viewport-edge toast). Map server code if present.
      showFieldError(formErr, null, e.message);
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
    b = await fetchBoard(slug);
  } catch (e) {
    root.innerHTML = `
      <div style="max-width:520px;margin:80px auto;text-align:center;padding:0 6vw">
        <p class="font-display" style="font-size:1.2rem;font-weight:800;color:var(--ink)">${esc(t('err_not_found'))}</p>
        <button id="go-home" class="cta-hero" style="margin-top:20px">💌 ${esc(t('home_link'))}</button>
      </div>`;
    root.querySelector('#go-home').addEventListener('click', () => goHome());
    return;
  }

  // Reveal gate: a guest cannot open the delivery view before reveal. The
  // organizer (token on the fetch) always previews it.
  if (!b.revealed && !getOrgToken(slug)) {
    root.innerHTML = `
      <main class="hero-blobs" style="max-width:560px;margin:0 auto;padding:60px 6vw 90px;text-align:center">
        <span class="cover-badge big">🔒</span>
        <p class="font-display" style="font-size:1.3rem;font-weight:800;color:var(--ink);margin-top:18px">${esc(t('gated_title'))}${b.reveal_at ? ` · ${esc(fmtRevealAt(b.reveal_at))}` : ''}</p>
        <p style="color:var(--muted);margin-top:10px">${esc(t('gated_hint'))}</p>
        <a class="font-display" href="#/${esc(slug)}" style="display:inline-block;margin-top:24px;color:var(--coral);font-weight:800;text-decoration:none">← ${esc(t('back_to_board'))}</a>
      </main>`;
    return;
  }

  const bc = safeHex(b.brand_color);
  root.innerHTML = `
    <main class="hero-blobs deliver-view" style="max-width:1000px;margin:0 auto;padding:40px 6vw 90px">
      <div class="deliver-head" style="text-align:center;max-width:640px;margin:0 auto">
        <div class="hero-reveal-1"><span class="cover-badge big"${bc ? ` style="box-shadow:0 0 0 3px ${bc}"` : ''}>${esc(b.cover || '💌')}</span></div>
        ${b.recipient ? `<p class="hero-reveal-2 font-display" style="color:var(--coral);font-weight:800;margin-top:14px;font-size:1.05rem">${esc(t('deliver_intro'))} ${esc(b.recipient)}</p>` : ''}
        <h1 class="hero-reveal-2 font-display" style="font-weight:900;font-size:clamp(1.9rem,5vw,3rem);color:var(--ink);letter-spacing:-0.02em;margin-top:6px">${esc(b.title)}</h1>
        <p class="hero-reveal-3" style="color:var(--muted);margin-top:10px">${esc(pluralWishes(b.cards.length))}</p>
      </div>

      <div class="hero-reveal-4" style="margin-top:32px">
        ${b.cards.length === 0
          ? `<p style="text-align:center;color:var(--muted)">${esc(t('empty_hint'))}</p>`
          : `<div class="masonry">${b.cards.map(c => wishHtml(c, false, false)).join('')}</div>`}
      </div>

      <div class="no-print" style="text-align:center;margin-top:36px;display:flex;gap:16px;justify-content:center;align-items:center;flex-wrap:wrap">
        <button id="deliver-print" class="btn-soft btn-press-sm">🖨 ${esc(t('download_pdf'))}</button>
        <a class="font-display" href="#/${esc(slug)}" style="color:var(--muted);font-weight:700;font-size:0.85rem;text-decoration:none">← ${esc(t('back_to_board'))}</a>
      </div>

      <footer class="print-only deliver-colophon">${bc ? `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${bc};margin-right:6px"></span>` : ''}${esc(b.title)} · ${esc(t('brand'))}</footer>
    </main>`;

  // Name the saved PDF sensibly after the card, reusing the i18n tab-title wiring.
  document.title = b.title || t('doc_title');
  const printBtn = root.querySelector('#deliver-print');
  if (printBtn) {
    printBtn.addEventListener('click', () =>
      exportDeliverPdf(root.querySelector('.deliver-view'), b.title || document.title)
    );
  }

  fireConfetti();
}

/** Client-side "Save as PDF" for the delivery view.
 *
 *  window.print() silently no-ops inside the Telegram/VK in-app browsers, so we
 *  rasterize the .deliver-view <main> with html2canvas-pro (the fork that parses
 *  the OKLCH colours this design system uses everywhere — classic html2canvas
 *  renders oklch as black) and lay the bitmap into a jsPDF A4 document, slicing
 *  across pages when the card is taller than one page.
 *
 *  EXCLUDED from the capture: the .no-print button row (via ignoreElements). The
 *  confetti overlay is a #confetti-canvas child of <body>, not of the captured
 *  <main>, so it is out of frame by construction.
 *
 *  Failure modes — a missing/blocked library, a canvas tainted by a cross-origin
 *  GIF (useCORS still leaves a non-CORS host tainted), or an out-of-memory on a
 *  very tall card — all fall back to window.print(), so the button is never worse
 *  than before. Only if print itself is unavailable do we surface an inline error. */
async function exportDeliverPdf(target, title) {
  const jspdfNs = window.jspdf;
  if (!target || typeof window.html2canvas !== 'function' || !(jspdfNs && jspdfNs.jsPDF)) {
    return _printFallback();
  }
  // --- Temporary, capture-only style mutations (ALL restored in finally) -------
  // FIX: the .print-only colophon is display:none outside @media print, so
  // html2canvas (which reads computed styles for SCREEN media) would omit the
  // branding footer that the native print() fallback shows. Force it visible.
  const colophon = target.querySelector('.print-only');
  const colophonDisplay = colophon ? colophon.style.display : null;
  if (colophon) colophon.style.display = 'block';

  // Collapse the CSS multi-column masonry to ONE column on the live node so each
  // .wish renders at (near) full content width — captured directly it then yields
  // crisp, non-reflowed text instead of a narrow column bitmap scaled up.
  const masonry = target.querySelector('.masonry');
  const masonryCol = masonry ? masonry.style.getPropertyValue('column-count') : null;
  const masonryColPrio = masonry ? masonry.style.getPropertyPriority('column-count') : '';
  if (masonry) masonry.style.setProperty('column-count', '1', 'important');

  // One FLAT warm-pastel card fill. html2canvas-pro rasterizes the cards' oklch
  // linear-gradients into a hard rectangular checkerboard (it can't render oklch
  // gradients smoothly) — a FLAT solid renders perfectly. Resolved oklch→rgb via
  // the same _cssToRgb canvas round-trip as the page tint. We drop the on-screen
  // 3-tint rotation: it can't survive per-block cloning (each card is its own
  // clone root, so nth-child/ancestor selectors match nothing — the export needs
  // colored+smooth, not variety).
  const rootStyle = getComputedStyle(document.documentElement);
  const [fr, fg, fb] = _cssToRgb(rootStyle.getPropertyValue('--coral-light').trim(), [255, 241, 238]);
  const FLAT = `rgb(${fr}, ${fg}, ${fb})`;

  // Shared html2canvas options — reused for EVERY per-block capture. onclone runs
  // per capture and (a) force-settles the entrance animations that start at
  // opacity:0 (else title/wish text vanish), (b) flattens each card's oklch
  // gradient to a solid INLINE on the element (kills the checkerboard artifact),
  // and (c) swaps un-loadable cross-origin images for a neutral placeholder.
  // backgroundColor:null keeps the flat card fills, composited over the page tint.
  const h2cOpts = {
    backgroundColor: null,
    scale: Math.min(2, window.devicePixelRatio || 1),
    useCORS: true,
    ignoreElements: (el) => el.classList && el.classList.contains('no-print'),
    onclone: (clonedDoc) => {
      const settle = clonedDoc.createElement('style');
      settle.textContent =
        '.hero-reveal-1,.hero-reveal-2,.hero-reveal-3,.hero-reveal-4,.wish,.wish.enter{' +
        'animation:none !important;opacity:1 !important;transform:none !important;}';
      clonedDoc.head.appendChild(settle);
      // Flatten INLINE on each element, not via ancestor/nth-child CSS: per-block
      // capture makes each .wish its own clone root, so `.deliver-view .masonry …`
      // selectors match nothing (and a lone card is always nth-child(1)). Inline
      // style always wins regardless of clone-root scope. box-shadow also
      // rasterizes as bands, so drop it too. Clone only — live card is untouched.
      clonedDoc.querySelectorAll('.wish').forEach((w) => {
        w.style.setProperty('background-image', 'none', 'important');
        w.style.setProperty('background-color', FLAT, 'important');
        w.style.setProperty('box-shadow', 'none', 'important');
      });
      const headEl = clonedDoc.querySelector('.deliver-head');
      if (headEl) {
        headEl.style.setProperty('background-image', 'none', 'important');
        headEl.style.setProperty('box-shadow', 'none', 'important');
      }
      const scope = clonedDoc.querySelector('.deliver-view') || clonedDoc.body;
      scope.querySelectorAll('img').forEach((img) => {
        if (img.complete && img.naturalWidth > 0) return;
        const ph = clonedDoc.createElement('div');
        ph.textContent = img.getAttribute('alt') || '🖼';
        ph.style.cssText =
          'display:flex;align-items:center;justify-content:center;min-height:120px;' +
          'padding:16px;border:2px dashed rgba(0,0,0,0.18);border-radius:16px;' +
          'color:rgba(0,0,0,0.45);font-size:0.85rem;text-align:center;word-break:break-word';
        if (img.parentNode) img.parentNode.replaceChild(ph, img);
      });
    },
  };

  try {
    void target.offsetHeight; // reflow after the single-column + colophon mutations

    // Blocks in visual order, each an ATOMIC unit that can never be split across a
    // page: header (icon+recipient+title+count) → each wish → colophon footer.
    const blocks = [];
    const head = target.querySelector('.deliver-head');
    if (head) blocks.push(head);
    target.querySelectorAll('.wish').forEach((w) => blocks.push(w));
    if (colophon) blocks.push(colophon);

    // Page tint = body base colour (cream/peach). The CSS defines it as
    // `--cream: oklch(...)`, so getComputedStyle returns an oklch() string; a naive
    // digit-regex would grab the oklch components (≠ rgb) and paint e.g. dark green.
    // Resolve to real RGB via a 1px canvas round-trip; if the body colour is
    // transparent (cream may come from a background-image), fall back to the
    // --cream var, then to a cream literal. jsPDF.setFillColor needs r,g,b and the
    // block compositor needs the css string to blend transparent card corners.
    const CREAM_FALLBACK = [255, 247, 236];
    let bgRgb = _cssToRgb(getComputedStyle(document.body).backgroundColor, null);
    if (!bgRgb) {
      const varCream = getComputedStyle(document.documentElement)
        .getPropertyValue('--cream')
        .trim();
      bgRgb = _cssToRgb(varCream, CREAM_FALLBACK);
    }
    const [r, g, b] = bgRgb;
    const bgCss = `rgb(${r}, ${g}, ${b})`;

    const pdf = new jspdfNs.jsPDF({ unit: 'pt', format: 'a4' });
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();
    const margin = 28;
    const gap = 10;
    const contentW = pageW - 2 * margin;
    const contentH = pageH - 2 * margin; // usable height for one page
    const fillPageBg = () => {
      pdf.setFillColor(r, g, b);
      pdf.rect(0, 0, pageW, pageH, 'F');
    };

    fillPageBg(); // page 1 tint, painted BEFORE any block
    let cursorY = margin;
    for (const el of blocks) {
      const bc = await window.html2canvas(el, h2cOpts);
      if (!bc.width || !bc.height) continue;
      // Composite the (transparent-cornered) block onto the page tint so the image
      // is opaque and the rounded-card corners blend into the page, not black. The
      // temp canvas is EXACTLY the block size, drawn at (0,0) — no offset strip.
      // Encode PNG (lossless): JPEG left a checkerboard/banding artifact on the
      // cards' smooth oklch gradients; per-block images are small so PNG size is fine.
      const comp = document.createElement('canvas');
      comp.width = bc.width;
      comp.height = bc.height;
      const cx = comp.getContext('2d');
      cx.fillStyle = bgCss;
      cx.fillRect(0, 0, comp.width, comp.height);
      cx.drawImage(bc, 0, 0);
      const data = comp.toDataURL('image/png');

      let w = contentW;
      let h = bc.height * (contentW / bc.width);
      // Only-shrink case: a single block taller than one usable page is scaled
      // down to fit (its own page) — never split. Everything else keeps full width.
      if (h > contentH) {
        w = contentW * (contentH / h);
        h = contentH;
      }
      // Page break when the block does not fit the remaining space on this page.
      if (cursorY + h > pageH - margin) {
        pdf.addPage();
        fillPageBg();
        cursorY = margin;
      }
      const x = margin + (contentW - w) / 2; // centre a shrunk block
      pdf.addImage(data, 'PNG', x, cursorY, w, h);
      cursorY += h + gap;
    }

    const safe = (title || 'otkrytka').replace(/[\\/:*?"<>|\n\r\t]+/g, ' ').trim() || 'otkrytka';
    pdf.save(`${safe}.pdf`);
  } catch (_) {
    _printFallback();
  } finally {
    // Restore every temporary mutation to the live DOM.
    if (colophon) colophon.style.display = colophonDisplay;
    if (masonry) {
      if (masonryCol) masonry.style.setProperty('column-count', masonryCol, masonryColPrio);
      else masonry.style.removeProperty('column-count');
    }
  }
}

function _printFallback() {
  try {
    window.print();
  } catch (_) {
    showToast(t('err_generic'));
  }
}

/** Resolve any CSS colour string (oklch/hsl/var/named/rgb) to concrete [r,g,b] via
 *  a 1px canvas round-trip — the browser does the colour-space conversion, so we
 *  never hand-parse oklch. Returns `fallback` when the colour is transparent
 *  (alpha 0) or the canvas is unavailable. */
function _cssToRgb(cssColor, fallback) {
  try {
    const c = document.createElement('canvas');
    c.width = c.height = 1;
    const cx = c.getContext('2d');
    cx.fillStyle = cssColor;
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    if (d[3] === 0) return fallback; // transparent → caller-supplied fallback
    return [d[0], d[1], d[2]];
  } catch (_) {
    return fallback;
  }
}

// ─── Global delegated clicks (lang toggle + home) ────────────────────────────
document.getElementById('app').addEventListener('click', e => {
  const home = e.target.closest('[data-home]');
  if (home) { e.preventDefault(); goHome(); return; }
  const btn = e.target.closest('[data-lang]');
  if (!btn) return;
  state.lang = btn.dataset.lang;
  lsSet('otkrytka_lang', state.lang);
  render();
});

// ─── Init ────────────────────────────────────────────────────────────────────
function init() {
  // Modal state is never persisted, so a normal load starts with no modal.
  // Tear down any overlay that might have survived in the initial markup.
  clearAllModals();
  document.documentElement.lang = state.lang;
  render();
  const rerender = () => {
    wsClose();
    state.board = null;
    render();
  };
  // hashchange covers the hash routes; popstate covers real-path /c/{slug}
  // navigation (back/forward after goHome pushes '/').
  window.addEventListener('hashchange', rerender);
  window.addEventListener('popstate', rerender);
  // bfcache restore (back/forward) can resurrect a DOM snapshot that still holds
  // an open modal; e.persisted marks that case. Clear it so no modal reappears.
  window.addEventListener('pageshow', e => { if (e.persisted) clearAllModals(); });
}

init();
