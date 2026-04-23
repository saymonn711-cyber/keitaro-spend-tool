#!/usr/bin/env python3
"""
Meta Ads → Keitaro Spend Tool
Запусти: python3 keitaro_tool.py
Потом открой браузер: http://localhost:8765
"""

import http.server
import json
import urllib.request
import urllib.error
import webbrowser
import threading
import os
import sys
from urllib.parse import urlparse, parse_qs

import os
PORT = int(os.environ.get('PORT', 8765))

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Meta → Keitaro Spend</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Unbounded:wght@400;700;900&display=swap');
  :root {
    --bg:#0a0a0f;--surface:#12121a;--card:#1a1a26;--border:#2a2a3a;
    --accent:#00e5ff;--accent2:#7b2fff;--green:#00ff88;--red:#ff4466;
    --text:#e8e8f0;--muted:#6a6a8a;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace;min-height:100vh;padding:32px 16px}
  .header{text-align:center;margin-bottom:36px}
  .header h1{font-family:'Unbounded',sans-serif;font-size:clamp(1.3rem,4vw,2rem);font-weight:900;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.02em;margin-bottom:8px}
  .header p{color:var(--muted);font-size:.75rem}
  .steps{display:flex;max-width:700px;margin:0 auto 36px;position:relative}
  .steps::before{content:'';position:absolute;top:18px;left:10%;width:80%;height:2px;background:var(--border);z-index:0}
  .step{flex:1;text-align:center;position:relative;z-index:1}
  .step-circle{width:36px;height:36px;border-radius:50%;border:2px solid var(--border);background:var(--bg);display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-family:'Unbounded',sans-serif;font-size:.75rem;font-weight:700;color:var(--muted);transition:all .3s}
  .step.active .step-circle{border-color:var(--accent);color:var(--accent);box-shadow:0 0 12px rgba(0,229,255,.3)}
  .step.done .step-circle{border-color:var(--green);background:var(--green);color:#000}
  .step-label{font-size:.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
  .step.active .step-label{color:var(--accent)}
  .step.done .step-label{color:var(--green)}
  .panel{max-width:700px;margin:0 auto;display:none}
  .panel.active{display:block}
  .card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:16px}
  .card-title{font-family:'Unbounded',sans-serif;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:20px}
  label{display:block;font-size:.7rem;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:.07em}
  input[type=text],input[type=password]{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:11px 14px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:.8rem;transition:border-color .2s;margin-bottom:16px}
  input[type=text]:focus,input[type=password]:focus{outline:none;border-color:var(--accent)}
  .upload-zone{border:2px dashed var(--border);border-radius:12px;padding:40px 24px;text-align:center;cursor:pointer;transition:all .2s;background:var(--surface);position:relative}
  .upload-zone:hover,.upload-zone.drag{border-color:var(--accent);background:rgba(0,229,255,.04)}
  .upload-zone input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
  .upload-icon{font-size:2.2rem;margin-bottom:10px}
  .upload-zone h3{font-family:'Unbounded',sans-serif;font-size:.82rem;font-weight:700;margin-bottom:5px}
  .upload-zone p{font-size:.7rem;color:var(--muted)}
  .file-ready{display:none;align-items:center;gap:12px;background:rgba(0,255,136,.06);border:1px solid rgba(0,255,136,.25);border-radius:10px;padding:14px 18px;margin-top:14px}
  .file-ready.show{display:flex}
  .file-ready span{font-size:.75rem;color:var(--green)}
  .file-ready .fname{color:var(--text);font-weight:500}
  .btn{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;border-radius:10px;padding:12px 28px;font-family:'Unbounded',sans-serif;font-size:.75rem;font-weight:700;cursor:pointer;transition:opacity .15s,transform .1s;text-transform:uppercase;letter-spacing:.06em;width:100%}
  .btn:hover{opacity:.88;transform:translateY(-1px)}
  .btn:active{transform:translateY(0)}
  .btn:disabled{opacity:.4;cursor:not-allowed;transform:none}
  .btn-secondary{background:var(--surface);color:var(--text);border:1px solid var(--border)}
  .btn-secondary:hover{border-color:var(--accent);color:var(--accent)}
  .error-box{display:none;background:rgba(255,68,102,.08);border:1px solid rgba(255,68,102,.3);border-radius:8px;padding:12px 16px;font-size:.73rem;color:var(--red);margin-bottom:14px}
  .error-box.show{display:block}
  .progress-wrap{display:none;margin-bottom:16px}
  .progress-wrap.show{display:block}
  .progress-info{display:flex;justify-content:space-between;font-size:.68rem;color:var(--muted);margin-bottom:8px}
  .progress-bar-bg{background:var(--surface);border-radius:99px;height:6px;overflow:hidden}
  .progress-bar-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px;transition:width .3s;width:0%}
  .results-wrap{max-width:900px;margin:0 auto;display:none}
  .results-wrap.active{display:block}
  .stats-bar{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}
  .stat-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 20px;flex:1;min-width:130px}
  .stat-label{font-size:.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px}
  .stat-val{font-family:'Unbounded',sans-serif;font-size:1.2rem;font-weight:700;color:var(--accent)}
  .stat-val.green{color:var(--green)}
  .stat-val.purple{color:var(--accent2)}
  .table-wrap{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;margin-bottom:24px}
  .table-header{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border)}
  .table-header span{font-family:'Unbounded',sans-serif;font-size:.7rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.1em}
  table{width:100%;border-collapse:collapse}
  thead th{background:var(--surface);padding:10px 18px;text-align:left;font-size:.64rem;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;font-weight:500}
  tbody td{padding:12px 18px;border-top:1px solid var(--border);font-size:.78rem}
  tbody tr:hover td{background:rgba(255,255,255,.02)}
  .td-id{font-weight:700;color:var(--accent);font-size:.72rem}
  .td-name{color:var(--text)}
  .td-name.unknown{color:var(--muted);font-style:italic}
  .td-spend{font-family:'Unbounded',sans-serif;font-size:.88rem;font-weight:700;color:var(--green);text-align:right}
  .td-count{color:var(--muted);font-size:.7rem;text-align:center}
  .badge-error{display:inline-block;background:rgba(255,68,102,.12);color:var(--red);border-radius:4px;padding:2px 7px;font-size:.62rem;margin-left:6px}
  .output-box{background:var(--surface);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:16px}
  .output-header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border)}
  .output-header span{font-size:.7rem;color:var(--muted)}
  .output-content{padding:16px;font-size:.75rem;line-height:1.9;white-space:pre;overflow-x:auto;max-height:260px;overflow-y:auto}
  .btn-row{display:flex;gap:10px}
  .btn-row .btn{width:auto;flex:1}
  .toast{position:fixed;bottom:24px;right:24px;background:var(--green);color:#000;padding:10px 20px;border-radius:8px;font-family:'Unbounded',sans-serif;font-size:.72rem;font-weight:700;transform:translateY(80px);opacity:0;transition:all .3s;z-index:100}
  .toast.show{transform:translateY(0);opacity:1}
  .send-btn{background:linear-gradient(135deg,var(--green),#00b360);color:#000;font-weight:700}
  .send-btn:hover{opacity:.88}
  .send-status{margin-top:12px;font-size:.72rem;line-height:1.8;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px;display:none}
  .send-status.show{display:block}
  .row-ok{color:var(--green)}
  .row-err{color:var(--red)}
  .row-skip{color:var(--muted)}
  .server-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,255,136,.08);border:1px solid rgba(0,255,136,.2);border-radius:20px;padding:4px 12px;font-size:.65rem;color:var(--green);margin-bottom:20px}
  .server-badge::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--green);display:inline-block;animation:pulse 1.5s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
