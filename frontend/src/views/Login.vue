<template>
  <div class="min-h-screen bg-slate-900 flex items-center justify-center text-slate-50">
    <div class="bg-slate-800 p-8 rounded border border-slate-700 w-96">
      <h1 class="text-xl font-bold mb-4">Sembako Analytics</h1>
      <p class="text-slate-400 mb-6 text-sm">Secure Authentication Gateway</p>
      <button @click="login" class="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-900 font-bold py-2 rounded transition-colors">
        Connect Securely
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  methods: {
    login() {
      // Mocking a successful authentication payload
      localStorage.setItem('JWT_TOKEN', 'mock-secure-token')
      this.$router.push('/')
    }
  }
}
</script>
