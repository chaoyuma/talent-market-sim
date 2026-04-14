import { ref } from "vue";
import { runSimulation } from "../api";

/**
 * 仿真运行逻辑
 * @param {object} formRef 表单数据引用
 */
export function useSimulation(formRef) {
  const loading = ref(false);
  const error = ref("");
  const result = ref(null);

  async function handleRunSimulation() {
    loading.value = true;
    error.value = "";
    result.value = null;

    try {
      const res = await runSimulation(formRef.value);
      result.value = res.data;
    } catch (e) {
      console.error(e);
      error.value = "运行仿真失败，请检查后端接口或参数设置。";
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    result,
    handleRunSimulation,
  };
}