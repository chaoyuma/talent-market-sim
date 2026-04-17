<script setup>
// 通用参数项组件
// 根据 fieldMeta 自动决定渲染 checkbox / select / number / text
// 并在参数名称后面自动显示范围与步长信息

import { computed } from "vue";
import FieldLabel from "../common/FieldLabel.vue";
import { fieldMeta } from "../../utils/fieldMeta";

// 接收字段名和当前值
const props = defineProps({
  fieldKey: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number, Boolean, null],
    default: null,
  },
});

// 向父组件回传新值
const emit = defineEmits(["update:value"]);

// 当前字段元数据
const meta = computed(() => fieldMeta[props.fieldKey] || {});

/**
 * 构造显示标签：
 * 例如：
 * 兴趣权重（范围 0~1，步长 0.01）
 * 仿真轮次（最小值 1，步长 1）
 */
const displayLabel = computed(() => {
  const baseLabel = meta.value.label || props.fieldKey;
  const bilingualLabel =
    baseLabel === props.fieldKey
      ? props.fieldKey
      : `${baseLabel}（${props.fieldKey}）`;

  const type = meta.value.type;

  // checkbox / text / select 不拼范围说明
  if (type !== "number") {
    return bilingualLabel;
  }

  const min = meta.value.min;
  const max = meta.value.max;
  const step = meta.value.step;

  const parts = [];

  if (min !== undefined && max !== undefined) {
    parts.push(`${min}~${max}`);
  } else if (min !== undefined) {
    parts.push(`≥${min}`);
  } else if (max !== undefined) {
    parts.push(`≤${max}`);
  }

  if (step !== undefined) {
    parts.push(`步长 ${step}`);
  }

  if (parts.length === 0) {
    return bilingualLabel;
  }

  return `${bilingualLabel}｜${parts.join("，")}`;
});

/**
 * 处理输入框变更
 * @param {Event} event 输入事件
 */
function handleInput(event) {
  const rawValue = event.target.value;

  if (meta.value.type === "number") {
    emit("update:value", Number(rawValue));
    return;
  }

  emit("update:value", rawValue);
}

/**
 * 处理下拉框变更
 * @param {Event} event 变更事件
 */
function handleSelect(event) {
  emit("update:value", event.target.value);
}

/**
 * 处理复选框变更
 * @param {Event} event 变更事件
 */
function handleCheckbox(event) {
  emit("update:value", event.target.checked);
}
</script>

<template>
  <!-- 复选框 -->
  <div v-if="meta.type === 'checkbox'" class="checkbox-row">
    <FieldLabel :label="displayLabel" :tooltip="meta.tooltip || ''" />
    <input
      :checked="!!value"
      @change="handleCheckbox"
      type="checkbox"
    />
  </div>

  <!-- 其他类型 -->
  <div v-else class="form-row">
    <FieldLabel :label="displayLabel" :tooltip="meta.tooltip || ''" />

    <!-- 数字 / 文本输入框 -->
    <input
      v-if="meta.type === 'number' || meta.type === 'text' || !meta.type"
      class="ui-input"
      :value="value"
      @input="handleInput"
      :type="meta.type === 'number' ? 'number' : 'text'"
      :step="meta.step"
      :min="meta.min"
      :max="meta.max"
    />

    <!-- 下拉框 -->
    <select
      v-else-if="meta.type === 'select'"
      class="ui-select"
      :value="value"
      @change="handleSelect"
    >
      <option
        v-for="option in meta.options || []"
        :key="option"
        :value="option"
      >
        {{ option }}
      </option>
    </select>
  </div>
</template>