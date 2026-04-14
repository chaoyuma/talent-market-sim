<script setup>
// 历史实验详情卡片
// 负责展示某次实验的基础信息和指标序列

defineProps({
  experiment: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div v-if="loading" style="margin-top: 20px;">
    正在加载实验详情...
  </div>

  <div v-else-if="experiment" class="ui-card" style="margin-top: 24px;">
    <h3 class="subsection-title">实验详情</h3>

    <p><b>experiment_id:</b> {{ experiment.experiment_id }}</p>
    <p><b>状态:</b> {{ experiment.status }}</p>
    <p><b>场景:</b> {{ experiment.scenario_name || "baseline" }}</p>

    <h4 class="subsection-title">指标序列</h4>

    <div class="table-wrapper">
      <table class="ui-table">
        <thead>
          <tr>
            <th>step</th>
            <th>employment_rate</th>
            <th>matching_rate</th>
            <th>cross_major_rate</th>
            <th>vacancy_rate</th>
            <th>filled_jobs</th>
            <th>avg_salary</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="m in experiment.metrics" :key="m.step">
            <td>{{ m.step }}</td>
            <td>{{ m.employment_rate }}</td>
            <td>{{ m.matching_rate }}</td>
            <td>{{ m.cross_major_rate }}</td>
            <td>{{ m.vacancy_rate }}</td>
            <td>{{ m.filled_jobs }}</td>
            <td>{{ m.avg_salary }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>