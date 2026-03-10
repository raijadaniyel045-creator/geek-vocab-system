<template>
  <div class="app-container">
    <header class="header">
      <h1 class="logo">Geek Vocab.</h1>
      <p class="subtitle">六级词汇智能突击系统</p>

      <div class="nav-segmented-control">
        <button @click="switchTab('stats')" :class="{ active: currentMode === 'stats' }">📊 数据看板</button>
        <button @click="switchTab('add')" :class="{ active: currentMode === 'add' }">✨ 生词录入</button>
        <button @click="switchTab('review_setup')" :class="{ active: currentMode.includes('review') }">🎯 专注复习</button>
        <button @click="loadAllWords" :class="{ active: currentMode === 'manage' }">📚 我的词库</button>
        <button @click="switchTab('ai_chat')" :class="{ active: currentMode === 'ai_chat' }" class="ai-nav-btn">🤖 AI 洞察</button>
      </div>
    </header>

    <main v-if="currentMode === 'stats'" class="card stats-card fade-in">
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-label">总词汇量</span>
          <span class="stat-value">{{ stats.total }}</span>
        </div>
        <div class="stat-box highlight">
          <span class="stat-label">待复习</span>
          <span class="stat-value">{{ stats.pending_now }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">已掌握 (EF>2.6)</span>
          <span class="stat-value">{{ stats.mastered }}</span>
        </div>
      </div>
    </main>

    <main v-if="currentMode === 'add'" class="card add-card fade-in">
      <div class="input-group">
        <input v-model="newWord" @keyup.enter="searchWord" type="text" placeholder="输入单词，按回车搜索..." />
        <button @click="searchWord" :disabled="loading" class="primary-btn">
          {{ loading ? '🔍 搜索中...' : '🔍 搜索' }}
        </button>
      </div>

      <div v-if="previewWord" class="preview-box">
        <div class="preview-header">
          <h2 class="preview-word">{{ previewWord.word }}</h2>
          <button v-if="previewWord.audio_url" @click="playAudio(previewWord.audio_url)" class="audio-btn">🔊 播放原声</button>
        </div>
        <p class="phonetic">{{ previewWord.phonetic }}</p>
        <div class="editor-group">
          <label>💡 精简释义 (可直接修改并保存)</label>
          <input type="text" v-model="previewWord.chinese_meaning" class="modern-input"/>
        </div>
        <button @click="confirmAddWord" class="confirm-btn">✅ 确认录入词库</button>
      </div>
      <div v-if="message" class="toast-message" :class="{'success': isSuccessMsg}">{{ message }}</div>
    </main>

    <main v-if="currentMode === 'review_setup'" class="card setup-card fade-in">
      <div class="setup-form">
        <div class="form-section">
          <label class="section-title">本次复习数量：<span class="highlight-text">{{ reviewLimit }} 个</span></label>
          <input type="range" v-model="reviewLimit" min="5" max="50" step="5" class="modern-range">
        </div>
        <div class="form-section">
          <label class="section-title">选择复习模式</label>
          <div class="radio-group">
            <label class="radio-label"><input type="radio" v-model="reviewType" value="flashcard"> 📇 经典翻卡</label>
            <label class="radio-label"><input type="radio" v-model="reviewType" value="spell_zh2en"> ✍️ 默写模式 (看中写英)</label>
            <label class="radio-label"><input type="radio" v-model="reviewType" value="spell_en2zh"> 🧠 释义挑战 (看英写中)</label>
          </div>
        </div>
        <button @click="startReview" class="primary-btn start-btn">🚀 开始复习</button>
      </div>
    </main>

    <main v-if="currentMode === 'reviewing'" class="card review-card fade-in">
      <div v-if="reviewList.length === 0" class="completion-state">
        <div class="completion-icon">🎉</div>
        <h2>本组复习已完成！</h2>
        <p class="completion-sub">太棒了，休息一下或者继续挑战吧。</p>
        <button @click="switchTab('review_setup')" class="secondary-btn">返回复习设置</button>
      </div>

      <div v-else class="flashcard">
        <div class="progress-bar-container">
          <span class="progress-text">剩余 <strong>{{ reviewList.length }}</strong> 词</span>
        </div>

        <div class="word-display">
          <h1 class="hero-word" v-if="reviewType !== 'spell_zh2en'">{{ currentReviewWord.word }}</h1>
          <h1 class="hero-word" v-if="reviewType === 'spell_zh2en'">{{ currentReviewWord.chinese_meaning }}</h1>
          <div class="phonetic-row" v-if="reviewType !== 'spell_zh2en'">
            <span class="phonetic">{{ currentReviewWord.phonetic }}</span>
            <button v-if="currentReviewWord.audio_url" @click="playAudio(currentReviewWord.audio_url)" class="audio-btn minimal">🔊</button>
          </div>
        </div>

        <div v-if="reviewType.startsWith('spell_') && !showMeaning" class="spell-area">
          <input ref="spellInputRef" v-model="userSpellInput" @keyup.enter="checkSpell" type="text" class="modern-input spell-input" placeholder="请输入你的答案..."/>
          <button @click="checkSpell" class="primary-btn">验证答案</button>
        </div>

        <div v-if="reviewType === 'flashcard' && !showMeaning" class="action-area">
          <button class="reveal-btn" @click="showMeaning = true">👀 点击显示答案</button>
        </div>

        <div v-if="showMeaning" class="meaning-area fade-in">
          <div v-if="reviewType.startsWith('spell_')" class="spell-feedback" :class="isSpellCorrect ? 'correct' : 'wrong'">
            {{ isSpellCorrect ? '✅ 回答正确！' : '❌ 回答有误，请核对标准答案：' }}
          </div>

          <div class="definition-block">
            <p class="meaning-zh"><strong>中文：</strong>{{ currentReviewWord.chinese_meaning }}</p>
            <p class="meaning-en"><strong>英文：</strong>{{ currentReviewWord.word }}</p>
          </div>

          <button @click="askAI" class="ai-tutor-btn" :disabled="aiLoading">
            {{ aiLoading ? '🤔 正在生成深度解析...' : '🤖 呼叫 AI 私教讲解考点' }}
          </button>
          <div v-if="aiResponse" class="ai-response-box">
            <div class="markdown-body" v-html="renderMarkdown(aiResponse)"></div>
          </div>

          <div class="rating-section">
            <p class="rating-hint">请诚实评估掌握程度，算法将为你安排下次复习：</p>
            <div class="rating-buttons">
              <button class="rate-btn hard" @click="submitScore(0)">
                <span>忘记</span><small>5分钟后</small>
              </button>
              <button class="rate-btn good" @click="submitScore(2)">
                <span>模糊</span><small>12小时后</small>
              </button>
              <button class="rate-btn easy" @click="submitScore(4)">
                <span>熟悉</span><small>延后几天</small>
              </button>
              <button class="rate-btn perfect" @click="submitScore(5)">
                <span>秒答</span><small>大幅延后</small>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <main v-if="currentMode === 'manage'" class="card manage-card fade-in">
       <div class="manage-header">
         <h2>📚 词库管理 (共 {{ allWords.length }} 词)</h2>
         <button @click="exportCSV" class="secondary-btn">⬇️ 导出 CSV</button>
       </div>
       <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>单词</th>
              <th>释义 (点击直接修改)</th>
              <th>掌握度 (EF)</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="word in allWords" :key="word.id">
              <td class="fw-500">{{ word.word }}</td>
              <td><input type="text" v-model="word.chinese_meaning" @blur="updateMeaning(word)" class="table-input" title="修改后自动保存"/></td>
              <td><span class="ef-badge" :title="'数值越高掌握越好，默认2.5'">{{ word.easiness_factor ? word.easiness_factor.toFixed(1) : '2.5' }}</span></td>
              <td><button @click="deleteWord(word.id)" class="text-danger-btn">删除</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <main v-if="currentMode === 'ai_chat'" class="card ai-chat-card fade-in">
      <div class="chat-header-clean">
        <h2>🤖 全局数据分析</h2>
        <p class="chat-subtitle">基于您的专属词库进行多维度推理与提炼</p>
      </div>

      <div class="quick-prompts-clean">
        <button @click="sendChatMessage('帮我把词库里的单词按照词性用表格分类总结出来。')">🗂️ 词性归纳</button>
        <button @click="sendChatMessage('提取写作高级替换词，并附带例句。')">✍️ 写作词汇提炼</button>
        <button @click="sendChatMessage('我的词库里有容易混淆的词吗？做个辨析。')">🔍 易混淆词辨析</button>
      </div>

      <div class="chat-window" ref="chatWindowRef">
        <div v-if="chatHistory.length === 0" class="empty-state">
          等待输入分析指令...
        </div>

        <div v-for="(msg, index) in chatHistory" :key="index" :class="['message-row', msg.role]">
          <div class="message-bubble">
            <div class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>
      </div>

      <div class="chat-input-wrapper">
        <textarea v-model="chatInput" @keyup.ctrl.enter="sendChatMessage(chatInput)" placeholder="输入分析指令 (按 Ctrl+Enter 快捷发送)..." rows="1"></textarea>
        <button @click="sendChatMessage(chatInput)" :disabled="globalAILoading" class="send-btn">
          {{ globalAILoading ? '分析中...' : '发送 🛫' }}
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
// [你的 <script setup> 业务逻辑完全保持原样不变！]
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const apiBase = 'http://127.0.0.1:8000/api'
const currentMode = ref('stats')
const stats = ref({ total: 0, pending_now: 0, mastered: 0 })
const allWords = ref([])
const newWord = ref(''); const message = ref(''); const isSuccessMsg = ref(false); const loading = ref(false); const previewWord = ref(null)
const reviewLimit = ref(15)
const reviewType = ref('flashcard')
const reviewList = ref([])
const showMeaning = ref(false)
const userSpellInput = ref('')
const isSpellCorrect = ref(false)
const spellInputRef = ref(null)
const aiLoading = ref(false); const aiResponse = ref('')
const chatInput = ref('')
const globalAILoading = ref(false)
const chatHistory = ref([])
const chatWindowRef = ref(null)

const currentReviewWord = computed(() => reviewList.value.length > 0 ? reviewList.value[0] : null)
const playAudio = (url) => { if (url) new Audio(url).play() }

const switchTab = (tab) => {
  currentMode.value = tab; previewWord.value = null; message.value = ''; aiResponse.value = ''
  if (tab === 'stats') fetchStats()
  if (tab === 'ai_chat') scrollToBottom()
}

const fetchStats = async () => { try { stats.value = (await axios.get(`${apiBase}/stats`)).data } catch (e) {} }

const searchWord = async () => {
  if (!newWord.value) return; loading.value = true; message.value = ''; previewWord.value = null
  try { previewWord.value = (await axios.get(`${apiBase}/search/${newWord.value}`)).data } catch (e) { message.value = "❌ 查询失败" } finally { loading.value = false }
}

const confirmAddWord = async () => {
  try { await axios.post(`${apiBase}/words`, previewWord.value); message.value = "录入成功"; isSuccessMsg.value=true; newWord.value = ''; previewWord.value = null; fetchStats() } catch (e) {}
}

const startReview = async () => {
  currentMode.value = 'reviewing'; showMeaning.value = false; userSpellInput.value = ''; aiResponse.value = ''
  try { reviewList.value = (await axios.get(`${apiBase}/words/due?limit=${reviewLimit.value}`)).data } catch (e) {}
  if (reviewType.value.startsWith('spell_')) nextTick(() => spellInputRef.value?.focus())
}

const checkSpell = () => {
  if (!userSpellInput.value.trim()) return
  const input = userSpellInput.value.trim().toLowerCase()
  isSpellCorrect.value = reviewType.value === 'spell_zh2en' ? (input === currentReviewWord.value.word.toLowerCase()) : currentReviewWord.value.chinese_meaning.includes(input)
  showMeaning.value = true
}

const submitScore = async (score) => {
  try { await axios.put(`${apiBase}/words/${currentReviewWord.value.id}/review`, { quality: score })
    reviewList.value.shift(); showMeaning.value = false; userSpellInput.value = ''; aiResponse.value = ''
    if (reviewType.value.startsWith('spell_') && reviewList.value.length > 0) nextTick(() => spellInputRef.value?.focus())
  } catch (e) {}
}

const askAI = async () => {
  aiLoading.value = true; aiResponse.value = "深度解析中..."
  try { aiResponse.value = (await axios.post(`${apiBase}/ai/tutor`, { word: currentReviewWord.value.word, question: "给个记忆口诀" })).data.answer }
  catch (e) { aiResponse.value = "解析失败" } finally { aiLoading.value = false }
}

const sendChatMessage = async (queryText) => {
  if (!queryText.trim() || globalAILoading.value) return
  chatHistory.value.push({ role: 'user', content: queryText })
  chatInput.value = ''; globalAILoading.value = true; scrollToBottom()
  chatHistory.value.push({ role: 'ai', content: '检索并推理中...' }); scrollToBottom()
  try {
    const res = await axios.post(`${apiBase}/ai/chat`, { question: queryText })
    chatHistory.value[chatHistory.value.length - 1].content = res.data.answer
  } catch (e) { chatHistory.value[chatHistory.value.length - 1].content = "请求失败" }
  finally { globalAILoading.value = false; scrollToBottom() }
}

const renderMarkdown = (text) => { if (!text) return ''; return marked(text) }
const scrollToBottom = () => { nextTick(() => { if (chatWindowRef.value) chatWindowRef.value.scrollTop = chatWindowRef.value.scrollHeight }) }
const loadAllWords = async () => { switchTab('manage'); try { allWords.value = (await axios.get(`${apiBase}/words/all`)).data } catch (e) {} }
const updateMeaning = async (word) => { try { await axios.put(`${apiBase}/words/${word.id}`, { chinese_meaning: word.chinese_meaning }) } catch (e) {} }
const deleteWord = async (id) => { if (confirm("确定删除？")) { try { await axios.delete(`${apiBase}/words/${id}`); allWords.value = allWords.value.filter(w => w.id !== id); fetchStats() } catch (e) {} } }
const exportCSV = () => window.open(`${apiBase}/words/export`, '_blank')

onMounted(() => { fetchStats() })
</script>

<style scoped>
/* ==========================================
   优化后的 UI：兼顾高级感与交互反馈
   ========================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-color: #f4f7f6;
  --card-bg: #ffffff;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --primary: #2563eb;      /* 回归明亮且清晰的科技蓝 */
  --primary-hover: #1d4ed8;
  --danger: #ef4444;
  --success: #10b981;
  --radius-lg: 20px;
  --radius-md: 12px;
  --shadow-soft: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
}

