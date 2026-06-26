<script setup>
import { onMounted, onUnmounted, ref, computed, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import rawDestinations from '../assets/data.json';
import { useLanguage } from '../composables/useLanguage';
import { useGeo } from '../composables/useGeo';

const { t, currentLang, toggleLang } = useLanguage();
const { countryName, cityName } = useGeo(currentLang);

const mapContainer = ref(null);
let map = null;

// flight path elements
let flightPath = null;
let marker = null;
const DEPARTURE_COORDS = [40.8518, 14.2681];

// UI state
const isInfoModalOpen = ref(false);
const isScoreboardOpen = ref(false);
const selectedDest = ref(null);

const sortedCountries = computed(() => {
  return Object.entries(countryData)
    .map(([code, data]) => ({
      code,
      name: countryName(code),
      totalIndex: data.totalIndex,
      topCity: data.locations[0],
      locations: data.locations
    }))
    .sort((a, b) => b.totalIndex - a.totalIndex);
});

// data preparation
const countryData = {};

rawDestinations.forEach(dest => {
  const code = dest.country_code; 
  if (!countryData[code]) 
    countryData[code] = { code, totalIndex: 0, locations: [] };
  
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
            const isMobile = window.innerWidth <= 640;
            const minWidth = isMobile ? 115 : 180; 
            const labelFontSize = isMobile ? '0.75rem' : '0.85rem';
            const valueFontSize = isMobile ? '1.1rem' : '1.4rem';
            const cityFontSize = isMobile ? '0.8rem' : '0.9rem';
            const cityIndexFontSize = isMobile ? '0.75rem' : '0.8rem';

            let popupContent = `
            <div style="text-align:center; min-width:${minWidth}px; font-family: sans-serif;">
                <h3 style="margin:0 0 5px 0; color:#084594; border-bottom: 2px solid #eee; padding-bottom:5px;">
                ${countryName(myData.code)}
                </h3>
                <div style="background:#f1f5f9; padding:8px; border-radius:6px; margin-bottom:12px;">
                <span style="font-size:${labelFontSize}; color:#64748b; display:block">${t.value.popup.nationalIndex}</span>
                <strong style="font-size:${valueFontSize}; color:#0f172a">${myData.totalIndex}</strong>
                </div>
                <div style="text-align:left; max-height:150px; overflow-y:auto;">
            `;

            // city list
            myData.locations.forEach(loc => {
                const isTop = loc.index === myData.locations[0].index;
                const style = isTop ? "font-weight:700; color:#084594" : "color:#334155";

                const trendColor = loc.trend === 'up' ? '#16a34a' : (loc.trend === 'down' ? '#dc2626' : '#94a3b8');
                const trendArrow = loc.trend === 'up' ? '↗' : (loc.trend === 'down' ? '↘' : '=');
                
                popupContent += `
                <div style="display:flex; justify-content:space-between; border-bottom:1px solid #f0f0f0; padding:4px 0; font-size:${cityFontSize};">
                    <span style="${style}">${cityName(loc.name)}</span>
                    <span style="background:#e2e8f0; padding:0 6px; border-radius:4px; font-size:${cityIndexFontSize}">${loc.index}</span>
                    <span style="font-size:0.8rem; margin-left:4px; color:${trendColor}; font-weight:bold">
                      ${trendArrow} ${loc.trend_diff > 0 ? '+' : ''}${loc.trend_diff}
                    </span>
                </div>`;
            });
            
            popupContent += `</div></div>`;
            
            L.popup()
                .setLatLng(e.latlng)
                .setContent(popupContent)
                .openOn(map);

            selectedDest.value = e.latlng;
        });

        layer.on('mouseover', function() {
            this.setStyle({ weight: 2, color: '#9ca3af' });
        });
        layer.on('mouseout', function() {
            this.setStyle({ weight: 1, color: '#ffffff' });
        });
    }
}

function handleKeydown(e) {
  if (e.key === 'Escape') {
    if (isInfoModalOpen.value) isInfoModalOpen.value = false;
    if (isScoreboardOpen.value) isScoreboardOpen.value = false;
  }
}

// initialization
onMounted(async () => {
  document.addEventListener('keydown', handleKeydown);
  
  map = L.map(mapContainer.value, {
      center: [40, 10], 
      zoom: 3,
      minZoom: 2,
      maxBounds: [[-90, -180], [90, 180]],
      zoomControl: false 
  });

  // Create a pane for flight path elements so they're always on top
  map.createPane('flightPathPane');
  map.getPane('flightPathPane').style.zIndex = 650;
  
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  map.on('popupclose', () => selectedDest.value = null);

  try {
    const response = await fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson');
    const geoJsonData = await response.json();

    L.geoJSON(geoJsonData, {
        style: styleFeature,
        onEachFeature: onEachFeature
    }).addTo(map);

  } catch (error) {
    console.error("Error loading map:", error);
  }
});

// flight path drawing
function drawPath(dest) {
  if (flightPath && map) {
    map.removeLayer(flightPath);
    flightPath = null;
  }

  if (marker && map) {
    map.removeLayer(marker);
    marker = null;
  }

  if (!dest || !map) return;

  const from = L.latLng(DEPARTURE_COORDS);
  const to = L.latLng(dest);

  const midLat = (from.lat + to.lat) / 2;
  const midLng = (from.lng + to.lng) / 2;

  // farthest the point, the "tallest" the curve
  const distance = from.distanceTo(to);
  const arcOffset = distance / 200000;

  const controlPoint = [midLat + arcOffset, midLng];

  // Generate points along a quadratic Bezier curve
  const curvePoints = [];
  const segments = 50;
  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const lat = (1 - t) * (1 - t) * from.lat + 2 * (1 - t) * t * controlPoint[0] + t * t * to.lat;
    const lng = (1 - t) * (1 - t) * from.lng + 2 * (1 - t) * t * controlPoint[1] + t * t * to.lng;
    curvePoints.push([lat, lng]);
  }

  flightPath = L.polyline(curvePoints, {
    color: 'blue',
    weight: 3,
    opacity: 0.8,
    dashArray: '10,10',
    pane: 'flightPathPane'
  }).addTo(map);

  marker = L.circleMarker([to.lat, to.lng], {
    radius: 3,
    color: 'red',
    fillColor: 'red',
    fillOpacity: 1,
    pane: 'flightPathPane'
  }).addTo(map);
}

