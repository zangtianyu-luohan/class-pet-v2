<template>
  <div class="classes-page">
    <div class="page-header">
      <h1>🏫 班级管理</h1>
      <el-button type="primary" @click="showAdd = true"><el-icon><Plus /></el-icon> 创建班级</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="8" v-for="cls in classStore.classes" :key="cls.id">
        <el-card shadow="hover" class="class-card" :class="{ active: cls.id === classStore.currentClassId }">
          <div class="class-header">
            <h3>{{ cls.name }}</h3>
            <el-tag v-if="cls.id === classStore.currentClassId" type="success" size="small">当前</el-tag>
          </div>
          <p class="class-desc">{{ cls.description || '暂无描述' }}</p>
          <div class="class-meta">
            <span>👥 {{ cls.student_count }} 名学生</span>
            <span>📅 {{ formatDate(cls.created_at) }}</span>
          </div>
          <el-space style="margin-top: 12px">
            <el-button size="small" type="primary" @click="classStore.setCurrentClass(cls.id)">切换</el-button>
            <el-button size="small" @click="editClass(cls)">编辑</el-button>
            <el-popconfirm title="确定删除此班级？" @confirm="deleteClass(cls.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑弹窗 -->
    <el-dialog v-model="showAdd" :title="editId ? '编辑班级' : '创建班级'" width="400px">
      <el-form :model="form" label-width="60px">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="如：三年级一班" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" placeholder="可选" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="submitClass">{{ editId ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const showAdd = ref(false)
const editId = ref(null)
const form = reactive({ name: '', description: '' })

function formatDate(d) { return dayjs(d).format('YYYY-MM-DD') }

function editClass(cls) {
  editId.value = cls.id
  form.name = cls.name
  form.description = cls.description
  showAdd.value = true
}

async function submitClass() {
  if (!form.name.trim()) { ElMessage.warning('请输入班级名称'); return }
  try {
    if (editId.value) {
      await api.put(`/api/classes/${editId.value}`, { name: form.name, description: form.description })
      ElMessage.success('已更新')
    } else {
      await api.post('/api/classes/', { name: form.name, description: form.description })
      ElMessage.success('创建成功')
    }
    showAdd.value = false
    editId.value = null
    form.name = ''
    form.description = ''
    await classStore.fetchClasses()
  } catch (e) { /* handled */ }
}

async function deleteClass(id) {
  try {
    await api.delete(`/api/classes/${id}`)
    ElMessage.success('已删除')
    await classStore.fetchClasses()
  } catch (e) { /* handled */ }
}
</script>

<style scoped>
.classes-page { max-width: 900px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 22px; }
.class-card { border-radius: 16px; margin-bottom: 16px; }
.class-card.active { border: 2px solid #6366f1; }
.class-header { display: flex; justify-content: space-between; align-items: center; }
.class-header h3 { margin: 0; }
.class-desc { color: #94a3b8; font-size: 13px; margin: 4px 0 8px; }
.class-meta { display: flex; gap: 16px; font-size: 13px; color: #64748b; }
</style>