.app-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  max-width: 700px;
  margin: 50px auto;
  color: var(--text-primary);
  min-height: 100vh;
}

/* 头部设计 */
.header { text-align: center; margin-bottom: 35px; }
.logo { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; margin: 0; color: #111827;}
.subtitle { color: var(--text-secondary); font-size: 14px; margin-top: 6px; margin-bottom: 24px; }

/* 导航 */
.nav-segmented-control {
  display: inline-flex; flex-wrap: wrap; justify-content: center;
  background: #f3f4f6; padding: 6px; border-radius: 14px; gap: 4px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.nav-segmented-control button {
  padding: 10px 16px; border: none; background: transparent; border-radius: 10px; font-size: 14px; font-weight: 600; color: #4b5563; cursor: pointer; transition: all 0.2s ease;
}
.nav-segmented-control button:hover { color: #111827; background: rgba(255,255,255,0.5); }
.nav-segmented-control button.active { background: #ffffff; color: var(--primary); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

/* 通用卡片与动画 */
.card { background: var(--card-bg); padding: 35px; border-radius: var(--radius-lg); box-shadow: var(--shadow-soft); border: 1px solid rgba(255,255,255,0.8); }
.fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

/* 表单与按钮 */
.modern-input { width: 100%; padding: 14px 18px; border: 2px solid var(--border-color); border-radius: var(--radius-md); font-size: 15px; transition: 0.2s; box-sizing: border-box; background: #f9fafb; }
.modern-input:focus { outline: none; border-color: var(--primary); background: #fff; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
.primary-btn { background: var(--primary); color: #fff; border: none; padding: 0 24px; border-radius: var(--radius-md); font-weight: 600; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); }
.primary-btn:hover { background: var(--primary-hover); transform: translateY(-1px); box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3); }
.secondary-btn { background: white; border: 1px solid #d1d5db; color: #374151; padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.secondary-btn:hover { background: #f3f4f6; border-color: #9ca3af;}

/* 看板 */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.stat-box { padding: 24px; border-radius: 16px; border: 1px solid var(--border-color); display: flex; flex-direction: column; align-items: center; justify-content: center; background: #fafafa;}
.stat-box.highlight { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);}
.stat-box.highlight .stat-label { color: #bfdbfe; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; font-weight: 600; }
.stat-value { font-size: 34px; font-weight: 800; letter-spacing: -1px; }

/* 录入界面 */
.input-group { display: flex; gap: 12px; margin-bottom: 25px;}
.preview-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 25px;}
.preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
.preview-word { margin: 0; font-size: 32px; font-weight: 800; color: #0f172a;}
.editor-group { margin: 20px 0; }
.editor-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 600; color: #475569;}
.confirm-btn { width: 100%; padding: 16px; background: #10b981; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s;}
.confirm-btn:hover { background: #059669; }

/* 复习卡片 */
.completion-state { text-align: center; padding: 40px 0; }
.completion-icon { font-size: 64px; margin-bottom: 20px; }
.completion-sub { color: #6b7280; margin-bottom: 30px;}
.flashcard { text-align: center; }
.progress-text { font-size: 13px; color: #6b7280; font-weight: 600; background: #f3f4f6; padding: 6px 14px; border-radius: 20px;}
.word-display { margin: 35px 0; }
.hero-word { font-size: 52px; font-weight: 800; letter-spacing: -1px; margin: 0 0 16px 0; color: #111827; }
.phonetic-row { display: inline-flex; align-items: center; gap: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 18px; border-radius: 20px; }
.phonetic { color: #64748b; font-family: monospace; font-size: 16px; }
.audio-btn.minimal { background: none; border: none; font-size: 18px; cursor: pointer; padding: 0; }

.spell-area { display: flex; gap: 10px; margin-bottom: 20px;}
.reveal-btn { width: 100%; padding: 18px; background: #f9fafb; border: 2px dashed #d1d5db; border-radius: var(--radius-md); font-size: 16px; font-weight: 600; color: #4b5563; cursor: pointer; transition: 0.2s;}
.reveal-btn:hover { background: #f3f4f6; border-color: #9ca3af; color: #111827; }

.meaning-area { text-align: left; border-top: 1px solid var(--border-color); padding-top: 30px; margin-top: 30px; }
.meaning-zh { font-size: 18px; margin: 0 0 10px 0; color: #1f2937;}
.meaning-en { color: #4b5563; font-size: 15px; margin: 0; }

.ai-tutor-btn { width: 100%; padding: 14px; margin: 25px 0; background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 12px; color: #6d28d9; font-weight: 600; cursor: pointer; transition: 0.2s; }
.ai-tutor-btn:hover { background: #ede9fe; border-color: #c4b5fd; }
.ai-response-box { background: #f8fafc; padding: 20px; border-radius: 12px; margin-bottom: 25px; border-left: 4px solid #8b5cf6; }

/* 🌟 恢复色彩的打分按钮 (柔和马卡龙色系) */
.rating-section { margin-top: 20px; }
.rating-hint { font-size: 13px; color: #6b7280; text-align: center; margin-bottom: 15px; font-weight: 500;}
.rating-buttons { display: flex; gap: 10px; }
.rate-btn { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 12px 0; border: none; border-radius: 12px; cursor: pointer; transition: 0.2s; border: 1px solid transparent;}
.rate-btn span { font-size: 15px; font-weight: 700; margin-bottom: 4px;}
.rate-btn small { font-size: 11px; opacity: 0.8; font-weight: 500;}

/* 柔和色彩定义 */
.rate-btn.hard { background: #fee2e2; color: #b91c1c; border-color: #fca5a5; }
.rate-btn.good { background: #fef3c7; color: #b45309; border-color: #fde68a; }
.rate-btn.easy { background: #d1fae5; color: #047857; border-color: #6ee7b7; }
.rate-btn.perfect { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.rate-btn:hover { transform: translateY(-3px); filter: brightness(0.95); box-shadow: 0 4px 6px rgba(0,0,0,0.05);}

/* 词库表格 (恢复 EF 列) */
.manage-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
.modern-table { width: 100%; border-collapse: collapse; }
.modern-table th { text-align: left; padding: 12px 14px; color: #6b7280; font-weight: 600; font-size: 13px; border-bottom: 2px solid var(--border-color); }
.modern-table td { padding: 14px; border-bottom: 1px solid #f3f4f6; font-size: 14px; vertical-align: middle;}
.table-input { width: 100%; border: none; background: transparent; padding: 8px; border-radius: 6px; font-size: 14px; color: #1f2937;}
.table-input:focus { background: #f9fafb; outline: 1px solid #d1d5db; }
.text-danger-btn { color: #ef4444; background: #fee2e2; border: none; font-weight: 600; padding: 6px 12px; border-radius: 6px; cursor: pointer; transition: 0.2s;}
.text-danger-btn:hover { background: #fca5a5; }
/* 🌟 EF 数值徽章 */
.ef-badge { background: #f3f4f6; color: #4b5563; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 700; border: 1px solid #e5e7eb;}

/* AI 聊天 */
.ai-chat-card { display: flex; flex-direction: column; height: 75vh; }
.chat-header-clean h2 { margin: 0 0 5px 0; font-weight: 800; color: #111827;}
.chat-subtitle { font-size: 13px; color: #6b7280; margin: 0 0 20px 0; }
.quick-prompts-clean { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px;}
.quick-prompts-clean button { flex: 1; padding: 10px 15px; background: white; border: 1px solid #d1d5db; border-radius: 10px; font-size: 13px; font-weight: 500; cursor: pointer; color: #4b5563; transition: 0.2s; white-space: nowrap;}
.quick-prompts-clean button:hover { border-color: #8b5cf6; color: #8b5cf6; background: #f5f3ff;}

.chat-window { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; padding: 15px; background: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb; margin-bottom: 20px;}
.empty-state { margin: auto; color: #9ca3af; font-size: 14px; font-weight: 500; }
.message-row { display: flex; width: 100%; }
.message-row.user { justify-content: flex-end; }
.message-row.ai { justify-content: flex-start; }
.message-bubble { max-width: 85%; padding: 14px 18px; border-radius: 16px; line-height: 1.6; font-size: 14px;}
.message-row.user .message-bubble { background: #8b5cf6; color: white; border-bottom-right-radius: 4px; }
.message-row.ai .message-bubble { background: #ffffff; border: 1px solid #e5e7eb; border-bottom-left-radius: 4px; color: #1f2937; box-shadow: 0 2px 4px rgba(0,0,0,0.02);}

.chat-input-wrapper { display: flex; gap: 10px; align-items: flex-end; }
.chat-input-wrapper textarea { flex: 1; padding: 14px; border: 2px solid #e5e7eb; border-radius: 12px; font-family: inherit; font-size: 14px; resize: none; background: #f9fafb; transition: 0.2s;}
.chat-input-wrapper textarea:focus { outline: none; border-color: #8b5cf6; background: white; }
.send-btn { background: #8b5cf6; color: white; border: none; padding: 14px 24px; border-radius: 12px; font-weight: 600; cursor: pointer; height: 50px; transition: 0.2s;}
.send-btn:hover:not(:disabled) { background: #7c3aed; }
.send-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* Markdown 优化 */
:deep(.markdown-body) { font-size: 14px; color: inherit; }
:deep(.markdown-body p) { margin-top: 0; margin-bottom: 0.8em; }
:deep(.markdown-body table) { width: 100%; border-collapse: collapse; margin: 15px 0; background: white; border-radius: 8px; overflow: hidden; outline: 1px solid #e5e7eb;}
:deep(.markdown-body th) { background-color: #f3f4f6; font-weight: 600; padding: 10px 12px; text-align: left; border-bottom: 1px solid #e5e7eb;}
:deep(.markdown-body td) { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; }
:deep(.markdown-body code) { background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #d946ef;}
</style>