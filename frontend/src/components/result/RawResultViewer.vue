<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
});

const fontSize = ref(13);

const prettyJson = computed(() => {
  if (!props.result) {
    return "";
  }
  return JSON.stringify(props.result, null, 2);
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
    <div
      style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 12px;
      "
    >
      <h3 class="subsection-title" style="margin-bottom: 0;">原始结果 JSON</h3>

      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button class="ui-btn" @click="zoomOut">缩小</button>
        <button class="ui-btn" @click="zoomIn">放大</button>
        <button class="ui-btn-primary" @click="copyJson">一键复制</button>
      </div>
    </div>

    <div
      class="json-box"
      style="
        max-height: 420px;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 1.6;
      "
      :style="{ fontSize: fontSize + 'px' }"
    >
      {{ prettyJson }}
    </div>
  </div>
</template>