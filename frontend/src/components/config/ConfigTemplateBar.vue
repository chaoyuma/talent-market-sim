<script setup>
// 参数模板工具条
// 用于保存当前模板、选择模板、加载模板

defineProps({
  templateList: {
    type: Array,
    default: () => [],
  },
  selectedConfigId: {
    type: String,
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
  <div class="ui-card section-gap">
    <h3 class="subsection-title">参数模板</h3>

    <div class="form-row">
      <label style="width: 220px; font-weight: 500;">模板名称</label>
      <input
        class="ui-input"
        :value="configName"
        @input="emit('update:configName', $event.target.value)"
        type="text"
        placeholder="例如：baseline_v1"
      />
    </div>

    <div class="form-row">
      <label style="width: 220px; font-weight: 500;">模板说明</label>
      <input
        class="ui-input"
        :value="configDescription"
        @input="emit('update:configDescription', $event.target.value)"
        type="text"
        placeholder="例如：基准场景第一版参数"
      />
    </div>

    <div class="form-row">
      <label style="width: 220px; font-weight: 500;">选择已有模板</label>
      <select
        class="ui-select"
        :value="selectedConfigId"
        @change="emit('update:selectedConfigId', $event.target.value)"
      >
        <option value="">请选择模板</option>
        <option
          v-for="item in templateList"
          :key="item.config_id"
          :value="item.config_id"
        >
          {{ item.config_name }}（{{ item.config_version }}）
        </option>
      </select>
    </div>

    <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 12px;">
      <button
        class="ui-btn"
        :disabled="configLoading"
        @click="emit('save-template')"
      >
        {{ configLoading ? "处理中..." : "保存参数模板" }}
      </button>

      <button
        class="ui-btn-primary"
        :disabled="configLoading"
        @click="emit('load-template')"
      >
        {{ configLoading ? "处理中..." : "加载参数模板" }}
      </button>
    </div>

    <div v-if="configError" class="error-text" style="margin-top: 12px;">
      {{ configError }}
    </div>

    <div
      v-if="currentConfigInfo"
      style="
        margin-top: 12px;
        padding: 10px 12px;
        background: #f5f7fa;
        border: 1px solid #e5e6eb;
        border-radius: 8px;
        font-size: 14px;
      "
    >
      当前模板：
      <b>{{ currentConfigInfo.config_name }}</b>
      <span v-if="currentConfigInfo.config_version">
        （{{ currentConfigInfo.config_version }}）
      </span>
    </div>
  </div>
</template>