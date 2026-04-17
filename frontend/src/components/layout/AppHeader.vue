<script setup>
// 顶部导航栏：负责页签切换

defineProps({
  activeTab: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["change-tab"]);
const activeBtnStyle = "background:#1570ef;color:#fff;border-color:#1570ef;";

/**
 * 切换页签
 * @param {string} tab 页签标识
 */
function switchTab(tab) {
  emit("change-tab", tab);
}
</script>

<template>
  <div
    style="
      position: sticky;
      top: 0;
      z-index: 20;
      background: #ffffff;
      border-bottom: 1px solid #eaecf0;
      padding: 14px 24px;
      margin-bottom: 20px;
    "
  >
    <div class="section-toolbar">
      <div style="font-size: 20px; font-weight: 700; color: #101828;">
        人才市场供需动态仿真系统
      </div>

      <div class="toolbar-group">
        <button
          class="ui-btn"
          :style="activeTab === 'simulation' ? activeBtnStyle : ''"
          @click="switchTab('simulation')"
        >
          仿真首页
        </button>

        <button
          class="ui-btn"
          :style="activeTab === 'dictionary' ? activeBtnStyle : ''"
          @click="switchTab('dictionary')"
        >
          数据字典
        </button>

        <button
          class="ui-btn"
          :style="activeTab === 'history' ? activeBtnStyle : ''"
          @click="switchTab('history')"
        >
          历史记录
        </button>

        <button
          class="ui-btn"
          :style="activeTab === 'report' ? activeBtnStyle : ''"
          @click="switchTab('report')"
        >
          分析报告
        </button>

        <button
          class="ui-btn"
          :style="activeTab === 'report-history' ? activeBtnStyle : ''"
          @click="switchTab('report-history')"
        >
          历史报告
        </button>
      </div>
    </div>
  </div>
</template>