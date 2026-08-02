/* Nucleo della pagina: testi, cambio sezione, diario, avvisi, sezione Audio.
 *
 * Regola unica, valida anche per i tre file delle altre sezioni: qui non si
 * decide niente di importante. La pagina raccoglie cio' che si scrive, lo
 * passa a Python, e mostra cio' che Python risponde. Ogni scelta vera - se un
 * URL sia una playlist, quale risoluzione abbia senso, se un ordine di tracce
 * ci stia su un CD - sta gia' nei moduli, ed e' li' che deve restare:
 * duplicarla qui significherebbe due risposte diverse alla stessa domanda.
 */

let TESTI = {};
let LINGUA = 'it';
let SEZIONE = 'audio';

/* Quali tracce sono spuntate, nella sezione Audio. Vive qui e non nel
 * documento perche' deve sopravvivere al ridisegno delle schede quando si
 * cambia lingua. */
let SCELTI = new Set();
let SCHEDE = [];

const FORMATI = { audio: ['m4a', 'mp3', 'opus'], video: ['mp4', 'mkv'] };

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function t(chiave, valori) {
  const voce = TESTI[chiave];
  let testo = voce ? (voce[LINGUA] || voce.it || chiave) : chiave;
  if (valori) {
    for (const [k, v] of Object.entries(valori)) testo = testo.split('{' + k + '}').join(v);
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
  if (window.traduciBurn) window.traduciBurn();
  if (window.traduciPix) window.traduciPix();
  if (window.traduciClip) window.traduciClip();
}

/* ── Cambio sezione ───────────────────────────────────────────────────────── */

function cambiaSezione(nome) {
  SEZIONE = nome;
  $$('.voce').forEach((v) => v.classList.toggle('attiva', v.dataset.va === nome));
  $$('.sezione').forEach((s) => s.classList.toggle('attiva', s.dataset.sez === nome));

  // Il diario e' uno solo e si sposta: tenerne quattro significherebbe quattro
  // cronologie diverse, e non sapere piu' dove guardare.
  const slot = document.querySelector(`.sezione[data-sez="${nome}"] .slot-diario`);
  const pannello = $('#pannello-diario');
  if (slot) { slot.appendChild(pannello); pannello.style.display = ''; }
  else { pannello.style.display = 'none'; }

  // Anche l'avanzamento segue la sezione aperta.
  const sezione = document.querySelector(`.sezione[data-sez="${nome}"]`);
  const colonne = sezione.querySelector('.due-colonne');
  if (colonne) sezione.insertBefore($('#avanzamento'), colonne);
}

/* ── Cose che Python chiama sulla pagina ──────────────────────────────────── */

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
  if (b.includes('✓') || b.includes('completat') || b.includes('scaricat') || b.includes('fatto')) return 'ok';
  if (b.includes('warning') || b.includes('attenzione')) return 'warn';
  return '';
}

window.cambiaStato = (stato) => {
  $('#spia').className = 'spia ' + (stato === 'idle' ? '' : stato);
  $('#stato').textContent = t('status.' + stato);
  const inCorso = stato === 'working';
  $$('.bottone.pieno, .bottone.contorno').forEach((b) => { b.disabled = inCorso; });
  if (!inCorso) {
    aggiornaSelezione();
    if (window.riabilitaBurn) window.riabilitaBurn();
    if (window.riabilitaPix) window.riabilitaPix();
  }
  $('#avanzamento').classList.toggle('visibile', inCorso);
  $('#barra').classList.toggle('indeterminata', inCorso);
  if (inCorso) $('#avanzamento-testo').textContent = t('status.working') + '…';
};

