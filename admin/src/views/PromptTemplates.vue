<template>
  <el-container class="page">
    <el-header class="header">
      <span>Prompt 模板库</span>
      <el-button @click="$router.push('/industries')">行业岗位</el-button>
    </el-header>
    <el-main>
      <el-form :inline="true" :model="filter" @submit.prevent="load">
        <el-form-item label="类型">
          <el-select v-model="filter.type" clearable placeholder="全部" style="width:140px">
            <el-option label="optimize" value="optimize" />
            <el-option label="parse" value="parse" />
          </el-select>
        </el-form-item>
        <el-form-item label="身份">
          <el-select v-model="filter.identity" clearable placeholder="全部" style="width:140px">
            <el-option v-for="i in IDENTITIES" :key="i" :label="i" :value="i" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load">查询</el-button>
          <el-button @click="onNew">+ 新建模板</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="identity" label="身份" width="100" />
        <el-table-column prop="industry" label="行业" width="80" />
        <el-table-column prop="level" label="职级" width="80" />
        <el-table-column prop="version" label="版本" width="60" />
        <el-table-column label="模板预览">
          <template #default="{ row }">
            <div class="preview">{{ row.template.slice(0, 80) }}{{ row.template.length > 80 ? '...' : '' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link @click="onEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <el-dialog v-model="dialogVisible" :title="editing.id ? '编辑模板' : '新建模板'" width="800px" top="5vh">
      <el-form :model="editing" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="类型">
              <el-select v-model="editing.type">
                <el-option label="optimize" value="optimize" />
                <el-option label="parse" value="parse" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="身份">
              <el-select v-model="editing.identity">
                <el-option v-for="i in IDENTITIES" :key="i" :label="i" :value="i" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="行业/职级">
              <el-input v-model="editing.industry" placeholder="* 表示通配" style="width:48%" />
              <el-input v-model="editing.level" placeholder="*" style="width:48%; margin-left:4%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="模板">
          <el-input v-model="editing.template" type="textarea" :rows="16" />
        </el-form-item>
        <el-form-item label="变量(逗号分隔)">
          <el-input v-model="editing.variablesText" placeholder="structuredResume, targetJob, targetLevel" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { api } from '../api';

const IDENTITIES = ['*', 'freshgrad', 'social', 'transition', 'stateowned', 'foreign'];

const list = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const filter = reactive({ type: '', identity: '' });
const editing = reactive({ id: '', type: 'optimize', identity: 'social', industry: '*', level: '*', template: '', variablesText: '' });

async function load() {
  loading.value = true;
  try {
    const payload = {};
    if (filter.type) payload.type = filter.type;
    if (filter.identity) payload.identity = filter.identity;
    const { list: l } = await api.listPromptTemplates(payload);
    list.value = l;
  } finally { loading.value = false; }
}

function onNew() {
  Object.assign(editing, { id: '', type: 'optimize', identity: 'social', industry: '*', level: '*', template: '', variablesText: '' });
  dialogVisible.value = true;
}

function onEdit(row) {
  Object.assign(editing, {
    id: row._id, type: row.type, identity: row.identity,
    industry: row.industry, level: row.level,
    template: row.template,
    variablesText: (row.variables || []).join(', '),
  });
  dialogVisible.value = true;
}

async function onSave() {
  const payload = {
    id: editing.id || undefined,
    type: editing.type, identity: editing.identity,
    industry: editing.industry, level: editing.level,
    template: editing.template,
    variables: editing.variablesText.split(',').map(s => s.trim()).filter(Boolean),
  };
  await api.savePromptTemplate(payload);
  ElMessage.success('已保存(版本 +1)');
  dialogVisible.value = false;
  load();
}

onMounted(load);
</script>

<style scoped>
.page { min-height: 100vh; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #ebeef5; }
.preview { font-family: monospace; font-size: 12px; color: #666; }
</style>
