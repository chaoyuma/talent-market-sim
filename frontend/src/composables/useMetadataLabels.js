import { ref } from "vue";
import { getMetadataByTableName } from "../api/metadata";
import { getDisplayLabel } from "../utils/displayLabels";

export function useMetadataLabels() {
  const metadataMap = ref({});

  async function loadTableMetadata(tableName) {
    try {
      const res = await getMetadataByTableName(tableName);
      const fields = res.data?.fields || [];
      const fieldMap = {};

      for (const field of fields) {
        const key = field.field_name;
        fieldMap[key] = {
          label: field.field_meaning || getDisplayLabel(tableName, key),
          notes: field.notes || "",
          raw: field,
        };
      }

      metadataMap.value[tableName] = fieldMap;
      return fieldMap;
    } catch (e) {
      console.warn(`metadata table load failed: ${tableName}`, e?.response?.status || e);
      metadataMap.value[tableName] = {};
      return {};
    }
  }

  async function loadMetadataTables(tableNames = []) {
    for (const tableName of tableNames) {
      if (!metadataMap.value[tableName]) {
        await loadTableMetadata(tableName);
      }
    }
  }

  function getFieldDisplayName(tableName, key) {
    const meta = metadataMap.value?.[tableName]?.[key];
    const label = meta?.label || getDisplayLabel(tableName, key);
    return label === key ? key : `${label}（${key}）`;
  }

  return {
    metadataMap,
    loadTableMetadata,
    loadMetadataTables,
    getFieldDisplayName,
  };
}
