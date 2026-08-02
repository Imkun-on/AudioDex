/* Logica della pagina.
 *
 * Regola unica: qui non si decide niente di importante. La pagina raccoglie
 * cio' che si scrive, lo passa a Python, e mostra cio' che Python risponde.
 * Ogni scelta vera - se un URL sia una playlist, quale formato sia
 * compatibile con quale media, cosa sia un album divisibile - sta gia' nei
 * moduli, ed e' li' che deve restare: duplicarla qui significherebbe due
 * comportamenti diversi per la stessa domanda.
 */

let TESTI = {};
let LINGUA = 'it';

/* Quali tracce sono spuntate. Vive qui e non nel DOM perche' deve
 * sopravvivere al ridisegno delle schede quando si cambia lingua. */
let SCELTI = new Set();
let SCHEDE = [];

/* I formati dipendono da cosa si scarica: chiedere un mp4 mentre si scarica
 * il solo audio e' un errore che il motore rifiuterebbe, quindi la scelta
 * non viene proprio offerta. */
const FORMATI = {
  audio: ['m4a', 'mp3', 'opus'],
  video: ['mp4', 'mkv'],
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function t(chiave, valori) {
  const voce = TESTI[chiave];
  let testo = voce ? (voce[LINGUA] || voce.it || chiave) : chiave;
  if (valori) {
    for (const [k, v] of Object.entries(valori)) {
      testo = testo.split('{' + k + '}').join(v);
    }
  }
  // I testi del catalogo portano il markup di Rich, che a schermo non serve.
  return testo.replace(/\[\/?[a-z_]+\]/g, '');
}

function traduciPagina() {
  $$('[data-t]').forEach((el) => { el.textContent = t(el.dataset.t); });
  aggiornaEtichettaIngresso();
  if (!$('#risultati').dataset.pieno) svuotaRisultati();
  if (!$('#diario').dataset.pieno) svuotaDiario();
  $('#stato').textContent = t('status.idle');
}

function aggiornaEtichettaIngresso() {
  const modo = $('#modo').value;
  $('#etichetta-input').textContent =
    t(modo === 'search' ? 'audio.input.search' : 'audio.input.url');
  $('#ingresso').placeholder =
    modo === 'search' ? 'Pink Floyd - Time' : 'https://www.youtube.com/watch?v=…';
}

function aggiornaFormati() {
  const media = $('#media').value;
  const sel = $('#formato');
  const precedente = sel.value;
  sel.innerHTML = '';
  FORMATI[media].forEach((f) => {
    const o = document.createElement('option');
    o.value = f; o.textContent = f.toUpperCase();
    sel.appendChild(o);
  });
  if (FORMATI[media].includes(precedente)) sel.value = precedente;
}

/* ── Cose che Python chiama sulla pagina ─────────────────────────────────── */

window.aggiungiRiga = (testo) => {
  const diario = $('#diario');
  if (!diario.dataset.pieno) { diario.innerHTML = ''; diario.dataset.pieno = '1'; }
  const riga = document.createElement('div');
  riga.className = 'riga-log ' + classeRiga(testo);
  riga.textContent = testo;
  diario.appendChild(riga);
  // Si tiene solo la coda: un download di cinquanta brani produce migliaia di
  // righe, e tenerle tutte nel documento rallenta lo scorrimento.
  while (diario.childElementCount > 400) diario.removeChild(diario.firstChild);
  diario.scrollTop = diario.scrollHeight;
};

function classeRiga(testo) {
  const b = testo.toLowerCase();
  if (b.includes('error') || b.includes('errore') || b.includes('✗') || b.includes('fallit')) return 'err';
  if (b.includes('✓') || b.includes('completat') || b.includes('scaricat')) return 'ok';
  if (b.includes('warning') || b.includes('attenzione')) return 'warn';
  return '';
}

window.cambiaStato = (stato) => {
  const spia = $('#spia');
  spia.className = 'spia ' + (stato === 'idle' ? '' : stato);
  $('#stato').textContent = t('status.' + stato);

  const inCorso = stato === 'working';
  $('#analizza').disabled = inCorso;
  $('#scarica').disabled = inCorso;
  $('#avanzamento').classList.toggle('visibile', inCorso);
  $('#barra').classList.toggle('indeterminata', inCorso);
  if (inCorso) $('#avanzamento-testo').textContent = t('status.working') + '…';
};

window.mostraRisultati = (dati) => {
  const elenco = $('#risultati');
  elenco.innerHTML = '';
  elenco.dataset.pieno = '1';
  $('#conteggio').textContent = dati.titolo || '';

  if (!dati.voci || !dati.voci.length) { svuotaRisultati(); return; }

  dati.voci.forEach((v, i) => {
    const scheda = document.createElement('div');
    scheda.className = 'scheda';
    // Le schede compaiono a cascata invece che tutte insieme: su venti
    // risultati la differenza fra "e' apparso un muro" e "si sta popolando"
    // e' tutta qui, e costa una riga.
    scheda.style.animationDelay = Math.min(i * 22, 420) + 'ms';

    scheda.innerHTML =
      '<div class="casella"></div>' +
      '<div class="miniatura">' +
        '<div class="numero">' + String(i + 1).padStart(2, '0') + '</div>' +
        (v.durata ? '<div class="durata-sopra"></div>' : '') +
      '</div>' +
      '<div class="scheda-testo">' +
        '<div class="scheda-titolo"></div>' +
        '<div class="scheda-sotto"></div>' +
      '</div>' +
      '<div class="pastiglia"></div>' +
      '<div class="filo"></div>';

    // Titoli e nomi di canale arrivano da YouTube: si scrivono sempre come
    // testo, mai come HTML, o un titolo con dentro un tag diventerebbe parte
    // della pagina.
    scheda.querySelector('.scheda-titolo').textContent = v.titolo || '';
    if (v.durata) scheda.querySelector('.durata-sopra').textContent = v.durata;

    const sotto = scheda.querySelector('.scheda-sotto');
    const pezzi = [v.canale, v.viste ? v.viste + ' ▶' : ''].filter(Boolean);
    pezzi.forEach((testo, k) => {
      if (k) {
        const punto = document.createElement('span');
        punto.className = 'punto'; punto.textContent = '·';
        sotto.appendChild(punto);
      }
      const span = document.createElement('span');
      span.textContent = testo;
      sotto.appendChild(span);
    });

    // La miniatura si aggiunge solo se arriva davvero: un riquadro con
    // l'icona rotta sarebbe peggio del riquadro vuoto.
    if (v.miniatura) {
      const img = new Image();
      img.loading = 'lazy';
      img.alt = '';
      img.onload = () => scheda.querySelector('.miniatura').prepend(img);
      img.src = v.miniatura;
    }

    // Tutta la riga fa da bersaglio: centrare col mouse una casella da 18 px
    // e' un fastidio che non serve a nessuno.
    scheda.addEventListener('click', () => commuta(i));
    SCHEDE[i] = scheda;
    SCELTI.add(i);
    elenco.appendChild(scheda);
  });
  aggiornaSelezione();
};

function commuta(i) {
  if (SCELTI.has(i)) SCELTI.delete(i); else SCELTI.add(i);
  aggiornaSelezione();
}

function aggiornaSelezione() {
  SCHEDE.forEach((s, i) => { if (s) s.classList.toggle('spenta', !SCELTI.has(i)); });
  const n = SCELTI.size;
  $('#conteggio').textContent = n ? t('sel.count', { n }) : '';
  $('#scarica').disabled = n === 0;
}

/* ── Stato della singola traccia, mentre scarica ──────────────────────────── */

window.iniziaLavoro = (totale) => {
  $('#avanzamento').classList.add('visibile');
  $('#barra').classList.remove('indeterminata');
  $('#barra').style.width = '0%';
  $('#avanzamento-testo').textContent = t('lavoro.avanzo', { fatte: 0, totale });
  SCHEDE.forEach((s, i) => {
    if (!s) return;
    s.classList.remove('in-corso', 'finita', 'fallita');
    const p = s.querySelector('.pastiglia');
    p.className = 'pastiglia';
    p.textContent = SCELTI.has(i) ? t('fase.attesa') : '';
  });
};

window.avanzaLavoro = (fatte, totale) => {
  $('#barra').style.width = Math.round((fatte / totale) * 100) + '%';
  $('#avanzamento-testo').textContent = t('lavoro.avanzo', { fatte, totale });
};

window.tracciaFase = (i, fase) => {
  const s = SCHEDE[i];
  if (!s) return;
  s.classList.add('in-corso');
  const p = s.querySelector('.pastiglia');
  p.className = 'pastiglia lavora';
  p.textContent = t('fase.' + fase);
  // La traccia che sta lavorando si porta sotto gli occhi da sola: su una
  // playlist da cinquanta brani, cercarla a mano sarebbe assurdo.
  s.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
};

window.tracciaFinita = (i, esito, errore) => {
  const s = SCHEDE[i];
  if (!s) return;
  s.classList.remove('in-corso');
  s.classList.add('finita');
  if (esito === 'fail') s.classList.add('fallita');
  const p = s.querySelector('.pastiglia');
  p.className = 'pastiglia ' + (esito === 'ok' ? 'ok' : esito === 'skip' ? 'skip' : 'fail');
  p.textContent = t('fase.' + (esito === 'ok' ? 'ok' : esito === 'skip' ? 'skip' : 'fail'));
  if (esito === 'fail' && errore) {
    avvisa(s.querySelector('.scheda-titolo').textContent + ' — ' + errore, 'fail');
  }
};

/* ── Avvisi a comparsa ────────────────────────────────────────────────────── */

function avvisa(testo, tipo) {
  const box = document.createElement('div');
  box.className = 'avviso ' + (tipo || '');
  const p = document.createElement('div');
  p.textContent = testo;
  box.appendChild(p);
  $('#avvisi').appendChild(box);
  // Gli errori restano piu' a lungo: si vuole avere il tempo di leggerli.
  setTimeout(() => {
    box.classList.add('uscita');
    setTimeout(() => box.remove(), 300);
  }, tipo === 'fail' ? 7000 : 4000);
}

window.mostraRiepilogo = (dati) => {
  $('#avanzamento-testo').textContent = dati.testo;
  $('#barra').classList.remove('indeterminata');
  $('#barra').style.width = '100%';
  window.aggiungiRiga(dati.testo);
  avvisa(dati.testo, dati.ok ? 'ok' : 'fail');
};

/* ── Cose che la pagina chiede a Python ──────────────────────────────────── */

function statoVuoto(testo) {
  const box = document.createElement('div');
  box.className = 'vuoto';
  box.innerHTML = '<svg class="icona" viewBox="0 0 24 24"><use href="#i-vuoto"/></svg>';
  const p = document.createElement('div');
  p.textContent = testo;
  box.appendChild(p);
  return box;
}

function svuotaRisultati() {
  const e = $('#risultati');
  SCELTI.clear(); SCHEDE = [];
  $('#scarica').disabled = true;
  e.dataset.pieno = '';
  e.innerHTML = '';
  e.appendChild(statoVuoto(t('audio.results.empty')));
  $('#conteggio').textContent = '';
}

function svuotaDiario() {
  const d = $('#diario');
  d.dataset.pieno = '';
  d.innerHTML = '';
  d.appendChild(statoVuoto(t('log.empty')));
}

function errore(messaggio) {
  window.aggiungiRiga(messaggio);
  avvisa(messaggio, 'fail');
  window.cambiaStato('error');
}

async function analizza() {
  const esito = await window.pywebview.api.analizza($('#ingresso').value, $('#modo').value);
  if (!esito.ok) errore(esito.errore);
}

async function scarica() {
  const esito = await window.pywebview.api.scarica({
    scelti:    Array.from(SCELTI).sort((a, b) => a - b),
    cartella:  $('#cartella').value,
    formato:   $('#formato').value,
    media:     $('#media').value,
    paralleli: $('#paralleli').value,
    testi:     $('#testi').checked,
    dividi:    $('#dividi').checked,
  });
  if (!esito.ok) errore(esito.errore);
}

async function sfoglia() {
  const esito = await window.pywebview.api.scegli_cartella();
  if (esito.ok && esito.cartella) $('#cartella').value = esito.cartella;
}

/* ── Avvio ───────────────────────────────────────────────────────────────── */

window.addEventListener('pywebviewready', async () => {
  const avvio = await window.pywebview.api.avvio();
  TESTI = avvio.testi;
  LINGUA = avvio.lingua;
  $('#lingua').value = LINGUA;
  $('#cartella').value = avvio.cartella;

  aggiornaFormati();
  traduciPagina();

  $('#modo').addEventListener('change', aggiornaEtichettaIngresso);
  $('#media').addEventListener('change', aggiornaFormati);
  $('#analizza').addEventListener('click', analizza);
  $('#scarica').addEventListener('click', scarica);
  $('#sfoglia').addEventListener('click', sfoglia);
  $('#svuota').addEventListener('click', svuotaDiario);
  $('#ingresso').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') analizza();
  });
  $('#tutti').addEventListener('click', () => {
    SCHEDE.forEach((_, i) => SCELTI.add(i));
    aggiornaSelezione();
  });
  $('#nessuno').addEventListener('click', () => {
    SCELTI.clear();
    aggiornaSelezione();
  });

  // Ctrl+Invio scarica da qualunque punto: chi ha appena spuntato le tracce
  // ha le mani sulla tastiera, non sul mouse.
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); scarica(); }
  });

  // Trascinare un link dal browser dentro la finestra: e' il gesto naturale,
  // e senza questo resterebbe l'unica cosa che ci si aspetta e non funziona.
  let dentro = 0;
  const velo = $('#velo-trascina');
  window.addEventListener('dragenter', (e) => {
    e.preventDefault(); dentro++; velo.classList.add('visibile');
  });
  window.addEventListener('dragover', (e) => e.preventDefault());
  window.addEventListener('dragleave', () => {
    if (--dentro <= 0) { dentro = 0; velo.classList.remove('visibile'); }
  });
  window.addEventListener('drop', (e) => {
    e.preventDefault(); dentro = 0; velo.classList.remove('visibile');
    const testo = (e.dataTransfer.getData('text/uri-list')
                || e.dataTransfer.getData('text/plain') || '').trim();
    if (!testo) return;
    $('#modo').value = 'url';
    aggiornaEtichettaIngresso();
    $('#ingresso').value = testo;
    analizza();
  });

  $('#lingua').addEventListener('change', async (e) => {
    const esito = await window.pywebview.api.cambia_lingua(e.target.value);
    LINGUA = esito.lingua;
    traduciPagina();
  });
});
