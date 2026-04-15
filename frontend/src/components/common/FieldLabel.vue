<script setup>
import InfoTip from "./InfoTip.vue";

defineProps({
  label: {
    type: String,
    required: true,
  },
  tooltip: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div
    style="
      min-width: 260px;
      max-width: 420px;
      font-size: 14px;
      color: #344054;
      line-height: 1.5;
      display: flex;
      align-items: flex-start;
      gap: 6px;
      flex-wrap: wrap;
    "
  >
    <span>{{ label }}</span>
    <InfoTip v-if="tooltip" :text="tooltip" />
  </div>
</template>