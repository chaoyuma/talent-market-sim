<script setup>
import PageHeader from "../components/common/PageHeader.vue";
import ExperimentHistory from "../components/result/ExperimentHistory.vue";
</script>

<template>
  <div
    style="
      padding: 24px;
      font-family: Arial, sans-serif;
      max-width: 1480px;
      margin: 0 auto;
    "
  >
    <PageHeader
      title="历史记录"
      subtitle="查看历史实验、展开实验详情，并对比逐轮指标结果。"
    />

    <ExperimentHistory />
  </div>
</template>