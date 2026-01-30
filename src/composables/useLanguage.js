import { ref, computed } from 'vue';

// Detect browser language on first load
function detectLang() {
  if (typeof navigator !== 'undefined') {
    const lang = navigator.language?.slice(0, 2).toLowerCase();
    if (lang === 'en') return 'en';
    if (lang === 'it') return 'it';
  }
  return 'it';
}

const currentLang = ref(detectLang());

const dictionary = {
  it: {
    notification: {
      icon: '🔎',
      text: 'Tocca sui paesi colorati per i dettagli.'
    },

    infoBtn: 'Come funziona?',

    modal: {
      title: 'Manuale di Sopravvivenza 🗺️',
      intro: 'Il <strong>Napoletani Index</strong> traccia l\'interesse dei campani verso le mete estere usando i dati di ricerca Google. <strong>Non indica dove vivono</strong>, ma le mete che vorrebbero invadere.',
      
      useCases: {
        find: {
          icon: '✊',
          title: 'Vuoi fare a <em>questione</em>?',
          text: 'Punta alle zone <span class="c-red">Rosse</span>. Ci sarà un parcheggiatore abusivo in aeroporto.'
        },
        avoid: {
          icon: '🤫',
          title: 'Vuoi evitare?',
          text: 'Punta alle zone <span class="c-white">Bianche</span> o <span class="c-yellow">Gialle</span>. Ideale per fingere di essere norvegese ed evitare quell\'antropologia del caos descritta come \'calore\' che il resto del mondo chiama \'reato di inquinamento acustico\'.'
        }
      },

      science: {
        title: 'La Scienza dietro l\'Hype 📈',
        intro: 'Come viene calcolato lo score (ed il colore) di un\'intera nazione? Viene utilizzata la logica del <strong>"Più Ricercato + Bonus"</strong>:',
        list: [
          '<strong>Il più ricercato:</strong> Lo score della nazione è dettato maggiormente dalla città più cercata (es. Amsterdam per l\'Olanda).',
          '<strong>Il bonus volume:</strong> Viene aggiunto un pizzico (15%) del volume delle altre città. Così la Spagna (che ha tante mete come Ibiza, Madrid, Barcellona) ottiene uno score "spalmato" senza "truccare" i numeri.'
        ]
      },

      nerdDetails: {
        title: 'Dettagli per Nerd 🤓☝️',
        items: [
          '<strong>Fonte:</strong> Google Trends (API)',
          '<strong>Query:</strong> "Voli [Città]" + "Hotel [Città]"',
          '<strong>Geo:</strong> Campania (IT-72)',
          '<strong>Timeframe:</strong> Ultimi 3 mesi (Rolling)',
          '<strong>Normalizzazione:</strong> Calibrato su "Milano" come costante nascosta.',
          '<strong>Confrontabilità:</strong> Poiché Google non permette di confrontare 50 città insieme, sono analizzate a gruppi di 4 usando sempre "Milano" come metro di paragone comune (anchor) per allineare tutti i punteggi sulla stessa scala.',
          '<strong>Tipo dato:</strong> Serie temporale; per ogni query viene calcolata la <em>media</em> dei punti nel timeframe (media degli <code>extracted_value</code>).',
          '<strong>Formula indice (per città):</strong> <code>index = (mean(query) / mean(anchor)) * visual_scale</code> → poi arrotondato a 1 decimale.',
          '<strong>Aggregazione per nazione (mappa):</strong> <code>score_country = top_city + 0.15 * sum(altre_città)</code> (poi arrotondato).',
          '<strong>Limite interpretazione:</strong> Trends è un proxy di interesse (ricerche), non prenotazioni/arrivi reali; confronti tra batch diversi dipendono dall\'ancora.'
        ]
      },

      warning: '⚠️ <strong>Nota:</strong> L\'indice misura il <em>desiderio</em> (ricerche), non la presenza fisica futura. Se vedi le Maldive rosse, stanno tutti sognando.',
      attribution: 'made by'
    },

    overlay: {
      title: 'Napoletani Index',
      subtitle: 'Dove sognano di andare in vacanza',
      legendTitle: 'Hype',
      axisLabels: {
        low: 'Deserto',
        high: 'Invasione'
      },
      bins: [
        { color: '#800026', label: '≥ 90 (Folla)' },
        { color: '#bd0026', label: '60–89' },
        { color: '#e31a1c', label: '40–59' },
        { color: '#fc4e2a', label: '20–39' },
        { color: '#fd8d3c', label: '12–19' },
        { color: '#feb24c', label: '8–11' },
        { color: '#fed976', label: '4–7' },
        { color: '#ffe128', label: '1–3' },
        { color: '#fff2a8', label: '0 (Pace)' }
      ],
      toggleBtn: 'Legenda',
      top3: {
        title: 'Top 3 Destinazioni',
        toggleBtn: 'Top 3'
      },
      updated: 'Aggiornato'
    },

    // Popup (country details)
    popup: {
      nationalIndex: 'Indice Nazionale'
    },

    // Attribution
    attribution: 'made by'
  },

  en: {
    notification: {
        icon: '🔎',
        text: 'Tap on the colored countries for details.'
    },

    infoBtn: 'How does it work?',

    modal: {
        title: 'Survival Manual 🗺️',
        intro: 'The <strong>Napoletani</strong> (Neapolitans) <strong>Index</strong> tracks the interest of people from Campania in foreign destinations using Google search data. <strong>It does not indicate where they live</strong>, but the places they dream of invading.',

        useCases: {
            find: {
                icon: '✊',
                title: 'Looking for a challenge?',
                text: 'Aim for the <span class="c-red">Red</span> zones. There will be an illegal parking attendant at the airport.'
            },
            avoid: {
                icon: '🤫',
                title: 'Want to avoid?',
                text: 'Aim for the <span class="c-white">White</span> or <span class="c-yellow">Yellow</span> zones. Perfect for pretending to be Norwegian and avoiding that anthropology of chaos described as "warmth" that the rest of the world calls "noise pollution crime".'
            }
        },

        science: {
            title: 'The Science Behind the Hype 📈',
            intro: 'How is the score (and color) of an entire nation calculated? The logic of <strong>"Most Searched + Bonus"</strong> is used:',
            list: [
                '<strong>Most searched:</strong> The nation\'s score is mainly determined by the most searched city (e.g., Amsterdam for the Netherlands).',
                '<strong>Volume bonus:</strong> A pinch (15%) of the volume from other cities is added. So Spain (which has many destinations like Ibiza, Madrid, Barcelona) gets a "spread" score without "fudging" the numbers.'
            ]
        },

        nerdDetails: {
            title: 'Nerd Details 🤓☝️',
            items: [
                '<strong>Source:</strong> Google Trends (API)',
                '<strong>Query:</strong> "Flights [City]" + "Hotel [City]"',
                '<strong>Geo:</strong> Campania (IT-72)',
                '<strong>Timeframe:</strong> Last 3 months (Rolling)',
                '<strong>Normalization:</strong> Calibrated on "Milan" as a hidden constant.',
                '<strong>Comparability:</strong> Since Google does not allow comparing 50 cities together, they are analyzed in groups of 4 always using "Milan" as a common benchmark (anchor) to align all scores on the same scale.',
                '<strong>Data type:</strong> Time series; for each query, the <em>average</em> of the points in the timeframe is calculated (average of <code>extracted_value</code>).',
                '<strong>Index formula (per city):</strong> <code>index = (mean(query) / mean(anchor)) * visual_scale</code> → then rounded to 1 decimal.',
                '<strong>Aggregation by country (map):</strong> <code>score_country = top_city + 0.15 * sum(other_cities)</code> (then rounded).',
                '<strong>Interpretation limit:</strong> Trends is a proxy for interest (searches), not real bookings/arrivals; comparisons between different batches depend on the anchor.'
            ]
        },

        warning: '⚠️ <strong>Note:</strong> The index measures <em>desire</em> (searches), not future physical presence. If you see the Maldives in red, everyone is just dreaming.',
        attribution: 'made by'
    },

    overlay: {
        title: 'Neapolitans Index',
        subtitle: 'Where they dream of going on vacation',
        legendTitle: 'Hype',
        axisLabels: {
            low: 'Desert',
            high: 'Invasion'
        },
        bins: [
            { color: '#800026', label: '≥ 90 (Crowd)' },
            { color: '#bd0026', label: '60–89' },
            { color: '#e31a1c', label: '40–59' },
            { color: '#fc4e2a', label: '20–39' },
            { color: '#fd8d3c', label: '12–19' },
            { color: '#feb24c', label: '8–11' },
            { color: '#fed976', label: '4–7' },
            { color: '#ffe128', label: '1–3' },
            { color: '#fff2a8', label: '0 (Peace)' }
        ],
        toggleBtn: 'Legend',
        top3: {
            title: 'Top 3 Destinations',
            toggleBtn: 'Top 3'
        },
        updated: 'Updated'
    },

    popup: {
        nationalIndex: 'National Index'
    },

    attribution: 'made by'
  }
};

export function useLanguage() {
    const t = computed(() => dictionary[currentLang.value]);

    const toggleLang = () => {
        currentLang.value = currentLang.value === 'it' ? 'en' : 'it';
    };

    return { t, currentLang, toggleLang }
}