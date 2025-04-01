<template>
  <div class="operacao-page">
    <h1>Operações</h1>
    <p>Bem-vindo à página da Operacao {{ id }}!</p>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id
</script>

<style scoped>
.operacao-page {
  padding: 20px;
}

.operacao-page h1 {
  color: #42b983;
}
</style>