<script setup>
import { onMounted, ref, computed } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import rawDestinations from '../assets/data.json';

const mapContainer = ref(null);
let map = null;

// UI state
const isOverlayOpen = ref(true);
const isTop3Open = ref(false);
const isInfoModalOpen = ref(false);
const isNotificationVisible = ref(true);

const top3Destinations = computed(() => {
  return [...rawDestinations]
    .map(d => ({ ...d, index: Number(d.index) }))
    .filter(d => Number.isFinite(d.index))
    .sort((a, b) => b.index - a.index)
    .slice(0, 3);
});

const lastUpdated = computed(() => rawDestinations?.[0]?.last_updated ?? null);

// data preparation
const countryData = {};

rawDestinations.forEach(dest => {
  const code = dest.country_code; 
  if (!countryData[code]) 
    countryData[code] = { name: dest.country_name, totalIndex: 0, locations: [] };
  
  countryData[code].locations.push(dest);
}); 

Object.keys(countryData).forEach(code => {
    const country = countryData[code];

    const sortedLocs = country.locations.sort((a, b) => b.index - a.index);
    const topScore = sortedLocs[0].index;
    
    let otherSums = 0;
    for (let i = 1; i < sortedLocs.length; i++)
        otherSums += sortedLocs[i].index;

    country.totalIndex = topScore + (otherSums * 0.15);
    country.totalIndex = Math.round(country.totalIndex * 10) / 10;
});

function getColor(d) {
    if (d === null || d === undefined) return '#cbd5e1'; 

    return d >= 90  ? '#800026' : 
           d >= 60  ? '#bd0026' : 
           d >= 40  ? '#e31a1c' : 
           d >= 20  ? '#fc4e2a' : 
           d >= 12  ? '#fd8d3c' : 
           d >= 8   ? '#feb24c' : 
           d >= 4   ? '#fed976' : 
           d >= 1   ? '#ffe128' : 
                      '#fff2a8';  // score 0
}

function styleFeature(feature) {
    const countryCode = feature.id;
    const hasData = countryData[countryCode];
    const score = !hasData ? null : hasData.totalIndex;

    return {
        fillColor: getColor(score),
        weight: 1,
        opacity: 1,
        color: '#ffffff',
        dashArray: '',
        fillOpacity: 1
    };
}

// interactions
function onEachFeature(feature, layer) {
    const countryCode = feature.id;
    const myData = countryData[countryCode];

    if (myData) {
        layer.on('click', (e) => {
            let popupContent = `
            <div style="text-align:center; min-width:180px; font-family: sans-serif;">
                <h3 style="margin:0 0 5px 0; color:#084594; border-bottom: 2px solid #eee; padding-bottom:5px;">
                ${myData.name}
                </h3>
                <div style="background:#f1f5f9; padding:8px; border-radius:6px; margin-bottom:12px;">
                <span style="font-size:0.85rem; color:#64748b; display:block">Indice Nazionale</span>
                <strong style="font-size:1.4rem; color:#0f172a">${myData.totalIndex}</strong>
                </div>
                <div style="text-align:left; max-height:150px; overflow-y:auto;">
            `;
            
            // city list
            myData.locations.forEach(loc => {
                const isChampion = loc.index === myData.locations[0].index;
                const style = isChampion ? "font-weight:700; color:#084594" : "color:#334155";
                
                popupContent += `
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #f0f0f0; padding:4px 0; font-size:0.9rem;">
                    <span style="${style}">${loc.name}</span>
                    <span style="background:#e2e8f0; padding:0 6px; border-radius:4px; font-size:0.8rem">${loc.index}</span>
                </div>`;
            });
            
            popupContent += `</div></div>`;
            
            L.popup()
                .setLatLng(e.latlng)
                .setContent(popupContent)
                .openOn(map);

            this.setStyle({ weight: 2, color: '#6b7280' });
        });

        layer.on('mouseover', function() {
            this.setStyle({ weight: 2, color: '#9ca3af' });
            this.bringToFront();
        });

        layer.on('mouseout', function() {
            this.setStyle({ weight: 1, color: '#ffffff' });
        });
    }
}