</style>
</head>
<body>

<div class="header">
  <h1>META ADS → KEITARO</h1>
  <p>Загрузи CSV из Meta → получи спенд по кампаниям Keitaro с названиями</p>
</div>

<div class="steps">
  <div class="step active" id="step1"><div class="step-circle">1</div><div class="step-label">Keitaro API</div></div>
  <div class="step" id="step2"><div class="step-circle">2</div><div class="step-label">CSV файл</div></div>
  <div class="step" id="step3"><div class="step-circle">3</div><div class="step-label">Результат</div></div>
</div>

<div class="panel active" id="panel1">
  <div class="card">
    <div class="card-title">Подключение к Keitaro</div>
    <div class="server-badge">Локальный прокси активен — CORS решён</div>
    <div id="apiError" class="error-box"></div>
    <label>URL твоего Keitaro (без слеша в конце)</label>
    <input type="text" id="keitaroUrl" placeholder="https://io-net.space" />
    <label>API ключ</label>
    <input type="password" id="apiKey" placeholder="••••••••••••••••" />
    <button class="btn" id="connectBtn" onclick="testAndNext()">Проверить подключение →</button>
  </div>
</div>

<div class="panel" id="panel2">
  <div class="card">
    <div class="card-title">CSV из Meta Ads</div>
    <div id="csvError" class="error-box"></div>
    <div class="upload-zone" id="uploadZone">
      <input type="file" id="fileInput" accept=".csv" multiple>
      <div class="upload-icon">📊</div>
      <h3>Загрузи отчёты из Meta Ads</h3>
      <p>Можно несколько файлов сразу — перетащи или нажми для выбора</p>
    </div>
    <div class="file-ready" id="fileReady">
      <span>✅</span>
      <span>Загружено: <span class="fname" id="fileName"></span></span>
    </div>
    <br>
    <div style="margin-bottom:16px">
      <label>Дата отчёта</label>
      <input type="date" id="reportDate" style="width:100%;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:11px 14px;color:var(--text);font-family:'JetBrains Mono',monospace;font-size:.8rem;margin-bottom:0">
    </div>
    <div class="progress-wrap" id="progressWrap">
      <div class="progress-info">
        <span id="progressText">Обрабатываем...</span>
        <span id="progressCount"></span>
      </div>
      <div class="progress-bar-bg"><div class="progress-bar-fill" id="progressFill"></div></div>
    </div>
    <div class="btn-row">
      <button class="btn btn-secondary" onclick="goStep(1)">← Назад</button>
      <button class="btn" id="processBtn" onclick="processFile()" disabled>Обработать →</button>
    </div>
  </div>
