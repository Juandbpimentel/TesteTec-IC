<template>
  <div class="operadora-detalhes">
    <!-- Seção de Dados Básicos -->
    <v-btn variant="outlined" color="primary" :to="'/'" style="margin-bottom: 1rem;">
      Voltar para Operações
    </v-btn>
    <h2 class="section-title">Dados da Operadora</h2>
    <div class="section-content">
      <v-row>
        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              Registro ANS:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.registro_operadora }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              CNPJ:
            </v-list-item-title>
            <v-list-item-subtitle>{{ formatCNPJ(operadora.cnpj) }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              Razão Social:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.razao_social }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>


        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              Nome Fantasia:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.nome_fantasia }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              Cidade:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.cidade }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              UF:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.uf }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <v-col cols="12" md="4">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">
              Modalidade:
            </v-list-item-title>
            <v-list-item-subtitle>{{ operadora.modalidade }}</v-list-item-subtitle>
          </v-list-item>
        </v-col>

        <!-- Adicione outros campos conforme necessário -->
      </v-row>
    </div>

    <!-- Seção de Demonstrações Contábeis -->
    <h2 class="section-title">Demonstrações Contábeis</h2>
    <div class="section-content">
      <!-- Filtros -->
      <v-row>
        <v-col cols="12" md="3">
          <v-text-field v-model="filtroDescricao" label="Filtrar por descrição" clearable
            @clear="handleFilterClear('descricao')" @input="resetAndLoad" />
        </v-col>

        <v-col cols="12" md="3">
          <v-select v-model="filtroTrimestre" :items="[1, 2, 3, 4]" label="Trimestre" clearable
            @clear="handleFilterClear('trimestre')" @change="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-select v-model="filtroAno" :items="[2023, 2024]" label="Ano" clearable @clear="handleFilterClear('ano')"
            @change="resetAndLoad" />
        </v-col>
      </v-row>

      <!-- Tabela Customizada -->
      <CustomDataTable :row-data="currentPageData" :column-defs="colunasDemonstracoes" :total-items="totalElementos"
        :items-per-page="paginacao.limit" :current-page="paginacao.page" :loading="carregando"
        @page-change="handlePageChange" :hide-actions="true" />
    </div>
    <!-- Botão para cancelar carregamento -->
    <v-btn variant="outlined" color="error" @click="cancelarRequisicoes">
      Cancelar Carregamento
    </v-btn>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute } from 'vue-router';
import CustomDataTable from '@/components/CustomDataTable.vue';
import { fetchOperadoraByRegistro, fetchDemonstracoes } from '@/services/apiService';

const route = useRoute();
const registroOperadora = route.params.registro_operadora;

// Estado reativo
const operadora = ref({
  registro_operadora: '',
  cnpj: '',
  razao_social: '',
  nome_fantasia: '',
  // ... outros campos
});

const pagesData = ref([]);
const carregando = ref(false);
const totalElementos = ref(0);

// Filtros
const filtroDescricao = ref('');
const filtroTrimestre = ref(null);
const filtroAno = ref(null);

// Paginação
const paginacao = ref({
  limit: 10,
  page: 1,
  cursors: [null],
});

// AbortController para cancelar requisições
let controller = new AbortController();

// Função para cancelar requisições
const cancelarRequisicoes = () => {
  if (controller) {
    console.log('Cancelando requisições...');
    controller.abort(); // Cancela as requisições em andamento
    controller = new AbortController(); // Cria um novo controller para futuras requisições
  }
};

// Carregamento inicial
onMounted(async () => {
  try {
    await carregarOperadora();
    await carregarDemonstracoes(1); // Carrega as demonstrações somente após carregar a operadora
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Carregamento inicial cancelado pelo usuário.');
    } else {
      console.error('Erro durante o carregamento inicial:', error);
    }
  }
});

// Limpa as requisições ao sair da página
onBeforeUnmount(() => {
  cancelarRequisicoes();
});

// Carregar dados da operadora
const carregarOperadora = async () => {
  try {
    carregando.value = true;

    const response = await fetchOperadoraByRegistro(registroOperadora, {
      signal: controller.signal, // Passa o sinal do AbortController
    });

    if (response?.data) {
      operadora.value = response.data;
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Requisição de operadora cancelada.');
    } else {
      console.error('Erro ao carregar dados da operadora:', error);
    }
  } finally {
    carregando.value = false;
  }
};

