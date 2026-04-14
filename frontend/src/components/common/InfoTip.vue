<script setup>
// 小问号提示组件
defineProps({
  text: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <span class="info-tip-wrapper">
    <span class="info-tip-icon">?</span>
    <span class="info-tip-popup">{{ text }}</span>
  </span>
</template>

<style scoped>
.info-tip-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  margin-left: 6px;
  cursor: pointer;
}

.info-tip-icon {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #1677ff;
  color: #fff;
  font-size: 12px;
  line-height: 16px;
  text-align: center;
  font-weight: bold;
}

.info-tip-popup {
  display: none;
  position: absolute;
  top: 22px;
  left: 0;
  width: 240px;
  padding: 8px 10px;
  background: #333;
  color: #fff;
  font-size: 12px;
  line-height: 1.4;
  border-radius: 6px;
  z-index: 1000;
  white-space: normal;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.info-tip-wrapper:hover .info-tip-popup {
  display: block;
}
</style>