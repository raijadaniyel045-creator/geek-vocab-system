<template>
  <div>
    <NavBarComponent/>
    <div id="spacer"></div>
    <section class="graph">
      <div class="stats-grid">
        <div class="stat-box">
          <span class="stat-label">总词汇量</span>
          <span class="stat-value">{{ model.total }}</span>
        </div>
        <div class="stat-box highlight">
          <span class="stat-label">待复习</span>
          <span class="stat-value">{{ model.pending_now }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">已掌握 (EF>2.6)</span>
          <span class="stat-value">{{ model.mastered }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {reactive} from "vue";

type statsModel = {
  total: number;
  pending_now: number;
  mastered: number;
}
const model = reactive<statsModel>({
  mastered: 0, pending_now: 0, total: 0
})
</script>

<style scoped>

#spacer {
  height: 30vh;
}

.graph {
  position: relative;
  top: 100%;
  width: 100%;
  padding-top: 80px;
  padding-bottom: 100px;
  font-size: 0;
  text-align: center;
  transition: .25s
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-box {
  padding: 24px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fafafa;
}

.stat-box.highlight {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border: none;
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
}

.stat-box.highlight .stat-label {
  color: #bfdbfe;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 600;
}

.stat-value {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -1px;
}
</style>