</div>

<div class="results-wrap" id="resultsWrap">
  <div class="stats-bar" id="statsBar"></div>
  <div class="table-wrap">
    <div class="table-header"><span>Кампании Keitaro со спендом</span></div>
    <table>
      <thead>
        <tr>
          <th>ID Keitaro</th>
          <th>Название кампании</th>
          <th>Объявление (sub1)</th>
          <th style="text-align:center">Комиссия</th>
          <th style="text-align:center">Строк</th>
          <th style="text-align:right">Спенд USD</th>
        </tr>
      </thead>
      <tbody id="resultsBody"></tbody>
    </table>
  </div>
  <div class="output-box">
    <div class="output-header">
      <span>Готовый вывод (ID · Название · Спенд)</span>
      <button class="btn" onclick="copyOutput()" style="width:auto;padding:6px 14px;font-size:.65rem">📋 Копировать</button>
    </div>
    <div class="output-content" id="outputContent"></div>
  </div>
  <div class="btn-row" style="margin-bottom:16px">
    <button class="btn btn-secondary" onclick="restart()">← Новый файл</button>
    <button class="btn" onclick="copyOutput()">📋 Копировать всё</button>
  </div>
  <button class="btn send-btn" id="sendBtn" onclick="sendToKeitaro()">🚀 Отправить спенд в Keitaro</button>
  <div class="send-status" id="sendStatus"></div>
</div>

<div class="toast" id="toast">Скопировано!</div>

<script>
let csvData = [], keitaroCampaigns = {}, apiUrl = '', apiKeyVal = '';

// Ставим сегодняшнюю дату по умолчанию
document.addEventListener('DOMContentLoaded', () => {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('reportDate').value = today;
});

