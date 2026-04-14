<script setup>




import { ref, computed } from "vue";
import { runSimulation } from "./api";
import VChart from "vue-echarts";
import FieldLabel from "./components/common/FieldLabel.vue";
import InfoTip from "./components/common/InfoTip.vue";
import { fieldMeta, resultMeta } from "./utils/fieldMeta";

import ExperimentHistory from "./components/result/ExperimentHistory.vue";

import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from "echarts/components";

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
]);

const appTitle = import.meta.env.VITE_APP_TITLE || "人才市场供需动态仿真系统";

const form = ref({
  base_config: {
    num_students: 200,
    num_schools: 3,
    num_employers: 20,
    steps: 5,
    random_seed: 42,
  },
  student_config: {
    interest_weight: 0.3,
    salary_weight: 0.2,
    major_weight: 0.3,
    city_weight: 0.1,
    market_signal_weight: 0.1,
    cross_major_acceptance: 0.7,
    information_transparency: 0.8,
  },
  employer_config: {
    major_preference_strength: 0.4,
    skill_preference_strength: 0.4,
    salary_elasticity: 0.05,
    hire_threshold: 0.55,
    cross_major_tolerance: 0.6,
  },
  school_config: {
    capacity_adjust_speed: 0.1,
    employment_feedback_weight: 0.6,
    market_feedback_weight: 0.4,
    training_quality: 0.7,
  },
  scenario_config: {
    macro_economy: 1.0,
    policy_support: 0.5,
    industry_boom_factor: 1.0,
  },
});

const loading = ref(false);
const errorMsg = ref("");
const result = ref(null);

async function handleRun() {
  loading.value = true;
  errorMsg.value = "";
  result.value = null;

  try {
    const res = await runSimulation(form.value);
    result.value = res.data;
  } catch (error) {
    console.error("运行失败:", error);

    if (error.response) {
      errorMsg.value = `接口报错：${error.response.status} - ${JSON.stringify(error.response.data)}`;
    } else if (error.request) {
      errorMsg.value = "请求已发出，但没有收到后端响应。请检查后端是否启动、端口是否正确。";
    } else {
      errorMsg.value = `前端请求配置异常：${error.message}`;
    }
  } finally {
    loading.value = false;
  }
}

const metrics = computed(() => result.value?.results || []);
const latest = computed(() =>
  metrics.value.length ? metrics.value[metrics.value.length - 1] : null
);

const statCards = computed(() => {
  if (!latest.value) return [];
  return [
    {
      label: "最终就业率",
      value: (latest.value.employment_rate * 100).toFixed(2) + "%",
    },
    {
      label: "最终对口率",
      value: (latest.value.matching_rate * 100).toFixed(2) + "%",
    },
    {
      label: "最终空缺率",
      value: (latest.value.vacancy_rate * 100).toFixed(2) + "%",
    },
    {
      label: "已填岗位数",
      value: latest.value.filled_jobs ?? "-",
    },
    {
      label: "平均薪资",
      value: latest.value.avg_salary ? latest.value.avg_salary.toFixed(2) : "-",
    },
    {
      label: "跨专业率",
      value:
        latest.value.cross_major_rate !== undefined
          ? (latest.value.cross_major_rate * 100).toFixed(2) + "%"
          : "-",
    },
  ];
});

const employmentChartOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { show: true },
  xAxis: {
    type: "category",
    data: metrics.value.map((item) => item.step),
    name: "step",
  },
  yAxis: {
    type: "value",
    name: "就业率",
    min: 0,
    max: 1,
  },
  series: [
    {
      name: "employment_rate",
      type: "line",
      smooth: true,
      data: metrics.value.map((item) => item.employment_rate),
    },
  ],
}));

const vacancyChartOption = computed(() => ({
  tooltip: { trigger: "axis" },
  legend: { show: true },
  xAxis: {
    type: "category",
    data: metrics.value.map((item) => item.step),
    name: "step",
  },
  yAxis: {
    type: "value",
    name: "空缺率",
    min: 0,
    max: 1,
  },
  series: [
    {
      name: "vacancy_rate",
      type: "line",
      smooth: true,
      data: metrics.value.map((item) => item.vacancy_rate),
    },
  ],
}));
</script>

