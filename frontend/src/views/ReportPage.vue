<script setup>
import { computed, onMounted, ref } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { BarChart, LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";

import PageHeader from "../components/common/PageHeader.vue";
import { getExperimentList, getExperimentDetail } from "../api/experiment";
import {
  generateComparisonReportAsync,
  getComparisonReportTask,
} from "../api/report";

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent]);

const experiments = ref([]);
const selectedIds = ref([]);
const detailMap = ref({});
const loading = ref(false);
const reportLoading = ref(false);
const error = ref("");
const reportTitle = ref("");
const reportMarkdown = ref("");
const reportTaskId = ref("");
const reportStatus = ref("");
const usedLlm = ref(false);
const fallbackReason = ref("");

async function loadExperiments() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getExperimentList();
    experiments.value = res.data || [];
  } catch (e) {
    console.error(e);
    error.value = "加载实验列表失败";
  } finally {
    loading.value = false;
  }
}

async function ensureSelectedDetails() {
  const missingIds = selectedIds.value.filter((id) => !detailMap.value[id]);
  if (!missingIds.length) {
    return;
  }

  const responses = await Promise.all(missingIds.map((id) => getExperimentDetail(id)));
  responses.forEach((res) => {
    const detail = res.data;
    detailMap.value[detail.experiment_id] = detail;
  });
}

async function pollReportTask(taskId) {
  const maxAttempts = 120; // 约 10 分钟
  let attempts = 0;

  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      attempts += 1;

      try {
        const res = await getComparisonReportTask(taskId);
        const task = res.data || {};

        reportStatus.value = task.status || "";
        usedLlm.value = !!task.used_llm;
        fallbackReason.value = task.fallback_reason || "";

        if (task.status === "finished") {
          clearInterval(timer);

          reportTitle.value = task.title || "仿真对比分析报告";
          reportMarkdown.value = "报告已生成，已保存到项目本地目录，并写入历史报告。";
          reportLoading.value = false;
          resolve(task);
        }

        if (task.status === "failed") {
          clearInterval(timer);
          error.value = `生成分析报告失败：${task.error || "未知错误"}`;
          reportLoading.value = false;
          reject(new Error(task.error || "report task failed"));
        }

        if (attempts >= maxAttempts) {
          clearInterval(timer);
          error.value = "报告生成超时，请稍后重试。";
          reportLoading.value = false;
          reject(new Error("report task timeout"));
        }
      } catch (e) {
        clearInterval(timer);
        console.error(e);
        error.value = "查询报告任务状态失败";
        reportLoading.value = false;
        reject(e);
      }
    }, 5000);
  });
}

async function handleGenerateReport() {
  if (!selectedIds.value.length) {
    error.value = "请至少选择一条历史记录";
    return;
  }

  reportLoading.value = true;
  error.value = "";
  reportMarkdown.value = "";
  reportTitle.value = "";
  reportTaskId.value = "";
  reportStatus.value = "";
  usedLlm.value = false;
  fallbackReason.value = "";

  try {
    await ensureSelectedDetails();

    const res = await generateComparisonReportAsync(selectedIds.value);
    reportTaskId.value = res.data?.task_id || "";
    reportStatus.value = res.data?.status || "pending";
    reportTitle.value = "仿真对比分析报告";
    reportMarkdown.value = "报告任务已创建，正在后台生成...";

    await pollReportTask(reportTaskId.value);
  } catch (e) {
    console.error(e);
    if (!error.value) {
      error.value = "生成分析报告失败";
    }
  } finally {
    reportLoading.value = false;
  }
}

const selectedDetails = computed(() =>
  selectedIds.value
    .map((id) => detailMap.value[id])
    .filter(Boolean)
    .map((detail) => detail.result_payload)
    .filter(Boolean)
);

const finalComparisonOption = computed(() => ({
  tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
  legend: { top: 4, type: "scroll" },
  grid: { left: 60, right: 24, top: 76, bottom: 48, containLabel: true },
  xAxis: {
    type: "category",
    data: selectedDetails.value.map((item) => item.experiment_id),
  },
  yAxis: { type: "value", min: 0, max: 1, name: "比例" },
  series: [
    {
      name: "最终累计就业率",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_employment_rate || 0),
    },
    {
      name: "最终累计对口率",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_matching_rate || 0),
    },
    {
      name: "最终本轮空缺率",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_round_vacancy_rate || 0),
    },
  ],
}));