function goStep(n) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active','done'));
  document.getElementById('resultsWrap').classList.remove('active');
  for (let i = 1; i < n; i++) document.getElementById('step'+i).classList.add('done');
  document.getElementById('step'+n).classList.add('active');
  if (n===1) document.getElementById('panel1').classList.add('active');
  if (n===2) document.getElementById('panel2').classList.add('active');
  if (n===3) { document.getElementById('step3').classList.add('done'); document.getElementById('resultsWrap').classList.add('active'); }
}

async function testAndNext() {
  const errEl = document.getElementById('apiError');
  apiUrl = document.getElementById('keitaroUrl').value.trim().replace(/\/$/,'');
  apiKeyVal = document.getElementById('apiKey').value.trim();
  if (!apiUrl || !apiKeyVal) { showErr(errEl,'Заполни URL и API ключ'); return; }
  const btn = document.getElementById('connectBtn');
  btn.disabled = true; btn.textContent = 'Подключаемся...'; errEl.classList.remove('show');
  try {
    const resp = await fetch('/proxy/campaigns?url='+encodeURIComponent(apiUrl)+'&apikey='+encodeURIComponent(apiKeyVal));
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'HTTP '+resp.status);
    const campaigns = Array.isArray(data) ? data : (data.campaigns || data.data || []);
    keitaroCampaigns = {};
    // Keitaro использует alias как идентификатор (не числовой id)
    campaigns.forEach(c => {
      if (c.alias) keitaroCampaigns[c.alias] = { name: c.name, numId: c.id, token: c.token || '' };
      keitaroCampaigns[String(c.id)] = { name: c.name, numId: c.id, token: c.token || '' };
    });
    btn.textContent = `✅ Готово — ${campaigns.length} кампаний →`;
    setTimeout(() => goStep(2), 700);
  } catch(e) {
    showErr(errEl, 'Ошибка: ' + e.message);
    btn.disabled = false; btn.textContent = 'Проверить подключение →';
  }
}

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag'));
uploadZone.addEventListener('drop', e => { e.preventDefault(); uploadZone.classList.remove('drag'); if(e.dataTransfer.files.length) loadFiles(Array.from(e.dataTransfer.files)); });
fileInput.addEventListener('change', () => { if(fileInput.files.length) loadFiles(Array.from(fileInput.files)); });

async function loadFiles(files) {
  const errEl = document.getElementById('csvError');
  errEl.classList.remove('show');
  csvData = [];
  let errors = [];
  for (const file of files) {
    await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = ev => {
        try {
          const rows = parseCSV(ev.target.result);
          csvData = csvData.concat(rows);
        } catch(err) { errors.push(file.name + ': ' + err.message); }
        resolve();
      };
      reader.readAsText(file, 'UTF-8');
    });
  }
  if (errors.length && !csvData.length) { showErr(errEl, errors.join(' | ')); return; }
  if (csvData.length) {
    document.getElementById('fileName').textContent = files.length === 1
      ? files[0].name
      : files.length + ' файлов (' + csvData.length + ' строк)';
    document.getElementById('fileReady').classList.add('show');
    document.getElementById('processBtn').disabled = false;
  }
}


