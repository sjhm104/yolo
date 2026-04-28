<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="aside">
      <div class="brand">Campus Waste Admin</div>

      <el-menu
        :default-active="route.path"
        class="menu"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#f8fafc"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>综合看板</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">基于无人机校园垃圾检测系统</el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { DataBoard } from "@element-plus/icons-vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const handleMenuSelect = (index) => {
  if (index !== route.path) {
    router.push(index);
  }
};
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f3f4f6;
}

.aside {
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: #f8fafc;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.brand {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 18px;
  font-weight: 700;
  letter-spacing: 0.2px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.menu {
  border-right: none;
}

.header {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.main {
  padding: 18px;
}
</style>
