<script setup>
import { ref, computed } from "vue";
import { generateResultExplanation } from "../../api/analysis";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

const loading = ref(false);
const explanation = ref("");
const error = ref("");

const latest = computed(() => {
  if (!props.result || !Array.isArray(props.result.results) || props.result.results.length === 0) {
    return null;
  }
  return props.result.results[props.result.results.length - 1];
});

async function handleGenerateExplanation() {
  if (!props.result) {
    return;
  }

  loading.value = true;
  error.value = "";
  explanation.value = "";

  try {
    const payload = {
      experiment_id: props.result.experiment_id,
      params: props.result.params,
      actual_runtime: props.result.actual_runtime || null,
      summary: props.result.summary || null,
      latest_result: latest.value,
      results: props.result.results || [],
    };

    const res = await generateResultExplanation(payload);
    explanation.value = res.data?.explanation || "未生成解释内容。";
  } catch (e) {
    console.error(e);
    error.value = "生成结果解释失败，请检查后端接口或大模型配置。";
  } finally {
    loading.value = false;
  }
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
        <h3 class="subsection-title" style="margin-bottom: 6px;">结果解释</h3>
        <div style="color: #667085; font-size: 14px;">
          基于当前实验结果，由大模型生成总体判断、关键现象、原因解释和调参建议。
        </div>
      </div>

      <button class="ui-btn-primary" @click="handleGenerateExplanation" :disabled="loading">
        {{ loading ? "生成中..." : "生成结果解释" }}
      </button>
    </div>

    <div v-if="error" class="error-text">
      {{ error }}
    </div>

    <div v-if="loading" style="color: #667085;">
      正在生成解释，请稍候...
    </div>

    <div
      v-else-if="explanation"
      class="json-box"
      style="white-space: pre-wrap; line-height: 1.7;"
    >
      {{ explanation }}
    </div>

    <div v-else style="color: #667085;">
      点击上方按钮生成结果解释。
    </div>
  </div>
</template>