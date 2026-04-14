<script setup>
import { ref, onMounted } from "vue";
import { getExperimentList, getExperimentDetail } from "../../api/experiment";
import ExperimentDetailCard from "./ExperimentDetailCard.vue";

// 历史实验列表
const experiments = ref([]);

// 当前选中的实验详情
const selectedExperiment = ref(null);

// 列表加载状态
const loading = ref(false);

// 详情加载状态
const detailLoading = ref(false);

// 错误信息
const error = ref("");

/**
 * 加载历史实验列表
 */
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

/**
 * 查看某次实验详情
 * @param {string} experimentId 实验ID
 */
async function handleSelectExperiment(experimentId) {
  detailLoading.value = true;
  error.value = "";

  try {
    const res = await getExperimentDetail(experimentId);
    selectedExperiment.value = res.data;
  } catch (e) {
    console.error(e);
    error.value = "加载实验详情失败";
  } finally {
    detailLoading.value = false;
  }
}

// 页面加载时自动拉取历史实验
onMounted(() => {
  loadExperiments();
});
</script>

<template>
  <div style="margin-top: 24px;">
    <h2 class="section-title">历史实验记录</h2>

    <div v-if="loading">正在加载实验列表...</div>

    <div v-else-if="error" class="error-text">
      {{ error }}
    </div>

    <div v-else class="table-wrapper">
      <table class="ui-table">
        <thead>
          <tr>
            <th>experiment_id</th>
            <th>场景</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="item in experiments" :key="item.experiment_id">
            <td>{{ item.experiment_id }}</td>
            <td>{{ item.scenario_name || "baseline" }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.created_at }}</td>
            <td>
              <button class="ui-btn" @click="handleSelectExperiment(item.experiment_id)">
                查看详情
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ExperimentDetailCard
      :experiment="selectedExperiment"
      :loading="detailLoading"
    />
  </div>
</template>