<script setup>
// =========================
// 基础依赖
// =========================
import { ref } from "vue";

// =========================
// 公共组件
// =========================
import PageHeader from "../components/common/PageHeader.vue";

// =========================
// 页面级区块组件
// =========================
import ConfigSection from "../components/config/ConfigSection.vue";
import ResultSection from "../components/result/ResultSection.vue";
import HistorySection from "../components/result/HistorySection.vue";

// =========================
// 工具与逻辑
// =========================
import { defaultForm } from "../utils/configDefaults";
import { useSimulation } from "../composables/useSimulation";

// 页面表单数据
const form = ref(structuredClone(defaultForm));

// 当前激活的参数面板
const activePanel = ref("base");

// 仿真运行逻辑
const { loading, error, result, handleRunSimulation } = useSimulation(form);

/**
 * 切换当前激活面板
 * @param {string} panelName 面板名称
 */
function handleChangePanel(panelName) {
  activePanel.value = panelName;
}
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
      title="人才市场供需动态仿真系统"
      subtitle="围绕学生学习与就业决策，模拟学校、企业反馈和环境场景影响。"
    />

    <!-- 参数配置总区 -->
    <ConfigSection
      :form="form"
      :activePanel="activePanel"
      :loading="loading"
      :error="error"
      @change-panel="handleChangePanel"
      @run="handleRunSimulation"
    />

    <!-- 结果展示区 -->
    <ResultSection :result="result" />

    <!-- 历史实验区 -->
    <HistorySection />
  </div>
</template>