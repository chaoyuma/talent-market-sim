<script setup>
import { computed } from "vue";

import SummaryCards from "./SummaryCards.vue";
import MetricsTable from "./MetricsTable.vue";
import ResultExplanation from "./ResultExplanation.vue";
import RawResultViewer from "./RawResultViewer.vue";
import StructureAnalysisSection from "./StructureAnalysisSection.vue";

import EmploymentChart from "../charts/EmploymentChart.vue";
import VacancyChart from "../charts/VacancyChart.vue";
import OfferFunnelChart from "../charts/OfferFunnelChart.vue";
import CarryoverTrendChart from "../charts/CarryoverTrendChart.vue";
import RegionalGapChart from "../charts/RegionalGapChart.vue";
import MajorHeatChart from "../charts/MajorHeatChart.vue";
import ParameterSuggestionSection from "./ParameterSuggestionSection.vue";

import { getLatestResult, buildGroupedStatCards } from "../../utils/resultHelpers";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
  title: {
    type: String,
    default: "仿真结果",
  },
  initialExplanation: {
    type: String,
    default: "",
  },
});

const latest = computed(() => getLatestResult(props.result));
const groupedStatCards = computed(() => buildGroupedStatCards(latest.value));
const emit = defineEmits(["apply-suggested-params"]);
function handleApplySuggestedParams(suggestedParams) {
  emit("apply-suggested-params", suggestedParams);
}
</script>

<template>
  <div v-if="result">
    <h2 class="section-title">{{ title }}</h2>

    <div v-if="result.actual_runtime" class="ui-card section-gap">
      <h3 class="subsection-title">实际运行规模</h3>
      <div class="responsive-grid-2">
        <div>学生：{{ result.actual_runtime.student_count }}</div>
        <div>学校：{{ result.actual_runtime.school_count }}</div>
        <div>企业：{{ result.actual_runtime.employer_count }}</div>
        <div>专业：{{ result.actual_runtime.major_count }}</div>
        <div>数据模式：{{ result.actual_runtime.data_mode }}</div>
        <div v-if="result.actual_runtime.seed_runs">
          随机种子重复：{{ result.actual_runtime.seed_runs }}
        </div>
        <div v-if="result.actual_runtime.aggregation">
          聚合方式：{{ result.actual_runtime.aggregation }}
        </div>
      </div>
    </div>

    <div
      v-for="group in groupedStatCards"
      :key="group.groupKey"
      class="section-gap"
    >
      <h3 class="subsection-title">{{ group.groupTitle }}</h3>
      <SummaryCards :cards="group.cards" />
    </div>

    <div class="responsive-grid-2 section-gap">
      <EmploymentChart :results="result.results" />
      <VacancyChart :results="result.results" />
      <OfferFunnelChart :results="result.results" />
      <CarryoverTrendChart :results="result.results" />
      <RegionalGapChart :structure-analysis="result.structure_analysis" />
      <MajorHeatChart :structure-analysis="result.structure_analysis" />
    </div>

    <StructureAnalysisSection :structure-analysis="result.structure_analysis" />
    <ResultExplanation :result="result" :initial-explanation="initialExplanation" />
    <ParameterSuggestionSection
      :result="result"
      @apply-suggested-params="handleApplySuggestedParams"
    />
    <MetricsTable :rows="result.results" />
    <RawResultViewer :result="result" />
  </div>
</template>
