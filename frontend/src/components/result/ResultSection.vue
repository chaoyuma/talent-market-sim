<script setup>
// 结果总区组件
// 统一组织结果卡片、图表、指标表和原始 JSON

import { computed } from "vue";

import SummaryCards from "./SummaryCards.vue";
import MetricsTable from "./MetricsTable.vue";
import ResultExplanation from "./ResultExplanation.vue";
import RawResultViewer from "./RawResultViewer.vue";
import EmploymentChart from "../charts/EmploymentChart.vue";
import VacancyChart from "../charts/VacancyChart.vue";

import { getLatestResult, buildGroupedStatCards } from "../../utils/resultHelpers";

// 接收完整结果对象
const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

// 最新一步结果
const latest = computed(() => getLatestResult(props.result));

// 分组结果卡片
const groupedStatCards = computed(() => buildGroupedStatCards(latest.value));
</script>

<template>
  <div v-if="result">
    <h2 class="section-title">仿真结果</h2>

    <!-- 实际运行规模 -->
    <div v-if="result.actual_runtime" class="ui-card section-gap">
      <h3 class="subsection-title">实际运行规模</h3>
      <div class="responsive-grid-2">
        <div>学生：{{ result.actual_runtime.student_count }}</div>
        <div>学校：{{ result.actual_runtime.school_count }}</div>
        <div>企业：{{ result.actual_runtime.employer_count }}</div>
        <div>专业：{{ result.actual_runtime.major_count }}</div>
        <div>数据模式：{{ result.actual_runtime.data_mode }}</div>
      </div>
    </div>

    <!-- 分组指标卡片 -->
    <div
      v-for="group in groupedStatCards"
      :key="group.groupKey"
      class="section-gap"
    >
      <h3 class="subsection-title">{{ group.groupTitle }}</h3>
      <SummaryCards :cards="group.cards" />
    </div>

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

    <!-- 结果解释 -->
    <ResultExplanation :result="result" />

    <!-- 每轮指标表 -->
    <MetricsTable :rows="result.results" />

    <!-- 原始 JSON -->
    <RawResultViewer :result="result" />
  </div>
</template>