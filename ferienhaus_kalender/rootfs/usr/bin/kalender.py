#!/usr/bin/env python3
"""
Casa dai Fiori – Calonico
Ferienhaus Buchungskalender
"""

from flask import Flask, jsonify, request, render_template_string, session, redirect, send_from_directory
import json
import os
import secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DATA_FILE = os.environ.get("DATA_FILE", "/share/ferienhaus_kalender_data.json")
OPTIONS_FILE = "/data/options.json"
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

DEFAULT_PERSONS = [
    {"name": "Person 1", "color": "#4A7C59"},
    {"name": "Person 2", "color": "#C0622A"},
    {"name": "Person 3", "color": "#7B5EA7"},
]

def load_options():
    if os.path.exists(OPTIONS_FILE):
        try:
            with open(OPTIONS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_persons():
    opts = load_options()
    persons = opts.get("persons", [])
    if persons:
        return persons
    return DEFAULT_PERSONS

def get_pin():
    opts = load_options()
    pin = str(opts.get("pin", "")).strip()
    return pin if pin else None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        pin = get_pin()
        if pin and not session.get("authed"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"bookings": []}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Casa dai Fiori – Calonico</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

  :root {
    --stone:   #F5F0E8;
    --stone2:  #EAE3D2;
    --earth:   #8B7355;
    --dark:    #2C2416;
    --green:   #4A7C59;
    --terracotta: #C0622A;
    --violet:  #7B5EA7;
    --white:   #FEFCF8;
    --border:  #D4C9B0;
    --shadow:  rgba(44,36,22,0.10);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', sans-serif;
    background: var(--stone);
    color: var(--dark);
    min-height: 100vh;
  }

  /* HEADER */
  header {
    background: var(--dark);
    background-image: linear-gradient(rgba(20,16,10,0.35), rgba(20,16,10,0.65)), url('/static/header.jpg');
    background-size: cover;
    background-position: center 70%;
    padding: 48px 32px 26px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }
  .header-title {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .header-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--earth);
  }
  header h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(22px, 4vw, 34px);
    font-weight: 400;
    color: var(--white);
    line-height: 1.15;
    text-shadow: 0 2px 10px rgba(0,0,0,0.4);
  }
  header h1 em {
    font-style: italic;
    color: var(--stone2);
    font-size: 0.7em;
    display: block;
    margin-top: 2px;
  }
  .header-nav {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .nav-btn {
    background: none;
    border: 1px solid rgba(255,255,255,0.2);
    color: var(--white);
    width: 36px; height: 36px;
    border-radius: 50%;
    font-size: 18px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.15s, border-color 0.15s;
  }
  .nav-btn:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.4); }
  .month-label {
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    color: var(--white);
    min-width: 160px;
    text-align: center;
  }

  /* LEGEND */
  .legend {
    background: var(--white);
    border-bottom: 1px solid var(--border);
    padding: 12px 32px;
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    align-items: center;
  }
  .legend-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--earth);
    margin-right: 4px;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
    cursor: pointer;
    padding: 5px 10px;
    border-radius: 20px;
    border: 1px solid transparent;
    transition: background 0.15s, border-color 0.15s;
    user-select: none;
  }
  .legend-item:hover { background: var(--stone2); }
  .legend-item.active { border-color: var(--border); background: var(--stone); }
  .legend-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .legend-name { font-size: 13px; font-weight: 500; }

  /* MAIN */
  main { padding: 28px 32px 48px; max-width: 1100px; margin: 0 auto; }

  /* CALENDAR GRID */
  .cal-header {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-bottom: 4px;
  }
  .cal-dow {
    text-align: center;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--earth);
    padding: 6px 0;
  }
  .cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
  }
  .cal-day {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    min-height: 100px;
    padding: 8px 8px 6px;
    display: flex;
    flex-direction: column;
    gap: 3px;
    transition: box-shadow 0.15s;
    position: relative;
  }
  .cal-day:hover { box-shadow: 0 2px 10px var(--shadow); }
  .cal-day.other-month { background: var(--stone2); opacity: 0.5; }
  .cal-day.today { border-color: var(--earth); border-width: 2px; }
  .day-num {
    font-size: 12px;
    font-weight: 600;
    color: var(--earth);
    line-height: 1;
    margin-bottom: 2px;
  }
  .cal-day.today .day-num {
    background: var(--dark);
    color: var(--white);
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px;
  }

  /* BOOKING CHIPS */
  .booking-chip {
    font-size: 10px;
    font-weight: 500;
    padding: 2px 7px;
    border-radius: 10px;
    color: #fff;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    opacity: 0.92;
    transition: opacity 0.1s, transform 0.1s;
    line-height: 1.5;
  }
  .booking-chip:hover { opacity: 1; transform: scale(1.03); }

  /* ADD BUTTON */
  .add-btn {
    position: absolute;
    bottom: 5px; right: 6px;
    width: 20px; height: 20px;
    border-radius: 50%;
    background: var(--stone2);
    border: 1px solid var(--border);
    color: var(--earth);
    font-size: 14px;
    line-height: 1;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.15s, background 0.15s;
  }
  .cal-day:hover .add-btn { opacity: 1; }
  .add-btn:hover { background: var(--earth); color: white; }

  /* MODAL */
  .modal-overlay {
    display: none;
    position: fixed; inset: 0;
    background: rgba(44,36,22,0.45);
    z-index: 100;
    align-items: center;
    justify-content: center;
    padding: 16px;
  }
  .modal-overlay.open { display: flex; }
  .modal {
    background: var(--white);
    border-radius: 16px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(44,36,22,0.25);
    overflow: hidden;
  }
  .modal-header {
    background: var(--dark);
    padding: 20px 24px 16px;
  }
  .modal-header h2 {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    color: var(--white);
    font-weight: 400;
  }
  .modal-header p {
    font-size: 12px;
    color: var(--stone2);
    margin-top: 3px;
  }
  .modal-body { padding: 24px; display: flex; flex-direction: column; gap: 18px; }

  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--earth);
  }
  .form-group input[type="date"] {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 9px 12px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--dark);
    background: var(--stone);
    outline: none;
    transition: border-color 0.15s;
    width: 100%;
  }
  .form-group input[type="date"]:focus { border-color: var(--earth); }

  .date-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  .person-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .person-pill {
    padding: 7px 16px;
    border-radius: 20px;
    border: 2px solid var(--border);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    background: transparent;
    color: var(--dark);
  }
  .person-pill.selected {
    color: white;
    border-color: transparent;
  }

  .form-group input[type="text"] {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 9px 12px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: var(--dark);
    background: var(--stone);
    outline: none;
    transition: border-color 0.15s;
    width: 100%;
  }
  .form-group input[type="text"]:focus { border-color: var(--earth); }

  .modal-footer {
    padding: 0 24px 24px;
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }
  .btn {
    padding: 9px 20px;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.15s;
  }
  .btn-ghost {
    background: transparent;
    color: var(--earth);
    border: 1px solid var(--border);
  }
  .btn-ghost:hover { background: var(--stone2); }
  .btn-primary {
    background: var(--dark);
    color: var(--white);
  }
  .btn-primary:hover { background: #3d3020; }
  .btn-danger {
    background: #c0392b;
    color: white;
    margin-right: auto;
  }
  .btn-danger:hover { background: #a93226; }

  /* TOAST */
  .toast {
    position: fixed;
    bottom: 24px; left: 50%;
    transform: translateX(-50%) translateY(80px);
    background: var(--dark);
    color: var(--white);
    padding: 10px 24px;
    border-radius: 24px;
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 8px 24px var(--shadow);
    transition: transform 0.3s ease;
    z-index: 200;
  }
  .toast.show { transform: translateX(-50%) translateY(0); }

  /* JAHRESÜBERSICHT LINK */
  .year-toggle {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
  }
  .year-toggle button {
    background: none;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 16px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: var(--earth);
    cursor: pointer;
    transition: background 0.15s;
  }
  .year-toggle button:hover { background: var(--stone2); }

  /* YEAR VIEW */
  .year-view { display: none; }
  .year-view.active { display: block; }
  .month-view { display: block; }
  .month-view.hidden { display: none; }

  .year-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
  .mini-month { background: var(--white); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
  .mini-month-title {
    font-family: 'Playfair Display', serif;
    font-size: 14px;
    margin-bottom: 8px;
    color: var(--dark);
  }
  .mini-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
  .mini-dow { font-size: 9px; text-align: center; color: var(--earth); font-weight: 600; padding: 2px 0; text-transform: uppercase; }
  .mini-day {
    height: 22px;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px;
    color: var(--dark);
    position: relative;
    cursor: pointer;
  }
  .mini-day:hover { background: var(--stone2); }
  .mini-day.has-booking { color: white; font-weight: 600; }
  .mini-day.other { opacity: 0.3; }
  .mini-day.today-mini { outline: 2px solid var(--earth); border-radius: 4px; }

  @media (max-width: 600px) {
    header { padding: 18px 16px 14px; }
    main { padding: 16px 10px 40px; }
    .legend { padding: 10px 16px; gap: 10px; }
    .cal-day { min-height: 70px; padding: 5px 5px 4px; }
    .booking-chip { font-size: 9px; }
    .year-grid { grid-template-columns: 1fr 1fr; }
  }
</style>
</head>
<body>

<header>
  <div class="header-title">
    <span class="header-eyebrow">Calonico · Valle Leventina</span>
    <h1>Casa dai Fiori <em>Buchungskalender</em></h1>
  </div>
  <div class="header-nav">
    <button class="nav-btn" onclick="changeMonth(-1)">&#8249;</button>
    <span class="month-label" id="monthLabel"></span>
    <button class="nav-btn" onclick="changeMonth(1)">&#8250;</button>
  </div>
</header>

<div class="legend">
  <span class="legend-label">Personen:</span>
  <div id="legendItems"></div>
</div>

<main>
  <div class="year-toggle">
    <button onclick="toggleView()">Jahresübersicht</button>
  </div>

  <div class="month-view" id="monthView">
    <div class="cal-header" id="calHeader"></div>
    <div class="cal-grid" id="calGrid"></div>
  </div>

  <div class="year-view" id="yearView">
    <div class="year-grid" id="yearGrid"></div>
  </div>
</main>

<!-- MODAL -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modalTitle">Aufenthalt eintragen</h2>
      <p id="modalSubtitle">Casa dai Fiori · Calonico</p>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>Wer?</label>
        <div class="person-pills" id="personPills"></div>
      </div>
      <div class="date-row">
        <div class="form-group">
          <label>Anreise</label>
          <input type="date" id="dateFrom">
        </div>
        <div class="form-group">
          <label>Abreise</label>
          <input type="date" id="dateTo">
        </div>
      </div>
      <div class="form-group">
        <label>Notiz (optional)</label>
        <input type="text" id="noteInput" placeholder="z.B. Sommerferien">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-danger" id="deleteBtn" onclick="deleteBooking()" style="display:none">Löschen</button>
      <button class="btn btn-ghost" onclick="closeModal()">Abbrechen</button>
      <button class="btn btn-primary" onclick="saveBooking()">Speichern</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const PERSONS = {{ persons_json | safe }};
const MONTHS_DE = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
const DAYS_DE = ['Mo','Di','Mi','Do','Fr','Sa','So'];

let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();
let bookings = [];
let editingId = null;
let selectedPerson = null;
let yearViewActive = false;
let visiblePersons = new Set(PERSONS.map(p => p.name));

async function fetchBookings() {
  const res = await fetch('/api/bookings');
  bookings = await res.json();
  render();
}

function render() {
  renderLegend();
  if (yearViewActive) renderYearView();
  else renderMonthView();
}

function renderLegend() {
  const container = document.getElementById('legendItems');
  container.style.display = 'flex';
  container.style.gap = '8px';
  container.style.flexWrap = 'wrap';
  container.innerHTML = PERSONS.map(p => `
    <div class="legend-item ${visiblePersons.has(p.name) ? 'active' : ''}"
         onclick="togglePerson('${p.name}')" title="Klicken zum Filtern">
      <div class="legend-dot" style="background:${p.color}"></div>
      <span class="legend-name">${p.name}</span>
    </div>
  `).join('');
}

function togglePerson(name) {
  if (visiblePersons.has(name)) {
    if (visiblePersons.size === 1) return;
    visiblePersons.delete(name);
  } else {
    visiblePersons.add(name);
  }
  render();
}

function renderMonthView() {
  document.getElementById('monthLabel').textContent = MONTHS_DE[currentMonth] + ' ' + currentYear;

  const header = document.getElementById('calHeader');
  header.innerHTML = DAYS_DE.map(d => `<div class="cal-dow">${d}</div>`).join('');

  const grid = document.getElementById('calGrid');
  grid.innerHTML = '';

  const firstDay = new Date(currentYear, currentMonth, 1);
  const lastDay = new Date(currentYear, currentMonth + 1, 0);
  const today = new Date(); today.setHours(0,0,0,0);

  let startDow = firstDay.getDay();
  if (startDow === 0) startDow = 7;

  // previous month fill
  for (let i = startDow - 1; i > 0; i--) {
    const d = new Date(currentYear, currentMonth, 1 - i);
    grid.appendChild(buildDayCell(d, true));
  }
  // current month
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = new Date(currentYear, currentMonth, d);
    grid.appendChild(buildDayCell(date, false));
  }
  // next month fill
  const cells = (startDow - 1) + lastDay.getDate();
  const remainder = cells % 7;
  if (remainder !== 0) {
    for (let i = 1; i <= 7 - remainder; i++) {
      const d = new Date(currentYear, currentMonth + 1, i);
      grid.appendChild(buildDayCell(d, true));
    }
  }
}

function buildDayCell(date, otherMonth) {
  const cell = document.createElement('div');
  cell.className = 'cal-day' + (otherMonth ? ' other-month' : '');
  const today = new Date(); today.setHours(0,0,0,0);
  if (date.getTime() === today.getTime()) cell.classList.add('today');

  const dayNum = document.createElement('div');
  dayNum.className = 'day-num';
  dayNum.textContent = date.getDate();
  cell.appendChild(dayNum);

  const dateStr = formatDate(date);
  const dayBookings = getBookingsForDate(dateStr);

  dayBookings.forEach(b => {
    if (!visiblePersons.has(b.person)) return;
    const p = PERSONS.find(x => x.name === b.person);
    const chip = document.createElement('div');
    chip.className = 'booking-chip';
    chip.style.background = p ? p.color : '#888';
    const isStart = b.from === dateStr;
    const isEnd = b.to === dateStr;
    chip.textContent = isStart ? b.person : (isEnd ? '↵ ' + b.person : '·');
    if (isStart && b.note) chip.title = b.note;
    chip.onclick = (e) => { e.stopPropagation(); openModal(dateStr, b.id); };
    cell.appendChild(chip);
  });

  const addBtn = document.createElement('button');
  addBtn.className = 'add-btn';
  addBtn.textContent = '+';
  addBtn.title = 'Eintrag hinzufügen';
  addBtn.onclick = (e) => { e.stopPropagation(); openModal(dateStr); };
  cell.appendChild(addBtn);

  cell.onclick = () => openModal(dateStr);
  return cell;
}

function getBookingsForDate(dateStr) {
  return bookings.filter(b => b.from <= dateStr && b.to >= dateStr);
}

function renderYearView() {
  const grid = document.getElementById('yearGrid');
  grid.innerHTML = '';
  for (let m = 0; m < 12; m++) {
    grid.appendChild(buildMiniMonth(currentYear, m));
  }
}

function buildMiniMonth(year, month) {
  const div = document.createElement('div');
  div.className = 'mini-month';
  div.innerHTML = `<div class="mini-month-title">${MONTHS_DE[month]}</div>`;

  const miniGrid = document.createElement('div');
  miniGrid.className = 'mini-grid';
  DAYS_DE.forEach(d => {
    const dow = document.createElement('div');
    dow.className = 'mini-dow';
    dow.textContent = d[0];
    miniGrid.appendChild(dow);
  });

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const today = new Date(); today.setHours(0,0,0,0);
  let startDow = firstDay.getDay(); if (startDow === 0) startDow = 7;

  for (let i = startDow - 1; i > 0; i--) {
    const cell = document.createElement('div');
    cell.className = 'mini-day other';
    const d = new Date(year, month, 1 - i);
    cell.textContent = d.getDate();
    miniGrid.appendChild(cell);
  }
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = new Date(year, month, d);
    const dateStr = formatDate(date);
    const dayBookings = getBookingsForDate(dateStr).filter(b => visiblePersons.has(b.person));
    const cell = document.createElement('div');
    cell.className = 'mini-day';
    if (date.getTime() === today.getTime()) cell.classList.add('today-mini');
    cell.textContent = d;
    if (dayBookings.length > 0) {
      cell.classList.add('has-booking');
      const p = PERSONS.find(x => x.name === dayBookings[0].person);
      cell.style.background = p ? p.color : '#888';
    }
    cell.onclick = () => {
      currentMonth = month;
      toggleView(true);
    };
    miniGrid.appendChild(cell);
  }

  div.appendChild(miniGrid);
  return div;
}

function toggleView(forceMonth) {
  yearViewActive = forceMonth ? false : !yearViewActive;
  document.getElementById('monthView').classList.toggle('hidden', yearViewActive);
  document.getElementById('yearView').classList.toggle('active', yearViewActive);
  document.querySelector('.year-toggle button').textContent = yearViewActive ? 'Monatsansicht' : 'Jahresübersicht';
  document.querySelector('.header-nav').style.display = yearViewActive ? 'none' : 'flex';
  render();
}

function changeMonth(dir) {
  currentMonth += dir;
  if (currentMonth > 11) { currentMonth = 0; currentYear++; }
  if (currentMonth < 0) { currentMonth = 11; currentYear--; }
  renderMonthView();
}

// MODAL
function openModal(dateStr, bookingId) {
  editingId = bookingId || null;
  const overlay = document.getElementById('modalOverlay');
  overlay.classList.add('open');

  // Person Pills
  const pills = document.getElementById('personPills');
  pills.innerHTML = PERSONS.map(p => `
    <button class="person-pill" data-name="${p.name}"
      style="--pill-color:${p.color}"
      onclick="selectPerson('${p.name}', '${p.color}', this)">
      ${p.name}
    </button>
  `).join('');

  if (bookingId) {
    const b = bookings.find(x => x.id === bookingId);
    if (b) {
      document.getElementById('dateFrom').value = b.from;
      document.getElementById('dateTo').value = b.to;
      document.getElementById('noteInput').value = b.note || '';
      selectPersonByName(b.person);
      document.getElementById('modalTitle').textContent = 'Aufenthalt bearbeiten';
      document.getElementById('deleteBtn').style.display = 'block';
    }
  } else {
    document.getElementById('dateFrom').value = dateStr;
    document.getElementById('dateTo').value = dateStr;
    document.getElementById('noteInput').value = '';
    selectedPerson = null;
    document.getElementById('modalTitle').textContent = 'Aufenthalt eintragen';
    document.getElementById('deleteBtn').style.display = 'none';
  }
}

function selectPersonByName(name) {
  const p = PERSONS.find(x => x.name === name);
  if (!p) return;
  document.querySelectorAll('.person-pill').forEach(el => {
    if (el.dataset.name === name) {
      el.classList.add('selected');
      el.style.background = p.color;
      selectedPerson = name;
    }
  });
}

function selectPerson(name, color, el) {
  document.querySelectorAll('.person-pill').forEach(p => {
    p.classList.remove('selected');
    p.style.background = 'transparent';
  });
  el.classList.add('selected');
  el.style.background = color;
  selectedPerson = name;
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  editingId = null;
  selectedPerson = null;
}

async function saveBooking() {
  const from = document.getElementById('dateFrom').value;
  const to = document.getElementById('dateTo').value;
  const note = document.getElementById('noteInput').value.trim();

  if (!from || !to) { showToast('Bitte Datum angeben'); return; }
  if (from > to) { showToast('Abreise muss nach Anreise sein'); return; }
  if (!selectedPerson) { showToast('Bitte Person wählen'); return; }

  const booking = { from, to, person: selectedPerson, note };
  if (editingId) booking.id = editingId;

  await fetch('/api/bookings', {
    method: editingId ? 'PUT' : 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(booking)
  });

  closeModal();
  showToast(editingId ? 'Eintrag aktualisiert' : 'Eintrag gespeichert');
  fetchBookings();
}

async function deleteBooking() {
  if (!editingId) return;
  await fetch('/api/bookings/' + editingId, { method: 'DELETE' });
  closeModal();
  showToast('Eintrag gelöscht');
  fetchBookings();
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

function formatDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

// Close modal on overlay click
document.getElementById('modalOverlay').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

fetchBookings();
</script>
</body>
</html>
"""

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Casa dai Fiori – Login</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600&family=Inter:wght@300;400;500;600&display=swap');
  * { box-sizing: border-box; margin:0; padding:0; }
  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(rgba(44,36,22,0.55), rgba(44,36,22,0.65)), url('/static/header.jpg') center/cover no-repeat;
    min-height: 100vh;
    display: flex; align-items: center; justify-content: center;
    padding: 20px;
  }
  .card {
    background: #FEFCF8;
    border-radius: 16px;
    padding: 36px 32px;
    max-width: 360px;
    width: 100%;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  }
  .eyebrow {
    font-size: 10px; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: #8B7355; margin-bottom: 6px;
  }
  h1 { font-family: 'Playfair Display', serif; font-weight: 400; font-size: 24px; color: #2C2416; margin-bottom: 24px; }
  input {
    width: 100%; padding: 12px 14px; border-radius: 8px;
    border: 1px solid #D4C9B0; background: #F5F0E8;
    font-size: 16px; text-align: center; letter-spacing: 0.1em;
    margin-bottom: 14px; outline: none;
  }
  input:focus { border-color: #8B7355; }
  button {
    width: 100%; padding: 11px; border-radius: 8px; border: none;
    background: #2C2416; color: #FEFCF8; font-weight: 600; font-size: 14px;
    cursor: pointer;
  }
  button:hover { background: #3d3020; }
  .error { color: #c0392b; font-size: 13px; margin-bottom: 12px; min-height: 16px; }
</style>
</head>
<body>
  <div class="card">
    <div class="eyebrow">Calonico · Valle Leventina</div>
    <h1>Casa dai Fiori</h1>
    <form method="POST" action="/login">
      <input type="password" name="pin" placeholder="PIN" autofocus inputmode="numeric">
      <div class="error">{{ error or '' }}</div>
      <button type="submit">Öffnen</button>
    </form>
  </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    pin = get_pin()
    if not pin:
        return redirect('/')
    error = None
    if request.method == 'POST':
        if request.form.get('pin', '').strip() == pin:
            session['authed'] = True
            session.permanent = True
            return redirect('/')
        error = 'Falscher PIN'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/')
@login_required
def index():
    import json as j
    persons_json = j.dumps(load_persons())
    return render_template_string(HTML, persons_json=persons_json)

@app.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    data = load_data()
    return jsonify(data['bookings'])

@app.route('/api/bookings', methods=['POST'])
@login_required
def add_booking():
    data = load_data()
    booking = request.json
    booking['id'] = str(int(datetime.now().timestamp() * 1000))
    data['bookings'].append(booking)
    save_data(data)
    return jsonify(booking), 201

@app.route('/api/bookings', methods=['PUT'])
@login_required
def update_booking():
    data = load_data()
    updated = request.json
    data['bookings'] = [b if b['id'] != updated['id'] else updated for b in data['bookings']]
    save_data(data)
    return jsonify(updated)

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    data = load_data()
    data['bookings'] = [b for b in data['bookings'] if b['id'] != booking_id]
    save_data(data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)
