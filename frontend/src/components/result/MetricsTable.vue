<script setup>
// 每轮指标表组件
defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div class="section-gap">
    <h3 class="subsection-title">每轮指标</h3>

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
          <tr v-for="item in rows" :key="item.step">
            <td>{{ item.step }}</td>
            <td>{{ item.employment_rate }}</td>
            <td>{{ item.matching_rate }}</td>
            <td>{{ item.cross_major_rate }}</td>
            <td>{{ item.vacancy_rate }}</td>
            <td>{{ item.filled_jobs }}</td>
            <td>{{ item.avg_salary }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>