<script setup>
// frontend/src/components/result/StructureAnalysisSection.vue
// 结构分析总区：统一组织专业供需偏差表、专业分布图、岗位行业分布图

import MajorSupplyDemandTable from "./MajorSupplyDemandTable.vue";
import MajorDistributionChart from "./MajorDistributionChart.vue";
import IndustryJobDistributionChart from "./IndustryJobDistributionChart.vue";

defineProps({
  structureAnalysis: {
    type: Object,
    default: null,
  },
});
</script>

<template>
  <div v-if="structureAnalysis" class="section-gap">
    <h3 class="subsection-title">结构分析</h3>

    <!-- 专业供需偏差表 -->
    <MajorSupplyDemandTable
      :rows="structureAnalysis.major_supply_demand_gap || []"
    />

    <!-- 分布图 -->
    <div
      style="
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-top: 16px;
      "
    >
      <MajorDistributionChart
        :student-distribution="structureAnalysis.major_student_distribution || []"
        :job-distribution="structureAnalysis.major_job_distribution || []"
      />

      <IndustryJobDistributionChart
        :rows="structureAnalysis.industry_job_distribution || []"
      />
    </div>
  </div>
</template>