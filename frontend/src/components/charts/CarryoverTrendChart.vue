<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

import { buildCarryoverTrendChartOption } from "../../utils/chartOptions";

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  results: {
    type: Array,
    default: () => [],
  },
});

const option = computed(() => buildCarryoverTrendChartOption(props.results));
</script>

<template>
  <div class="ui-card">
    <h3 class="subsection-title">滞留求职趋势</h3>
    <VChart :option="option" autoresize style="height: 320px;" />
  </div>
</template>
