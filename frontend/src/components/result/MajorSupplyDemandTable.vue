<script setup>
// frontend/src/components/result/MajorSupplyDemandTable.vue
// 专业供需偏差表：展示各专业学生供给与岗位需求差值

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
});

/**
 * 百分比格式化
 */
function formatPercent(value) {
  return `${((value || 0) * 100).toFixed(1)}%`;
}

/**
 * gap 格式化
 */
function formatGap(value) {
  const num = value || 0;
  return `${num >= 0 ? "+" : ""}${(num * 100).toFixed(1)}%`;
}
</script>

<template>
  <div class="ui-card">
    <h4 class="subsection-title" style="margin-bottom: 12px;">专业供需偏差</h4>

    <div class="table-wrapper">
      <table class="ui-table">
        <thead>
          <tr>
            <th>专业</th>
            <th>学生数</th>
            <th>岗位数</th>
            <th>学生占比</th>
            <th>岗位占比</th>
            <th>Gap</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.major">
            <td>{{ row.major }}</td>
            <td>{{ row.student_count }}</td>
            <td>{{ row.job_count }}</td>
            <td>{{ formatPercent(row.student_share) }}</td>
            <td>{{ formatPercent(row.job_share) }}</td>
            <td>
              <span
                :style="{
                  color: (row.gap || 0) > 0 ? '#d97706' : ((row.gap || 0) < 0 ? '#2563eb' : '#344054'),
                  fontWeight: 600,
                }"
              >
                {{ formatGap(row.gap) }}
              </span>
            </td>
          </tr>

          <tr v-if="!rows.length">
            <td colspan="6" style="text-align: center; color: #667085;">
              暂无专业供需偏差数据
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>