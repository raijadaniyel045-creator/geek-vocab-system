<script setup lang="ts">

</script>

<template>
  <main v-if="currentMode === 'review_setup'" class="card setup-card fade-in">
    <div class="setup-form">
      <div class="form-section">
        <label class="section-title">本次复习数量：<span class="highlight-text">{{ reviewLimit }} 个</span></label>
        <input v-model="reviewLimit" class="modern-range" max="50" min="5" step="5" type="range">
      </div>
      <div class="form-section">
        <label class="section-title">选择复习模式</label>
        <div class="radio-group">
          <label class="radio-label"><input v-model="reviewType" type="radio" value="flashcard"> 📇 经典翻卡</label>
          <label class="radio-label"><input v-model="reviewType" type="radio" value="spell_zh2en"> ✍️ 默写模式 (看中写英)</label>
          <label class="radio-label"><input v-model="reviewType" type="radio" value="spell_en2zh"> 🧠 释义挑战 (看英写中)</label>
        </div>
      </div>
      <button class="primary-btn start-btn" @click="startReview">🚀 开始复习</button>
    </div>
  </main>
</template>

<style scoped>

</style>