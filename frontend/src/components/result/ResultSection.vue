<script setup>
// 结果总区组件
// 统一组织结果卡片、图表、指标表和原始 JSON

import { computed } from "vue";

import SummaryCards from "./SummaryCards.vue";
import MetricsTable from "./MetricsTable.vue";
import RawResultViewer from "./RawResultViewer.vue";
import EmploymentChart from "../charts/EmploymentChart.vue";
import VacancyChart from "../charts/VacancyChart.vue";

import { getLatestResult, buildStatCards } from "../../utils/resultHelpers";

// 接收完整结果对象
const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

// 最新一步结果
const latest = computed(() => getLatestResult(props.result));

// 结果卡片数组
const statCards = computed(() => buildStatCards(latest.value));
</script>

<template>
  <div v-if="result">
    <h2>仿真结果</h2>

    <!-- 顶部结果卡片 -->
    <SummaryCards :cards="statCards" />

    <!-- 图表区 -->
    <div
      style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
      "
    >
      <EmploymentChart :results="result.results" />
      <VacancyChart :results="result.results" />
    </div>

    <!-- 每轮指标表 -->
    <MetricsTable :rows="result.results" />

    <!-- 原始 JSON -->
    <RawResultViewer :result="result" />
  </div>
</template>