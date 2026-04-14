import { ref } from "vue";
import {
  getConfigTemplateList,
  getConfigTemplateDetail,
  saveConfigTemplate,
} from "../api/config";

/**
 * 参数模板管理逻辑
 * @param {object} formRef 页面表单数据引用
 */
export function useConfigTemplates(formRef) {
  const templateList = ref([]);
  const selectedConfigId = ref("");
  const configName = ref("");
  const configDescription = ref("");
  const configLoading = ref(false);
  const configError = ref("");
  const currentConfigInfo = ref(null);

  /**
   * 加载模板列表
   */
  async function loadTemplateList() {
    configLoading.value = true;
    configError.value = "";

    try {
      const res = await getConfigTemplateList();
      templateList.value = res.data || [];
    } catch (e) {
      console.error(e);
      configError.value = "加载参数模板列表失败";
    } finally {
      configLoading.value = false;
    }
  }

  /**
   * 保存当前表单为模板
   */
  async function handleSaveTemplate() {
    configLoading.value = true;
    configError.value = "";

    try {
      const payload = {
        config_name: configName.value,
        description: configDescription.value,
        ...formRef.value,
      };

      const res = await saveConfigTemplate(payload);
      currentConfigInfo.value = res.data || null;

      // 保存成功后刷新模板列表
      await loadTemplateList();
    } catch (e) {
      console.error(e);
      configError.value = "保存参数模板失败";
    } finally {
      configLoading.value = false;
    }
  }

  /**
   * 加载某个模板并回填到当前表单
   */
  async function handleLoadTemplate() {
    if (!selectedConfigId.value) return;

    configLoading.value = true;
    configError.value = "";

    try {
      const res = await getConfigTemplateDetail(selectedConfigId.value);
      const data = res.data;

      // 回填页面表单
      formRef.value = {
        base_config: data.base_config_json,
        student_config: data.student_config_json,
        school_config: data.school_config_json,
        employer_config: data.employer_config_json,
        scenario_config: data.scenario_config_json,
        type_config: data.type_config_json,
        data_config: data.data_config_json,
        llm_config: data.llm_config_json,
      };

      currentConfigInfo.value = {
        config_id: data.config_id,
        config_name: data.config_name,
        config_version: data.config_version,
      };
    } catch (e) {
      console.error(e);
      configError.value = "加载参数模板失败";
    } finally {
      configLoading.value = false;
    }
  }

  return {
    templateList,
    selectedConfigId,
    configName,
    configDescription,
    configLoading,
    configError,
    currentConfigInfo,
    loadTemplateList,
    handleSaveTemplate,
    handleLoadTemplate,
  };
}