<script setup>
// 通用卡片容器
// 用来统一各个参数块和结果块的视觉风格

defineProps({
  title: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div
    style="
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
      background: #fff;
    "
  >
    <h3 v-if="title" style="margin-top: 0;">
      {{ title }}
    </h3>

    <slot />
  </div>
</template>