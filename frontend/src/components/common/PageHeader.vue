<script setup>
// 页面头部组件
// 当前先负责显示主标题，后续可扩展为副标题、说明文字、全局按钮等。

defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div style="margin-bottom: 20px;">
    <h1 style="margin: 0 0 8px 0;">{{ title }}</h1>

    <div v-if="subtitle" style="color: #666; font-size: 14px;">
      {{ subtitle }}
    </div>
  </div>
</template>