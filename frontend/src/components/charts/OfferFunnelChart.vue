<script setup>
import { computed } from "vue";
import VChart from "vue-echarts";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";

import { buildOfferFunnelChartOption } from "../../utils/chartOptions";

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent]);

const props = defineProps({
  results: {
    type: Array,
    default: () => [],
  },
});

const option = computed(() => buildOfferFunnelChartOption(props.results));
</script>

<template>
  <div class="ui-card">
    <h3 class="subsection-title">申请-Offer转化</h3>
    <VChart :option="option" autoresize style="height: 320px;" />
  </div>
</template>
