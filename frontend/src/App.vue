<script setup>
import { ref } from "vue";

import AppHeader from "./components/layout/AppHeader.vue";
import SimulationPage from "./views/SimulationPage.vue";
import DataDictionaryPage from "./views/DataDictionaryPage.vue";
import HistoryPage from "./views/HistoryPage.vue";

const activeTab = ref("simulation");

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
  </div>
</template>