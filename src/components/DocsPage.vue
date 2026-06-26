<script setup>
import { useLanguage } from '../composables/useLanguage'

const { t, currentLang, toggleLang } = useLanguage()
</script>

<template>
  <div class="docs-page">
    <div class="docs-shell">
      <header class="docs-topbar">
        <a class="docs-back" href="#/" :aria-label="t.docs.backToMap" :title="t.docs.backToMap">
          ⬅️
        </a>

        <a
          class="docs-repo"
          href="https://github.com/sansarc/napoletani-index"
          target="_blank"
          rel="noopener"
        >
          {{ t.docs.attribution }}
        </a>

        <button class="docs-lang" @click="toggleLang">
          {{ currentLang === 'it' ? '🇺🇸' : '🇮🇹' }}
        </button>
      </header>

      <main class="docs-main">
        <section class="docs-hero docs-card--accent">
          <p class="docs-kicker">{{ t.infoBtn }}</p>
          <h1>{{ t.docs.title }}</h1>
          <p class="docs-intro" v-html="t.docs.intro"></p>
        </section>

        <section class="docs-grid">
          <article class="docs-card">
            <div class="docs-card-icon">{{ t.docs.useCases.find.icon }}</div>
            <h2 v-html="t.docs.useCases.find.title"></h2>
            <p v-html="t.docs.useCases.find.text"></p>
          </article>

          <article class="docs-card">
            <div class="docs-card-icon">{{ t.docs.useCases.avoid.icon }}</div>
            <h2>{{ t.docs.useCases.avoid.title }}</h2>
            <p v-html="t.docs.useCases.avoid.text"></p>
          </article>
        </section>

        <aside class="docs-warning" v-html="t.docs.warning"></aside>

        <section class="docs-section docs-card--accent">
          <h2>{{ t.docs.science.title }}</h2>
          <p class="docs-copy" v-html="t.docs.science.intro"></p>

          <ul class="docs-list">
            <li v-for="(item, i) in t.docs.science.list" :key="i" v-html="item" />
          </ul>
        </section>

        <details class="docs-section docs-details">
        <summary class="docs-details-summary">
            {{ t.docs.nerdDetails.title }}
        </summary>

        <ul class="docs-list docs-list--tight">
            <li
            v-for="(item, i) in t.docs.nerdDetails.items"
            :key="i"
            v-html="item"
            />
        </ul>
        </details>

      </main>
    </div>
  </div>
</template>

<style scoped>
.docs-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(8, 69, 148, 0.12), transparent 34%),
    radial-gradient(circle at right 20%, rgba(255, 226, 40, 0.14), transparent 26%),
    linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  color: #0f172a;
}

.docs-shell {
  max-width: 1024px;
  margin: 0 auto;
  padding: 92px 20px 20px;
}

.docs-topbar {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: min(1024px - 40px, calc(100vw - 40px));
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  padding: 0;
}

.docs-back,
.docs-lang,
.docs-repo {
  --hover-scale: 1.05;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(8, 69, 148, 0.12);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s, background 0.2s, box-shadow 0.2s;
}

.docs-back:hover,
.docs-lang:hover,
.docs-repo:hover {
  background: #f0f9ff;
  box-shadow: 0 4px 12px rgba(8, 69, 148, 0.18);
  transform: scale(var(--hover-scale));
}

.docs-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #084594;
  text-decoration: none;
  font-weight: 800;
  border-radius: 999px;
  width: 44px;
  height: 44px;
  padding: 0;
  justify-self: start;
  font-size: 1.2rem;
}

.docs-lang {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.35rem;
  justify-self: end;
  --hover-scale: 1.1;
}

.docs-repo {
  justify-self: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border-radius: 999px;
  color: #084594;
  text-decoration: none;
  font-weight: 800;
  white-space: nowrap;
  min-width: 140px;
}

.docs-main {
  display: grid;
  gap: 20px;
}

.docs-hero,
.docs-section,
.docs-warning,
.docs-card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.docs-hero {
  border-radius: 28px;
  padding: 30px;
}

.docs-kicker {
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 800;
}

.docs-hero h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.5rem);
  line-height: 1;
  letter-spacing: -0.05em;
}

.docs-intro {
  margin: 18px 0 0;
  max-width: 70ch;
  color: #334155;
  font-size: 1.05rem;
  line-height: 1.7;
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.docs-card {
  border-radius: 24px;
  padding: 22px;
}

.docs-card--accent {
  border-color: rgba(8, 69, 148, 0.18);
  background: linear-gradient(180deg, rgba(8, 69, 148, 0.08), rgba(255, 255, 255, 0.95));
}

.docs-card-icon {
  font-size: 2rem;
  line-height: 1;
  margin-bottom: 14px;
}

.docs-card h2,
.docs-section h2 {
  margin: 0 0 10px;
  font-size: 1.35rem;
  letter-spacing: -0.03em;
}

.docs-card p,
.docs-copy {
  margin: 0;
  color: #475569;
  line-height: 1.65;
}

.docs-section {
  border-radius: 24px;
  padding: 24px 26px;
}

.docs-section--details {
  background: rgba(255, 255, 255, 0.94);
}

.docs-list {
  margin: 16px 0 0;
  padding-left: 1.2rem;
  color: #334155;
}

.docs-list li {
  margin-bottom: 10px;
  line-height: 1.6;
}

.docs-list--tight li {
  margin-bottom: 8px;
}

.docs-warning {
  border-radius: 22px;
  padding: 18px 20px;
  color: #92400e;
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
  line-height: 1.6;
}

:deep(.c-red) {
  color: #d32f2f;
  font-weight: 700;
}

:deep(.c-white) {
  color: #94a3b8;
  font-weight: 700;
}

:deep(.c-yellow) {
  color: #f59e0b;
  font-weight: 700;
}

:deep(code) {
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

@media (max-width: 760px) {
  .docs-shell {
    padding: 16px 16px 96px;
  }

  .docs-grid {
    grid-template-columns: 1fr;
  }

  .docs-hero,
  .docs-section,
  .docs-card {
    border-radius: 20px;
  }

  .docs-hero {
    padding: 24px;
  }

  .docs-section {
    padding: 20px;
  }

  .docs-topbar {
    top: auto;
    bottom: 16px;
    left: 5px;
    transform: none;
    width: calc(100vw - 32px);
    grid-template-columns: auto 1fr auto;
    padding: 10px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.18);
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
    backdrop-filter: blur(10px);
  }

  .docs-back,
  .docs-repo {
    font-size: 0.88rem;
  }

  .docs-back {
    justify-self: start;
    width: 40px;
    height: 40px;
  }

  .docs-repo {
    min-width: 0;
    padding-inline: 14px;
    justify-self: center;
  }

  .docs-lang {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
    justify-self: end;
  }
}
</style>