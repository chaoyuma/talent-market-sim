<script setup>
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
import ConfigTemplateBar from "./ConfigTemplateBar.vue";

const props = defineProps({
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
  "change-panel",
  "run",
  "update:selectedConfigId",
  "update:configName",
  "update:configDescription",
  "save-template",
  "load-template",
]);

function handleChangePanel(panelName) {
  emit("change-panel", panelName);
}

function handleRun() {
  emit("run");
}
</script>

<template>
  <div
    style="
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
      background: #fafafa;
    "
  >
    <h2 style="margin-top: 0;">参数配置</h2>

    <!-- 参数模板条 -->
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

    <ActionBar
      :activePanel="activePanel"
      :loading="loading"
      @change-panel="handleChangePanel"
      @run="handleRun"
    />

    <div v-if="error" style="margin-bottom: 16px; color: red;">
      {{ error }}
    </div>

    <div
      style="
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
        gap: 20px;
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
        <SectionCard title="数据配置">
          <DataConfigPanel v-model="form.data_config" />
        </SectionCard>

        <SectionCard title="智能配置">
          <LLMConfigPanel v-model="form.llm_config" />
        </SectionCard>
      </template>
    </div>
  </div>
</template>