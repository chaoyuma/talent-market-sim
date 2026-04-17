<script setup>
// frontend/src/components/result/IndustryJobDistributionChart.vue
// 岗位行业分布图：展示岗位在各行业的分布情况

import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
});

const option = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { show: false },
  grid: { left: 60, right: 30, top: 30, bottom: 60 },
  xAxis: {
    type: "category",
    data: props.rows.map((x) => x.industry),
    name: "行业",
    axisLabel: {
      interval: 0,
      rotate: 20,
    },
  },
  yAxis: {
    type: "value",
    name: "岗位数",
  },
  series: [
    {
      name: "岗位数",
      type: "bar",
      data: props.rows.map((x) => x.count),
    },
  ],
}));
</script>

<template>
  <div class="ui-card">
    <h4 class="subsection-title">岗位行业分布</h4>
    <VChart :option="option" autoresize style="height: 360px;" />
  </div>
</template>