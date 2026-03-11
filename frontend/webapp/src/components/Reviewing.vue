<script setup lang="ts">

</script>

<template>
  <main v-if="currentMode === 'reviewing'" class="card review-card fade-in">
    <div v-if="reviewList.length === 0" class="completion-state">
      <div class="completion-icon">🎉</div>
      <h2>本组复习已完成！</h2>
      <p class="completion-sub">太棒了，休息一下或者继续挑战吧。</p>
      <button class="secondary-btn" @click="switchTab('review_setup')">返回复习设置</button>
    </div>

    <div v-else class="flashcard">
      <div class="progress-bar-container">
        <span class="progress-text">剩余 <strong>{{ reviewList.length }}</strong> 词</span>
      </div>

      <div class="word-display">
        <h1 v-if="reviewType !== 'spell_zh2en'" class="hero-word">{{ currentReviewWord.word }}</h1>
        <h1 v-if="reviewType === 'spell_zh2en'" class="hero-word">{{ currentReviewWord.chinese_meaning }}</h1>
        <div v-if="reviewType !== 'spell_zh2en'" class="phonetic-row">
          <span class="phonetic">{{ currentReviewWord.phonetic }}</span>
          <button v-if="currentReviewWord.audio_url" class="audio-btn minimal"
                  @click="playAudio(currentReviewWord.audio_url)">🔊
          </button>
        </div>
      </div>

      <div v-if="reviewType.startsWith('spell_') && !showMeaning" class="spell-area">
        <input ref="spellInputRef" v-model="userSpellInput" class="modern-input spell-input"
               placeholder="请输入你的答案..."
               type="text" @keyup.enter="checkSpell"/>
        <button class="primary-btn" @click="checkSpell">验证答案</button>
      </div>

      <div v-if="reviewType === 'flashcard' && !showMeaning" class="action-area">
        <button class="reveal-btn" @click="showMeaning = true">👀 点击显示答案</button>
      </div>

      <div v-if="showMeaning" class="meaning-area fade-in">
        <div v-if="reviewType.startsWith('spell_')" :class="isSpellCorrect ? 'correct' : 'wrong'"
             class="spell-feedback">
          {{ isSpellCorrect ? '✅ 回答正确！' : '❌ 回答有误，请核对标准答案：' }}
        </div>

        <div class="definition-block">
          <p class="meaning-zh"><strong>中文：</strong>{{ currentReviewWord.chinese_meaning }}</p>
          <p class="meaning-en"><strong>英文：</strong>{{ currentReviewWord.word }}</p>
        </div>

        <button :disabled="aiLoading" class="ai-tutor-btn" @click="askAI">
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
</template>

<style scoped>

</style>