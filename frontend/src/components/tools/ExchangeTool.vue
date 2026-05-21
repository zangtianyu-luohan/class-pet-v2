<template>
  <el-dialog v-model="visible" title="🎁 积分兑换" width="480px" @close="$emit('update:modelValue', false)">
    <div style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-weight:600;">奖品设置</span>
        <el-button size="small" @click="addItem">+ 添加</el-button>
      </div>
      <div v-for="(item, idx) in items" :key="idx" style="display:flex;gap:8px;align-items:center;margin-bottom:6px;">
        <el-input v-model="item.name" style="flex:1;" placeholder="奖品名称" />
        <el-input-number v-model="item.cost" :min="1" style="width:120px;" />
        <el-button type="danger" size="small" circle @click="items.splice(idx,1)">×</el-button>
      </div>
      <div style="text-align:right;margin-top:8px;">
        <el-button size="small" @click="resetItems">恢复默认</el-button>
        <el-button type="primary" size="small" @click="saveItems">保存</el-button>
      </div>
    </div>
    <el-divider />
    <el-form label-width="80px">
      <el-form-item label="学生">
        <el-select v-model="studentId" filterable placeholder="选择学生" style="width:100%;">
          <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.points}分)`" :value="s.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="奖品">
        <el-select v-model="itemIdx" placeholder="选择奖品" style="width:100%;">
          <el-option v-for="(item, idx) in items" :key="idx" :label="`${item.name} (${item.cost}分)`" :value="idx" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button type="primary" @click="doExchange">确认兑换</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])
const classStore = useClassStore()

const visible = ref(props.modelValue)
const students = ref([])
const studentId = ref(null)
const itemIdx = ref(null)

const defaultItems = [
  { name: '📐 文具套装', cost: 50 },
  { name: '📒 笔记本', cost: 30 },
  { name: '✏️ 铅笔礼包', cost: 20 },
]
const items = ref(JSON.parse(localStorage.getItem('exchange_items') || 'null') || defaultItems)

watch(() => props.modelValue, v => { visible.value = v; if (v) { loadStudents(); studentId.value = null; itemIdx.value = null } })
watch(visible, v => emit('update:modelValue', v))

function addItem() { items.value.push({ name: '🎁 新奖品', cost: 10 }) }
function saveItems() { localStorage.setItem('exchange_items', JSON.stringify(items.value)); ElMessage.success('奖品已保存') }
function resetItems() { items.value = JSON.parse(JSON.stringify(defaultItems)); localStorage.removeItem('exchange_items'); ElMessage.success('已恢复默认') }

async function loadStudents() {
  try { const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } }); students.value = res.data }
  catch { students.value = [] }
}

async function doExchange() {
  const student = students.value.find(s => s.id === studentId.value)
  const item = items.value[itemIdx.value]
  if (!student || !item) return
  if (student.points < item.cost) { ElMessage.warning(`${student.name} 积分不足（当前${student.points}分，需要${item.cost}分）`); return }
  try {
    await api.post('/api/students/points/adjust', { student_id: student.id, points: -item.cost, reason: `积分兑换：${item.name}`, category: 'exchange' })
    ElMessage.success(`${student.name} 成功兑换 ${item.name}！`)
    studentId.value = null; itemIdx.value = null; loadStudents()
  } catch { ElMessage.error('兑换失败') }
}
</script>
