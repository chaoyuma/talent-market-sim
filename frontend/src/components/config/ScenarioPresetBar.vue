<script setup>
import { scenarioTemplateList } from "../../utils/scenarioTemplates";

defineProps({
  activeScenario: {
    type: String,
    default: "baseline",
  },
});

const emit = defineEmits(["apply-scenario"]);
</script>

<template>
  <div class="ui-card section-gap">
    <h3 class="subsection-title">预设场景</h3>

    <div
      style="
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 12px;
      "
    >
      <button
        v-for="item in scenarioTemplateList"
        :key="item.key"
        class="ui-btn"
        :style="activeScenario === item.key ? 'background:#1570ef;color:#fff;border-color:#1570ef;' : ''"
        @click="$emit('apply-scenario', item)"
      >
        {{ item.name }}
      </button>
    </div>

    <div style="font-size: 14px; color: #667085;">
      点击按钮可一键套用对应场景参数，用于快速开展对比仿真。
    </div>
  </div>
</template>