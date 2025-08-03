/**
 * SKJ Simulator Pro - Prototype (TryHackMe-like)
 * - Tabs navigation
 * - Load Markdown overview from embedded constant (from user's brief)
 * - Rooms (Semester/Modules)
 * - Challenges with simple canvas simulation and step tasks
 * - Leaderboard & Profile (LocalStorage)
 */

const $ = (sel, scope = document) => scope.querySelector(sel);
const $$ = (sel, scope = document) => Array.from(scope.querySelectorAll(sel));

const STORAGE_KEYS = {
  profile: "skj_profile",
  progress: "skj_progress",
  leaderboard: "skj_leaderboard"
};

const initialMarkdown = `
# APLIKASI SIMULASI SISTEM KEAMANAN JARINGAN (SKJ)
**Untuk Mendukung Pembelajaran di SMK Kelas XI dan XII**

## 🎯 Deskripsi Aplikasi
Aplikasi simulasi untuk memahami Sistem Keamanan Jaringan dengan simulasi interaktif, visualisasi, dan praktik aman.

## 📚 Modul Berdasarkan Semester
- Semester 1: Dasar Keamanan (Ancaman, Enkripsi, Firewall)
- Semester 2: Implementasi Dasar (Firewall, Scanning, AAA)
- Semester 3: Lanjutan (Pentest, IDS/IPS, PKI)
- Semester 4: Proyek (Desain, Simulasi Serangan, Laporan)

## 🛠️ Teknologi
Frontend: HTML5/JS, Canvas. Backend (ke depan): Flask/React. Simulasi: Docker/GNS3 (tahap lanjut).
`;

const ROOMS = [
  { id: "s1", title: "Semester 1 - Dasar Keamanan", badge: "Pemula", modules: [
    { id: "m1", title: "Modul 1: Pengenalan Ancaman", challenges: [
      { id: "c1", title: "Phishing Email Attack", tasks: [
        "Baca email mencurigakan pada panel simulasi",
        "Identifikasi indikator phishing",
        "Tandai sebagai phishing dan laporkan"
      ]},
      { id: "c2", title: "DDoS Attack Visualization", tasks: [
        "Amati lonjakan trafik pada canvas",
        "Aktifkan rate-limit",
        "Verifikasi penurunan trafik"
      ]}
    ]},
    { id: "m2", title: "Modul 2: Enkripsi Dasar", challenges: [
      { id: "c3", title: "Caesar Cipher", tasks: [
        "Masukkan pesan",
        "Geser kunci",
        "Bandingkan plaintext vs ciphertext"
      ]}
    ]},
    { id: "m3", title: "Modul 3: Firewall & Keamanan", challenges: [
      { id: "c4", title: "Packet Filtering", tasks: [
        "Tentukan rule allow/deny",
        "Blokir port 23 (Telnet)",
        "Uji paket dan lihat hasil"
      ]}
    ]}
  ]},
  { id: "s2", title: "Semester 2 - Implementasi Dasar", badge: "Dasar", modules: [
    { id: "m4", title: "Modul 4: Konfigurasi Firewall", challenges: [
      { id: "c5", title: "NAT & Port Forwarding", tasks: [
        "Tambahkan rule NAT",
        "Buat port forwarding 8080->80",
        "Verifikasi koneksi"
      ]}
    ]},
    { id: "m5", title: "Modul 5: Scanning & Monitoring", challenges: [
      { id: "c6", title: "Nmap Scan Virtual", tasks: [
        "Pilih target simulasi",
        "Jalankan scan",
        "Analisis hasil"
      ]}
    ]},
    { id: "m6", title: "Modul 6: Autentikasi & AAA", challenges: [
      { id: "c7", title: "Simulasi MFA", tasks: [
        "Masukkan password",
        "Verifikasi OTP",
        "Akses diberikan"
      ]}
    ]}
  ]},
  { id: "s3", title: "Semester 3 - Lanjutan", badge: "Menengah", modules: [
    { id: "m7", title: "Modul 7: Penetration Testing", challenges: [
      { id: "c8", title: "Eksploitasi Dasar", tasks: [
        "Enumerasi service",
        "Temukan CVE",
        "Eksploitasi aman"
      ]}
    ]},
    { id: "m8", title: "Modul 8: IDS/IPS & SIEM", challenges: [
      { id: "c9", title: "Snort Rule Basics", tasks: [
        "Aktifkan rule",
        "Picu alert",
        "Analisis log"
      ]}
    ]},
    { id: "m9", title: "Modul 9: PKI & Sertifikat", challenges: [
      { id: "c10", title: "TLS Handshake Visual", tasks: [
        "Lihat client hello",
        "Verifikasi sertifikat",
        "Negosiasi kunci"
      ]}
    ]}
  ]},
  { id: "s4", title: "Semester 4 - Proyek", badge: "Lanjut", modules: [
    { id: "m10", title: "Modul 10: Desain Keamanan", challenges: [
      { id: "c11", title: "Security Zone Planning", tasks: [
        "Buat DMZ",
        "Pisahkan VLAN",
        "Tambahkan redundansi"
      ]}
    ]},
    { id: "m11", title: "Modul 11: Cyber Attack Simulation", challenges: [
      { id: "c12", title: "Ransomware Scenario", tasks: [
        "Isolasi host",
        "Pulihkan dari backup",
        "Review kebijakan"
      ]}
    ]},
    { id: "m12", title: "Modul 12: Laporan Teknis", challenges: [
      { id: "c13", title: "Template Reporting", tasks: [
        "Isi temuan",
        "Tambahkan bukti",
        "Ekspor JSON (sementara)"
      ]}
    ]}
  ]}
];

