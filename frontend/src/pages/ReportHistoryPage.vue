<script setup>
import { ref, onMounted } from "vue";
import {
  getReportHistoryList,
  getReportHistoryDetail,
  downloadReportHistoryFile,
  deleteReportHistoryItem,
} from "../api/report";

const reports = ref([]);
const currentReport = ref(null);
const loading = ref(false);
const error = ref("");

async function loadReports() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getReportHistoryList();
    reports.value = res.data || [];
  } catch (e) {
    console.error(e);
    error.value = "加载历史报告失败";
  } finally {
    loading.value = false;
  }
}

async function handleView(reportId) {
  try {
    const res = await getReportHistoryDetail(reportId);
    currentReport.value = res.data;
  } catch (e) {
    console.error(e);
    error.value = "加载报告详情失败";
  }
}

async function handleDownload(reportId, fileName) {
  try {
    const res = await downloadReportHistoryFile(reportId);
    const blob = new Blob([res.data], { type: "text/markdown;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName || `${reportId}.md`;
    link.click();
    URL.revokeObjectURL(link.href);
  } catch (e) {
    console.error(e);
    error.value = "下载报告失败";
  }
}

async function handleDelete(reportId) {
  try {
    await deleteReportHistoryItem(reportId);
    if (currentReport.value?.report_id === reportId) {
      currentReport.value = null;
    }
    await loadReports();
  } catch (e) {
    console.error(e);
    error.value = "删除报告失败";
  }
}

onMounted(() => {
  loadReports();
});
</script>

<template>
  <div class="page-container">
    <h2 class="section-title">历史报告</h2>

    <div v-if="loading">正在加载历史报告...</div>
    <div v-else-if="error" class="error-text">{{ error }}</div>

    <div v-else class="responsive-grid-2">
      <div class="ui-card">
        <h3 class="subsection-title">报告列表</h3>

        <div v-if="!reports.length" style="color: #667085;">
          暂无历史报告
        </div>

        <div v-for="item in reports" :key="item.report_id" class="section-gap">
          <div><b>{{ item.title }}</b></div>
          <div>报告ID：{{ item.report_id }}</div>
          <div>状态：{{ item.status }}</div>
          <div>生成时间：{{ item.created_at }}</div>
          <div>{{ item.used_llm ? "大模型生成" : "规则回退生成" }}</div>

          <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
            <button class="ui-btn" @click="handleView(item.report_id)">查看</button>
            <button class="ui-btn" @click="handleDownload(item.report_id, item.file_name)">下载</button>
            <button class="ui-btn" @click="handleDelete(item.report_id)">删除</button>
          </div>
        </div>
      </div>

      <div class="ui-card">
        <h3 class="subsection-title">报告详情</h3>

        <div v-if="currentReport">
          <div><b>{{ currentReport.title }}</b></div>
          <div style="color: #667085; margin: 8px 0;">
            {{ currentReport.used_llm ? "本报告由大模型生成" : "本报告为规则回退生成" }}
          </div>
          <div
            class="json-box"
            style="white-space: pre-wrap; line-height: 1.8; max-height: 600px; overflow: auto;"
          >
            {{ currentReport.report_markdown }}
          </div>
        </div>

        <div v-else style="color: #667085;">
          请选择左侧报告查看详情
        </div>
      </div>
    </div>
  </div>
</template>