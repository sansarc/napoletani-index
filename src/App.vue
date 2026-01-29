<script setup>
import MapIndex from './components/MapIndex.vue'
</script>

<template>
  <MapIndex />
</template>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden; 
}

.leaflet-container {
  background: transparent !important;
}
</style>