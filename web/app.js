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

function cambiaSezione(nome, immediato) {
  if (nome === SEZIONE && !immediato) return;
  const uscente = document.querySelector('.sezione.attiva');
  SEZIONE = nome;
  $$('.voce').forEach((v) => v.classList.toggle('attiva', v.dataset.va === nome));

  // Prima la sezione che se ne va sfuma e arretra, poi entra la nuova
  // dall'altro lato: si capisce di essersi spostati, invece di ritrovarsi
  // altrove senza sapere come. Il ritardo e' quello dell'animazione di
  // uscita, non un numero scelto a caso.
  const entra = () => {
    $$('.sezione').forEach((s) => {
      s.classList.remove('uscita');
      s.classList.toggle('attiva', s.dataset.sez === nome);
    });
    spostaComuni(nome);
  };

  if (uscente && uscente.dataset.sez !== nome && !immediato) {
    uscente.classList.add('uscita');
    uscente.classList.remove('attiva');
    setTimeout(entra, 200);
  } else {
    entra();
  }
}

function spostaComuni(nome) {
  // Il diario e' uno solo e si sposta: tenerne quattro significherebbe
  // quattro cronologie diverse, e non sapere piu' dove guardare.
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
  if (inCorso) {
    // La barra riparte da zero, non da un valore finto: il primo numero vero
    // arriva dal motore entro una frazione di secondo.
    $('#barra').style.width = '0%';
    $('#barra').classList.remove('attesa');
    $('#avanzamento-testo').textContent = t('status.working') + '…';
  }
};

window.iniziaLavoro = (totale) => {
  $('#avanzamento').classList.add('visibile');
  // 'attesa' e' il caso in cui il motore non ha ancora detto quanto sia il
  // lavoro: la barra non finge un avanzamento, resta una striscia spenta
  // finche' non arriva il primo conteggio.
  $('#barra').classList.toggle('attesa', !totale);
  $('#barra').style.width = totale ? '0%' : '';
  $('#avanzamento-testo').textContent = totale
    ? t('lavoro.avanzo', { fatte: 0, totale }) : t('status.working') + '…';
  if (SEZIONE !== 'audio') return;
  SCHEDE.forEach((s, i) => {
    if (!s) return;
    s.classList.remove('in-corso', 'finita', 'fallita');
    const filo = s.querySelector('.filo');
    if (filo) filo.style.width = '0%';
    const p = s.querySelector('.pastiglia');
    p.className = 'pastiglia';
    p.textContent = SCELTI.has(i) ? t('fase.attesa') : '';
  });
};

/* L'avanzamento vero.
 *
 *   fatte, totale   le unita' del motore: tracce, fotogrammi, brani incisi.
 *   frazione        opzionale, da 0 a 1: il riempimento reale della barra
 *                   quando e' piu' fine del conteggio a unita' intere - i
 *                   byte di un download stanno dentro una traccia sola.
 *                   Se e' null il motore non sa quanto manca, e la barra
 *                   resta ferma invece di inventare.
 *   testo           opzionale: cosa sta lavorando in questo momento.
 */
window.avanzaLavoro = (fatte, totale, frazione = null, testo = '') => {
  const barra = $('#barra');
  const noto = frazione !== null && frazione !== undefined;
  barra.classList.toggle('attesa', !noto && !totale);
  if (noto) {
    barra.style.width = (Math.max(0, Math.min(1, frazione)) * 100).toFixed(1) + '%';
  } else if (totale) {
    barra.style.width = Math.round((fatte / totale) * 100) + '%';
  }
  const conteggio = totale ? t('lavoro.avanzo', { fatte, totale }) : '';
  $('#avanzamento-testo').textContent =
    [testo, conteggio].filter(Boolean).join('  ·  ') || t('status.working') + '…';
};

