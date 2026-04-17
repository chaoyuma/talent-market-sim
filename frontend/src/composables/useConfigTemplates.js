import { ref } from "vue";
import {
  getConfigTemplateList,
  getConfigTemplateDetail,
  saveConfigTemplate,
} from "../api/config";

/**
 * 保险的纯对象拷贝
 * 适合当前这种纯配置对象，避免 structuredClone 碰到不可克隆对象时报错
 */
function clonePlainObject(obj) {
  return JSON.parse(JSON.stringify(obj ?? {}));
}

/**
 * 深合并对象，避免模板加载时丢失新字段
 * 这里不要用 structuredClone，防止 formRef 里混入不可克隆对象时报错
 */
function deepMerge(target, source) {
  const output = clonePlainObject(target);

  for (const key of Object.keys(source || {})) {
    const sourceValue = source[key];
    const targetValue = output[key];

    if (
      sourceValue &&
      typeof sourceValue === "object" &&
      !Array.isArray(sourceValue) &&
      targetValue &&
      typeof targetValue === "object" &&
      !Array.isArray(targetValue)
    ) {
      output[key] = deepMerge(targetValue, sourceValue);
    } else {
      output[key] = sourceValue;
    }
  }

  return output;
}

/**
 * 只提取模板保存所需的纯配置字段
 * 避免把事件对象、window、响应式代理等脏数据带进去
 */
function buildPureConfigSnapshot(formValue) {
  return {
    scenario_name: formValue?.scenario_name ?? "baseline",
    base_config: clonePlainObject(formValue?.base_config),
    student_config: clonePlainObject(formValue?.student_config),
    school_config: clonePlainObject(formValue?.school_config),
    employer_config: clonePlainObject(formValue?.employer_config),
    scenario_config: clonePlainObject(formValue?.scenario_config),
    type_config: clonePlainObject(formValue?.type_config),
    data_config: clonePlainObject(formValue?.data_config),
    llm_config: clonePlainObject(formValue?.llm_config),
  };
}

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
      templateList.value = res.data?.data || res.data || [];
    } catch (e) {
      console.error("load template list error =", e);
      console.error("load template list response =", e?.response?.data);
      console.error("load template list status =", e?.response?.status);

      configError.value =
        e?.response?.data?.message ||
        e?.response?.data?.detail ||
        "加载参数模板列表失败";
    } finally {
      configLoading.value = false;
    }
  }
  // 回填表单数据时，先把当前选中模板的信息展示出来，方便用户确认
  async function handleSelectTemplate(templateId) {
    selectedConfigId.value = templateId;
    configError.value = "";

    if (!templateId) {
      configName.value = "";
      configDescription.value = "";
      currentConfigInfo.value = null;
      return;
    }

    try {
      const id = Number(templateId);
      if (!id) {
        configError.value = "请选择有效模板";
        return;
      }

      const res = await getConfigTemplateDetail(id);
      const detail = res.data?.data || res.data;

      configName.value = detail?.template_name || "";
      configDescription.value = detail?.template_desc || "";
      currentConfigInfo.value = {
        id: detail?.id,
        template_name: detail?.template_name,
        template_desc: detail?.template_desc,
      };
    } catch (e) {
      console.error("select template error =", e);
      console.error("select template response =", e?.response?.data);
      console.error("select template status =", e?.response?.status);

      configError.value =
        e?.response?.data?.message ||
        e?.response?.data?.detail ||
        "读取模板信息失败";
    }
  }
  /**
   * 保存当前表单为模板
   */
  async function handleSaveTemplate() {
    if (!configName.value?.trim()) {
      configError.value = "请先填写模板名称";
      return;
    }

    configLoading.value = true;
    configError.value = "";

    try {
      const payload = {
        template_name: configName.value.trim(),
        template_desc: configDescription.value?.trim() || "",
        config_json: buildPureConfigSnapshot(formRef.value),
      };

      console.log("save template payload =", payload);

      const res = await saveConfigTemplate(payload);
      currentConfigInfo.value = res.data?.data || res.data || null;

      await loadTemplateList();
    } catch (e) {
      console.error("save template error =", e);
      console.error("save template response =", e?.response?.data);
      console.error("save template status =", e?.response?.status);

      configError.value =
        e?.response?.data?.message ||
        e?.response?.data?.detail ||
        "保存参数模板失败";
    } finally {
      configLoading.value = false;
    }
  }

  /**
   * 加载某个模板并回填到当前表单
   */
  async function handleLoadTemplate() {
    if (!selectedConfigId.value) {
      configError.value = "请先选择一个模板";
      return;
    }

    configLoading.value = true;
    configError.value = "";

    try {
      const templateId = Number(selectedConfigId.value);
      if (!templateId) {
        configError.value = "请选择有效模板";
        return;
      }

      const res = await getConfigTemplateDetail(templateId);
      console.log("load template response =", res.data);

      const detail = res.data?.data || res.data;
      const configJson = detail?.config_json || {};

      formRef.value = deepMerge(formRef.value, configJson);

      currentConfigInfo.value = {
        id: detail?.id,
        template_name: detail?.template_name,
        template_desc: detail?.template_desc,
      };

      configName.value = detail?.template_name || "";
      configDescription.value = detail?.template_desc || "";
    } catch (e) {
      console.error("load template error =", e);
      console.error("load template response =", e?.response?.data);
      console.error("load template status =", e?.response?.status);

      configError.value =
        e?.response?.data?.message ||
        e?.response?.data?.detail ||
        "加载参数模板失败";
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
    handleSelectTemplate,
  };
}