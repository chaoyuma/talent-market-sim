<script setup>
// 企业反馈参数面板
// 用于配置企业招聘偏好、门槛和调薪机制

import FieldLabel from "../common/FieldLabel.vue";
import { fieldMeta } from "../../utils/fieldMeta";

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
});

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
    <div class="form-row">
      <FieldLabel :label="fieldMeta.major_preference_strength.label" :tooltip="fieldMeta.major_preference_strength.tooltip" />
      <input
        class="ui-input"
        :value="modelValue.major_preference_strength"
        @input="updateField('major_preference_strength', Number($event.target.value))"
        type="number"
        step="0.01"
        min="0"
        max="1"
      />
    </div>

    <div class="form-row">
      <FieldLabel :label="fieldMeta.skill_preference_strength.label" :tooltip="fieldMeta.skill_preference_strength.tooltip" />
      <input
        class="ui-input"
        :value="modelValue.skill_preference_strength"
        @input="updateField('skill_preference_strength', Number($event.target.value))"
        type="number"
        step="0.01"
        min="0"
        max="1"
      />
    </div>

    <div class="form-row">
      <FieldLabel :label="fieldMeta.hire_threshold.label" :tooltip="fieldMeta.hire_threshold.tooltip" />
      <input
        class="ui-input"
        :value="modelValue.hire_threshold"
        @input="updateField('hire_threshold', Number($event.target.value))"
        type="number"
        step="0.01"
        min="0"
        max="1"
      />
    </div>

    <div class="form-row">
      <FieldLabel :label="fieldMeta.cross_major_tolerance.label" :tooltip="fieldMeta.cross_major_tolerance.tooltip" />
      <input
        class="ui-input"
        :value="modelValue.cross_major_tolerance"
        @input="updateField('cross_major_tolerance', Number($event.target.value))"
        type="number"
        step="0.01"
        min="0"
        max="1"
      />
    </div>

    <div class="form-row">
      <FieldLabel :label="fieldMeta.salary_elasticity.label" :tooltip="fieldMeta.salary_elasticity.tooltip" />
      <input
        class="ui-input"
        :value="modelValue.salary_elasticity"
        @input="updateField('salary_elasticity', Number($event.target.value))"
        type="number"
        step="0.01"
        min="0"
      />
    </div>
  </div>
</template>