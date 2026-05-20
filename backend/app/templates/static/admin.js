const { createApp, ref, reactive, computed, onMounted, onUnmounted } = Vue
createApp({
  setup() {
    const token = ref(localStorage.getItem('admin_token') || '')
    const page = ref('dashboard')
    const currentTime = ref('')
    const sidebarOpen = ref(false)
    let timeTimer = null

    function goTo(p) { page.value = p; sidebarOpen.value = false }

    function api(method, url, data) {
      return axios({ method, url, data, headers: { Authorization: 'Bearer ' + token.value }, responseType: url.includes('/backup') ? 'blob' : 'json' })
        .catch(err => { if (err.response?.status === 401) { token.value = ''; localStorage.removeItem('admin_token') }; throw err })
    }

    const loginForm = reactive({ username: '', password: '', captcha: '' })
    const loginLoading = ref(false)
    const loginError = ref('')
    const captchaId = ref('')
    const captchaQuestion = ref('加载中...')

    async function loadCaptcha() {
      try { const res = await api('get', '/api/auth/captcha/json'); captchaId.value = res.data.captcha_id; captchaQuestion.value = res.data.question; loginForm.captcha = '' }
      catch { captchaQuestion.value = '加载失败' }
    }

    async function doLogin() {
      if (!loginForm.username || !loginForm.password || !loginForm.captcha) { loginError.value = '请填写完整'; return }
      loginLoading.value = true; loginError.value = ''
      try {
        const res = await axios.post('/api/auth/login', { username: loginForm.username, password: loginForm.password, captcha_id: captchaId.value, captcha_answer: loginForm.captcha })
        // 检查是否为管理员
        const userRes = await axios.get('/api/auth/me', { headers: { Authorization: 'Bearer ' + res.data.access_token } })
        if (!userRes.data.is_admin) {
          loginError.value = '该账号不是管理员，无法登录管理后台'
          loginLoading.value = false
          return
        }
        token.value = res.data.access_token
        localStorage.setItem('admin_token', token.value)
        loadAll()
      } catch (e) { loginError.value = e.response?.data?.detail || '登录失败'; loadCaptcha() }
      finally { loginLoading.value = false }
    }

    function doLogout() { token.value = ''; localStorage.removeItem('admin_token') }

    const stats = ref({ overview: {}, daily_stats: [], recent_logins: [], system: {} })
    const users = ref([])
    const loginLogs = ref([])
    const pointsLogs = ref([])
    const logFilter = ref('all')
    const backingUp = ref(false)

    const weekTotal = computed(() => (stats.value.daily_stats || []).reduce((s, d) => s + d.count, 0))
    function barPct(count) { const max = Math.max(...(stats.value.daily_stats || []).map(d => d.count), 1); return Math.max((count / max) * 100, 3) }
    function fmtTime(d) { if (!d) return '-'; const t = new Date(d); return t.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }

    async function loadStats() { try { const res = await api('get', '/api/admin/stats'); stats.value = res.data } catch {} }
    async function loadUsers() { try { const res = await api('get', '/api/admin/users'); users.value = res.data } catch {} }
    async function loadLoginLogs() { try { const params = logFilter.value === 'success' ? '?success_only=true' : ''; const res = await api('get', '/api/admin/login-logs' + params); loginLogs.value = logFilter.value === 'fail' ? res.data.filter(l => !l.success) : res.data } catch {} }
    async function loadPointsLogs() { try { const res = await api('get', '/api/admin/points-logs'); pointsLogs.value = res.data } catch {} }
    function loadAll() { loadStats(); loadUsers(); loadLoginLogs(); loadPointsLogs() }

    const showCreateUser = ref(false)
    const newUser = reactive({ username: '', password: '', display_name: '' })
    const showResetPwd = ref(false)
    const resetTarget = ref(null)
    const newPassword = ref('')

    async function createUser() {
      try { await api('post', '/api/admin/users', newUser); showCreateUser.value = false; Object.assign(newUser, { username: '', password: '', display_name: '' }); loadUsers() }
      catch (e) { alert(e.response?.data?.detail || '创建失败') }
    }
    async function deleteUser(id) { if (!confirm('确定删除该用户？此操作不可撤销。')) return; try { await api('delete', '/api/admin/users/' + id); loadUsers() } catch (e) { alert(e.response?.data?.detail || '删除失败') } }
    function openResetPwd(u) { resetTarget.value = u; newPassword.value = ''; showResetPwd.value = true }
    async function resetPassword() { try { await api('post', '/api/admin/users/' + resetTarget.value.id + '/reset-password', { new_password: newPassword.value }); showResetPwd.value = false; alert('密码已重置') } catch (e) { alert(e.response?.data?.detail || '重置失败') } }

    // 有效期管理
    const showExpiry = ref(false)
    const expiryTarget = ref(null)
    const expiryDate = ref('')
    function openEditExpiry(u) {
      expiryTarget.value = u
      if (u.expires_at) { const d = new Date(u.expires_at); expiryDate.value = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') + 'T' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0') } else { expiryDate.value = '' }
      showExpiry.value = true
    }
    async function saveExpiry() {
      try {
        const expires_at = expiryDate.value ? new Date(expiryDate.value).toISOString() : null
        await api('put', '/api/admin/users/' + expiryTarget.value.id + '/expiry', { expires_at })
        showExpiry.value = false
        loadUsers()
        alert('有效期已更新')
      } catch (e) { alert(e.response?.data?.detail || '更新失败') }
    }

    async function doBackup() {
      backingUp.value = true
      try {
        const res = await api('post', '/api/admin/backup')
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a'); a.href = url; a.download = 'sps_backup_' + new Date().toISOString().slice(0,19).replace(/[-:T]/g,'') + '.json'; a.click()
        URL.revokeObjectURL(url)
      } catch {} finally { backingUp.value = false }
    }

    onMounted(() => { loadCaptcha(); if (token.value) loadAll(); timeTimer = setInterval(() => { currentTime.value = new Date().toLocaleString('zh-CN') }, 1000) })
    onUnmounted(() => clearInterval(timeTimer))

    // ── 数据库管理 ──
    const dbTables = ref([])
    const dbActiveTable = ref('')
    const dbRows = ref([])
    const dbCurrentCols = ref([])
    const dbTotal = ref(0)
    const dbPage = ref(1)
    const dbPageSize = ref(20)
    const dbSearch = ref('')
    const dbModal = reactive({ show: false, isNew: true, data: {}, error: '' })

    const dbModalCols = computed(() => {
      if (dbModal.isNew) return dbCurrentCols.value.filter(c => c.editable && c.key !== 'id')
      return dbCurrentCols.value.filter(c => c.editable)
    })

    async function dbLoadTables() {
      try {
        const res = await api('get', '/api/admin/db/tables')
        dbTables.value = res.data
        if (!dbActiveTable.value && res.data.length) dbActiveTable.value = res.data[0].name
        dbLoadRows(1)
      } catch {}
    }

    async function dbLoadRows(p) {
      if (p < 1) return
      dbPage.value = p
      const t = dbTables.value.find(t => t.name === dbActiveTable.value)
      if (t) dbCurrentCols.value = t.columns
      try {
        const params = `?page=${p}&page_size=${dbPageSize.value}&search=${encodeURIComponent(dbSearch.value)}`
        const res = await api('get', `/api/admin/db/${dbActiveTable.value}${params}`)
        dbRows.value = res.data.rows
        dbTotal.value = res.data.total
      } catch (e) { dbRows.value = []; dbTotal.value = 0 }
    }

    function dbShowAdd() {
      dbModal.isNew = true
      dbModal.data = {}
      dbModal.error = ''
      dbCurrentCols.value.forEach(c => { if (c.editable && c.key !== 'id') dbModal.data[c.key] = c.type === 'bool' ? false : (c.type === 'datetime' ? null : '') })
      dbModal.show = true
    }

    function dbShowEdit(row) {
      dbModal.isNew = false
      dbModal.data = { ...row }
      // Convert ISO datetime strings to datetime-local format
      for (const col of dbCurrentCols.value) {
        if (col.type === 'datetime' && dbModal.data[col.key]) {
          const d = new Date(dbModal.data[col.key]); dbModal.data[col.key] = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') + 'T' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0')
        }
      }
      dbModal.error = ''
      dbModal.show = true
    }

    async function dbSaveRow() {
      dbModal.error = ''
      // 必填校验
      for (const col of dbModalCols.value) {
        if (col.required && (dbModal.data[col.key] === '' || dbModal.data[col.key] === undefined || dbModal.data[col.key] === null)) {
          dbModal.error = `${col.label} 为必填项`; return
        }
      }
      // Convert datetime-local values to ISO format
      const saveData = { ...dbModal.data }
      for (const col of dbModalCols.value) {
        if (col.type === 'datetime') {
          if (saveData[col.key]) {
            try { saveData[col.key] = new Date(saveData[col.key]).toISOString() } catch(e) { saveData[col.key] = null }
          } else {
            saveData[col.key] = null
          }
        }
      }
      try {
        if (dbModal.isNew) {
          await api('post', `/api/admin/db/${dbActiveTable.value}`, saveData)
        } else {
          await api('put', `/api/admin/db/${dbActiveTable.value}/${dbModal.data.id}`, saveData)
        }
        dbModal.show = false
        dbLoadRows(dbPage.value)
      } catch (e) { dbModal.error = e.response?.data?.detail || '保存失败' }
    }

    async function dbDeleteRow(id) {
      if (!confirm('确定删除这条记录？')) return
      try { await api('delete', `/api/admin/db/${dbActiveTable.value}/${id}`); dbLoadRows(dbPage.value) }
      catch (e) { alert(e.response?.data?.detail || '删除失败') }
    }

    return { token, page, currentTime, sidebarOpen, goTo, stats, users, loginLogs, pointsLogs, logFilter, backingUp, weekTotal, loginForm, loginLoading, loginError, captchaQuestion, showCreateUser, newUser, showResetPwd, resetTarget, newPassword, doLogin, doLogout, loadCaptcha, loadUsers, loadLoginLogs, loadPointsLogs, barPct, fmtTime, createUser, deleteUser, openResetPwd, resetPassword, doBackup,
      dbTables, dbActiveTable, dbRows, dbCurrentCols, dbTotal, dbPage, dbPageSize, dbSearch, dbModal, dbModalCols, dbLoadTables, dbLoadRows, dbShowAdd, dbShowEdit, dbSaveRow, dbDeleteRow,
      showExpiry, expiryTarget, expiryDate, openEditExpiry, saveExpiry }
  }
}).mount('#app')
