<template>
  <div id="app-container">
    <main>
      <router-view v-slot="{ Component }">
        <transition mode="out-in" name="fade">
          <component :is="Component"/>
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script lang="ts" setup>
</script>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>
