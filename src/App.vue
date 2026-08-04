<script setup>
import RivePreview from "./components/RivePreview.vue";
</script>

<template>
  <main class="stage">
    <RivePreview />
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
