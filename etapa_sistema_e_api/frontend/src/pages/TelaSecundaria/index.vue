<script setup></script>

<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto" max-width="900">
      <div class="text-center">
        <p class="text-body-2 font-weight-light mb-n1">Bem vindo ao </p>

        <h1 class="text-h4 font-weight-bold">Sistema de Operadoras de Saúde</h1>
        <v-btn to="/" text="Tela Home" />
      </div>
    </v-responsive>
  </v-container>
</template>

<style>
h1 {
  color: #42b983;
}
p {
  font-size: 20px;
}

tela_secundaria_container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100%;
  background-color: #f5f5f5;
}
</style>
