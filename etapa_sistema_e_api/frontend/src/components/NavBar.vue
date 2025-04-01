<template>
  <v-app-bar app>
    <v-toolbar-title>Sistema</v-toolbar-title>
    <v-spacer />
    <v-btn v-for="route in routes" :key="route.name" :to="route.path" :class="{ active: $route.path === route.path }"
      text>
      {{ route.name }}
    </v-btn>
  </v-app-bar>
</template>

<script setup>

const routes = [
  { name: 'Home', path: '/' },
  { name: 'Operadoras', path: '/operadoras' },
  { name: 'Demonstracoes', path: '/demonstracoes' },
  { name: 'Relatorios', path: '/relatorios' },
]
</script>

<style scoped>
.v-btn.active {
  background-color: #42b983;
  color: white;
}
</style>