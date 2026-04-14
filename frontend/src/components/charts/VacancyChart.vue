<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";

// 显式注册 ECharts 所需模块
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

import { buildVacancyChartOption } from "../../utils/chartOptions";

// 注册图表依赖模块
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent]);

// 岗位空缺率变化图组件
const props = defineProps({
  results: {
    type: Array,
    default: () => [],
  },
});

// 根据结果动态生成图表配置
const option = computed(() => buildVacancyChartOption(props.results));
</script>

<template>
  <div
    style="
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      background: #fff;
    "
  >
    <h3 style="margin-top: 0;">岗位空缺率变化</h3>
    <VChart :option="option" autoresize style="height: 320px;" />
  </div>
</template>