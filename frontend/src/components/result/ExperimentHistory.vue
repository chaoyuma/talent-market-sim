<script setup>
import { ref, onMounted } from "vue";
import { getExperimentList, getExperimentDetail } from "../../api/experiment";
import ResultSection from "./ResultSection.vue";

const experiments = ref([]);
const expandedExperimentId = ref(null);
const experimentDetailMap = ref({});
const loading = ref(false);
const detailLoadingId = ref(null);
const error = ref("");

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

async function handleToggleExperiment(experimentId) {
  if (expandedExperimentId.value === experimentId) {
    expandedExperimentId.value = null;
    return;
  }

  expandedExperimentId.value = experimentId;
  if (experimentDetailMap.value[experimentId]) {
    return;
  }

  detailLoadingId.value = experimentId;
  error.value = "";
  try {
    const res = await getExperimentDetail(experimentId);
    experimentDetailMap.value[experimentId] = res.data;
  } catch (e) {
    console.error(e);
    error.value = "加载实验详情失败";
  } finally {
    detailLoadingId.value = null;
  }
}

function getExperimentDetailData(experimentId) {
  return experimentDetailMap.value[experimentId] || null;
}

onMounted(() => {
  loadExperiments();
});
</script>

<template>
  <div
    style="
      margin-top: 24px;
      width: 100%;
      max-width: 100%;
      overflow-x: hidden;
    "
  >
    <h2 class="section-title">历史实验记录</h2>

    <div v-if="loading">正在加载实验列表...</div>
    <div v-else-if="error" class="error-text">{{ error }}</div>

    <div
      v-else
      class="table-wrapper"
      style="
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
      "
    >
      <table class="ui-table">
        <thead>
          <tr>
            <th>实验ID</th>
            <th>场景</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>

        <tbody>
          <template v-for="item in experiments" :key="item.experiment_id">
            <tr>
              <td>{{ item.experiment_id }}</td>
              <td>{{ item.scenario_name || "baseline" }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.created_at }}</td>
              <td>
                <button class="ui-btn" @click="handleToggleExperiment(item.experiment_id)">
                  {{ expandedExperimentId === item.experiment_id ? "收起详情" : "查看详情" }}
                </button>
              </td>
            </tr>

            <tr v-if="expandedExperimentId === item.experiment_id">
              <td
                colspan="5"
                style="
                  background: #fafafa;
                  max-width: 0;
                  overflow: hidden;
                "
              >
                <div
                  style="
                    padding: 16px 8px;
                    width: 100%;
                    max-width: 100%;
                    overflow-x: hidden;
                    box-sizing: border-box;
                  "
                >
                  <div v-if="detailLoadingId === item.experiment_id">
                    正在加载实验详情...
                  </div>

                  <div v-else-if="getExperimentDetailData(item.experiment_id)">
                    <div class="ui-card section-gap">
                      <h3 class="subsection-title">历史记录详情</h3>
                      <div class="responsive-grid-2">
                        <div>实验ID：{{ getExperimentDetailData(item.experiment_id).experiment_id }}</div>
                        <div>状态：{{ getExperimentDetailData(item.experiment_id).status }}</div>
                        <div>场景：{{ getExperimentDetailData(item.experiment_id).scenario_name || "baseline" }}</div>
                        <div>创建时间：{{ getExperimentDetailData(item.experiment_id).created_at }}</div>
                      </div>
                    </div>

                    <ResultSection
                      v-if="getExperimentDetailData(item.experiment_id).result_payload"
                      :result="getExperimentDetailData(item.experiment_id).result_payload"
                      :initial-explanation="getExperimentDetailData(item.experiment_id).latest_explanation || ''"
                      title="历史仿真结果"
                    />
                  </div>

                  <div v-else>暂无实验详情数据</div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
