<template>
  <div
      id="nav-bar"
      :class="{ sticky: store.isSticky }"
  >
    <div id="nav-logo-container">

    </div>
    <div id="nav-link-container">
      <router-link class="nav-link" to="/">首页</router-link>
      <router-link class="nav-link" to="/add">生词录入</router-link>
      <router-link class="nav-link" to="/review">专注复习</router-link>
      <router-link class="nav-link" to="/manage">我的词库</router-link>
      <router-link class="nav-link" to="/ai_chat">AI洞察</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import {useNavbarStore} from "../store";

const store = useNavbarStore();
</script>

<style scoped>

:root {
  --nav-height: 90px;
}

#nav-bar {
  position: absolute;
  top: 0;
  width: 100%;
  height: var(--nav-height);
  transition: .25s
}

#nav-bar.sticky {
  z-index: 99;
  position: fixed;
  --nav-height: 82px;
  background-color: var(--bg-w-pure);
  box-shadow: rgba(0, 0, 0, .1) 0 5px 20px
}

#nav-logo-container {
  position: absolute;
  top: 20px;
  left: 200px;
  font-size: 0;
  transition: .25s
}

#nav-logo-main, #nav-logo-text {
  display: inline-block;
  height: 50px;
  background-repeat: no-repeat;
  background-size: contain;
  background-position: left center;
  transition: .25s
}

#nav-logo-main {
  width: 50px;
  background-color: var(--bg-w-pure);
}

#nav-logo-text {
  width: 100px;
}

#nav-bar.sticky #nav-logo-container {
  top: 16px
}

#nav-link-container {
  position: absolute;
  right: 170px;
  top: 30px;
  white-space: nowrap;
  transition: .25s
}

.nav-link {
  position: relative;
  cursor: pointer;
  transition: .25s
}

#nav-bar .nav-link {
  margin: 0 10px;
  padding: 10px 20px;
  border-radius: 5px;
  color: #fff;
  font-size: 15px;
}

#nav-bar .nav-link:before {
  position: absolute;
  left: 20px;
  bottom: 3px;
  width: calc(100% - 40px);
  height: 3px;
  content: '';
  background: var(--theme-color);
  border-radius: 2px;
  transition: .25s;
  transform: scale(0);
  opacity: 0
}


#nav-bar .nav-link:hover {
  background-color: var(--b-alpha-5)
}

#nav-bar .nav-link:hover:before {
  transform: scale(1);
  opacity: 1
}

#nav-bar .nav-link:active, #nav-bar .nav-link:active:before {
  opacity: .6
}

#nav-bar.sticky .nav-link {
  color: var(--txt-b-pure)
}


@media screen and (max-width: 1300px) {
  #nav-logo-container {
    left: 100px
  }

  #nav-link-container {
    right: 70px
  }
}

@media screen and (max-width: 900px) {
  #nav-logo-container {
    left: 70px
  }

  #nav-link-container {
    right: 40px
  }
}

@media screen and (max-width: 760px) {
  #nav-logo-container {
    left: 25px
  }

  #nav-link-container {
    display: none
  }
}
</style>