window.iniziaLavoro = (totale) => {
  $('#avanzamento').classList.add('visibile');
  $('#barra').classList.toggle('indeterminata', !totale);
  $('#barra').style.width = totale ? '0%' : '';
  $('#avanzamento-testo').textContent = totale
    ? t('lavoro.avanzo', { fatte: 0, totale }) : t('status.working') + '…';
  if (SEZIONE !== 'audio') return;
  SCHEDE.forEach((s, i) => {
    if (!s) return;
    s.classList.remove('in-corso', 'finita', 'fallita');
    const p = s.querySelector('.pastiglia');
    p.className = 'pastiglia';
    p.textContent = SCELTI.has(i) ? t('fase.attesa') : '';
  });
};

window.avanzaLavoro = (fatte, totale) => {
  $('#barra').classList.remove('indeterminata');
  $('#barra').style.width = Math.round((fatte / (totale || 1)) * 100) + '%';
  $('#avanzamento-testo').textContent = t('lavoro.avanzo', { fatte, totale });
};

window.tracciaFase = (i, fase) => {
  const s = SCHEDE[i];
  if (!s) return;
  s.classList.add('in-corso');
  const p = s.querySelector('.pastiglia');
  p.className = 'pastiglia lavora';
  p.textContent = t('fase.' + fase);
  // La traccia che lavora si porta sotto gli occhi da sola: su una playlist da
  // cinquanta brani, cercarla a mano sarebbe assurdo.
  s.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
};

window.tracciaFinita = (i, esito, errore) => {
  const s = SCHEDE[i];
  if (!s) return;
  s.classList.remove('in-corso');
  s.classList.add('finita');
  if (esito === 'fail') s.classList.add('fallita');
  const cl = esito === 'ok' ? 'ok' : esito === 'skip' ? 'skip' : 'fail';
  const p = s.querySelector('.pastiglia');
  p.className = 'pastiglia ' + cl;
  p.textContent = t('fase.' + cl);
  if (esito === 'fail' && errore) {
    avvisa(s.querySelector('.scheda-titolo').textContent + ' — ' + errore, 'fail');
  }
};

window.mostraRiepilogo = (dati) => {
  $('#avanzamento-testo').textContent = dati.testo;
  $('#barra').classList.remove('indeterminata');
  $('#barra').style.width = '100%';
  window.aggiungiRiga(dati.testo);
  avvisa(dati.testo, dati.ok ? 'ok' : 'fail');
};

