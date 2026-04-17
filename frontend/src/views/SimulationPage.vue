<script setup>
// 
// 基础依赖
// 
import { ref, onMounted } from "vue";

// 
// 公共组件
// 
import PageHeader from "../components/common/PageHeader.vue";

// 
// 页面级区块组件
// 
import ConfigSection from "../components/config/ConfigSection.vue";
import ResultSection from "../components/result/ResultSection.vue";

// 
// 工具与逻辑
// 
import { defaultForm } from "../utils/configDefaults";
import { useSimulation } from "../composables/useSimulation";
import { useConfigTemplates } from "../composables/useConfigTemplates";

// import ScenarioPresetBar from "../components/config/ScenarioPresetBar.vue";
// import { applyScenarioTemplate } from "../utils/applyScenarioTemplate";

// 页面表单数据
const form = ref(structuredClone(defaultForm));

// 当前激活的参数面板
const activePanel = ref("base");

// 仿真运行逻辑
const { loading, error, result, handleRunSimulation } = useSimulation(form);

// 场景模板
// const activeScenario = ref("baseline");

// 参数模板逻辑
const {
  templateList,
  selectedConfigId,
  configName,
  configDescription,
  configLoading,
  configError,
  currentConfigInfo,
  loadTemplateList,
  handleSaveTemplate,
  handleLoadTemplate,
  handleSelectTemplate
} = useConfigTemplates(form);

/**
 * 切换当前激活面板
 * @param {string} panelName 面板名称
 */
function handleChangePanel(panelName) {
  activePanel.value = panelName;
}

/**
 * 将参数调优建议回填到当前表单，并自动生成模板名称与模板说明
 * @param {Object} suggestedParams 结构化建议参数
 */
function handleApplySuggestedParams(suggestedParams) {
  // console.log("DEBUG SimulationPage received suggestedParams =", JSON.parse(JSON.stringify(suggestedParams)));

  if (!suggestedParams || typeof suggestedParams !== "object") {
    alert("没有收到可应用的建议参数。");
    return;
  }

  // 1. 回填参数
  for (const [groupKey, groupValues] of Object.entries(suggestedParams)) {
    if (!groupValues || typeof groupValues !== "object") {
      continue;
    }

    if (!form.value[groupKey] || typeof form.value[groupKey] !== "object") {
      form.value[groupKey] = {};
    }

    for (const [paramKey, paramValue] of Object.entries(groupValues)) {
      form.value[groupKey][paramKey] = paramValue;
    }
  }

  // 2. 自动生成模板名称
  const scenarioName = form.value?.scenario_name || "baseline";
  const now = new Date();
  const timeText = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}_${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;

  configName.value = `${scenarioName}_调优建议_${timeText}`;

  // 3. 自动生成模板说明
  const summaryLines = [];
  for (const [groupKey, groupValues] of Object.entries(suggestedParams)) {
    if (!groupValues || typeof groupValues !== "object") {
      continue;
    }

    for (const [paramKey, paramValue] of Object.entries(groupValues)) {
      summaryLines.push(`${groupKey}.${paramKey}=${paramValue}`);
    }
  }

  configDescription.value = `基于仿真结果自动生成的调优参数建议。已回填参数：${summaryLines.join("；")}`;

  // console.log("DEBUG form after apply =", JSON.parse(JSON.stringify(form.value)));
  // console.log("DEBUG configName =", configName.value);
  // console.log("DEBUG configDescription =", configDescription.value);

  alert("已将建议参数回填到当前参数配置，并自动填写模板名称与模板说明。");
}

// function handleApplyScenario(template) {
//   form.value = applyScenarioTemplate(form.value, template);
//   activeScenario.value = template.key;
// }

onMounted(() => {
  loadTemplateList();
});
</script>

<template>
  <div
    style="
      padding: 24px;
      font-family: Arial, sans-serif;
      max-width: 1480px;
      margin: 0 auto;
    "
  >
    <!-- 页面头部 -->
    <PageHeader
      title="仿真首页"
      subtitle="配置参数、运行实验并查看当前结果。"
    />

    <!-- 预设场景 -->
    <!-- <ScenarioPresetBar
      :active-scenario="activeScenario"
      @apply-scenario="handleApplyScenario"
    /> -->

    <!-- 参数配置总区 -->
    <ConfigSection
      :form="form"
      :activePanel="activePanel"
      :loading="loading"
      :error="error"

      :templateList="templateList"
      :selectedConfigId="selectedConfigId"
      :configName="configName"
      :configDescription="configDescription"
      :configLoading="configLoading"
      :configError="configError"
      :currentConfigInfo="currentConfigInfo"

      @change-panel="handleChangePanel"
      @run="handleRunSimulation"

      @update:selectedConfigId="handleSelectTemplate($event)"
      @update:configName="configName = $event"
      @update:configDescription="configDescription = $event"
      
      @save-template="handleSaveTemplate"
      @load-template="handleLoadTemplate"
    />

    <!-- 结果展示区 -->
    <ResultSection
      :result="result"
      @apply-suggested-params="handleApplySuggestedParams"
    />
  </div>
</template>