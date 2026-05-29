<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-logo">
            <span class="logo-icon">🏢</span>
          </div>
          <h1 class="auth-title">城市建筑检测系统</h1>
          <p class="auth-subtitle">欢迎登录</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="auth-form" autocomplete="off">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input 
                v-model="form.username"
                type="text" 
                class="form-input"
                placeholder="请输入用户名"
                autocomplete="off"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input 
                v-model="form.password"
                type="password" 
                class="form-input"
                placeholder="请输入密码"
                autocomplete="off"
              />
            </div>
          </div>
          
          <button 
            type="submit"
            class="auth-btn"
            :disabled="loading"
          >
            <span v-if="loading" class="btn-loading">
              <span class="loading-spinner"></span>
              登录中...
            </span>
            <span v-else>登 录</span>
          </button>
        </form>
        
        <div class="auth-footer">
          <p>还没有账号？ 
            <router-link to="/register" class="auth-link">立即注册</router-link>
          </p>
        </div>
        
        <div v-if="error" class="auth-error">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const form = reactive({
  username: '',
  password: ''
});

const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);
    
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: form.username,
        password: form.password
      }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const data = await response.json();
      error.value = data.detail || `登录失败 (${response.status})`;
      return;
    }
    
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('username', data.username);
    router.push('/');
  } catch (e) {
    if (e && typeof e === 'object' && 'name' in e && e.name === 'AbortError') {
      error.value = '请求超时，请重试';
    } else {
      error.value = '网络错误，请检查后端服务是否正常运行';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 40px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  font-size: 40px;
}

.auth-title {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
}

.auth-subtitle {
  font-size: 14px;
  color: #8c8c8c;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #595959;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: #8c8c8c;
}

.form-input {
  width: 100%;
  padding: 14px 14px 14px 48px;
  border: 1px solid #d9d9d9;
  border-radius: 10px;
  font-size: 14px;
  color: #262626;
  background: #fafafa;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.form-input::placeholder {
  color: #bfbfbf;
}

.auth-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
}

.auth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #8c8c8c;
}

.auth-link {
  color: #1890ff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.auth-link:hover {
  color: #096dd9;
}

.auth-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  color: #d93026;
  font-size: 13px;
}

.error-icon {
  font-size: 14px;
}
</style>