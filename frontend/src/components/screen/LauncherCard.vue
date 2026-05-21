<template>
  <div class="launcher-card">
    <div class="card-header">
      <h3>{{ icon }} {{ title }}</h3>
    </div>
    <div class="card-body">
      <div class="launcher-content">
        <div class="launcher-icon">{{ icon }}</div>
        <div class="launcher-title">{{ title }}</div>
        <div class="launcher-desc">{{ desc }}</div>
        <el-button type="primary" @click="showDialog = true" style="margin-top:12px;">打开</el-button>
      </div>
    </div>
    <component
      v-if="dialogComponent"
      :is="dialogComponent"
      v-model="showDialog"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  icon: { type: String, default: '' },
  desc: { type: String, default: '' },
  dialogComponent: { type: Object, default: null }
})

const showDialog = ref(false)
</script>

<style scoped>
.launcher-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; align-items: center; justify-content: center; }
.launcher-content { text-align: center; }
.launcher-icon { font-size: 48px; margin-bottom: 8px; }
.launcher-title { font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 4px; }
.launcher-desc { font-size: 13px; color: #94a3b8; }
</style>
