<script setup>
import PageHeader from "../components/common/PageHeader.vue";
import DataDictionary from "../components/data_dictionary/DataDictionary.vue";
</script>

<template>
  <div
    style="
      padding: 24px;
      font-family: Arial, sans-serif;
      max-width: 1480px;
      margin: 0 auto;
    "
  >
    <PageHeader
      title="数据字典"
      subtitle="查看系统数据表、字段含义、数据来源与示例值。"
    />

    <DataDictionary />
  </div>
</template>