<template>
  <div class="operacoes-page">
    <h1>Operadoras</h1>

    <div class="filters">
      <v-select v-model="selectedUf" :items="ufs" label="Selecione a UF" outlined dense />
      <v-select v-model="selectedModalidade" :items="modalidades" label="Selecione a Modalidade" outlined dense />
    </div>

    <CustomDataTable :row-data="operadoras" :column-defs="baseColumnDefs" :total-items="totalOperadoras"
      :items-per-page="pagination.limit" :current-page="pagination.page" @page-change="handlePageChange"
      @view-details="handleViewDetails" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
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
const totalOperadoras = ref(0);

const pagination = ref({
  limit: 20,
  page: 1,
  // O índice 0 (primeira página) não tem cursor (null)
  cursors: [null]
});

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
    // Usa o cursor da página atual (página - 1 pois o array inicia com índice 0)
    const start_cursor = pagination.value.cursors[pagination.value.page - 1];
    const requestParams = {
      ...params,
      limit: pagination.value.limit,
      start_cursor
    };

    const { data } = await fetchOperadoras(requestParams);
    console.log('Response recebida:', data);
    if (Array.isArray(data.operadoras)) {
      operadoras.value = data.operadoras;
      totalOperadoras.value = data.total_elementos;

      // Atualiza o array de cursores: se avançando para uma nova página, armazena o cursor retornado
      if (pagination.value.cursors.length < pagination.value.page + 1) {
        pagination.value.cursors.push(data.next_cursor);
      } else {
        pagination.value.cursors[pagination.value.page] = data.next_cursor;
      }
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

const fetchOperadorasWithFilters = (uf, modalidade) => {
  const params = {};
  if (uf) params.uf = uf;
  if (modalidade) params.modalidade = modalidade;
  // Reseta a paginação ao alterar os filtros
  pagination.value.page = 1;
  pagination.value.cursors = [null];
  loadOperadoras(params);
};

watch([selectedUf, selectedModalidade], ([newUf, newModalidade]) => {
  fetchOperadorasWithFilters(newUf, newModalidade);
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

const handlePageChange = (payload) => {
  // O payload pode ser um número (nova página) ou um objeto { page, itemsPerPage }
  if (typeof payload === 'number') {
    pagination.value.page = payload;
  } else if (typeof payload === 'object') {
    // Ao alterar o número de itens por página, reiniciamos a paginação
    pagination.value.limit = payload.itemsPerPage;
    pagination.value.page = payload.page;
    pagination.value.cursors = [null];
  }
  loadOperadoras({
    uf: selectedUf.value,
    modalidade: selectedModalidade.value,
  });
};

const totalPages = computed(() => {
  return Math.ceil(totalOperadoras.value / pagination.value.limit);
});
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
