<script setup>
defineProps({
  templateList: {
    type: Array,
    default: () => [],
  },
  selectedConfigId: {
    type: [String, Number],
    default: "",
  },
  configName: {
    type: String,
    default: "",
  },
  configDescription: {
    type: String,
    default: "",
  },
  configLoading: {
    type: Boolean,
    default: false,
  },
  configError: {
    type: String,
    default: "",
  },
  currentConfigInfo: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits([
  "update:selectedConfigId",
  "update:configName",
  "update:configDescription",
  "save-template",
  "load-template",
]);
</script>

<template>
  <div
    style="
      display: flex;
      flex-wrap: wrap;
      gap: 10px 12px;
      align-items: center;
      padding: 10px 12px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      background: #fafafa;
    "
  >
    <!-- 选择模板放最前 -->
    <select
      class="ui-select"
      :value="selectedConfigId"
      @change="emit('update:selectedConfigId', $event.target.value)"
      style="width: 240px;"
    >
      <option value="">选择已有模板</option>
      <option
        v-for="item in templateList"
        :key="item.id"
        :value="item.id"
      >
        {{ item.template_name }}
      </option>
    </select>

    <input
      class="ui-input"
      :value="configName"
      @input="emit('update:configName', $event.target.value)"
      type="text"
      placeholder="模板名称"
      style="width: 180px;"
    />

    <input
      class="ui-input"
      :value="configDescription"
      @input="emit('update:configDescription', $event.target.value)"
      type="text"
      placeholder="模板说明"
      style="width: 320px;"
    />

    <button
      type="button"
      class="ui-btn"
      :disabled="configLoading"
      @click="emit('save-template')"
    >
      {{ configLoading ? "处理中..." : "保存" }}
    </button>

    <button
      type="button"
      class="ui-btn-primary"
      :disabled="configLoading"
      @click="emit('load-template')"
    >
      {{ configLoading ? "处理中..." : "加载" }}
    </button>

    <div
      v-if="currentConfigInfo"
      style="font-size: 13px; color: #475467;"
    >
      当前：<b>{{ currentConfigInfo.template_name }}</b>
    </div>

    <div
      v-if="configError"
      class="error-text"
      style="width: 100%; font-size: 13px;"
    >
      {{ configError }}
    </div>
  </div>
</template>