function parseCSV(text) {
  // Снимаем BOM если есть
  if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);

  const lines = text.trim().split('\n');
  if (lines.length < 2) throw new Error('Файл пустой');

  // Определяем разделитель
  const sep = lines[0].includes(';') ? ';' : ',';
  const hdr = splitLine(lines[0], sep).map(h => h.replace(/"/g,'').trim());

  // Поддержка двух форматов:
  // Формат 1 (стандартный): "Название кампании" + "Потраченная сумма (USD)"
  // Формат 2 (по аккаунтам): "Кампания" + "Расход"
  const ni = hdr.findIndex(h => /название.?кампани|campaign.?name|^кампани/i.test(h));
  const ai = hdr.findIndex(h => /название.?объявл|ad.?name/i.test(h)); // колонка с названием объявления
  const si = hdr.findIndex(h => /потраченн|spend|amount.?spent|^расход$/i.test(h));
  const di = hdr.findIndex(h => /начал|start|reporting.?starts/i.test(h));
  const ci = hdr.findIndex(h => /валют|currency/i.test(h));

  if (ni===-1) throw new Error('Не найдена колонка с названием. Колонки: ' + hdr.join(', '));
  if (si===-1) throw new Error('Не найдена колонка со спендом. Колонки: ' + hdr.join(', '));

  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const row = splitLine(lines[i], sep).map(h => h.replace(/^"|"$/g,'').trim());
    const rawName = (row[ni]||'').trim();
    if (!rawName) continue;

    let id = null;

    // Формат 1: PfWwFFWF/5 | NL PP Cross ...
    let commission = 0;
    const pipe = rawName.indexOf('|');
    if (pipe !== -1) {
      let rawId = rawName.substring(0, pipe).trim();
      const commMatch = rawId.match(/\/([0-9]+)$/);
      if (commMatch) commission = parseFloat(commMatch[1]) || 0;
      rawId = rawId.replace(/\/\d+$/, '').trim();
      if (rawId) id = rawId;
    }

    // Формат 2: c2njpmMR/5_kr_... или G2jLTsHt\5_uk_... (прямой или обратный слеш)
    if (!id) {
      const m = rawName.match(/^([A-Za-z0-9]+)[/\\]([0-9]+)[_\s]/);
      if (m) { id = m[1]; commission = parseFloat(m[2]) || 0; }
    }

    if (!id) continue;

    const spendRaw = (row[si]||'0').replace(/[^0-9.,]/g,'').replace(',','.');
    const spend = parseFloat(spendRaw) || 0;
    const date = di >= 0 ? (row[di]||'').replace(/"/g,'').trim() : '';
    const currency = ci >= 0 ? (row[ci]||'USD').replace(/"/g,'').trim().toUpperCase() : 'USD';
    const adName = ai >= 0 ? (row[ai]||'').replace(/^"|"$/g,'').trim() : '';
    rows.push({ id, spend, date, currency, commission, adName });
  }
  if (!rows.length) throw new Error('Нет строк с распознанным форматом ID');
  return rows;
}

function splitLine(line, sep=',') {
  const r=[]; let cur='', inQ=false;
  for(let i=0;i<line.length;i++){
    const ch=line[i];
    if(ch==='"'){inQ=!inQ;}
    else if(ch===sep&&!inQ){r.push(cur.trim());cur='';}
    else{cur+=ch;}
  }
  r.push(cur.trim()); return r;
}

async function processFile() {
  const btn = document.getElementById('processBtn');
  btn.disabled = true; btn.textContent = 'Обрабатываем...';
  const pw=document.getElementById('progressWrap'), pf=document.getElementById('progressFill');
  const pt=document.getElementById('progressText'), pc=document.getElementById('progressCount');
  pw.classList.add('show');

  // Загружаем курсы валют
  pt.textContent = 'Загружаем курсы валют...';
  const rates = await getExchangeRates();

  // Группируем только по alias — суммируем весь спенд по кампании
  const groups = {};
  for (const row of csvData) {
    const spendUSD = convertToUSD(row.spend, row.currency || 'USD', rates);
    const commission = row.commission || 0;
    const spendWithComm = spendUSD * (1 + commission / 100);
    if (!groups[row.id]) groups[row.id] = { id: row.id, spend: 0, count: 0, commission };
    groups[row.id].spend += spendWithComm;
    groups[row.id].count++;
  }

  const ids = Object.keys(groups);
  for (let i=0;i<ids.length;i++) {
    pc.textContent=`${i+1} / ${ids.length}`;
    pf.style.width=`${Math.round((i+1)/ids.length*100)}%`;
    pt.textContent=`Сопоставляем: ${ids[i]}`;
    await new Promise(r=>setTimeout(r,20));
  }
  pt.textContent='✅ Готово!'; pf.style.width='100%';

  const results = Object.keys(groups).map(id => {
    const g = groups[id];
    return {
      id: g.id,
      adName: '',
      name: keitaroCampaigns[g.id] ? keitaroCampaigns[g.id].name : null,
      keitaroId: keitaroCampaigns[g.id] ? keitaroCampaigns[g.id].numId : null,
      token: keitaroCampaigns[g.id] ? keitaroCampaigns[g.id].token : null,
      spend: g.spend,
      count: g.count,
      commission: g.commission || 0
    };
  }).sort((a,b)=>b.spend-a.spend);
  lastResults = results;

  renderResults(results);
  setTimeout(()=>{
    goStep(3); btn.disabled=false; btn.textContent='Обработать →'; pw.classList.remove('show');
  },500);
}

function renderResults(results) {
  const total = results.reduce((s,r)=>s+r.spend,0);
  const found = results.filter(r=>r.name).length;
  const notFound = results.length-found;
  document.getElementById('statsBar').innerHTML=`
    <div class="stat-card"><div class="stat-label">Итого спенд</div><div class="stat-val green">$${total.toFixed(2)}</div></div>
    <div class="stat-card"><div class="stat-label">ID кампаний</div><div class="stat-val">${results.length}</div></div>
    <div class="stat-card"><div class="stat-label">Найдено в Keitaro</div><div class="stat-val purple">${found}</div></div>
    ${notFound?`<div class="stat-card"><div class="stat-label">Не найдено</div><div class="stat-val" style="color:var(--red)">${notFound}</div></div>`:''}
  `;
  document.getElementById('resultsBody').innerHTML=results.map(r=>`
    <tr>
      <td class="td-id">${esc(r.id)}</td>
      <td class="td-name ${r.name?'':'unknown'}">${r.name?esc(r.name):'Не найдено в Keitaro'}${!r.name?'<span class="badge-error">?</span>':''}</td>
      <td class="td-name" style="font-size:.68rem;color:var(--muted)">${r.adName ? esc(r.adName) : '—'}</td>
      <td class="td-count">${r.commission ? '+'+r.commission+'%' : '—'}</td>
      <td class="td-count">${r.count}</td>
      <td class="td-spend">$${r.spend.toFixed(2)}</td>
    </tr>
  `).join('');
  document.getElementById('outputContent').textContent=
    results.map(r=>`${r.id}\t${r.name||'НЕ НАЙДЕНО'}\t$${r.spend.toFixed(2)}`).join('\n');
}

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function showErr(el,msg){el.textContent=msg;el.classList.add('show');}
function copyOutput(){
  const text=document.getElementById('outputContent').textContent;
  if(!text.trim())return;
  navigator.clipboard.writeText(text).then(()=>{
    const t=document.getElementById('toast');
    t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000);
  });
}
function restart(){
  csvData=[];
  document.getElementById('fileReady').classList.remove('show');
  document.getElementById('processBtn').disabled=true;
  document.getElementById('fileName').textContent='';
  document.getElementById('csvError').classList.remove('show');
  fileInput.value='';
  goStep(2);
}

// Хранение последних результатов для отправки
let lastResults = [];
let exchangeRates = {}; // кэш курсов валют

async function getExchangeRates() {
  if (Object.keys(exchangeRates).length) return exchangeRates;
  try {
    const resp = await fetch('/proxy/rates');
    const data = await resp.json();
    // data.rates содержит курсы к USD: { EUR: 0.92, UAH: 41.5, ... }
    // Нам нужно конвертировать X → USD, значит делим на rate
    exchangeRates = data.rates || {};
    return exchangeRates;
  } catch(e) {
    console.warn('Не удалось получить курсы валют:', e);
    return {};
  }
}

function convertToUSD(amount, currency, rates) {
  if (!currency || currency === 'USD') return amount;
  const rate = rates[currency];
  if (!rate) return amount; // если валюта не найдена — оставляем как есть
  return amount / rate; // rate = сколько единиц валюты в 1 USD
}

async function sendToKeitaro() {
  if (!lastResults.length) return;
  const btn = document.getElementById('sendBtn');
  const statusEl = document.getElementById('sendStatus');
  btn.disabled = true;
  btn.textContent = '⏳ Отправляем...';
  statusEl.classList.add('show');
  statusEl.innerHTML = '';

  const manualDate = document.getElementById('reportDate').value;
  const csvDate = csvData[0] ? csvData[0].date : '';
  const dateStr = manualDate || csvDate || new Date().toISOString().split('T')[0];

  let okCount = 0, errCount = 0, skipCount = 0;

  // Группируем по keitaroId — суммируем весь спенд по кампании
  const byId = {};
  for (const r of lastResults) {
    if (!r.name) {
      statusEl.innerHTML += `<div class="row-skip">⏭ ${esc(r.id)} — пропущено (не найдено в Keitaro)</div>`;
      skipCount++;
      continue;
    }
    if (!byId[r.keitaroId]) byId[r.keitaroId] = { name: r.name, spend: 0 };
    byId[r.keitaroId].spend += r.spend;
  }

  for (const [campaignId, group] of Object.entries(byId)) {
    try {
      const payload = {
        start_date: dateStr + ' 00:00',
        end_date: dateStr + ' 23:59',
        timezone: 'Europe/Kyiv',
        cost: group.spend.toFixed(2),
        currency: 'USD'
      };
      const resp = await fetch('/proxy/update_costs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: apiUrl, apikey: apiKeyVal, campaign_id: campaignId, payload })
      });
      const data = await resp.json().catch(() => ({}));
      if (resp.ok) {
        statusEl.innerHTML += `<div class="row-ok">✅ ${esc(group.name)} — $${group.spend.toFixed(2)} отправлено</div>`;
        okCount++;
      } else {
        statusEl.innerHTML += `<div class="row-err">❌ ${esc(group.name)} — ${esc(data.error || 'HTTP '+resp.status)}</div>`;
        errCount++;
      }
    } catch(e) {
      statusEl.innerHTML += `<div class="row-err">❌ ${esc(group.name)} — ${esc(e.message)}</div>`;
      errCount++;
    }
    statusEl.scrollTop = statusEl.scrollHeight;
    await new Promise(res => setTimeout(res, 200));
  }

  statusEl.innerHTML += `<br><strong>Итого: ✅ ${okCount} отправлено, ❌ ${errCount} ошибок, ⏭ ${skipCount} пропущено</strong>`;
  btn.disabled = false;
  btn.textContent = '🚀 Отправить снова';
  btn.style.background = 'linear-gradient(135deg, #ff4466, #ff8800)';
  btn.onclick = () => {
    if (confirm('⚠️ Повторная отправка добавит новые клики и спенд удвоится!\n\nВы уверены?')) {
      sendToKeitaro();
    }
  };
}
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # отключаем логи в терминале

    def do_GET(self):
        parsed = urlparse(self.path)

        # Главная страница
        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
            return

        # Прокси к Keitaro API
        if parsed.path == '/proxy/campaigns':
            params = parse_qs(parsed.query)
            keitaro_url = params.get('url', [''])[0]
            api_key = params.get('apikey', [''])[0]

            if not keitaro_url or not api_key:
                self._json_error(400, 'Не указан url или apikey')
                return

            target = keitaro_url.rstrip('/') + '/admin_api/v1/campaigns'
            req = urllib.request.Request(target, headers={
                'Api-Key': api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            })
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
            except urllib.error.HTTPError as e:
                self._json_error(e.code, f'Keitaro вернул HTTP {e.code}')
            except urllib.error.URLError as e:
                self._json_error(502, f'Не удалось подключиться к Keitaro: {e.reason}')
            except Exception as e:
                self._json_error(500, str(e))
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == '/proxy/fake_click':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                click_url = data.get('url', '')
                if not click_url:
                    self._json_error(400, 'Не указан url')
                    return
                print(f'Fake click URL: {click_url}', flush=True)
                req = urllib.request.Request(
                    click_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }
                )
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        resp.read()
                except urllib.error.HTTPError as e:
                    # 403/404 от оффера — клик всё равно записался в Keitaro
                    print(f'Fake click HTTP {e.code} (ok, click recorded)', flush=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f'Fake click error: {e}', flush=True)
                self._json_error(500, str(e))
            return

        if parsed.path == '/proxy/update_costs':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                keitaro_url = data.get('url', '').rstrip('/')
                api_key = data.get('apikey', '')
                campaign_id = data.get('campaign_id')
                payload = data.get('payload', {})

                if not keitaro_url or not api_key or not campaign_id:
                    self._json_error(400, 'Не хватает параметров')
                    return

                target = f"{keitaro_url}/admin_api/v1/campaigns/{campaign_id}/update_costs"
                req_body = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    target,
                    data=req_body,
                    headers={
                        'Api-Key': api_key,
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0'
                    },
                    method='POST'
                )
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        resp_body = resp.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(resp_body if resp_body else b'{"ok":true}')
                except urllib.error.HTTPError as e:
                    err_body = e.read().decode('utf-8', errors='replace')
                    self._json_error(e.code, f'Keitaro: HTTP {e.code} — {err_body[:200]}')
                except urllib.error.URLError as e:
                    self._json_error(502, f'Не удалось подключиться: {e.reason}')
            except Exception as e:
                self._json_error(500, str(e))
            return

        if parsed.path == '/proxy/check_clicks':
            params = parse_qs(parsed.query)
            keitaro_url = params.get('url', [''])[0]
            api_key = params.get('apikey', [''])[0]
            campaign_id = params.get('campaign_id', [''])[0]
            sub1 = params.get('sub1', [''])[0]
            date = params.get('date', [''])[0]
            target = keitaro_url.rstrip('/') + '/admin_api/v1/report/build'
            body = json.dumps({
                'range': {'from': date + ' 00:00', 'to': date + ' 23:59', 'timezone': 'Europe/Kyiv'},
                'filters': [
                    {'name': 'campaign_id', 'operator': '==', 'expression': campaign_id},
                    {'name': 'sub_id_1', 'operator': '==', 'expression': sub1}
                ],
                'metrics': ['clicks'],
                'grouping': ['sub_id_1']
            }).encode('utf-8')
            req = urllib.request.Request(target, data=body, headers={
                'Api-Key': api_key, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'
            }, method='POST')
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_body = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp_body)
            except Exception as e:
                self._json_error(500, str(e))
            return

        if parsed.path == '/proxy/fake_click':
            # GET запрос — для обратной совместимости
            params = parse_qs(parsed.query)
            click_url = params.get('url', [''])[0]
            if not click_url:
                self._json_error(400, 'Не указан url')
                return
            try:
                from urllib.parse import unquote
                # Убедимся что URL правильно декодирован
                click_url = unquote(click_url)
                print(f'Fake click URL: {click_url}', flush=True)
                req = urllib.request.Request(
                    click_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f'Fake click error: {e}', flush=True)
                self._json_error(500, str(e))
            return

        if parsed.path == '/proxy/rates':
            try:
                req = urllib.request.Request(
                    'https://open.er-api.com/v6/latest/USD',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self._json_error(500, str(e))
            return

        self.send_response(404)
        self.end_headers()

    def _json_error(self, code, message):
        body = json.dumps({'error': message}).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)


def main():
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)

    print('=' * 50)
    print('  Meta Ads → Keitaro Spend Tool')
    print('=' * 50)
    print(f'\n  ✅ Сервер запущен на порту {PORT}')
    print('  🌐 Открываю браузер...')
    print('\n  Чтобы остановить — нажми Ctrl+C')
    print('=' * 50)

    # Локально открываем браузер, на сервере пропускаем
    if not os.environ.get('PORT'):
        def open_browser():
            import time, subprocess
            time.sleep(1)
            url = f'http://localhost:{PORT}'
            chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
            ]
            opened = False
            for path in chrome_paths:
                if os.path.exists(path):
                    subprocess.Popen([path, url])
                    opened = True
                    break
            if not opened:
                print(f'\n  Открой вручную: http://localhost:{PORT}')
                webbrowser.open(url)
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n\n  Сервер остановлен. Пока!')
        server.shutdown()


if __name__ == '__main__':
    main()
