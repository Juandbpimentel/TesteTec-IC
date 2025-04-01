<template>
  <div class="demonstracao-page">
    <h1>Operações</h1>
    <p>Bem-vindo à página da Demonstracao {{ id }}!</p>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id
</script>

<style scoped>
.demonstracao-page {
  padding: 20px;
}

.demonstracao-page h1 {
  color: #42b983;
}
</style>