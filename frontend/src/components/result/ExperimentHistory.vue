<script setup>
import { ref, onMounted } from "vue";
import { getExperimentList, getExperimentDetail } from "../../api/experiment";

// 历史实验列表
const experiments = ref([]);

// 当前展开的实验 ID
const expandedExperimentId = ref(null);

// 当前实验详情缓存
const experimentDetailMap = ref({});

// 参数快照折叠状态
const configExpandedMap = ref({});

// 列表加载状态
const loading = ref(false);

// 详情加载状态
const detailLoadingId = ref(null);

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
 * 查看或收起某次实验详情
 * @param {string} experimentId 实验ID
 */
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

    if (configExpandedMap.value[experimentId] === undefined) {
      configExpandedMap.value[experimentId] = false;
    }
  } catch (e) {
    console.error(e);
    error.value = "加载实验详情失败";
  } finally {
    detailLoadingId.value = null;
  }
}

/**
 * 切换参数快照展开/收起
 * @param {string} experimentId
 */
function toggleConfigSnapshot(experimentId) {
  configExpandedMap.value[experimentId] = !configExpandedMap.value[experimentId];
}

/**
 * 获取某次实验详情
 * @param {string} experimentId
 * @returns {object|null}
 */
function getExperimentDetailData(experimentId) {
  return experimentDetailMap.value[experimentId] || null;
}

/**
 * 美化 JSON
 * @param {any} data
 * @returns {string}
 */
function prettyJson(data) {
  if (!data) {
    return "";
  }
  try {
    return JSON.stringify(data, null, 2);
  } catch (e) {
    return String(data);
  }
}

/**
 * 格式化数值展示
 * @param {number|string|null|undefined} value
 * @returns {string}
 */
function formatValue(value) {
  if (value === null || value === undefined) {
    return "-";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }

  return String(value);
}

/**
 * 每轮卡片里要显示的指标分组
 */
