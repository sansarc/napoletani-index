<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import MapIndex from './components/MapIndex.vue'
import DocsPage from './components/DocsPage.vue'

function getActiveView() {
  return window.location.hash === '#/docs' ? 'docs' : 'map'
}

const activeView = ref(getActiveView())

function syncActiveView() {
  activeView.value = getActiveView()
}

const activeComponent = computed(() => (activeView.value === 'docs' ? DocsPage : MapIndex))

onMounted(() => {
  window.addEventListener('hashchange', syncActiveView)
})

onBeforeUnmount(() => {
  window.removeEventListener('hashchange', syncActiveView)
})
</script>

<template>
  <component :is="activeComponent" />
</template>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
}

body {
  overflow-x: hidden;
  background: #f8fafc;
}

.leaflet-container {
  background: transparent !important;
}
</style>