<template>
  <el-container class="page">
    <el-header class="header">
      <span>行业岗位库</span>
      <el-button @click="$router.push('/prompts')">Prompt 模板</el-button>
    </el-header>
    <el-main>
      <el-button type="primary" @click="onNew">+ 新增行业</el-button>
      <el-table :data="list" v-loading="loading" style="margin-top:16px">
        <el-table-column prop="code" label="Code" width="120" />
        <el-table-column prop="name" label="行业名" width="120" />
        <el-table-column prop="icon" label="图标" width="60" />
        <el-table-column label="岗位数">
          <template #default="{ row }">{{ (row.jobs || []).length }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link @click="onEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <el-dialog v-model="dialogVisible" :title="editing.id ? '编辑行业' : '新增行业'" width="600px">
      <el-form :model="editing" label-width="80px">
        <el-form-item label="Code"><el-input v-model="editing.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="editing.name" /></el-form-item>
        <el-form-item label="图标"><el-input v-model="editing.icon" placeholder="单 emoji,如 💻" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="editing.sort" :min="1" /></el-form-item>
        <el-form-item label="岗位(JSON)">
          <el-input v-model="editing.jobsText" type="textarea" :rows="6"
                    placeholder='[{"code":"frontend","name":"前端工程师","levels":[{"code":"mid","name":"中级"}]}]' />
        </el-form-item>
        <el-form-item label="企业名录"><el-input v-model="editing.companiesText" placeholder="逗号分隔" /></el-form-item>
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

const list = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editing = reactive({ id: '', code: '', name: '', icon: '💼', sort: 99, jobsText: '[]', companiesText: '' });

async function load() {
  loading.value = true;
  try {
    const { list: l } = await api.listIndustries();
    list.value = l;
  } finally { loading.value = false; }
}

function onNew() {
  Object.assign(editing, { id: '', code: '', name: '', icon: '💼', sort: 99, jobsText: '[]', companiesText: '' });
  dialogVisible.value = true;
}

function onEdit(row) {
  Object.assign(editing, {
    id: row._id, code: row.code, name: row.name, icon: row.icon || '💼', sort: row.sort || 99,
    jobsText: JSON.stringify(row.jobs || [], null, 2),
    companiesText: (row.companies || []).join(','),
  });
  dialogVisible.value = true;
}

async function onSave() {
  let jobs;
  try { jobs = JSON.parse(editing.jobsText); }
  catch (e) { return ElMessage.error('岗位 JSON 格式错误'); }
  const payload = {
    id: editing.id || undefined,
    code: editing.code, name: editing.name, icon: editing.icon, sort: editing.sort,
    jobs,
    companies: editing.companiesText.split(/[,，]/).map(s => s.trim()).filter(Boolean),
  };
  await api.saveIndustry(payload);
  ElMessage.success('已保存');
  dialogVisible.value = false;
  load();
}

onMounted(load);
</script>

<style scoped>
.page { min-height: 100vh; }
.header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #ebeef5; }
</style>
