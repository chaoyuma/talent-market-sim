<script setup>
import { ref, onMounted, watch } from "vue";
import { getMetadataTableList, getMetadataByTableName } from "../../api/metadata";

const tableList = ref([]);
const selectedTable = ref("");
const tableDetail = ref(null);

const loadingTables = ref(false);
const loadingDetail = ref(false);
const error = ref("");

async function loadTableList() {
  loadingTables.value = true;
  error.value = "";

  try {
    const res = await getMetadataTableList();
    tableList.value = res.data?.tables || [];

    if (tableList.value.length > 0 && !selectedTable.value) {
      selectedTable.value = tableList.value[0];
    }
  } catch (e) {
    console.error(e);
    error.value = "加载数据字典表列表失败";
  } finally {
    loadingTables.value = false;
  }
}

async function loadTableDetail(tableName) {
  if (!tableName) {
    tableDetail.value = null;
    return;
  }

  loadingDetail.value = true;
  error.value = "";

  try {
    const res = await getMetadataByTableName(tableName);
    tableDetail.value = res.data;
  } catch (e) {
    console.error(e);
    error.value = `加载表 ${tableName} 的元数据失败`;
    tableDetail.value = null;
  } finally {
    loadingDetail.value = false;
  }
}

watch(selectedTable, (newVal) => {
  loadTableDetail(newVal);
});

onMounted(() => {
  loadTableList();
});
</script>

<template>
  <div class="section-gap">
    <h2 class="section-title">数据字典</h2>

    <div class="ui-card section-gap">
      <div class="form-row">
        <label style="min-width: 160px; font-weight: 600;">选择数据表</label>

        <select v-model="selectedTable" class="ui-select" :disabled="loadingTables">
          <option value="" disabled>请选择表</option>
          <option v-for="name in tableList" :key="name" :value="name">
            {{ name }}
          </option>
        </select>
      </div>

      <div v-if="loadingTables" style="color: #667085; margin-top: 8px;">
        正在加载表列表...
      </div>

      <div v-if="error" class="error-text" style="margin-top: 8px;">
        {{ error }}
      </div>
    </div>

    <div v-if="loadingDetail" class="ui-card">
      正在加载表详情...
    </div>

    <div v-else-if="tableDetail" class="section-gap">
      <!-- 表级说明 -->
      <div class="ui-card">
        <h3 class="subsection-title">表说明</h3>
        <div style="line-height: 1.8;">
          <div><b>表名：</b>{{ tableDetail.table_name }}</div>
          <div><b>业务含义：</b>{{ tableDetail.table_info?.field_meaning || "-" }}</div>
          <div><b>数据来源：</b>{{ tableDetail.table_info?.data_source || "-" }}</div>
          <div><b>备注：</b>{{ tableDetail.table_info?.notes || "-" }}</div>
        </div>
      </div>

      <!-- 字段说明 -->
      <div class="ui-card">
        <h3 class="subsection-title">字段说明</h3>

        <div class="table-wrapper">
          <table class="ui-table">
            <thead>
              <tr>
                <th>字段名</th>
                <th>类型</th>
                <th>可空</th>
                <th>默认值</th>
                <th>字段含义</th>
                <th>示例值</th>
                <th>数据来源</th>
                <th>备注</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="field in tableDetail.fields" :key="field.field_name">
                <td>{{ field.field_name }}</td>
                <td>{{ field.field_type || "-" }}</td>
                <td>{{ field.is_nullable === 1 ? "是" : field.is_nullable === 0 ? "否" : "-" }}</td>
                <td>{{ field.default_value ?? "-" }}</td>
                <td>{{ field.field_meaning || "-" }}</td>
                <td>{{ field.example_value || "-" }}</td>
                <td>{{ field.data_source || "-" }}</td>
                <td>{{ field.notes || "-" }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>