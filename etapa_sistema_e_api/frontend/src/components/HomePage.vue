<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-btn to="/TelaSecundaria" color="primary" variant="outlined">
      Ir para Tela Secundária
    </v-btn>
  </v-container>
</template>

<script setup>
// Nenhum script necessário para esta página simplificada
</script>

<style scoped>
  .v-btn {
    font-size: 16px;
    font-weight: bold;
    padding: 16px 32px;
    text-align: center; /* Centraliza o texto do botão */
  }
  .v-btn:hover {
    background-color: #42b983;
    color: white;
  }
  .v-btn:active {
    background-color: #36a372;
    color: white;
  }
  .v-btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.5);
  }
  .v-btn:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
  }
  .v-btn:disabled:hover {
    background-color: #e0e0e0;
    color: #9e9e9e;
  }
  .v-btn:disabled:active {
    background-color: #e0e0e0;
    color: #9e9e9e;
  }
  .v-btn:disabled:focus {
    outline: none;
    box-shadow: none;
  }
  .v-btn:disabled:focus-visible {
    outline: none;
    box-shadow: none;
  }
</style>