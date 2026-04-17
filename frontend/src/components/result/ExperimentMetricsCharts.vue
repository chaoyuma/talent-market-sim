<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  metrics: {
    type: Array,
    default: () => [],
  },
});

const steps = computed(() => props.metrics.map((m) => m.step));

function buildLegend() {
  return {
    top: 6,
    left: 8,
    right: 8,
    type: "scroll",
  };
}

function buildGrid(extra = {}) {
  return {
    left: 60,
    right: 36,
    top: 78,
    bottom: 48,
    containLabel: true,
    ...extra,
  };
}

const cumulativeOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: buildLegend(),
  grid: buildGrid({ right: 56 }),
  xAxis: { type: "category", data: steps.value, name: "轮次" },
  yAxis: [
    { type: "value", min: 0, max: 1.2, name: "比例/满意度" },
    { type: "value", name: "薪资" },
  ],
  series: [
    { name: "累计就业率", type: "line", smooth: true, data: props.metrics.map((m) => m.employment_rate), yAxisIndex: 0 },
    { name: "累计对口率", type: "line", smooth: true, data: props.metrics.map((m) => m.matching_rate), yAxisIndex: 0 },
    { name: "累计跨专业率", type: "line", smooth: true, data: props.metrics.map((m) => m.cross_major_rate), yAxisIndex: 0 },
    { name: "累计平均满意度", type: "line", smooth: true, data: props.metrics.map((m) => m.avg_satisfaction), yAxisIndex: 0 },
    { name: "累计平均薪资", type: "line", smooth: true, data: props.metrics.map((m) => m.avg_salary), yAxisIndex: 1 },
  ],
}));

const flowOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: buildLegend(),
  grid: buildGrid({ right: 56 }),
  xAxis: { type: "category", data: steps.value, name: "轮次" },
  yAxis: [
    { type: "value", min: 0, name: "人数/岗位数" },
    { type: "value", min: 0, max: 1, name: "比例" },
  ],
  series: [
    { name: "活跃求职人数", type: "bar", data: props.metrics.map((m) => m.active_job_seekers), yAxisIndex: 0 },
    { name: "本轮岗位数", type: "bar", data: props.metrics.map((m) => m.round_job_count), yAxisIndex: 0 },
    { name: "本轮已填岗位数", type: "bar", data: props.metrics.map((m) => m.round_filled_jobs), yAxisIndex: 0 },
    { name: "本轮空缺率", type: "line", smooth: true, data: props.metrics.map((m) => m.round_vacancy_rate), yAxisIndex: 1 },
    { name: "本轮新增就业率", type: "line", smooth: true, data: props.metrics.map((m) => m.round_new_employment_rate), yAxisIndex: 1 },
  ],
}));

const structureOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: buildLegend(),
  grid: buildGrid(),
  xAxis: { type: "category", data: steps.value, name: "轮次" },
  yAxis: { type: "value", min: 0, name: "指标值" },
  series: [
    { name: "结构错配指数", type: "line", smooth: true, data: props.metrics.map((m) => m.mismatch_index) },
    { name: "扎堆指数", type: "line", smooth: true, data: props.metrics.map((m) => m.herding_index) },
    { name: "平均招聘阈值", type: "line", smooth: true, data: props.metrics.map((m) => m.avg_hire_threshold) },
    { name: "平均跨专业容忍度", type: "line", smooth: true, data: props.metrics.map((m) => m.avg_cross_major_tolerance) },
    { name: "平均培养质量", type: "line", smooth: true, data: props.metrics.map((m) => m.avg_training_quality) },
  ],
}));
</script>

<template>
  <div class="section-gap">
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div class="ui-card">
        <h3 class="subsection-title">累计结果指标趋势</h3>
        <VChart :option="cumulativeOption" autoresize style="height: 360px;" />
      </div>

      <div class="ui-card">
        <h3 class="subsection-title">本轮流量指标趋势</h3>
        <VChart :option="flowOption" autoresize style="height: 360px;" />
      </div>

      <div class="ui-card">
        <h3 class="subsection-title">结构与反馈指标趋势</h3>
        <VChart :option="structureOption" autoresize style="height: 380px;" />
      </div>
    </div>
  </div>
</template>
