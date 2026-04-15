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

const cumulativeOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { type: "scroll" },
  grid: { left: 50, right: 50, top: 50, bottom: 40 },
  xAxis: {
    type: "category",
    data: steps.value,
    name: "step",
  },
  yAxis: [
    {
      type: "value",
      min: 0,
      max: 1.2,
      name: "比例/满意度",
    },
    {
      type: "value",
      name: "薪资",
    },
  ],
  series: [
    {
      name: "累计就业率",
      type: "line",
      smooth: true,
      data: props.metrics.map((m) => m.employment_rate),
      yAxisIndex: 0,
    },
    {
      name: "累计对口率",
      type: "line",
      smooth: true,
      data: props.metrics.map((m) => m.matching_rate),
      yAxisIndex: 0,
    },
    {
      name: "累计跨专业率",
      type: "line",
      smooth: true,
      data: props.metrics.map((m) => m.cross_major_rate),
      yAxisIndex: 0,
    },
    {
      name: "累计满意度",
      type: "line",
      smooth: true,
      data: props.metrics.map((m) => m.avg_satisfaction),
      yAxisIndex: 0,
    },
    {
      name: "累计平均薪资",
      type: "line",
      smooth: true,
      data: props.metrics.map((m) => m.avg_salary),
      yAxisIndex: 1,
    },
  ],
}));

const flowOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { type: "scroll" },
  grid: { left: