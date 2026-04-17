<script setup>
import { ref } from "vue";
import { generateParameterSuggestions } from "../../api/analysis";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["apply-suggested-params"]);

const loading = ref(false);
const error = ref("");
const diagnosis = ref([]);
const suggestions = ref([]);
const suggestedParams = ref({});
const usedLlm = ref(false);
const fallbackReason = ref("");

async function handleGenerateSuggestions() {
  if (!props.result) {
    return;
  }

  loading.value = true;
  error.value = "";
  diagnosis.value = [];
  suggestions.value = [];
  suggestedParams.value = {};
  usedLlm.value = false;
  fallbackReason.value = "";

  try {
    const res = await generateParameterSuggestions(props.result);
    const data = res.data || {};

    diagnosis.value = data.diagnosis || [];
    suggestions.value = data.parameter_suggestions || [];
    suggestedParams.value = data.suggested_params || {};
    usedLlm.value = !!data.used_llm;
    fallbackReason.value = data.fallback_reason || "";

    // console.log("DEBUG suggestedParams loaded =", JSON.parse(JSON.stringify(suggestedParams.value)));
  } catch (e) {
    console.error(e);
    error.value = "生成参数调优建议失败";
  } finally {
    loading.value = false;
  }
}

function handleApplySuggestedParams() {
  // console.log("DEBUG click apply suggested params");
  // console.log("DEBUG current suggestedParams =", JSON.parse(JSON.stringify(suggestedParams.value)));

  if (!suggestedParams.value || !Object.keys(suggestedParams.value).length) {
    alert("当前没有可应用的建议参数。");
    return;
  }

  emit("apply-suggested-params", suggestedParams.value);
}

function formatDirection(value) {
  if (value === "increase") return "上调";
  if (value === "decrease") return "下调";
  if (value === "keep") return "保持";
  return value || "-";
}
</script>

<template>
  <div class="ui-card section-gap">
    <div
      style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 12px;
      "
    >
      <div>
        <h3 class="subsection-title" style="margin-bottom: 6px;">参数调优建议</h3>
        <div style="color: #667085; font-size: 14px;">
          基于当前实验结果，由大模型或规则引擎生成参数调整建议。
        </div>
      </div>

      <button class="ui-btn-primary" @click="handleGenerateSuggestions" :disabled="loading">
        {{ loading ? "生成中..." : "生成调参建议" }}
      </button>
    </div>

    <div v-if="error" class="error-text">
      {{ error }}
    </div>

    <div v-if="loading" style="color: #667085;">
      正在分析当前实验结果，请稍候...
    </div>

    <template v-else-if="diagnosis.length || suggestions.length">
      <div style="margin-bottom: 14px;">
        <div v-if="usedLlm" style="color: #067647; font-weight: 600;">
          本次建议由大模型生成。
        </div>
        <div v-else style="color: #b54708; font-weight: 600;">
          本次建议为规则回退生成。
          <span v-if="fallbackReason">原因：{{ fallbackReason }}</span>
        </div>
      </div>

      <div
        class="ui-card"
        style="
          margin-bottom: 14px;
          padding: 14px 16px;
          background: #fcfcfd;
        "
      >
        <h4 style="margin-bottom: 8px; font-size: 15px; color: #101828;">诊断结论</h4>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8; color: #344054;">
          <li v-for="(item, idx) in diagnosis" :key="idx">
            {{ item }}
          </li>
        </ul>
      </div>

      <div v-if="suggestions.length" class="table-wrapper">
        <table class="ui-table">
          <thead>
            <tr>
              <th>参数组</th>
              <th>参数</th>
              <th>当前值</th>
              <th>建议值</th>
              <th>调整方向</th>
              <th>预期作用</th>
              <th>原因</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in suggestions" :key="idx">
              <td>{{ item.config_group || "-" }}</td>
              <td>{{ item.parameter || "-" }}</td>
              <td>{{ item.current_value ?? "-" }}</td>
              <td>{{ item.suggested_value ?? "-" }}</td>
              <td>{{ formatDirection(item.direction) }}</td>
              <td>{{ item.expected_effect || "-" }}</td>
              <td>{{ item.reason || "-" }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="Object.keys(suggestedParams).length"
        style="margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap;"
      >
        <button class="ui-btn-primary" @click="handleApplySuggestedParams">
          应用建议参数
        </button>
      </div>

      <div
        v-if="Object.keys(suggestedParams).length"
        class="ui-card"
        style="
          margin-top: 14px;
          padding: 14px 16px;
          background: #f8fafc;
        "
      >
        <h4 style="margin-bottom: 8px; font-size: 15px; color: #101828;">建议参数快照</h4>
        <div
          class="json-box"
          style="
            white-space: pre-wrap;
            line-height: 1.7;
            max-height: 320px;
            overflow: auto;
          "
        >
          {{ JSON.stringify(suggestedParams, null, 2) }}
        </div>
      </div>
    </template>

    <div v-else style="color: #667085;">
      点击上方按钮生成参数调优建议。
    </div>
  </div>
</template>