/* Quanto e' scaricata *questa* traccia, in byte: il filo sotto la scheda. */
window.tracciaAvanza = (i, frazione) => {
  const s = SCHEDE[i];
  if (!s) return;
  const filo = s.querySelector('.filo');
  if (filo) filo.style.width = (Math.max(0, Math.min(1, frazione)) * 100).toFixed(1) + '%';
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
  $('#barra').classList.remove('attesa');
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

const T_AVVIO = performance.now();

/* I passi dell'avvio, contati.
 *
 * Sono i pezzi che vanno messi insieme prima che l'interfaccia sia usabile,
 * ed e' un elenco chiuso e noto: per questo la barra del velo puo' dire un
 * numero vero invece di scorrere avanti e indietro. Ogni chiamata a
 * passoAvvio() e' un pezzo davvero finito, non un'attesa a tempo. */
const PASSI_AVVIO = 7;
let passiFatti = 0;

function passoAvvio() {
  passiFatti = Math.min(passiFatti + 1, PASSI_AVVIO);
  const b = document.querySelector('.avvio-barra span');
  if (b) b.style.width = (passiFatti / PASSI_AVVIO * 100).toFixed(0) + '%';
}

/* Toglie il velo di caricamento. Si puo' chiamare quante volte si vuole.
 *
 * L'elemento non viene rimosso subito ma dopo la dissolvenza, altrimenti
 * sparirebbe di scatto; e viene rimosso davvero, non solo nascosto, perche'
 * un rettangolo a tutto schermo che resta nell'albero e' un rischio inutile
 * per i clic.
 *
 * I 500 ms minimi non sono un'attesa finta: su una macchina veloce la pagina
 * e' pronta in un attimo, e un velo che appare e sparisce in cinquanta
 * millesimi si vede come uno sfarfallio, non come un caricamento. */
function togliVelo() {
  const v = document.getElementById('velo-avvio');
  if (!v || v.dataset.uscita) return;
  v.dataset.uscita = '1';
  const resta = Math.max(0, 500 - (performance.now() - T_AVVIO));
  setTimeout(() => {
    v.classList.add('via');
    setTimeout(() => v.remove(), 600);
  }, resta);
}

function avvia() {
  /* Se l'apertura si inceppa - un errore nel motore, una chiamata che non
   * torna - il velo deve comunque andarsene: meglio un'interfaccia a meta',
   * che si vede e si puo' chiudere, che una schermata di caricamento
   * perpetua. */
  setTimeout(togliVelo, 12000);
  passoAvvio();                       // 1. la pagina e i suoi script ci sono

  window.addEventListener('pywebviewready', async () => {
    passoAvvio();                     // 2. il ponte con Python risponde
    const dati = await window.pywebview.api.avvio();
    passoAvvio();                     // 3. testi, lingua e cartelle sono arrivati
    // La finestra adesso e' sullo schermo, quindi i fotogrammi ripartono: al
    // primo davvero composto si dice a Python di togliere l'immagine di
    // caricamento. Due requestAnimationFrame annidati perche' il primo finisce
    // il fotogramma in corso e il secondo comincia quello dopo, a disegno
    // fatto.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      try { window.pywebview.api.dipinta(); } catch (e) { /* la rete di
        sicurezza in Python la toglie comunque */ }
    }));
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
    passoAvvio();                     // 4. la sezione Audio e' pronta
    if (window.initBurn) window.initBurn();
    if (window.initPix) window.initPix();
    if (window.initClip) window.initClip();
    passoAvvio();                     // 5. e anche le altre tre
    traduciPagina();
    if (window.potenziaTendine) window.potenziaTendine();
    passoAvvio();                     // 6. tutto e' nella lingua giusta
    cambiaSezione('audio', true);

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

    // Ultima riga: da qui l'interfaccia e' disegnata, tradotta e reattiva.
    // Toglierlo prima avrebbe scoperto un'interfaccia che non risponde ancora
    // ai clic, che e' peggio di un attimo di attesa in piu'.
    passoAvvio();                     // 7. risponde ai comandi: si puo' usare
    togliVelo();
  });
}
