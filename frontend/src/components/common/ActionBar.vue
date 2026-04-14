<script setup>
// 顶部操作栏
const props = defineProps({
  activePanel: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["change-panel", "run"]);

function handleChangePanel(panelName) {
  emit("change-panel", panelName);
}

function handleRun() {
  emit("run");
}

function isActive(panelName) {
  return props.activePanel === panelName;
}
</script>

<template>
  <div
    style="
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 20px;
    "
  >
    <div class="toolbar-group">
      <button
        class="ui-btn"
        :class="{ 'ui-btn-tab-active': isActive('base') }"
        @click="handleChangePanel('base')"
      >
        基础设置
      </button>

      <button
        class="ui-btn"
        :class="{ 'ui-btn-tab-active': isActive('decision') }"
        @click="handleChangePanel('decision')"
      >
        决策参数
      </button>

      <button
        class="ui-btn"
        :class="{ 'ui-btn-tab-active': isActive('feedback') }"
        @click="handleChangePanel('feedback')"
      >
        反馈参数
      </button>

      <button
        class="ui-btn"
        :class="{ 'ui-btn-tab-active': isActive('scenario') }"
        @click="handleChangePanel('scenario')"
      >
        场景参数
      </button>

      <button
        class="ui-btn"
        :class="{ 'ui-btn-tab-active': isActive('advanced') }"
        @click="handleChangePanel('advanced')"
      >
        高级配置
      </button>
    </div>

    <div>
      <button class="ui-btn-primary" @click="handleRun" :disabled="loading">
        {{ loading ? "运行中..." : "运行仿真" }}
      </button>
    </div>
  </div>
</template>