// initialization
onMounted(async () => {
  map = L.map(mapContainer.value, {
      center: [40, 10], 
      zoom: 3,
      minZoom: 2,
      maxBounds: [[-90, -180], [90, 180]],
      zoomControl: false 
  });
  
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  setTimeout(() => {
    hideNotification();
  }, 5000);

  map.on('click', hideNotification);
  map.on('dragstart', hideNotification);

  try {
    const response = await fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson');
    const geoJsonData = await response.json();

    L.geoJSON(geoJsonData, {
        style: styleFeature,
        onEachFeature: onEachFeature
    }).addTo(map);

  } catch (error) {
    console.error("Errore caricamento mappa:", error);
  }
});

function hideNotification() {
  isNotificationVisible.value = false;
}
</script>

<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <!-- Notification Toast -->
    <Transition name="notification">
      <div v-if="isNotificationVisible" class="notification-toast" @click="hideNotification">
        <span class="notification-icon">🔎</span>
        <span class="notification-text">Tocca sui paesi colorati per i dettagli.</span>
      </div>
    </Transition>

    <button 
      class="info-btn" 
      @click="isInfoModalOpen = true"
      aria-label="Informazioni e Metodologia"
    >
      <span class="info-btn-text">Come funziona?</span>
    </button>

    <div v-if="isInfoModalOpen" class="modal-backdrop" @click.self="isInfoModalOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Manuale di Sopravvivenza 🗺️</h2>
          <button class="modal-close" @click="isInfoModalOpen = false">×</button>
        </div>
        
        <div class="modal-body">
          <p class="modal-intro">
            Il <strong>Napoletani Index</strong> traccia l'interesse dei campani verso le mete estere usando i dati di ricerca Google.
            <strong>Non indica dove vivono</strong>, ma le mete che vorrebbero invadere.
          </p>
          
          <div class="modal-use-cases">
            <div class="use-case">
              <span class="uc-icon">🤝</span>
              <div class="uc-text">
                <strong>Vuoi fare a <em>questione</em>?</strong>
                <p>Punta alle zone <span class="c-red">Rosse</span>. Ci sarà un parcheggiatore abusivo in aeroporto.</p>
              </div>
            </div>
            <div class="use-case">
              <span class="uc-icon">🤫</span>
              <div class="uc-text">
                <strong>Vuoi evitare?</strong>
                <p>Punta alle zone <span class="c-white">Bianche</span> o <span class="c-yellow">Gialle</span>. Ideale per fingere di essere norvegese ed evitare quell'antropologia del caos descritta come 'calore' che il resto del mondo chiama 'reato di inquinamento acustico'.</p>
              </div>
            </div>
          </div>

          <hr class="modal-divider">

          <h3>La Scienza dietro l'Hype 🧪</h3>
          <p class="modal-text-sm">
            Come viene calcolato lo score (ed il colore) di un'intera nazione? Viene utilizzata la logica del <strong>"Più Ricercato + Bonus"</strong>:
          </p>
          <ul class="tech-list">
            <li>
              <strong>Il più ricercato:</strong> Lo score della nazione è dettato maggiormente dalla città più cercata (es. Amsterdam per l'Olanda).
            </li>
            <li>
              <strong>Il bonus volume:</strong> Viene aggiunto un pizzico (15%) del volume delle altre città. Così la Spagna (che ha tante mete come Ibiza, Madrid, Barcellona) ottiene uno score "spalmato" senza "truccare" i numeri.
            </li>
          </ul>

          <details class="tech-details">
            <summary>Dettagli per Nerd 🤓☝️</summary>
            <ul>
              <li><strong>Fonte:</strong> Google Trends (API)</li>
              <li><strong>Query:</strong> "Voli [Città]" + "Hotel [Città]"</li>
              <li><strong>Geo:</strong> Campania (IT-72)</li>
              <li><strong>Timeframe:</strong> Ultimi 3 mesi (Rolling)</li>
              <li><strong>Normalizzazione:</strong> Calibrato su "Milano" come costante nascosta.</li>

              <li><strong>Confrontabilità:</strong> Poiché Google non permette di confrontare 50 città insieme, sono analizzate a gruppi di 4 usando sempre "Milano" come metro di paragone comune (anchor) per allineare tutti i punteggi sulla stessa scala.</li>
              <li><strong>Tipo dato:</strong> Serie temporale; per ogni query viene calcolata la <em>media</em> dei punti nel timeframe (media degli <code>extracted_value</code>).</li>
              <li><strong>Formula indice (per città):</strong> <code>index = (mean(query) / mean(anchor)) * visual_scale</code> → poi arrotondato a 1 decimale.</li>
              <li><strong>Aggregazione per nazione (mappa):</strong> <code>score_country = top_city + 0.15 * sum(altre_città)</code> (poi arrotondato).</li>
              <li><strong>Limite interpretazione:</strong> Trends è un proxy di interesse (ricerche), non prenotazioni/arrivi reali; confronti tra batch diversi dipendono dall'ancora.</li>
            </ul>
          </details>

          <div class="modal-warning">
            ⚠️ <strong>Nota:</strong> L'indice misura il <em>desiderio</em> (ricerche), non la presenza fisica futura. Se vedi le Maldive rosse, stanno tutti sognando.
          </div>
        </div>
        
        <div class="modal-attribution">
          made by <a href="https://github.com/sansarc/napoletani-index" target="_blank" rel="noopener">sansarc</a>
        </div>
      </div>
    </div>

    <div class="attribution">
      made by <a href="https://github.com/sansarc/napoletani-index" target="_blank" rel="noopener">sansarc</a>
    </div>

    <button v-if="!isOverlayOpen" class="overlay-toggle" @click="isOverlayOpen = true">
      Legenda
    </button>

    <div v-if="isOverlayOpen" class="overlay">
      <div class="overlay-header">
        <div class="overlay-title">
          <h1>Napoletani Index</h1>
          <span class="overlay-subtitle">Dove sognano di andare in vacanza</span>
        </div>
        <button class="overlay-close" @click="isOverlayOpen = false">×</button>
      </div>

      <div class="legend">
        <div class="legend-title">Hype</div>
        <div class="legend-gradient-row">
          <span class="legend-axis-label">Deserto</span>
          <div class="legend-gradient"></div>
          <span class="legend-axis-label">Invasione</span>
        </div>
        
        <div class="legend-bins">
          <div class="legend-item"><span class="legend-swatch" style="background:#800026"></span><span class="legend-label">≥ 90 (Folla)</span></div>
          <div class="legend-item"><span class="legend-swatch" style="background:#bd0026"></span><span class="legend-label">60–89</span></div>

          <div class="legend-item"><span class="legend-swatch" style="background:#e31a1c"></span><span class="legend-label">40–59</span></div>
          <div class="legend-item"><span class="legend-swatch" style="background:#fc4e2a"></span><span class="legend-label">20–39</span></div>

          <div class="legend-item"><span class="legend-swatch" style="background:#fd8d3c"></span><span class="legend-label">12–19</span></div>
          <div class="legend-item"><span class="legend-swatch" style="background:#feb24c"></span><span class="legend-label">8–11</span></div>

          <div class="legend-item"><span class="legend-swatch" style="background:#fed976"></span><span class="legend-label">4–7</span></div>
          <div class="legend-item"><span class="legend-swatch" style="background:#ffe128"></span><span class="legend-label">1–3</span></div>

          <div class="legend-item"><span class="legend-swatch" style="background:#fff2a8"></span><span class="legend-label">0 (Pace)</span></div>
        </div>
      </div>

      <div v-if="isTop3Open" class="top3">
        <div class="top3-header">
          <div class="top3-title">Top 3 Destinazioni</div>
          <button class="top3-close" @click="isTop3Open = false">×</button>
        </div>
        <div class="top3-list">
          <div v-for="(d, i) in top3Destinations" :key="i" class="top3-item">
            <span class="top3-rank">#{{ i + 1 }}</span>
            <span class="top3-name">{{ d.name }}</span>
            <span class="top3-score">{{ d.index }}</span>
          </div>
        </div>
        <div v-if="lastUpdated" class="legend-updated" style="margin-top: 8px; text-align: right;">
          Aggiornato: {{ lastUpdated }}
        </div>
      </div>
      <button v-else class="top3-toggle" @click="isTop3Open = true">Top 3</button>

      <div v-if="lastUpdated" class="legend-updated legend-updated--bottom">
        Aggiornato: {{ lastUpdated }}
      </div>
    </div>
  </div>
</template>

<style scoped>
    /* =========================================
    NOTIFICATION TOAST
    ========================================= */

.notification-toast {
  position: absolute;
  bottom: auto;
  top: 50%;
  left: 50%;
  transform: translateX(-50%) translateY(-50%);
  z-index: 1001;
  background: rgba(255, 255, 255, 0.95);
  color: #1e293b;
  padding: 10px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.08);
  cursor: pointer;
  max-width: calc(100% - 40px);
  font-size: 0.85rem;
  font-weight: 500;
  transition: opacity 0.2s, transform 0.2s;
}

