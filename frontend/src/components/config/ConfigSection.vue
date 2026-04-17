<script setup>
import { ref } from "vue";

import ActionBar from "../common/ActionBar.vue";
import SectionCard from "../common/SectionCard.vue";

import BaseConfigPanel from "./BaseConfigPanel.vue";
import StudentConfigPanel from "./StudentConfigPanel.vue";
import SchoolConfigPanel from "./SchoolConfigPanel.vue";
import EmployerConfigPanel from "./EmployerConfigPanel.vue";
import ScenarioConfigPanel from "./ScenarioConfigPanel.vue";
import AdvancedConfigPanel from "./AdvancedConfigPanel.vue";
import LLMConfigPanel from "./LLMConfigPanel.vue";
import DataConfigPanel from "./DataConfigPanel.vue";
import TypeConfigPanel from "./TypeConfigPanel.vue";
import ConfigTemplateBar from "./ConfigTemplateBar.vue";

defineProps({
  form: {
    type: Object,
    required: true,
  },
  activePanel: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: "",
  },

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
  "change-panel",
  "run",
  "update:selectedConfigId",
  "update:configName",
  "update:configDescription",
  "save-template",
  "load-template",
]);

const collapsed = ref(false);

function handleChangePanel(panelName) {
  emit("change-panel", panelName);
}

function handleRun() {
  emit("run");
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value;
}
</script>

<template>
  <div class="ui-card section-gap" style="padding: 16px 18px; margin-bottom: 18px;">
    <!-- 顶部标题 -->
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 14px;">
      <h2 style="margin: 0; font-size: 24px; line-height: 1.2;">参数配置</h2>

      <button
        type="button"
        class="ui-btn"
        style="padding: 6px 12px; font-size: 13px;"
        @click="toggleCollapsed"
      >
        {{ collapsed ? "展开参数" : "收起参数" }}
      </button>
    </div>

    <!-- 模板栏 -->
    <div style="margin-bottom: 14px;">
      <ConfigTemplateBar
        :templateList="templateList"
        :selectedConfigId="selectedConfigId"
        :configName="configName"
        :configDescription="configDescription"
        :configLoading="configLoading"
        :configError="configError"
        :currentConfigInfo="currentConfigInfo"
        @update:selectedConfigId="emit('update:selectedConfigId', $event)"
        @update:configName="emit('update:configName', $event)"
        @update:configDescription="emit('update:configDescription', $event)"
        @save-template="emit('save-template')"
        @load-template="emit('load-template')"
      />
    </div>

    <!-- 标签栏 + 运行按钮 -->
    <div
      style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 14px;
      "
    >
      <div style="flex: 1; min-width: 520px;">
        <ActionBar
          :activePanel="activePanel"
          :loading="loading"
          @change-panel="handleChangePanel"
          @run="handleRun"
        />
      </div>
    </div>

    <div v-if="error" style="margin-bottom: 12px; color: red;">
      {{ error }}
    </div>

    <!-- 参数面板 -->
    <div v-if="!collapsed">
      <div
        style="
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
          gap: 16px;
        "
      >
        <template v-if="activePanel === 'base'">
          <SectionCard title="基础实验设置">
            <BaseConfigPanel v-model="form.base_config" />
          </SectionCard>
        </template>

        <template v-if="activePanel === 'decision'">
          <SectionCard title="学生决策参数">
            <StudentConfigPanel v-model="form.student_config" />
          </SectionCard>
        </template>

        <template v-if="activePanel === 'feedback'">
          <SectionCard title="学校反馈参数">
            <SchoolConfigPanel v-model="form.school_config" />
          </SectionCard>

          <SectionCard title="企业反馈参数">
            <EmployerConfigPanel v-model="form.employer_config" />
          </SectionCard>
        </template>

        <template v-if="activePanel === 'scenario'">
          <SectionCard title="基础场景参数">
            <ScenarioConfigPanel v-model="form.scenario_config" />
          </SectionCard>

          <SectionCard title="高级场景参数">
            <AdvancedConfigPanel v-model="form.scenario_config" />
          </SectionCard>
        </template>

        <template v-if="activePanel === 'advanced'">
          <SectionCard title="机制开关与类型配置">
            <TypeConfigPanel v-model="form.type_config" />
          </SectionCard>
          <SectionCard title="数据配置">
            <DataConfigPanel v-model="form.data_config" />
          </SectionCard>

          <SectionCard title="智能配置">
            <LLMConfigPanel v-model="form.llm_config" />
          </SectionCard>
        </template>
      </div>
    </div>
  </div>
</template>