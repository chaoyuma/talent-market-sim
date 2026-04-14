<script setup>
// 企业反馈参数面板（自动渲染版）

import ConfigField from "./ConfigField.vue";
import { employerConfigFields } from "../../utils/panelFields";

// 接收父组件的 v-model
const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});

// 向父组件回传更新
const emit = defineEmits(["update:modelValue"]);

/**
 * 更新字段值
 * @param {string} key 字段名
 * @param {any} value 新值
 */
function updateField(key, value) {
  emit("update:modelValue", {
    ...props.modelValue,
    [key]: value,
  });
}
</script>

<template>
  <div>
    <ConfigField
      v-for="fieldKey in employerConfigFields"
      :key="fieldKey"
      :field-key="fieldKey"
      :value="modelValue[fieldKey]"
      @update:value="updateField(fieldKey, $event)"
    />
  </div>
</template>