.notification-toast:hover {
  background: #ffffff;
  box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
}

.notification-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.notification-text {
  line-height: 1.4;
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(calc(-50% + 20px));
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(calc(-50% + 10px));
}

/* =========================================
   1. MODAL STYLES (INFO & USE CASES)
   ========================================= */

@keyframes pulse-attention {
  0% { box-shadow: 0 0 0 0 rgba(8, 69, 148, 0.4); transform: scale(1); }
  50% { box-shadow: 0 0 0 10px rgba(8, 69, 148, 0); transform: scale(1.05); }
  100% { box-shadow: 0 0 0 0 rgba(8, 69, 148, 0); transform: scale(1); }
}

.info-btn {
  position: absolute;
  top: 25px;
  left: 25px;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 999px;
  background: #084594;
  border: none;
  box-shadow: 0 4px 15px rgba(8, 69, 148, 0.3);
  font-weight: 700;
  font-size: 0.9rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: pulse-attention 2.5s infinite;
}

.info-btn:hover {
  transform: scale(1.05);
  background: #0a5bc4;
  box-shadow: 0 6px 20px rgba(8, 69, 148, 0.4);
  animation: none;
}

.info-btn-text {
  white-space: nowrap;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
  z-index: 2000;
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 550px; 
  border-radius: 20px;
  box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  animation: modalEnter 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalEnter {
  from { opacity: 0; transform: scale(0.95) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-header {
  padding: 20px 28px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem; 
  color: #111827;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #9ca3af;
  line-height: 1;
  padding: 0;
  transition: color 0.2s;
  display: flex;
  align-items: center;
}
.modal-close:hover { color: #111827; }

.modal-body {
  padding: 28px; 
  color: #4b5563;
  line-height: 1.6;
  overflow-y: auto;
  font-size: 1.05rem;
  flex: 1; 
}

.modal-intro {
  margin-top: -10px;
  margin-bottom: 24px;
}

/* USE CASES STYLING */
.modal-use-cases {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.use-case {
  display: flex;
  gap: 16px;
  background: #f9fafb;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
}

.use-case:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateY(-2px);
  border-color: #d1d5db;
}

.uc-icon {
  font-size: 2rem; 
  line-height: 1;
}

.uc-text strong {
  display: block;
  color: #111827;
  font-size: 1.1rem; 
  margin-bottom: 4px;
}

.uc-text p {
  margin: 0;
  font-size: 0.95rem;
  color: #6b7280;
}

.c-red { color: #d32f2f; font-weight: 700; }
.c-white { color: #9ca3af; font-weight: 700; }
.c-yellow { color: #f59e0b; font-weight: 700; }

.modal-divider {
  border: 0;
  border-top: 1px dashed #e5e7eb;
  margin: 24px 0;
}

.modal-body h3 {
  margin: 0 0 12px 0;
  font-size: 1.2rem; 
  color: #111827;
  font-weight: 800;
}

.modal-text-sm {
  font-size: 1rem;
  margin-bottom: 12px;
}

.tech-list {
  padding-left: 1.2rem;
  margin: 0 0 20px 0;
}

.tech-list li {
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.tech-details {
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
}

.tech-details summary {
  padding: 12px 16px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  list-style: none;
}
.tech-details summary::-webkit-details-marker { display: none; }
.tech-details summary::after { content: "+"; float: right; font-weight: bold; font-size: 1.2em; }
.tech-details[open] summary::after { content: "-"; }

.tech-details ul {
  padding: 0 16px 16px 32px;
  margin: 0;
  font-size: 0.9rem;
  color: #475569;
}
.tech-details li { margin-bottom: 6px; }

.tech-details code {
  font-size: 0.88em;              
  font-family: monospace;
  background: #e2e8f0;            
  color: #0f172a;
  padding: 0.12em 0.38em;
  border-radius: 6px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  white-space: normal;            
  word-break: break-word;
}

.modal-warning {
  background: #fffbeb;
  padding: 16px;
  border-radius: 8px;
  font-size: 0.95rem;
  border-left: 4px solid #f59e0b;
  color: #92400e;
  line-height: 1.5;
}

.modal-attribution {
  padding: 16px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
  font-size: 0.95rem;
  color: #94a3b8;
  background: white;
  flex-shrink: 0;
}

.modal-attribution a {
  color: #084594;
  font-weight: 700;
  text-decoration: none;
  margin-left: 0; 
}

.modal-attribution a:hover {
  text-decoration: underline;
}

/* =========================================
   2. MAP AND LEGEND STYLES 
   ========================================= */

.map-wrapper { position: relative; height: 100vh; width: 100vw; }
.map-container { height: 100%; width: 100%; z-index: 1; }

.overlay { 
  position: absolute; top: 25px; right: 25px; 
  background: rgba(255, 255, 255, 0.95); 
  padding: 20px; border-radius: 16px; 
  box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
  z-index: 1000; max-width: 300px; 
  backdrop-filter: blur(10px);
}
.overlay-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.overlay-title h1 { margin: 0 0 2px 0; font-size: 1.4rem; color: #1e293b; letter-spacing: -0.5px; }
.overlay-subtitle { font-size: 0.75rem; color: #64748b; font-weight: 500; display: block; }
.overlay-close { flex: 0 0 auto; border: 0; background: transparent; font-size: 22px; line-height: 1; padding: 0 4px; cursor: pointer; color: #64748b; }

.overlay-toggle { 
  position: absolute; top: 25px; right: 25px; z-index: 1001; 
  border: 1px solid rgba(0,0,0,0.08); background: white; 
  border-radius: 999px; padding: 10px 20px; font-weight: 700; 
  cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
  font-size: 0.95rem; color: #1e293b; transition: transform 0.1s;
}
.overlay-toggle:hover { transform: scale(1.02); }

.legend { margin-top: 10px; }
.legend-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }
.legend-gradient-row { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.legend-axis-label { font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase; }

.legend-gradient { 
  flex: 1; height: 10px; border-radius: 5px; 
  border: 1px solid rgba(0,0,0,0.1); 
  background: linear-gradient(90deg, #fff2a8 0%, #fc4e2a 50%, #800026 100%);
}

.legend-bins { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.legend-swatch { width: 14px; height: 14px; border-radius: 4px; display: inline-block; border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0; }
.legend-label { font-size: 12px; color: #334155; }

.attribution { 
  position: absolute; left: 25px; bottom: 25px; z-index: 1002; 
  font-size: 16px; color: #111827; 
  background: rgba(255, 255, 255, 0.95); 
  border: 1px solid rgba(0,0,0,0.1); 
  border-radius: 999px; padding: 10px 18px; 
  backdrop-filter: blur(4px); font-weight: 500;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.attribution a { color: #084594; font-weight: 700; text-decoration: none; }
.attribution a:hover { text-decoration: underline; }

/* TOP 3 STYLING */
.top3 { margin-top: 20px; padding: 0; background: transparent; border: 0; }
.top3-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.top3-title { font-weight: 800; font-size: 0.85rem; color: #475569; text-transform: uppercase; }
.top3-close { border: 0; background: transparent; font-size: 18px; cursor: pointer; color: #94a3b8; }

.top3-list { display: flex; flex-direction: column; gap: 8px; }
.top3-item { 
  display: flex; align-items: center; gap: 12px; 
  padding: 10px 12px; border-radius: 10px; 
  background: #f8fafc; border: 1px solid #e2e8f0; 
  transition: transform 0.1s;
}
.top3-item:hover { transform: translateX(3px); border-color: #cbd5e1; background: #fff; }

.top3-rank { 
  background: #0f172a; color: white; 
  font-size: 11px; font-weight: 700; 
  width: 20px; height: 20px; border-radius: 50%; 
  display: flex; align-items: center; justify-content: center; 
}
.top3-name { font-size: 13px; color: #0f172a; font-weight: 600; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.top3-score { font-size: 13px; font-weight: 800; color: #084594; }

.top3-toggle { 
  margin-top: 16px; width: 100%; 
  border: 1px dashed #cbd5e1; background: #f8fafc; 
  color: #475569; border-radius: 8px; 
  padding: 10px; font-size: 0.9rem; font-weight: 700; 
  cursor: pointer; transition: all 0.2s;
}
.top3-toggle:hover { background: #f1f5f9; border-color: #94a3b8; color: #0f172a; }

.legend-updated { font-size: 11px; color: #94a3b8; }
.legend-updated--bottom { margin-top: 16px; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 10px; }

/* =========================================
   3. MEDIA QUERIES (MOBILE)
   ========================================= */
@media (max-width: 640px) {
  .modal-backdrop {
    padding: 10px;
    align-items: center;
  }

  .modal-content {
    max-width: 95%; 
    width: 100%;
    max-height: 85dvh;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    padding: 16px 20px; 
  }
  
  .modal-header h2 {
    font-size: 1.25rem; 
  }

  .modal-body {
    padding: 20px;
    font-size: 1rem; 
  }

  .modal-intro {
    font-size: 1rem;
    margin-bottom: 20px;
  }

  .uc-icon { font-size: 1.5rem; }
  .uc-text strong { font-size: 0.95rem; }
  .uc-text p { font-size: 0.9rem; }
  
  .modal-body h3 { font-size: 1.1rem; }
  .tech-list li { font-size: 0.95rem; }
  .modal-warning { font-size: 0.9rem; }

  /* --- FIX MAP AND MOBILE OVERLAY --- */
  .overlay { top: 10px; right: 10px; padding: 12px; width: 200px; }
  .info-btn { 
    top: 10px; 
    left: 10px; 
    padding: 8px 12px; 
    font-size: 0.8rem; 
    gap: 6px;
  }
  .overlay-toggle { top: 10px; right: 10px; padding: 6px 12px; font-size: 0.8rem; }
  
  .attribution { 
    left: 10px;
    right: auto; 
    bottom: 120px; 
    font-size: 12px; 
    padding: 6px 12px;
  }

  /* hover reset on mobile (avoids stickiness) */
  .use-case:hover, .top3-item:hover { transform: none; box-shadow: none; background: #f9fafb; border-color: #e5e7eb; }
}
</style>