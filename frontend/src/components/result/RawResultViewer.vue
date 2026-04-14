<script setup>
// 原始结果查看组件
defineProps({
  result: {
    type: Object,
    default: null,
  },
});
</script>

<template>
  <div style="margin-bottom: 24px;">
    <h3>原始结果 JSON</h3>
    <pre
      style="
        background: #f5f5f5;
        padding: 16px;
        border-radius: 8px;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
      "
    >{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>