function buildMetricGroups(metric) {
  return [
    {
      title: "实际参与规模",
      items: [
        { label: "学生数", value: metric.student_count },
        { label: "学校数", value: metric.school_count },
        { label: "企业数", value: metric.employer_count },
      ],
    },
    {
      title: "累计结果指标",
      items: [
        { label: "累计就业率", value: metric.employment_rate },
        { label: "累计对口率", value: metric.matching_rate },
        { label: "累计跨专业率", value: metric.cross_major_rate },
        { label: "累计平均薪资", value: metric.avg_salary },
        { label: "累计满意度", value: metric.avg_satisfaction },
      ],
    },
    {
      title: "本轮流量指标",
      items: [
        { label: "活跃求职人数", value: metric.active_job_seekers },
        { label: "本轮岗位数", value: metric.round_job_count },
        { label: "本轮已填岗位", value: metric.round_filled_jobs },
        { label: "本轮空缺率", value: metric.round_vacancy_rate },
        { label: "本轮新增就业率", value: metric.round_new_employment_rate },
      ],
    },
    {
      title: "结构与反馈指标",
      items: [
        { label: "结构错配指数", value: metric.mismatch_index },
        { label: "扎堆指数", value: metric.herding_index },
        { label: "平均招聘阈值", value: metric.avg_hire_threshold },
        { label: "平均跨专业容忍度", value: metric.avg_cross_major_tolerance },
        { label: "平均培养质量", value: metric.avg_training_quality },
      ],
    },
  ];
}

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
          <template v-for="item in experiments" :key="item.experiment_id">
            <!-- 主记录行 -->
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

            <!-- 展开详情行 -->
            <tr v-if="expandedExperimentId === item.experiment_id">
              <td colspan="5" style="background: #fafafa;">
                <div style="padding: 12px 4px;">
                  <div v-if="detailLoadingId === item.experiment_id">
                    正在加载实验详情...
                  </div>

                  <div v-else-if="getExperimentDetailData(item.experiment_id)">
                    <!-- 基本信息 -->
                    <div class="ui-card" style="margin-bottom: 12px;">
                      <h3 class="subsection-title">实验详情</h3>
                      <div><b>experiment_id：</b>{{ getExperimentDetailData(item.experiment_id).experiment_id }}</div>
                      <div><b>状态：</b>{{ getExperimentDetailData(item.experiment_id).status }}</div>
                      <div><b>场景：</b>{{ getExperimentDetailData(item.experiment_id).scenario_name || "baseline" }}</div>
                    </div>

                    <!-- 参数快照 -->
                    <div class="ui-card" style="margin-bottom: 12px;">
                      <div
                        style="
                          display: flex;
                          justify-content: space-between;
                          align-items: center;
                          gap: 12px;
                          flex-wrap: wrap;
                        "
                      >
                        <h3 class="subsection-title" style="margin-bottom: 0;">参数快照</h3>
                        <button
                          class="ui-btn"
                          @click="toggleConfigSnapshot(item.experiment_id)"
                        >
                          {{
                            configExpandedMap[item.experiment_id]
                              ? "收起参数快照"
                              : "展开参数快照"
                          }}
                        </button>
                      </div>

                      <div
                        v-if="configExpandedMap[item.experiment_id]"
                        class="json-box"
                        style="
                          margin-top: 12px;
                          max-height: 360px;
                          min-width: 480px;
                          max-width: 100%;
                          width: 760px;
                          resize: horizontal;
                          overflow: auto;
                          white-space: pre-wrap;
                          word-break: break-word;
                          line-height: 1.6;
                        "
                      >
                        {{ prettyJson(getExperimentDetailData(item.experiment_id).config_snapshot_json) }}
                      </div>

                      <div
                        v-else
                        style="margin-top: 10px; color: #667085;"
                      >
                        点击“展开参数快照”查看本次实验的完整参数配置。
                      </div>
                    </div>

                    <!-- 指标序列：卡片形式 -->
                    <div class="ui-card">
                      <h3 class="subsection-title">指标序列</h3>

                      <div
                        style="
                          display: grid;
                          grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
                          gap: 16px;
                        "
                      >
                        <div
                          v-for="m in getExperimentDetailData(item.experiment_id).metrics"
                          :key="m.step"
                          class="ui-card"
                          style="
                            background: #fcfcfd;
                            border: 1px solid #eaecf0;
                          "
                        >
                          <div
                            style="
                              display: flex;
                              justify-content: space-between;
                              align-items: center;
                              margin-bottom: 12px;
                              padding-bottom: 8px;
                              border-bottom: 1px solid #eaecf0;
                            "
                          >
                            <div style="font-size: 16px; font-weight: 700; color: #101828;">
                              第 {{ m.step }} 轮
                            </div>
                            <div style="font-size: 13px; color: #667085;">
                              step = {{ m.step }}
                            </div>
                          </div>

                          <div
                            v-for="group in buildMetricGroups(m)"
                            :key="group.title"
                            style="margin-bottom: 14px;"
                          >
                            <div
                              style="
                                font-size: 14px;
                                font-weight: 600;
                                color: #344054;
                                margin-bottom: 8px;
                              "
                            >
                              {{ group.title }}
                            </div>

                            <div
                              style="
                                display: grid;
                                grid-template-columns: repeat(2, minmax(0, 1fr));
                                gap: 8px 12px;
                              "
                            >
                              <div
                                v-for="metricItem in group.items"
                                :key="metricItem.label"
                                style="
                                  padding: 8px 10px;
                                  background: #ffffff;
                                  border: 1px solid #eaecf0;
                                  border-radius: 8px;
                                "
                              >
                                <div
                                  style="
                                    font-size: 12px;
                                    color: #667085;
                                    margin-bottom: 4px;
                                  "
                                >
                                  {{ metricItem.label }}
                                </div>
                                <div
                                  style="
                                    font-size: 15px;
                                    font-weight: 600;
                                    color: #101828;
                                  "
                                >
                                  {{ formatValue(metricItem.value) }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else>
                    暂无实验详情数据
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>