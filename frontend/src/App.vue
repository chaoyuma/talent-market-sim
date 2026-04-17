<script setup>
// 应用主入口：统一管理顶部页签与页面切换

import { ref } from "vue";

import AppHeader from "./components/layout/AppHeader.vue";
import SimulationPage from "./views/SimulationPage.vue";
import DataDictionaryPage from "./views/DataDictionaryPage.vue";
import HistoryPage from "./views/HistoryPage.vue";
import ReportPage from "./views/ReportPage.vue";
import ReportHistoryPage from "./views/ReportHistoryPage.vue"; // 新增：历史报告页

// 当前激活页签
const activeTab = ref("simulation");

/**
 * 切换顶部页签
 * @param {string} tab 页签标识
 */
function handleChangeTab(tab) {
  activeTab.value = tab;
}
</script>

<template>
  <div style="min-height: 100vh; background: #f8fafc;">
    <AppHeader :active-tab="activeTab" @change-tab="handleChangeTab" />

    <template v-if="activeTab === 'simulation'">
      <SimulationPage />
    </template>

    <template v-else-if="activeTab === 'dictionary'">
      <DataDictionaryPage />
    </template>

    <template v-else-if="activeTab === 'history'">
      <HistoryPage />
    </template>

    <template v-else-if="activeTab === 'report'">
      <ReportPage />
    </template>

    <template v-else-if="activeTab === 'report-history'">
      <ReportHistoryPage />
    </template>
  </div>
</template>