watch(selectedDest, (newDest) => drawPath(newDest));

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  
  if (flightPath && map) {
    map.removeLayer(flightPath);
  }
  if (marker && map) {
    map.removeLayer(marker);
  }
});
</script>

<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <!-- Language toggle -->
    <button class="lang-btn" @click="toggleLang">
      {{ currentLang === 'it' ? '🇺🇸' : '🇮🇹' }}
    </button>

    <!-- Info button -->
    <button
      class="info-btn"
      @click="isInfoModalOpen = true"
    >
      <span class="info-btn-text">{{ t.infoBtn }}</span>
    </button>

    <!-- Modal -->
    <div
      v-if="isInfoModalOpen"
      class="modal-backdrop"
      @click.self="isInfoModalOpen = false"
    >
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ t.modal.title }}</h2>
          <button class="modal-close" @click="isInfoModalOpen = false">×</button>
        </div>

        <div class="modal-body">
          <p class="modal-intro" v-html="t.modal.intro"></p>

          <!-- Use cases -->
          <div class="modal-use-cases">
            <div class="use-case">
              <span class="uc-icon">{{ t.modal.useCases.find.icon }}</span>
              <div class="uc-text">
                <strong v-html="t.modal.useCases.find.title"></strong>
                <p v-html="t.modal.useCases.find.text"></p>
              </div>
            </div>

            <div class="use-case">
              <span class="uc-icon">{{ t.modal.useCases.avoid.icon }}</span>
              <div class="uc-text">
                <strong>{{ t.modal.useCases.avoid.title }}</strong>
                <p v-html="t.modal.useCases.avoid.text"></p>
              </div>
            </div>
          </div>

          <hr class="modal-divider" />

          <!-- Science -->
          <h3>{{ t.modal.science.title }}</h3>
          <p class="modal-text-sm" v-html="t.modal.science.intro"></p>

          <ul class="tech-list">
            <li
              v-for="(item, i) in t.modal.science.list"
              :key="i"
              v-html="item"
            />
          </ul>

          <!-- Nerd details -->
          <details class="tech-details">
            <summary>{{ t.modal.nerdDetails.title }}</summary>
            <ul>
              <li
                v-for="(item, i) in t.modal.nerdDetails.items"
                :key="i"
                v-html="item"
              />
            </ul>
          </details>

          <div class="modal-warning" v-html="t.modal.warning"></div>
        </div>

        <div class="modal-attribution">
          {{ t.modal.attribution }}
          <a
            href="https://github.com/sansarc/napoletani-index"
            target="_blank"
            rel="noopener"
          >
            sansarc
          </a>
        </div>
      </div>
    </div>

    <!-- Scoreboard Modal -->
    <div
      v-if="isScoreboardOpen"
      class="modal-backdrop"
      @click.self="isScoreboardOpen = false"
    >
      <div class="modal-content scoreboard-modal">
        <div class="modal-header">
          <h2>{{ t.overlay.scoreboard.title }}</h2>
          <button class="modal-close" @click="isScoreboardOpen = false">×</button>
        </div>

        <div class="modal-body scoreboard-body">
          <div class="scoreboard-list">
            <div
              v-for="(country, i) in sortedCountries"
              :key="country.code"
              class="scoreboard-item"
            >
              <span class="scoreboard-rank">#{{ i + 1 }}</span>
              <span class="scoreboard-name">{{ country.name }}</span>
              <span class="scoreboard-score">{{ country.totalIndex }}</span>
              <span 
                v-if="country.topCity?.trend && country.topCity.trend !== 'stable'" 
                :class="['trend-badge', country.topCity.trend]"
              >
                {{ country.topCity.trend === 'up' ? '↗' : '↘' }}
                {{ country.topCity.trend_diff > 0 ? '+' : '' }}{{ country.topCity.trend_diff }}
              </span>
              <span v-else class="trend-badge stable">=</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Attribution -->
    <div class="attribution">
      {{ t.attribution }}
      <a
        href="https://github.com/sansarc/napoletani-index"
        target="_blank"
        rel="noopener"
      >
        sansarc
      </a>
    </div>

    <!-- Overlay -->
    <div class="overlay">
      <div class="legend">
        <div class="legend-title">{{ t.overlay.legendTitle }}</div>

        <div class="legend-gradient-row">
          <span class="legend-axis-label">
            {{ t.overlay.axisLabels.low }}
          </span>
          <div class="legend-gradient"></div>
          <span class="legend-axis-label">
            {{ t.overlay.axisLabels.high }}
          </span>
        </div>

        <div class="legend-bins">
          <div
            class="legend-item"
            v-for="(bin, i) in t.overlay.bins"
            :key="i"
          >
            <span
              class="legend-swatch"
              :style="{ background: bin.color }"
            ></span>
            <span class="legend-label">{{ bin.label }}</span>
          </div>
        </div>
      </div>

      <!-- Scoreboard button -->
      <button
        class="scoreboard-toggle"
        @click="isScoreboardOpen = true"
      >
        {{ t.overlay.scoreboard.toggleBtn }}
      </button>
    </div>
  </div>
</template>

<style src="../styles/MapIndex.css"></style>