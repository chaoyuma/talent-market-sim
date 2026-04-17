<script setup>
import ConfigField from "./ConfigField.vue";
import { typeConfigFields } from "../../utils/panelFields";

const modelValue = defineModel({
  type: Object,
  required: true,
});

function updateField(fieldKey, value) {
  modelValue.value[fieldKey] = value;
}
</script>

<template>
  <div class="config-grid">
    <ConfigField
      v-for="fieldKey in typeConfigFields"
      :key="fieldKey"
      :field-key="fieldKey"
      :value="modelValue[fieldKey]"
      @update:value="updateField(fieldKey, $event)"
    />
  </div>
</template>