const structureComparisonOption = computed(() => ({
  tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
  legend: { top: 4, type: "scroll" },
  grid: { left: 60, right: 24, top: 76, bottom: 48, containLabel: true },
  xAxis: {
    type: "category",
    data: selectedDetails.value.map((item) => item.experiment_id),
  },
  yAxis: { type: "value", min: 0, name: "指标值" },
  series: [
    {
      name: "最终结构错配指数",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_mismatch_index || 0),
    },
    {
      name: "最终扎堆指数",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_herding_index || 0),
    },
    {
      name: "最终平均薪资",
      type: "bar",
      data: selectedDetails.value.map((item) => item.summary?.final_avg_salary || 0),
    },
  ],
}));

const trendComparisonOption = computed(() => {
  const stepLabels = Array.from(
    new Set(
      selectedDetails.value.flatMap((item) =>
        (item.results || []).map((row) => row.step)
      )
    )
  ).sort((a, b) => a - b);

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 4, type: "scroll" },
    grid: { left: 60, right: 24, top: 76, bottom: 48, containLabel: true },
    xAxis: {
      type: "category",
      data: stepLabels,
      name: "轮次",
    },
    yAxis: { type: "value", min: 0, max: 1, name: "累计就业率" },
    series: selectedDetails.value.map((item) => ({
      name: item.experiment_id,
      type: "line",
      smooth: true,
      data: stepLabels.map((step) => {
        const row = (item.results || []).find((result) => result.step === step);
        return row?.employment_rate || 0;
      }),
    })),
  };
});

onMounted(() => {
  loadExperiments();
});
</script>

<template>
  <div class="page-container">
    <PageHeader
      title="分析报告"
      subtitle="选择多条历史实验记录，人工触发生成对比分析报告。报告由后端异步生成并自动保存到系统。"
    />

    <div class="ui-card section-gap">
      <div class="section-toolbar">
        <h3 class="subsection-title" style="margin-bottom: 0;">实验选择</h3>
        <div class="toolbar-group">
          <button
            class="ui-btn-primary"
            @click="handleGenerateReport"
            :disabled="reportLoading || !selectedIds.length"
          >
            {{ reportLoading ? "生成中..." : "生成分析报告" }}
          </button>

          <button class="ui-btn" disabled>
            报告由后端自动保存
          </button>
        </div>
      </div>

      <div v-if="reportLoading" class="ui-card section-gap">
        <div>报告任务正在后台生成中，当前状态：{{ reportStatus || "pending" }}</div>
        <div v-if="reportTaskId">任务ID：{{ reportTaskId }}</div>
      </div>

      <div v-if="reportMarkdown" class="ui-card section-gap">
        <div style="margin-bottom: 12px;">
          <div v-if="usedLlm" style="color: #067647; font-weight: 600;">
            本次分析报告由大模型生成。
          </div>
          
        </div>

        <h3 class="subsection-title">{{ reportTitle || "仿真对比分析报告" }}</h3>
        <div class="json-box" style="white-space: pre-wrap; line-height: 1.8;">
          {{ reportMarkdown }}
        </div>
      </div>

      <div v-if="loading">正在加载实验列表...</div>
      <div v-else-if="error" class="error-text">{{ error }}</div>
      <div v-else class="table-wrapper">
        <table class="ui-table">
          <thead>
            <tr>
              <th>选择</th>
              <th>实验ID</th>
              <th>场景</th>
              <th>状态</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in experiments" :key="item.experiment_id">
              <td>
                <input v-model="selectedIds" type="checkbox" :value="item.experiment_id" />
              </td>
              <td>{{ item.experiment_id }}</td>
              <td>{{ item.scenario_name || "baseline" }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedDetails.length" class="responsive-grid-2 section-gap">
      <div class="ui-card report-export-chart">
        <h3 class="subsection-title">关键结果对比</h3>
        <VChart :option="finalComparisonOption" autoresize style="height: 360px;" />
      </div>
      <div class="ui-card report-export-chart">
        <h3 class="subsection-title">结构与薪资对比</h3>
        <VChart :option="structureComparisonOption" autoresize style="height: 360px;" />
      </div>
    </div>

    <div v-if="selectedDetails.length" class="ui-card section-gap report-export-chart">
      <h3 class="subsection-title">累计就业率趋势对比</h3>
      <VChart :option="trendComparisonOption" autoresize style="height: 380px;" />
    </div>
  </div>
</template>