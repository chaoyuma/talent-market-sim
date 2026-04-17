<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

import { buildRegionalGapChartOption } from "../../utils/chartOptions";

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent]);

const props = defineProps({
  structureAnalysis: {
    type: Object,
    default: () => ({}),
  },
});

const option = computed(() => buildRegionalGapChartOption(props.structureAnalysis));
</script>

<template>
  <div class="ui-card">
    <h3 class="subsection-title">区域供需与吸纳</h3>
    <VChart :option="option" autoresize style="height: 320px;" />
  </div>
</template>
