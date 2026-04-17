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

            <!-- 实际参与规模 -->
            <th>student_count</th>
            <th>school_count</th>
            <th>employer_count</th>

            <!-- 存量指标 -->
            <th>employment_rate</th>
            <th>matching_rate</th>
            <th>cross_major_rate</th>
            <th>avg_salary</th>
            <th>avg_satisfaction</th>
            <th>low_satisfaction_employment_rate</th>
            <th>same_region_employment_rate</th>
            <th>carryover_student_count</th>
            <th>new_cohort_student_count</th>
            <th>new_cohort_employment_rate</th>
            <th>carryover_employment_rate</th>
            <th>carryover_pool_share</th>
            <th>avg_carryover_rounds</th>

            <!-- 流量指标 -->
            <th>active_job_seekers</th>
            <th>round_job_count</th>
            <th>round_filled_jobs</th>
            <th>round_vacancy_rate</th>
            <th>round_new_employment_rate</th>
            <th>round_application_count</th>
            <th>round_offer_count</th>
            <th>round_accepted_offer_count</th>
            <th>round_rejected_offer_count</th>
            <th>avg_applications_per_job</th>
            <th>avg_offers_per_student</th>

            <!-- 结构与机制指标 -->
            <th>mismatch_index</th>
            <th>herding_index</th>
            <th>avg_hire_threshold</th>
            <th>avg_cross_major_tolerance</th>
            <th>avg_training_quality</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in rows" :key="item.step">
            <td>{{ item.step }}</td>

            <!-- 实际参与规模 -->
            <td>{{ item.student_count }}</td>
            <td>{{ item.school_count }}</td>
            <td>{{ item.employer_count }}</td>

            <!-- 存量指标 -->
            <td>{{ item.employment_rate }}</td>
            <td>{{ item.matching_rate }}</td>
            <td>{{ item.cross_major_rate }}</td>
            <td>{{ item.avg_salary }}</td>
            <td>{{ item.avg_satisfaction }}</td>
            <td>{{ item.low_satisfaction_employment_rate }}</td>
            <td>{{ item.same_region_employment_rate }}</td>
            <td>{{ item.carryover_student_count }}</td>
            <td>{{ item.new_cohort_student_count }}</td>
            <td>{{ item.new_cohort_employment_rate }}</td>
            <td>{{ item.carryover_employment_rate }}</td>
            <td>{{ item.carryover_pool_share }}</td>
            <td>{{ item.avg_carryover_rounds }}</td>

            <!-- 流量指标 -->
            <td>{{ item.active_job_seekers }}</td>
            <td>{{ item.round_job_count }}</td>
            <td>{{ item.round_filled_jobs }}</td>
            <td>{{ item.round_vacancy_rate }}</td>
            <td>{{ item.round_new_employment_rate }}</td>
            <td>{{ item.round_application_count }}</td>
            <td>{{ item.round_offer_count }}</td>
            <td>{{ item.round_accepted_offer_count }}</td>
            <td>{{ item.round_rejected_offer_count }}</td>
            <td>{{ item.avg_applications_per_job }}</td>
            <td>{{ item.avg_offers_per_student }}</td>

            <!-- 结构与机制指标 -->
            <td>{{ item.mismatch_index }}</td>
            <td>{{ item.herding_index }}</td>
            <td>{{ item.avg_hire_threshold }}</td>
            <td>{{ item.avg_cross_major_tolerance }}</td>
            <td>{{ item.avg_training_quality }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
