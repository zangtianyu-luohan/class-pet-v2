<template>
  <div class="screen-card" :class="`size-${size}`">
    <button class="card-remove" @click="$emit('remove')" title="移除卡片">×</button>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'normal'
  }
})

defineEmits(['remove'])
</script>

<style scoped>
.screen-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.screen-card:hover .card-remove {
  opacity: 1;
}

.card-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(239, 68, 68, 0.8);
  color: #fff;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-remove:hover {
  background: rgba(239, 68, 68, 1);
}

.size-normal {
  grid-column: span 1;
  grid-row: span 1;
}

.size-wide {
  grid-column: span 2;
  grid-row: span 1;
}

.size-tall {
  grid-column: span 1;
  grid-row: span 2;
}

.size-full {
  grid-column: span 3;
  grid-row: span 1;
}
</style>
