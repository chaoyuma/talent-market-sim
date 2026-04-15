<script setup>
// 结果摘要卡片组件

import InfoTip from "../common/InfoTip.vue";

defineProps({
  cards: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div
    class="section-gap"
    style="
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
    "
  >
    <div
      v-for="card in cards"
      :key="card.key"
      class="ui-card"
      style="min-height: 88px;"
    >
      <div
        style="
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 10px;
          color: #667085;
          font-size: 14px;
          font-weight: 500;
        "
      >
        <span>{{ card.title }}</span>
        <InfoTip v-if="card.tooltip" :text="card.tooltip" />
      </div>

      <div
        style="
          font-size: 18px;
          font-weight: 700;
          color: #101828;
          line-height: 1.2;
        "
      >
        {{ card.value }}
      </div>
    </div>
  </div>
</template>