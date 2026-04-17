<script setup>
// frontend/src/components/result/MajorDistributionChart.vue
// 专业分布对比图：学生专业分布 vs 岗位专业分布

import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  studentDistribution: {
    type: Array,
    default: () => [],
  },
  jobDistribution: {
    type: Array,
    default: () => [],
  },
});

const majors = computed(() => props.studentDistribution.map((x) => x.major));

const option = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { top: 6, left: 8, right: 8, type: "scroll" },
  grid: { left: 60, right: 24, top: 76, bottom: 48, containLabel: true },
  xAxis: {
    type: "category",
    data: majors.value,
    name: "专业",
  },
  yAxis: {
    type: "value",
    name: "人数",
  },
  series: [
    {
      name: "学生人数",
      type: "bar",
      data: props.studentDistribution.map((x) => x.count),
    },
    {
      name: "岗位人数",
      type: "bar",
      data: props.jobDistribution.map((x) => x.count),
    },
  ],
}));
</script>

<template>
  <div class="ui-card">
    <h4 class="subsection-title">专业分布对比</h4>
    <VChart :option="option" autoresize style="height: 360px;" />
  </div>
</template>
