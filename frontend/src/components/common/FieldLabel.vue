<script setup>
import InfoTip from "./InfoTip.vue";

// 参数标签组件：显示名称 + 提示
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
  <label class="field-label">
    <span>{{ label }}</span>
    <InfoTip v-if="tooltip" :text="tooltip" />
  </label>
</template>

<style scoped>
.field-label {
  display: inline-flex;
  align-items: center;
  width: 220px;
  font-weight: 500;
}
</style>