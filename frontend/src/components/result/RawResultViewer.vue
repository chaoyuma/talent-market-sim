<script setup>
import { computed, ref, onMounted } from "vue";
import { useMetadataLabels } from "../../composables/useMetadataLabels";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

const fontSize = ref(13);

const PARAM_TABLES = [
  "base_config",
  "student_config",
  "employer_config",
  "school_config",
  "scenario_config",
  "type_config",
  "data_config",
  "llm_config",
];

const TOP_LEVEL_TABLE = "result_payload";
const METRIC_TABLE = "experiment_metrics";
const SUMMARY_TABLE = "experiment_summary";
const RUNTIME_TABLE = "actual_runtime";

const STRUCTURE_TABLE_MAP = {
  major_supply_demand_gap: "major_supply_demand_gap",
  major_school_adjustment_bias: "major_school_adjustment_bias",
  major_student_distribution: "major_student_distribution",
  major_job_distribution: "major_job_distribution",
  industry_job_distribution: "industry_job_distribution",
  major_market_signals: "major_market_signals",
  major_outcomes: "major_outcomes",
  student_type_outcomes: "student_type_outcomes",
  employer_type_metrics: "employer_type_metrics",
  school_type_metrics: "school_type_metrics",
};

const { loadMetadataTables, getFieldDisplayName } = useMetadataLabels();

onMounted(async () => {
  await loadMetadataTables([
    TOP_LEVEL_TABLE,
    ...PARAM_TABLES,
    METRIC_TABLE,
    SUMMARY_TABLE,
    RUNTIME_TABLE,
    ...Object.values(STRUCTURE_TABLE_MAP),
    "regional_flow_rows",
  ]);
});

function transformObjectByTable(tableName, obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) {
    return obj;
  }
  const output = {};
  for (const [key, value] of Object.entries(obj)) {
    output[getFieldDisplayName(tableName, key)] = value;
  }
  return output;
}

function transformParams(params) {
  if (!params || typeof params !== "object") {
    return params;
  }

  const output = {};
  for (const [groupKey, groupValue] of Object.entries(params)) {
    const displayGroupKey = getFieldDisplayName(TOP_LEVEL_TABLE, groupKey);
    if (PARAM_TABLES.includes(groupKey)) {
      output[displayGroupKey] = transformObjectByTable(groupKey, groupValue);
    } else {
      output[displayGroupKey] = groupValue;
    }
  }
  return output;
}

function transformResults(results) {
  if (!Array.isArray(results)) {
    return results;
  }
  return results.map((row) => transformObjectByTable(METRIC_TABLE, row));
}

function transformSummary(summary) {
  return transformObjectByTable(SUMMARY_TABLE, summary);
}

function transformActualRuntime(runtime) {
  return transformObjectByTable(RUNTIME_TABLE, runtime);
}

function transformRegionalFlowMetrics(data) {
  if (!data || typeof data !== "object") {
    return data;
  }

  return {
    [getFieldDisplayName(TOP_LEVEL_TABLE, "rows")]: (data.rows || []).map((row) =>
      transformObjectByTable("regional_flow_rows", row)
    ),
    [getFieldDisplayName(TOP_LEVEL_TABLE, "same_region_employment_rate")]:
      data.same_region_employment_rate,
  };
}

function transformStructureAnalysis(data) {
  if (!data || typeof data !== "object") {
    return data;
  }

  const output = {};
  for (const [sectionKey, sectionValue] of Object.entries(data)) {
    const displaySectionKey = getFieldDisplayName(TOP_LEVEL_TABLE, sectionKey);
    if (sectionKey === "regional_flow_metrics") {
      output[displaySectionKey] = transformRegionalFlowMetrics(sectionValue);
      continue;
    }

    const tableName = STRUCTURE_TABLE_MAP[sectionKey];
    if (Array.isArray(sectionValue) && tableName) {
      output[displaySectionKey] = sectionValue.map((item) =>
        transformObjectByTable(tableName, item)
      );
    } else {
      output[displaySectionKey] = sectionValue;
    }
  }
  return output;
}

function transformSeedResults(seedResults) {
  if (!Array.isArray(seedResults)) {
    return seedResults;
  }
  return seedResults.map((item) => ({
    [getFieldDisplayName(TOP_LEVEL_TABLE, "seed")]: item.seed,
    [getFieldDisplayName(TOP_LEVEL_TABLE, "results")]: transformResults(item.results || []),
    [getFieldDisplayName(TOP_LEVEL_TABLE, "summary")]: transformObjectByTable(
      METRIC_TABLE,
      item.final_result || {}
    ),
  }));
}

function transformResultForDisplay(result) {
  if (!result || typeof result !== "object") {
    return result;
  }

  const output = {};
  for (const [key, value] of Object.entries(result)) {
    const displayTopKey = getFieldDisplayName(TOP_LEVEL_TABLE, key);

    if (key === "params") {
      output[displayTopKey] = transformParams(value);
    } else if (key === "results") {
      output[displayTopKey] = transformResults(value);
    } else if (key === "summary") {
      output[displayTopKey] = transformSummary(value);
    } else if (key === "structure_analysis") {
      output[displayTopKey] = transformStructureAnalysis(value);
    } else if (key === "actual_runtime") {
      output[displayTopKey] = transformActualRuntime(value);
    } else if (key === "multi_seed") {
      output[displayTopKey] = transformObjectByTable("multi_seed", value);
    } else if (key === "seed_results") {
      output[displayTopKey] = transformSeedResults(value);
    } else {
      output[displayTopKey] = value;
    }
  }
  return output;
}

const prettyJson = computed(() => {
  if (!props.result) {
    return "";
  }

  try {
    return JSON.stringify(transformResultForDisplay(props.result), null, 2);
  } catch (e) {
    console.error("pretty json transform failed =", e);
    return JSON.stringify(props.result, null, 2);
  }
});

function zoomIn() {
  fontSize.value = Math.min(fontSize.value + 1, 22);
}

function zoomOut() {
  fontSize.value = Math.max(fontSize.value - 1, 10);
}

async function copyJson() {
  try {
    await navigator.clipboard.writeText(prettyJson.value || "");
    alert("原始结果已复制");
  } catch (e) {
    console.error(e);
    alert("复制失败，请检查浏览器权限");
  }
}
</script>

<template>
  <div class="ui-card section-gap">
    <div class="section-toolbar">
      <h3 class="subsection-title" style="margin-bottom: 0;">原始结果 JSON</h3>
      <div class="toolbar-group">
        <button class="ui-btn" @click="zoomOut">缩小</button>
        <button class="ui-btn" @click="zoomIn">放大</button>
        <button class="ui-btn-primary" @click="copyJson">一键复制</button>
      </div>
    </div>

    <div
      class="json-box"
      style="max-height: 420px; overflow: auto;"
      :style="{ fontSize: fontSize + 'px' }"
    >
      {{ prettyJson }}
    </div>
  </div>
</template>