<template>
  <div
    style="
      padding: 24px;
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
    "
  >
    <h1>{{ appTitle }}</h1>
    <p style="color: #666; margin-bottom: 20px">
      最小可运行版本：参数配置 → 调用后端 → 返回仿真结果
    </p>

    <div
      style="
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 24px;
        background: #fafafa;
      "
    >
      <h2 style="margin-top: 0">参数配置</h2>

      <div style="margin-bottom: 12px">
        <label style="display: inline-block; width: 120px">学生数量</label>
        <input v-model.number="form.base_config.num_students" type="number" min="1" />
      </div>

      <div style="margin-bottom: 12px">
        <label style="display: inline-block; width: 120px">学校数量</label>
        <input v-model.number="form.base_config.num_schools" type="number" min="1" />
      </div>

      <div style="margin-bottom: 12px">
        <label style="display: inline-block; width: 120px">企业数量</label>
        <input v-model.number="form.base_config.num_employers" type="number" min="1" />
      </div>

      <div style="margin-bottom: 12px">
        <label style="display: inline-block; width: 120px">仿真轮次</label>
        <input v-model.number="form.base_config.steps" type="number" min="1" />
      </div>
      <div style="margin-bottom: 12px;">
        <label style="display: inline-block; width: 120px;">随机种子</label>
        <input v-model.number="form.base_config.random_seed" type="number" min="1" />
      </div>
<div style="margin-top: 20px; margin-bottom: 12px;">
  <h3 style="margin-bottom: 12px;">高级参数</h3>
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">学生跨专业接受度</label>
  <input
    v-model.number="form.student_config.cross_major_acceptance"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">学生信息透明度</label>
  <input
    v-model.number="form.student_config.information_transparency"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">企业专业偏好强度</label>
  <input
    v-model.number="form.employer_config.major_preference_strength"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">企业技能偏好强度</label>
  <input
    v-model.number="form.employer_config.skill_preference_strength"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">企业招聘阈值</label>
  <input
    v-model.number="form.employer_config.hire_threshold"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">企业跨专业容忍度</label>
  <input
    v-model.number="form.employer_config.cross_major_tolerance"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>

<div style="margin-bottom: 12px">
  <label style="display: inline-block; width: 220px">学校培养质量</label>
  <input
    v-model.number="form.school_config.training_quality"
    type="number"
    step="0.05"
    min="0"
    max="1"
  />
</div>
      <button
        @click="handleRun"
        :disabled="loading"
        style="
          padding: 8px 16px;
          border: none;
          background: #1677ff;
          color: white;
          border-radius: 4px;
          cursor: pointer;
        "
      >
        {{ loading ? "运行中..." : "运行仿真" }}
      </button>
    </div>

    <div v-if="errorMsg" style="margin-bottom: 16px; color: red">
      <strong>错误：</strong>{{ errorMsg }}
    </div>

    <div
      v-if="result"
      style="
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
      "
    >
      <h2 style="margin-top: 0">仿真结果</h2>

      <div style="margin-bottom: 16px">
        <p><strong>message：</strong>{{ result.message }}</p>
        <p v-if="result.experiment_id">
          <strong>experiment_id：</strong>{{ result.experiment_id }}
        </p>
      </div>

      <div
        v-if="statCards.length"
        style="
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 24px;
        "
      >
        <div
          v-for="card in statCards"
          :key="card.label"
          style="
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 16px;
            background: #fff;
          "
        >
          <div style="color: #666; font-size: 14px; margin-bottom: 8px">
            {{ card.label }}
          </div>
          <div style="font-size: 24px; font-weight: bold">
            {{ card.value }}
          </div>
        </div>
      </div>

      <div
        style="
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 24px;
        "
      >
        <div style="border: 1px solid #eee; border-radius: 8px; padding: 12px">
          <h3 style="margin-top: 0">就业率变化</h3>
          <VChart :option="employmentChartOption" autoresize style="height: 320px" />
        </div>

        <div style="border: 1px solid #eee; border-radius: 8px; padding: 12px">
          <h3 style="margin-top: 0">岗位空缺率变化</h3>
          <VChart :option="vacancyChartOption" autoresize style="height: 320px" />
        </div>
      </div>

      <div v-if="metrics.length">
        <h3>每轮指标</h3>
        <table
          border="1"
          cellspacing="0"
          cellpadding="8"
          style="border-collapse: collapse; width: 100%"
        >
          <thead>
            <tr>
              <th>step</th>
              <th>employment_rate</th>
              <th>matching_rate</th>
              <th>vacancy_rate</th>
              <th>cross_major_rate</th>
              <th>filled_jobs</th>
              <th>avg_salary</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in metrics" :key="item.step">
              <td>{{ item.step }}</td>
              <td>{{ item.employment_rate }}</td>
              <td>{{ item.matching_rate }}</td>
              <td>{{ item.vacancy_rate }}</td>
              <td>{{ item.cross_major_rate }}</td>
              <td>{{ item.filled_jobs }}</td>
              <td>{{ item.avg_salary }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style="margin-top: 20px">
        <h3>原始 JSON</h3>
        <pre
          style="background: #f6f6f6; padding: 12px; overflow-x: auto"
        >{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
    </div>
  </div>
  <ExperimentHistory />
</template>