// Basic LocalStorage helpers
function loadJSON(key, fallback){ try{ return JSON.parse(localStorage.getItem(key)) ?? fallback; }catch{ return fallback; } }
function saveJSON(key, val){ localStorage.setItem(key, JSON.stringify(val)); }

let API_BASE = "http://127.0.0.1:5000/api"; // default, akan autodetect

// State (local cache; sumber kebenaran di backend)
const profile = loadJSON(STORAGE_KEYS.profile, { name: "", id: null });
const progress = loadJSON(STORAGE_KEYS.progress, {
  points: 0,
  challengesDone: 0,
  streak: 0,
  completedChallengeIds: []
});
let leaderboard = [];

// Tabs
function initTabs(){
  $$(".tab-btn").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const id = btn.dataset.tab;
      $$(".tab").forEach(s=>s.classList.remove("active"));
      $("#"+id).classList.add("active");
    });
  });
}

// Markdown minimal renderer (very small subset)
function mdToHtml(md){
  // code blocks
  md = md.replace(/```([\s\S]*?)```/g, (_,code)=>`<pre><code>${escapeHtml(code)}</code></pre>`);
  // headers
  md = md.replace(/^### (.*)$/gm, "<h3>$1</h3>");
  md = md.replace(/^## (.*)$/gm, "<h2>$1</h2>");
  md = md.replace(/^# (.*)$/gm, "<h1>$1</h1>");
  // bold
  md = md.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  // lists
  md = md.replace(/^\- (.*)$/gm, "<li>$1</li>").replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");
  // paragraphs
  md = md.replace(/^(?!<h\d|<ul|<pre|<\/ul|<li|<\/li|<p|<strong|<code|<\/code|<\/pre)(.+)$/gm, "<p>$1</p>");
  return md;
}
function escapeHtml(s){ return s.replace(/[&<>"']/g, c=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

function renderDashboard(){
  $("#points").textContent = progress.points;
  $("#challengesDone").textContent = progress.challengesDone;
  $("#streak").textContent = progress.streak;
  $("#rank").textContent = progress.points >= 500 ? "Lanjut" : progress.points >= 200 ? "Menengah" : "Pemula";
  const totalChallenges = ROOMS.flatMap(r=>r.modules).flatMap(m=>m.challenges).length;
  const pct = Math.min(100, Math.round((progress.challengesDone/totalChallenges)*100));
  $("#progressBar").style.width = pct + "%";
  $("#markdown").innerHTML = mdToHtml(initialMarkdown);
}

async function fetchJSON(url, opt){
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opt });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

async function ensureUser(){
  if(profile.id) return profile;
  const name = $("#profileName")?.value?.trim() || profile.name || "Guest";
  const data = await fetchJSON(`${API_BASE}/users`, { method: "POST", body: JSON.stringify({ name }) });
  profile.id = data.id; profile.name = data.name;
  saveJSON(STORAGE_KEYS.profile, profile);
  return profile;
}

async function loadModules(){
  const mods = await fetchJSON(`${API_BASE}/modules`);
  // map ke struktur ROOMS-like untuk UI
  const roomsBySem = {};
  mods.forEach(m=>{
    roomsBySem[m.semester] = roomsBySem[m.semester] || { id:`s${m.semester}`, title:`Semester ${m.semester} -`, badge: m.semester===1?"Pemula":m.semester===2?"Dasar":m.semester===3?"Menengah":"Lanjut", modules: [] };
    roomsBySem[m.semester].modules.push({
      id: m.id, title: m.title, challenges: m.challenges.map(c=>({ id: c.id, title: c.title, tasks: JSON.parse(c.tasks_json) }))
    });
  });
  // gabungkan judul semester lengkap
  Object.values(roomsBySem).forEach(r=>{
    const semNum = parseInt(r.id.slice(1),10);
    const label = ["Dasar Keamanan","Implementasi Dasar","Lanjutan","Proyek"][semNum-1] || "";
    r.title = `Semester ${semNum} - ${label}`;
  });
  return Object.values(roomsBySem).sort((a,b)=>a.id.localeCompare(b.id));
}

let ROOMS_CACHE = [];

async function renderRooms(){
  const wrap = $("#roomsList");
  wrap.innerHTML = "";
  if(ROOMS_CACHE.length === 0){
    ROOMS_CACHE = await loadModules();
  }
  ROOMS_CACHE.forEach(room=>{
    const el = document.createElement("div");
    el.className = "room";
    el.innerHTML = `
      <div class="badge">${room.badge}</div>
      <h3>${room.title}</h3>
      <div class="meta">${room.modules.length} modul</div>
      <button class="primary">Lihat Modul</button>
      <div class="modules"></div>
    `;
    const btn = $("button.primary", el);
    const modulesBox = $(".modules", el);
    btn.addEventListener("click", ()=>{
      modulesBox.innerHTML = room.modules.map(m=>`
        <div class="challenge">
          <h3>${m.title}</h3>
          <div class="meta">${m.challenges.length} challenge</div>
          <button class="warn" data-mid="${m.id}" data-rid="${room.id}">Buka Challenges</button>
        </div>
      `).join("");
      $$(".warn", modulesBox).forEach(b=>{
        b.addEventListener("click", ()=>{
          openChallengesList(room.id, b.dataset.mid);
          // navigate to Challenges tab
          $$(".tab").forEach(s=>s.classList.remove("active"));
          $("#challenges").classList.add("active");
        });
      });
    });
    wrap.appendChild(el);
  });
}

async function openChallengesList(roomId, moduleId){
  const room = ROOMS_CACHE.find(r=>r.id===roomId);
  const mod = room.modules.find(m=>m.id===moduleId);
  const list = $("#challengeList");
  // sinkron status selesai dari backend
  const me = await ensureUser();
  const prog = await fetchJSON(`${API_BASE}/progress/${me.id}`);
  progress.points = prog.points;
  progress.completedChallengeIds = prog.completed;
  saveJSON(STORAGE_KEYS.progress, progress);
  list.innerHTML = mod.challenges.map(ch=>renderChallengeCard(ch)).join("");
  attachChallengeCardHandlers(mod.challenges);
}

// This function is now defined above with enhancements
function attachChallengeCardHandlers(challenges){
  $$("#challengeList .primary").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const ch = challenges.find(c=>c.id===btn.dataset.cid) ||
                 ROOMS.flatMap(r=>r.modules).flatMap(m=>m.challenges).find(c=>c.id===btn.dataset.cid);
      startChallenge(ch);
    });
  });
}

// Simple canvas simulation (traffic spikes / nodes)
let currentChallenge = null;
let currentTaskIndex = 0;

// Global network simulation variables
let networkTopology = null;
let networkControls = null;

// Helper function to determine challenge types
function getModuleChallengeTypes(module) {
  const types = new Set();
  module.challenges.forEach(challenge => {
    if (challenge.id.includes("phish") || challenge.id === "c1") {
      types.add("Phishing");
    } else if (challenge.id.includes("caesar") || challenge.id === "c3") {
      types.add("Enkripsi");
    } else if (challenge.id.includes("firewall") || challenge.id === "c4") {
      types.add("Firewall");
    } else if (["c2", "c5", "c6", "c11", "c12"].includes(challenge.id)) {
      types.add("Network");
    } else {
      types.add("Simulasi");
    }
  });
  return Array.from(types);
}

// Enhanced challenge card rendering
function renderChallengeCard(ch) {
  const completed = progress.completedChallengeIds.includes(ch.id);
  const simulationType = getSimulationType(ch.id);
  
  return `
    <div class="challenge">
      <div class="simulation-type">${simulationType}</div>
      <h3>${ch.title}</h3>
      <div class="meta">${ch.tasks.length} langkah</div>
      <div class="meta">${completed ? "✅ Selesai" : "⏳ Belum"}</div>
      <button class="primary" data-cid="${ch.id}">${completed?"Ulangi":"Mulai"}</button>
    </div>
  `;
}

function getSimulationType(challengeId) {
  const types = {
    "c1": "📧 Phishing",
    "c2": "🌐 Network", 
    "c3": "🔐 Crypto",
    "c4": "🛡️ Firewall",
    "c5": "🔀 NAT",
    "c6": "🔍 Scanning",
    "c7": "🔑 Auth",
    "c8": "⚔️ Pentest",
    "c9": "🚨 IDS",
    "c10": "🔒 PKI",
    "c11": "🏗️ Design",
    "c12": "🦠 Malware",
    "c13": "📄 Report"
  };
  return types[challengeId] || "🎯 Challenge";
}

function startChallenge(ch){
  currentChallenge = ch; currentTaskIndex = 0;
  $("#challengeTitle").textContent = ch.title;
  $("#taskList").innerHTML = ch.tasks.map((t,i)=>`<li data-i="${i}">${i===0?'<strong>':""}${t}${i===0?'</strong>':""}</li>`).join("");
  $("#challengePlayground").classList.remove("hidden");
  
  // Hide all simulation panels first
  $("#phishGame")?.classList.add("hidden");
  $("#caesarGame")?.classList.add("hidden");
  $("#firewallGame")?.classList.add("hidden");
  $("#networkSimContainer")?.classList.add("hidden");
  $("#simCanvas").style.display = "block";
  
  // Show appropriate simulation based on challenge type
  if (ch.id === "c1") {
    $("#phishGame").classList.remove("hidden");
  } else if (ch.id === "c3") {
    $("#caesarGame").classList.remove("hidden");
  } else if (ch.id === "c4") {
    $("#firewallGame").classList.remove("hidden");
  } else if (ch.id === "c2" || ch.id === "c5" || ch.id === "c6" || isNetworkChallenge(ch)) {
    // Network simulation challenges
    $("#simCanvas").style.display = "none";
    $("#networkSimContainer").classList.remove("hidden");
    initNetworkSimulation();
  }
  
  drawSimInit();
}

function isNetworkChallenge(challenge) {
  // Check if challenge requires network simulation
  const networkChallengeIds = ["c2", "c5", "c6", "c11", "c12"];
  return networkChallengeIds.includes(challenge.id) || 
         (challenge.simulation_type && challenge.simulation_type === "network");
}

function initNetworkSimulation() {
  const canvas = $("#networkCanvas");
  if (!canvas) return;
  
  // Initialize network topology if not already done
  if (!networkTopology) {
    networkTopology = new NetworkTopology(canvas);
  }
  
  // Initialize network controls if not already done
  if (!networkControls) {
    networkControls = new NetworkControls(networkTopology, "networkControlsContainer");
  }
  
  // Setup challenge-specific network scenario
  setupNetworkScenario(currentChallenge);
}

function setupNetworkScenario(challenge) {
  if (!networkTopology) return;
  
  // Clear existing topology
  networkTopology.clear();
  
  // Setup different scenarios based on challenge
  switch (challenge.id) {
    case "c2": // DDoS Attack Visualization
      setupDDoSScenario();
      break;
    case "c5": // NAT & Port Forwarding
      setupNATScenario();
      break;
    case "c6": // Nmap Scan Virtual
      setupNmapScenario();
      break;
    case "c11": // Security Zone Planning
      setupSecurityZoneScenario();
      break;
    case "c12": // Ransomware Scenario
      setupRansomwareScenario();
      break;
    default:
      setupBasicNetworkScenario();
  }
}

function setupDDoSScenario() {
  // Create a basic network with server under attack
  const server = networkTopology.addDevice("server", 400, 250, {
    name: "Web Server",
    ip: "192.168.1.10"
  });
  
  const firewall = networkTopology.addDevice("firewall", 200, 250, {
    name: "Firewall",
    ip: "192.168.1.1"
  });
  
  const router = networkTopology.addDevice("router", 100, 150, {
    name: "Internet Router",
    ip: "10.0.0.1"
  });
  
  // Add multiple attacking workstations
  for (let i = 0; i < 5; i++) {
    const attacker = networkTopology.addDevice("workstation", 50 + i * 30, 50 + i * 20, {
      name: `Attacker ${i + 1}`,
      ip: `10.0.0.${10 + i}`
    });
    networkTopology.addConnection(router, attacker);
  }
  
  networkTopology.addConnection(router, firewall);
  networkTopology.addConnection(firewall, server);
  
  // Start DDoS simulation
  setTimeout(() => {
    if (networkControls) {
      networkControls.startSimulation();
      networkControls.logEvent("DDoS attack simulation started");
    }
  }, 1000);
}

function setupNATScenario() {
  // Create NAT/Port forwarding scenario
  const router = networkTopology.addDevice("router", 300, 200, {
    name: "NAT Router",
    ip: "192.168.1.1"
  });
  
  const server = networkTopology.addDevice("server", 500, 200, {
    name: "Internal Server",
    ip: "192.168.1.100"
  });
  
  const client = networkTopology.addDevice("workstation", 100, 200, {
    name: "External Client",
    ip: "10.0.0.50"
  });
  
  networkTopology.addConnection(client, router);
  networkTopology.addConnection(router, server);
}

function setupNmapScenario() {
  // Create network for scanning
  const scanner = networkTopology.addDevice("workstation", 100, 300, {
    name: "Scanner PC",
    ip: "192.168.1.50"
  });
  
  const switch1 = networkTopology.addDevice("switch", 300, 200, {
    name: "Main Switch",
    ip: "192.168.1.2"
  });
  
  // Add various target devices
  const targets = [
    { type: "server", name: "Web Server", ip: "192.168.1.10", x: 500, y: 100 },
    { type: "server", name: "DB Server", ip: "192.168.1.11", x: 500, y: 200 },
    { type: "workstation", name: "Admin PC", ip: "192.168.1.20", x: 500, y: 300 },
    { type: "firewall", name: "Firewall", ip: "192.168.1.1", x: 400, y: 350 }
  ];
  
  targets.forEach(target => {
    const device = networkTopology.addDevice(target.type, target.x, target.y, {
      name: target.name,
      ip: target.ip
    });
    networkTopology.addConnection(switch1, device);
  });
  
  networkTopology.addConnection(scanner, switch1);
}

function setupSecurityZoneScenario() {
  // Create security zones (DMZ, Internal, External)
  const firewall = networkTopology.addDevice("firewall", 300, 250, {
    name: "Main Firewall",
    ip: "192.168.1.1"
  });
  
  // External zone
  const router = networkTopology.addDevice("router", 100, 250, {
    name: "Internet Router",
    ip: "10.0.0.1"
  });
  
  // DMZ zone
  const dmzServer = networkTopology.addDevice("server", 500, 150, {
    name: "DMZ Web Server",
    ip: "192.168.2.10"
  });
  
  // Internal zone
  const internalSwitch = networkTopology.addDevice("switch", 500, 350, {
    name: "Internal Switch",
    ip: "192.168.3.1"
  });
  
  const internalServer = networkTopology.addDevice("server", 650, 300, {
    name: "Internal DB",
    ip: "192.168.3.10"
  });
  
  const workstation = networkTopology.addDevice("workstation", 650, 400, {
    name: "Employee PC",
    ip: "192.168.3.20"
  });
  
  // Connect zones
  networkTopology.addConnection(router, firewall);
  networkTopology.addConnection(firewall, dmzServer);
  networkTopology.addConnection(firewall, internalSwitch);
  networkTopology.addConnection(internalSwitch, internalServer);
  networkTopology.addConnection(internalSwitch, workstation);
}

function setupRansomwareScenario() {
  // Create network showing ransomware spread
  const switch1 = networkTopology.addDevice("switch", 300, 250, {
    name: "Main Switch",
    ip: "192.168.1.1"
  });
  
  // Add multiple workstations (some infected)
  const workstations = [
    { name: "Patient PC", ip: "192.168.1.10", x: 150, y: 150, status: "error" },
    { name: "Admin PC", ip: "192.168.1.11", x: 450, y: 150, status: "error" },
    { name: "Backup PC", ip: "192.168.1.12", x: 150, y: 350, status: "active" },
    { name: "Server", ip: "192.168.1.100", x: 450, y: 350, status: "active" }
  ];
  
  workstations.forEach(ws => {
    const device = networkTopology.addDevice(
      ws.name.includes("Server") ? "server" : "workstation", 
      ws.x, ws.y, {
        name: ws.name,
        ip: ws.ip,
        status: ws.status
      }
    );
    networkTopology.addConnection(switch1, device);
  });
}

function setupBasicNetworkScenario() {
  // Default basic network
  const router = networkTopology.addDevice("router", 200, 200, {
    name: "Router",
    ip: "192.168.1.1"
  });
  
  const switch1 = networkTopology.addDevice("switch", 400, 200, {
    name: "Switch",
    ip: "192.168.1.2"
  });
  
  const server = networkTopology.addDevice("server", 600, 150, {
    name: "Server",
    ip: "192.168.1.10"
  });
  
  const workstation = networkTopology.addDevice("workstation", 600, 250, {
    name: "PC",
    ip: "192.168.1.20"
  });
  
  networkTopology.addConnection(router, switch1);
  networkTopology.addConnection(switch1, server);
  networkTopology.addConnection(switch1, workstation);
}

function drawSimInit(){
  const c = $("#simCanvas"); const ctx = c.getContext("2d");
  // Inisialisasi handler mini-game (sekali saat canvas dibangun)
  initPhishingGame();
  initCaesarGame();
  initFirewallGame();
  let t = 0;
  function loop(){
    ctx.fillStyle = "#07111f"; ctx.fillRect(0,0,c.width,c.height);
    // nodes
    const nodes = [
      {x:80, y:160, label:"Client"},
      {x:300, y:80, label:"FW"},
      {x:520, y:160, label:"Server"}
    ];
    ctx.strokeStyle = "#18406b"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(nodes[0].x, nodes[0].y); ctx.lineTo(nodes[1].x, nodes[1].y); ctx.lineTo(nodes[2].x, nodes[2].y); ctx.stroke();

    nodes.forEach(n=>{
      ctx.fillStyle = "#0f1b2d"; ctx.strokeStyle = "#1e2a40";
      ctx.beginPath(); ctx.arc(n.x, n.y, 22, 0, Math.PI*2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#00e5a8"; ctx.font = "12px Segoe UI";
      ctx.textAlign = "center"; ctx.fillText(n.label, n.x, n.y+38);
    });

    // packets
    const spike = currentChallenge?.id === "c2" ? (Math.sin(t/5)+1.2) : 0.5;
    for(let i=0;i<8*spike;i++){
      const p = i/8; // 0..1
      const x = 80 + (220 * ((t+i)%60)/60);
      const y = 160 - 80 * ((t+i)%60)/60;
      ctx.fillStyle = "#23d18b";
      ctx.fillRect(x, y, 6, 3);
    }
    t++;
    requestAnimationFrame(loop);
  }
  loop();
}

$("#btnCompleteTask").addEventListener("click", ()=>{
  if(!currentChallenge) return;
  const items = $$("#taskList li");
  items[currentTaskIndex].innerHTML = items[currentTaskIndex].textContent; // remove bold
  currentTaskIndex = Math.min(currentTaskIndex+1, items.length-1);
  items[currentTaskIndex].innerHTML = `<strong>${items[currentTaskIndex].textContent}</strong>`;
});
$("#btnFinishChallenge").addEventListener("click", async ()=>{
  if(!currentChallenge) return;
  const me = await ensureUser();
  // 50 poin per challenge selesai (contoh)
  await fetchJSON(`${API_BASE}/progress`, {
    method: "POST",
    body: JSON.stringify({ user_id: me.id, challenge_id: currentChallenge.id, status: "completed", points: 50 })
  });
  // refresh cache progress + UI
  const prog = await fetchJSON(`${API_BASE}/progress/${me.id}`);
  progress.points = prog.points;
  progress.completedChallengeIds = prog.completed;
  progress.challengesDone = prog.completed.length;
  saveJSON(STORAGE_KEYS.progress, progress);
  renderDashboard();
  openChallengesListForCurrentChallenge();
  $("#challengePlayground").classList.add("hidden");
  $("#phishGame")?.classList.add("hidden");
  currentChallenge = null;
});

function openChallengesListForCurrentChallenge(){
  // re-render current module list containing currentChallenge
  const all = ROOMS.flatMap(r=>r.modules).flatMap(m=>m.challenges);
  const ch = all.find(c=>c.id===currentChallenge?.id);
  const list = $("#challengeList");
  if(!ch){ // fallback refresh all challenges from first module
    const first = ROOMS[0].modules[0];
    list.innerHTML = first.challenges.map(renderChallengeCard).join("");
    attachChallengeCardHandlers(first.challenges);
    return;
  }
  // just refresh the displayed list by rebuilding it from existing DOM state
  const currentModuleChallenges = all.filter(c=>true); // simple refresh to show updated status
  list.innerHTML = currentModuleChallenges.slice(0, list.childElementCount || 6).map(renderChallengeCard).join("");
  attachChallengeCardHandlers(currentModuleChallenges);
}

// Leaderboard & Profile
async function renderLeaderboard(){
  const data = await fetchJSON(`${API_BASE}/leaderboard`);
  leaderboard = data;
  const list = $("#leaderboardList");
  list.innerHTML = leaderboard.map(x=>`<li class="leader"><span>${x.name}</span><span>${x.points} pts</span></li>`).join("");
  saveJSON(STORAGE_KEYS.leaderboard, leaderboard);
}

function initProfile(){
  const input = $("#profileName");
  input.value = profile.name || "";
  $("#saveProfile").addEventListener("click", async ()=>{
    profile.name = input.value.trim() || "Guest";
    saveJSON(STORAGE_KEYS.profile, profile);
    await ensureUser();
    await renderLeaderboard();
  });
}

// Initialize on load
async function detectBackend(){
  const ports = [5000,5050,5060,5070,5080,5090,5100];
  for(const p of ports){
    try{
      const res = await fetch(`http://127.0.0.1:${p}/api/leaderboard`, { method:"GET" });
      if(res.ok){
        API_BASE = `http://127.0.0.1:${p}/api`;
        console.log("Backend detected at", API_BASE);
        return true;
      }
    }catch(_e){}
  }
  console.warn("Backend not detected on known ports, staying offline mode.");
  return false;
}

function caesarShiftChar(ch, shift){
  const A = "A".charCodeAt(0), Z = "Z".charCodeAt(0);
  const a = "a".charCodeAt(0), z = "z".charCodeAt(0);
  const c = ch.charCodeAt(0);
  if(c>=A && c<=Z){ return String.fromCharCode(((c - A + shift + 2600) % 26) + A); }
  if(c>=a && c<=z){ return String.fromCharCode(((c - a + shift + 2600) % 26) + a); }
  return ch;
}
function caesarCipher(text, shift){
  return (text||"").split("").map(ch=>caesarShiftChar(ch, shift)).join("");
}
function initCaesarGame(){
  const plain = document.getElementById("caesarPlain");
  const shift = document.getElementById("caesarShift");
  const cipher = document.getElementById("caesarCipher");
  const btnEnc = document.getElementById("btnEncryptCaesar");
  const btnDec = document.getElementById("btnDecryptCaesar");
  const feedback = document.getElementById("caesarFeedback");
  if(!plain || !shift || !cipher || !btnEnc || !btnDec) return;
  feedback.textContent = ""; cipher.textContent = "";
  btnEnc.onclick = async ()=>{
    const s = parseInt(shift.value||"0",10);
    const out = caesarCipher(plain.value||"", s);
    cipher.textContent = out;
    feedback.textContent = "Encrypted dengan shift " + s + ". +10 poin parsial.";
    try{
      const me = await ensureUser();
      await fetchJSON(`${API_BASE}/progress`, { method:"POST", body: JSON.stringify({
        user_id: me.id, challenge_id: "c3", status: "started", points: 10
      })});
      const prog = await fetchJSON(`${API_BASE}/progress/${me.id}`);
      progress.points = prog.points; saveJSON(STORAGE_KEYS.progress, progress); renderDashboard();
    }catch(e){ console.warn(e); }
  };
  btnDec.onclick = ()=>{
    const s = parseInt(shift.value||"0",10);
    const out = caesarCipher(plain.value||"", -s);
    cipher.textContent = out;
    feedback.textContent = "Dekripsi percobaan dengan shift " + s + ".";
  };
}
function ipInCidr(ip, cidr){
  // very small helper: supports /24 only and exact ip matches for MVP
  if(!cidr || cidr.toLowerCase()==="any") return true;
  if(!cidr.includes("/")) return ip === cidr;
  const [net, maskStr] = cidr.split("/");
  const mask = parseInt(maskStr,10);
  if(mask !== 24) return ip === net; // simplistic for MVP
  const to3 = (s)=>s.split(".").slice(0,3).join(".");
  return to3(ip) === to3(net);
}
function matchPacket(rule, pkt){
  const okProto = rule.proto === pkt.proto;
  const okPort = Number(rule.port) === Number(pkt.port);
  const srcCidr = rule.src && rule.src.trim() ? rule.src.trim() : (rule.srcPreset||"any");
  const dstCidr = rule.dst && rule.dst.trim() ? rule.dst.trim() : (rule.dstPreset||"any");
  const okSrc = ipInCidr(pkt.src, srcCidr);
  const okDst = ipInCidr(pkt.dst, dstCidr);
  return okProto && okPort && okSrc && okDst;
}
function evalPacket(rules, pkt){
  // first-match wins
  for(const r of rules){
    if(matchPacket(r, pkt)) return r.action; // "allow" atau "deny"
  }
  return "allow"; // default allow jika tidak cocok (sederhana)
}

function initFirewallGame(){
  const el = document.getElementById("firewallGame");
  if(!el) return;
  const action = document.getElementById("fwAction");
  const proto = document.getElementById("fwProto");
  const port = document.getElementById("fwPort");
  const srcPreset = document.getElementById("fwSrcPreset");
  const src = document.getElementById("fwSrc");
  const dstPreset = document.getElementById("fwDstPreset");
  const dst = document.getElementById("fwDst");
  const addBtn = document.getElementById("btnAddRule");
  const list = document.getElementById("fwRuleList");
  const pktPreset = document.getElementById("fwPktPreset");
  const btnEval = document.getElementById("btnEval");
  const result = document.getElementById("fwResult");
  const feedback = document.getElementById("fwFeedback");

  if(!action || !proto || !port || !srcPreset || !dstPreset || !addBtn || !list || !pktPreset || !btnEval) return;

  // state local rule
  let rules = [];

  function renderRules(){
    list.innerHTML = rules.map((r,i)=>`
      <li>
        ${r.action.toUpperCase()} ${r.proto}:${r.port}
        ${r.srcPreset||"any"}${r.src?` (${r.src})`:""} -> ${r.dstPreset||"any"}${r.dst?` (${r.dst})`:""}
        <button data-i="${i}" class="mini danger" style="margin-left:6px">hapus</button>
      </li>
    `).join("");
    list.querySelectorAll("button.mini.danger").forEach(btn=>{
      btn.addEventListener("click", ()=>{
        const idx = parseInt(btn.getAttribute("data-i"),10);
        rules.splice(idx,1); renderRules();
      });
    });
  }

  addBtn.onclick = ()=>{
    const r = {
      action: action.value,
      proto: proto.value,
      port: parseInt(port.value||"0",10),
      srcPreset: srcPreset.value,
      src: src.value.trim(),
      dstPreset: dstPreset.value,
      dst: dst.value.trim()
    };
    if(!r.port || r.port<1 || r.port>65535){ feedback.textContent = "Port tidak valid (1-65535)."; return; }
    rules.push(r); renderRules();
    feedback.textContent = "Rule ditambahkan.";
  };

  btnEval.onclick = async ()=>{
    // preset format: "PROTO,PORT,SRC,DST"
    const [pProto, pPort, pSrc, pDst] = (pktPreset.value||"TCP,23,10.0.0.20,10.0.0.10").split(",");
    const pkt = { proto: pProto, port: parseInt(pPort,10), src: pSrc, dst: pDst };
    const decision = evalPacket(rules, pkt);
    result.textContent = `Hasil: ${decision.toUpperCase()} untuk ${pkt.proto}:${pkt.port} ${pkt.src} -> ${pkt.dst}`;

    // poin parsial target: Deny untuk Telnet (TCP:23) Client->Server
    const isTelnet = pkt.proto==="TCP" && pkt.port===23 && pkt.dst==="10.0.0.10";
    if(isTelnet && decision==="deny"){
      feedback.textContent = "Benar! Rule memblok Telnet (TCP:23). +20 poin.";
      try{
        const me = await ensureUser();
        await fetchJSON(`${API_BASE}/progress`, { method:"POST", body: JSON.stringify({
          user_id: me.id, challenge_id: "c4", status: "started", points: 20, meta: { type:"fw_deny_telnet" }
        })});
        const prog = await fetchJSON(`${API_BASE}/progress/${me.id}`);
        progress.points = prog.points; saveJSON(STORAGE_KEYS.progress, progress); renderDashboard();
      }catch(e){ console.warn(e); }
    }else{
      feedback.textContent = "Coba blok Telnet (TCP:23) ke Server agar mendapatkan poin parsial.";
    }
  };
}

function initPhishingGame(){
  const markBtn = document.getElementById("btnMarkPhish");
  const openBtn = document.getElementById("btnOpenLink");
  const feedback = document.getElementById("phishFeedback");
  if(!markBtn || !openBtn) return;
  // reset feedback setiap mulai challenge baru
  feedback.textContent = "";

  markBtn.onclick = async ()=>{
    if(currentChallenge?.id !== "c1") return;
    feedback.textContent = "Benar! Ini email phishing (domain mencurigakan paypa1.com). +20 poin.";
    try{
      const me = await ensureUser();
      // Tambah poin parsial 20 untuk tindakan benar
      await fetchJSON(`${API_BASE}/progress`, { method:"POST", body: JSON.stringify({
        user_id: me.id, challenge_id: "c1", status: "started", points: 20
      })});
      const prog = await fetchJSON(`${API_BASE}/progress/${me.id}`);
      progress.points = prog.points;
      saveJSON(STORAGE_KEYS.progress, progress);
      renderDashboard();
    }catch(e){ console.warn(e); }
  };

  openBtn.onclick = ()=>{
    if(currentChallenge?.id !== "c1") return;
    feedback.textContent = "Hati-hati! Ini tautan phishing. Coba tandai sebagai phishing.";
  };
}

window.addEventListener("DOMContentLoaded", async ()=>{
  initTabs();
  initProfile();
  const backendUp = await detectBackend();
  await ensureUser().catch(()=>{});
  // muat progress awal (jika backend tersedia)
  if(backendUp && profile.id){
    try{
      const prog = await fetchJSON(`${API_BASE}/progress/${profile.id}`);
      progress.points = prog.points;
      progress.completedChallengeIds = prog.completed;
      progress.challengesDone = prog.completed.length;
      saveJSON(STORAGE_KEYS.progress, progress);
    }catch(e){ console.warn("progress fetch failed:", e); }
  }
  renderDashboard();
  if(backendUp){
    await renderRooms();
    await renderLeaderboard();
  }else{
    // fallback: gunakan ROOMS statis lama jika backend belum nyala
    ROOMS_CACHE = ROOMS;
    await renderRooms();
  }
});
