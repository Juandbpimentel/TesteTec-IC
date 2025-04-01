<template>
  <NavBar />
  <v-main>
    <router-view />
  </v-main>
  <AppFooter />
</template>

<script setup>
import NavBar from '@/components/NavBar.vue'
</script>