// Carregar demonstrações com cursor
const carregarDemonstracoes = async (page = 1) => {
  if (carregando.value) return;

  try {
    carregando.value = true;

    while (pagesData.value.length < page) {
      const currentPageIndex = pagesData.value.length;
      const start_cursor = paginacao.value.cursors[currentPageIndex] || null;

      const params = {
        registro_operadora: registroOperadora,
        start_cursor,
        limit: paginacao.value.limit,
        ...(filtroDescricao.value && { descricao: filtroDescricao.value.toUpperCase() }),
        ...(filtroTrimestre.value && { trimestre: filtroTrimestre.value }),
        ...(filtroAno.value && { ano: filtroAno.value }),
      };

      console.log('Carregando demonstrações com params:', params);

      const response = await fetchDemonstracoes(params, {
        signal: controller.signal, // Passa o sinal do AbortController
      });

      if (response?.data) {
        pagesData.value.push(response.data.demonstracoes);
        totalElementos.value = response.data.total_elementos;
        paginacao.value.cursors.push(response.data.next_cursor);
      } else {
        break;
      }
    }

    paginacao.value.page = page;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Requisição de demonstrações cancelada.');
    } else {
      console.error('Erro ao carregar demonstrações:', error);
    }
  } finally {
    carregando.value = false;
  }
};

// Dados da página atual
const currentPageData = computed(() => {
  return pagesData.value[paginacao.value.page - 1] || [];
});

// Manipuladores de paginação
const handlePageChange = (payload) => {
  if (typeof payload === 'object') {
    paginacao.value.limit = payload.itemsPerPage;
    resetAndLoad();
  } else {
    paginacao.value.page = payload;
    if (!pagesData.value[payload - 1]) {
      carregarDemonstracoes(payload);
    }
  }
};

// Função para resetar e recarregar os dados ao atualizar filtros
const resetAndLoad = () => {
  paginacao.value.page = 1;
  paginacao.value.cursors = [null];
  pagesData.value = [];
  carregarDemonstracoes(1);
};

// Função para limpar filtros específicos
const handleFilterClear = (filter) => {
  if (filter === 'descricao') filtroDescricao.value = '';
  if (filter === 'trimestre') filtroTrimestre.value = null;
  if (filter === 'ano') filtroAno.value = null;
  resetAndLoad();
};

// Watch para filtros
watch([filtroDescricao, filtroTrimestre, filtroAno], resetAndLoad);

// Formatação de dados
const formatarData = (data) => {
  if (!data || data === '-') return '-';
  try {
    return new Date(data).toLocaleDateString('pt-BR');
  } catch {
    return data;
  }
};

const formatCNPJ = (cnpj) => {
  if (!cnpj) return '-';
  const cleaned = cnpj.toString().replace(/\D/g, '');
  return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
};

// Definição das colunas
const colunasDemonstracoes = ref([
  {
    headerName: 'Trimestre',
    field: 'trimestre',
    align: 'center',
    format: (value) => value || '-',
  },
  {
    headerName: 'Ano',
    field: 'ano',
    align: 'center',
    format: (value) => value || '-',
  },
  {
    headerName: 'Descrição',
    field: 'descricao',
    format: (value) => value || '-',
  },
  {
    headerName: 'Data',
    field: 'data_demonstracao',
    format: (value) => formatarData(value),
  },
  {
    headerName: 'Saldo Inicial',
    field: 'vl_saldo_inicial',
    align: 'end',
    format: (value) =>
      Number(value)?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) || '-',
  },
  {
    headerName: 'Saldo Final',
    field: 'vl_saldo_final',
    align: 'end',
    format: (value) =>
      Number(value)?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) || '-',
  },
]);
</script>

<style scoped>
.operadora-detalhes {
  padding: 20px;
  max-width: 100vw;
  margin: 0 auto;
  background-color: #1e1e1e;
  color: #ffffff;
  min-height: 100vh;
}

.section-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #42b983;
}

.section-content {
  margin-bottom: 2rem;
}

.v-list-item-subtitle {
  color: #b0b0b0 !important;
}

.font-weight-bold {
  font-weight: 600;
  color: #ffffff;
}

.v-text-field ::v-deep(.v-input__control),
.v-select ::v-deep(.v-input__control) {
  background-color: #3d3d3d;
  border-radius: 4px;
}
</style>