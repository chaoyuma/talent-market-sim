<script setup>
// 历史报告页：卡片化展示报告列表，并支持查看详情、下载、删除

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

function formatTime(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").slice(0, 19);
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

    <div
      v-else
      style="
        display: grid;
        grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
        gap: 20px;
        align-items: start;
      "
    >
      <!-- 左侧：报告列表 -->
      <div class="ui-card" style="padding: 18px;">
        <div
          style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
          "
        >
          <h3 class="subsection-title" style="margin-bottom: 0;">报告列表</h3>
          <span
            style="
              font-size: 13px;
              color: #475467;
              background: #f2f4f7;
              padding: 4px 10px;
              border-radius: 999px;
            "
          >
            {{ reports.length }} 份
          </span>
        </div>

        <div v-if="!reports.length" style="color: #667085; padding: 16px 4px;">
          暂无历史报告
        </div>

        <div
          v-for="item in reports"
          :key="item.report_id"
          class="report-list-card"
          :style="{
            border: currentReport?.report_id === item.report_id ? '1px solid #1570ef' : '1px solid #eaecf0',
            background: currentReport?.report_id === item.report_id ? '#eff8ff' : '#ffffff'
          }"
        >
          <div style="display: flex; justify-content: space-between; gap: 12px; align-items: start;">
            <div style="min-width: 0; flex: 1;">
              <div
                style="
                  font-size: 15px;
                  font-weight: 700;
                  color: #101828;
                  line-height: 1.5;
                  margin-bottom: 6px;
                  word-break: break-word;
                "
              >
                {{ item.title }}
              </div>

              <div style="font-size: 13px; color: #667085; line-height: 1.7;">
                <div>报告ID：{{ item.report_id }}</div>
                <div>状态：{{ item.status }}</div>
                <div>时间：{{ formatTime(item.created_at) }}</div>
              </div>
            </div>

            <div>
              <span
                :style="{
                  display: 'inline-block',
                  fontSize: '12px',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  color: item.used_llm ? '#067647' : '#b54708',
                  background: item.used_llm ? '#ecfdf3' : '#fffaeb',
                  whiteSpace: 'nowrap'
                }"
              >
                {{ item.used_llm ? "大模型生成" : "规则回退" }}
              </span>
            </div>
          </div>

          <div
            style="
              display: flex;
              gap: 8px;
              flex-wrap: wrap;
              margin-top: 14px;
            "
          >
            <button class="ui-btn-primary" @click="handleView(item.report_id)">查看详情</button>
            <button class="ui-btn" @click="handleDownload(item.report_id, item.file_name)">下载</button>
            <button class="ui-btn" @click="handleDelete(item.report_id)">删除</button>
          </div>
        </div>
      </div>

      <!-- 右侧：报告详情 -->
      <div class="ui-card" style="padding: 20px; min-height: 520px;">
        <h3 class="subsection-title">报告详情</h3>

        <div v-if="currentReport">
          <div
            style="
              border: 1px solid #eaecf0;
              border-radius: 12px;
              padding: 16px;
              background: #fcfcfd;
              margin-bottom: 16px;
            "
          >
            <div
              style="
                font-size: 18px;
                font-weight: 700;
                color: #101828;
                line-height: 1.5;
                margin-bottom: 10px;
              "
            >
              {{ currentReport.title }}
            </div>

            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 10px;">
              <span
                :style="{
                  display: 'inline-block',
                  fontSize: '12px',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  color: currentReport.used_llm ? '#067647' : '#b54708',
                  background: currentReport.used_llm ? '#ecfdf3' : '#fffaeb'
                }"
              >
                {{ currentReport.used_llm ? "本报告由大模型生成" : "本报告为规则回退生成" }}
              </span>

              <span
                v-if="currentReport.fallback_reason"
                style="
                  display: inline-block;
                  font-size: 12px;
                  padding: 4px 10px;
                  border-radius: 999px;
                  color: #475467;
                  background: #f2f4f7;
                "
              >
                原因：{{ currentReport.fallback_reason }}
              </span>
            </div>

            <div style="font-size: 13px; color: #667085; line-height: 1.8;">
              <div>报告ID：{{ currentReport.report_id }}</div>
              <div>类型：{{ currentReport.report_type || "-" }}</div>
              <div>状态：{{ currentReport.status || "-" }}</div>
              <div>生成时间：{{ formatTime(currentReport.created_at) }}</div>
            </div>
          </div>

          <div
            class="json-box"
            style="
              white-space: pre-wrap;
              line-height: 1.9;
              max-height: 680px;
              overflow: auto;
              padding: 18px;
              border-radius: 12px;
              background: #ffffff;
              border: 1px solid #eaecf0;
            "
          >
            {{ currentReport.report_markdown }}
          </div>
        </div>

        <div
          v-else
          style="
            height: 420px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #667085;
            background: #fcfcfd;
            border: 1px dashed #d0d5dd;
            border-radius: 12px;
          "
        >
          请在左侧选择一份报告查看详情
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-list-card {
  border-radius: 14px;
  padding: 16px;
  transition: all 0.2s ease;
  margin-bottom: 14px;
}

.report-list-card:hover {
  box-shadow: 0 4px 14px rgba(16, 24, 40, 0.08);
  transform: translateY(-1px);
}
</style>