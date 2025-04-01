<template>
  <div class="operacoes-page">
    <h1>Operadoras</h1>

    <div class="filters">
      <v-select v-model="selectedUf" :items="ufs" label="Selecione a UF" outlined dense />
      <v-select v-model="selectedModalidade" :items="modalidades" label="Selecione a Modalidade" outlined dense />
    </div>

    <CustomDataTable :row-data="operadoras" :column-defs="baseColumnDefs" @view-details="handleViewDetails"
      :total-items="totalOperadoras" :items-per-page="pagination.limit" :current-page="pagination.page"
      @page-change="handlePageChange" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import CustomDataTable from '@/components/CustomDataTable.vue';
import { fetchOperadoras, fetchUfs, fetchModalidades } from '@/services/apiService';
import { useRouter } from 'vue-router';
import { VSelect } from 'vuetify/components/VSelect';

const router = useRouter();

const operadoras = ref([]);
const ufs = ref([]);
const modalidades = ref([]);
const selectedUf = ref(null);
const selectedModalidade = ref(null);
const totalOperadoras = ref(0); // Novo estado para o total de operadoras
const pagination = ref({ // Estado para a paginação
  limit: 20,
  page: 1,
});
const startCursor = ref(null);

const baseColumnDefs = ref([
  { headerName: 'Registro Operadora', field: 'registro_operadora', sortable: true, filter: true },
  { headerName: 'CNPJ', field: 'cnpj', sortable: true, filter: true },
  { headerName: 'Razão Social', field: 'razao_social', sortable: true, filter: true },
  { headerName: 'Nome Fantasia', field: 'nome_fantasia', sortable: true, filter: true },
  { headerName: 'Modalidade', field: 'modalidade', sortable: true, filter: true },
  { headerName: 'UF', field: 'uf', filter: true },
  { headerName: 'Cidade', field: 'cidade', sortable: true, filter: true },
  { headerName: 'Telefone', field: 'telefone', sortable: false, filter: true },
]);

const loadOperadoras = async (params = {}) => {
  try {
    // Adiciona os parâmetros de paginação à requisição
    const requestParams = {
      ...params,
      limit: pagination.value.limit,
      start_cursor: startCursor.value,
    };

    const { data } = await fetchOperadoras(requestParams);
    console.log('Operadoras recebidas no pai:', data.operadoras);
    if (Array.isArray(data.operadoras)) {
      operadoras.value = data.operadoras;
      totalOperadoras.value = data.total; // Atualiza o total de operadoras
    } else {
      console.error('Dados inválidos recebidos:', data);
      operadoras.value = [];
      totalOperadoras.value = 0;
    }
  } catch (error) {
    console.error('Erro ao carregar operadoras:', error);
    operadoras.value = [];
    totalOperadoras.value = 0;
  }
};

const loadFilters = async () => {
  try {
    const [ufsResponse, modalidadesResponse] = await Promise.all([
      fetchUfs(),
      fetchModalidades(),
    ]);
    ufs.value = ufsResponse.data;
    modalidades.value = modalidadesResponse.data;
  } catch (error) {
    console.error('Erro ao carregar filtros:', error);
  }
};

watch([selectedUf, selectedModalidade], ([newUf, newModalidade]) => {
  const params = {};
  if (newUf) params.uf = newUf;
  if (newModalidade) params.modalidade = newModalidade;
  loadOperadoras(params);
});

onMounted(async () => {
  await loadFilters();
  await loadOperadoras();
});

const handleViewDetails = (operadoraData) => {
  console.log('Visualizar detalhes para:', operadoraData);
  const operadoraId = operadoraData.registro_operadora || operadoraData.id;
  if (operadoraId) {
    router.push({ name: 'DetalhesOperadora', params: { id: operadoraId } });
  } else {
    console.warn("Não foi possível encontrar um ID para navegar.");
  }
};

const handlePageChange = (newPage) => {
  console.log('Nova página:', newPage);
  pagination.value.page = newPage;
  // Calcula o novo start_cursor com base na página e no limite.
  // start_cursor é um exemplo, ajuste conforme a API do backend
  startCursor.value = (newPage - 1) * pagination.value.limit;
  loadOperadoras({
    uf: selectedUf.value,
    modalidade: selectedModalidade.value,
  });
};
</script>

<style scoped>
.operacoes-page {
  padding: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filters>* {
  min-width: 200px;
  flex-grow: 1;
}
</style>
