<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>简历优化管理后台</h2>
      <el-form @submit.prevent="onSubmit" :model="form" label-width="0">
        <el-form-item>
          <el-input v-model="form.username" placeholder="账号" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="onSubmit" style="width:100%">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { api } from '../api';

const router = useRouter();
const loading = ref(false);
const form = reactive({ username: '', password: '' });

async function onSubmit() {
  if (!form.username || !form.password) {
    return ElMessage.warning('请输入账号密码');
  }
  loading.value = true;
  try {
    const { token } = await api.login(form.username, form.password);
    localStorage.setItem('adminToken', token);
    ElMessage.success('登录成功');
    router.push('/industries');
  } catch (e) { /* toast 已触发 */ }
  finally { loading.value = false; }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: #f5f7fa;
}
.login-card { width: 380px; }
.login-card h2 { text-align: center; margin-bottom: 24px; }
</style>