window.mostraRisultati = (dati) => {
  const elenco = $('#risultati');
  elenco.innerHTML = '';
  elenco.dataset.pieno = '1';
  SCELTI.clear(); SCHEDE = [];
  if (!dati.voci || !dati.voci.length) { svuotaRisultati(); return; }

  dati.voci.forEach((v, i) => {
    const scheda = document.createElement('div');
    scheda.className = 'scheda';
    // A cascata invece che tutte insieme: su venti risultati e' la differenza
    // fra "e' apparso un muro" e "si sta popolando".
    scheda.style.animationDelay = Math.min(i * 22, 420) + 'ms';
    scheda.innerHTML =
      '<div class="casella"></div>' +
      '<div class="miniatura">' +
        '<div class="numero">' + String(i + 1).padStart(2, '0') + '</div>' +
        (v.durata ? '<div class="durata-sopra"></div>' : '') +
      '</div>' +
      '<div class="scheda-testo"><div class="scheda-titolo"></div>' +
        '<div class="scheda-sotto"></div></div>' +
      '<div class="pastiglia"></div><div class="filo"></div>';

    // I titoli arrivano da YouTube: si scrivono come testo, mai come HTML.
    scheda.querySelector('.scheda-titolo').textContent = v.titolo || '';
    if (v.durata) scheda.querySelector('.durata-sopra').textContent = v.durata;

    const sotto = scheda.querySelector('.scheda-sotto');
    [v.canale, v.viste ? v.viste + ' ▶' : ''].filter(Boolean).forEach((testo, k) => {
      if (k) {
        const punto = document.createElement('span');
        punto.className = 'punto'; punto.textContent = '·';
        sotto.appendChild(punto);
      }
      const span = document.createElement('span');
      span.textContent = testo;
      sotto.appendChild(span);
    });

    // La miniatura si aggiunge solo se arriva: un riquadro con l'icona rotta
    // sarebbe peggio del riquadro vuoto.
    if (v.miniatura) {
      const img = new Image();
      img.loading = 'lazy'; img.alt = '';
      img.onload = () => scheda.querySelector('.miniatura').prepend(img);
      img.src = v.miniatura;
    }

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

/* ── Stati vuoti ──────────────────────────────────────────────────────────── */

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
  e.dataset.pieno = ''; e.innerHTML = '';
  e.appendChild(statoVuoto(t('audio.results.empty')));
  $('#conteggio').textContent = '';
}

function svuotaDiario() {
  const d = $('#diario');
  d.dataset.pieno = ''; d.innerHTML = '';
  d.appendChild(statoVuoto(t('log.empty')));
}

function errore(messaggio) {
  window.aggiungiRiga(messaggio);
  avvisa(messaggio, 'fail');
  window.cambiaStato('error');
}

// Cio' che i file delle altre sezioni usano.
window.statoVuoto = statoVuoto;
window.avvisa = avvisa;
window.errore = errore;
window.t = t;
window.$ = $;

/* ── Sezione Audio ────────────────────────────────────────────────────────── */

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
  const prima = sel.value;
  sel.innerHTML = '';
  FORMATI[media].forEach((f) => {
    const o = document.createElement('option');
    o.value = f; o.textContent = f.toUpperCase();
    sel.appendChild(o);
  });
  if (FORMATI[media].includes(prima)) sel.value = prima;
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

/* ── Avvio ────────────────────────────────────────────────────────────────── */

function avvia() {
  window.addEventListener('pywebviewready', async () => {
    const dati = await window.pywebview.api.avvio();
    TESTI = dati.testi;
    LINGUA = dati.lingua;
    $('#lingua').value = LINGUA;
    $('#cartella').value = dati.cartella;
    $('#b-cartella').value = dati.cartella;

    // Il video di sfondo, se il file e' sul disco. Si aggiunge solo dopo che
    // il primo fotogramma e' pronto: senza, si vedrebbe un rettangolo nero
    // coprire i gradienti per il tempo del caricamento.
    if (dati.sfondo) {
      const v = $('#video-sfondo');
      v.addEventListener('loadeddata', () => v.classList.add('acceso'), { once: true });
      v.src = dati.sfondo;
    }

    aggiornaFormati();
    if (window.initBurn) window.initBurn();
    if (window.initPix) window.initPix();
    if (window.initClip) window.initClip();
    traduciPagina();
    cambiaSezione('audio');

    $$('.voce[data-va]').forEach((v) =>
      v.addEventListener('click', () => cambiaSezione(v.dataset.va)));

    $('#modo').addEventListener('change', aggiornaEtichettaIngresso);
    $('#media').addEventListener('change', aggiornaFormati);
    $('#analizza').addEventListener('click', analizza);
    $('#scarica').addEventListener('click', scarica);
    $('#svuota').addEventListener('click', svuotaDiario);
    $('#sfoglia').addEventListener('click', async () => {
      const e = await window.pywebview.api.scegli_cartella();
      if (e.ok && e.cartella) $('#cartella').value = e.cartella;
    });
    $('#ingresso').addEventListener('keydown', (e) => { if (e.key === 'Enter') analizza(); });
    $('#tutti').addEventListener('click', () => {
      SCHEDE.forEach((_, i) => SCELTI.add(i)); aggiornaSelezione();
    });
    $('#nessuno').addEventListener('click', () => { SCELTI.clear(); aggiornaSelezione(); });

    // Ctrl+Invio avvia l'operazione della sezione aperta: chi ha appena
    // riempito il modulo ha le mani sulla tastiera, non sul mouse.
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter' || !(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      ({ audio: scarica,
         burn:  () => $('#b-avvia').click(),
         pix:   () => $('#p-avvia').click(),
         clip:  () => $('#c-avvia').click() }[SEZIONE] || (() => {}))();
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
      cambiaSezione('audio');
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
}
