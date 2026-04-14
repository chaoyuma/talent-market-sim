<script setup>
import InfoTip from "../common/InfoTip.vue";
import { resultMeta } from "../../utils/fieldMeta";

// 结果卡片组件
// cards 由父组件传入，格式见 buildStatCards 的输出
defineProps({
  cards: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div
    style="
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    "
  >
    <div
      v-for="card in cards"
      :key="card.key"
      style="
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        background: #fff;
      "
    >
      <div
        style="
          color: #666;
          font-size: 14px;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
        "
      >
        <span>{{ card.label }}</span>
        <InfoTip
          v-if="resultMeta[card.key]"
          :text="resultMeta[card.key].tooltip"
        />
      </div>

      <div style="font-size: 24px; font-weight: bold;">
        {{ card.value }}
      </div>
    </div>
  </div>
</template>