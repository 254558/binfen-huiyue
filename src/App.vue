<script setup>
import CanvasPreview from "./components/CanvasPreview.vue";
</script>

<template>
  <main class="stage">
    <CanvasPreview />
  </main>
</template>

<style scoped>
.stage {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #000;
}
</style>
