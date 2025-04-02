<template>
  <div class="operacoes-page">
    <h1 class="section-title">
      Operadoras
    </h1>

    <div class="filters">
      <v-row>
        <v-col cols="12" md="3">
          <v-select v-model="selectedUf" :items="ufs" label="Selecione a UF" clearable outlined dense
            @change="resetAndLoad" @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-select v-model="selectedModalidade" :items="modalidades" label="Selecione a Modalidade" clearable outlined
            dense @change="resetAndLoad" @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
      </v-row>
    </div>

    <div class="search-filters">
      <v-row>
        <v-col cols="12" md="3">
          <v-text-field v-model="searchFilters.registro_operadora" label="Registro Operadora" clearable outlined dense
            @input="resetAndLoad" @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="searchFilters.cnpj" label="CNPJ" clearable outlined dense @input="resetAndLoad"
            @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="searchFilters.razao_social" label="Razão Social" clearable outlined dense
            @input="resetAndLoad" @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="searchFilters.nome_fantasia" label="Nome Fantasia" clearable outlined dense
            @input="resetAndLoad" @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="searchFilters.cidade" label="Cidade" clearable outlined dense @input="resetAndLoad"
            @clear="resetAndLoad" @vue:updated="resetAndLoad" />
        </v-col>
      </v-row>
    </div>

    <div class="button-group">
      <v-btn variant="tonal" color="error" @click="clearFilters">
        Limpar Filtros
      </v-btn>
      <v-btn variant="outlined" color="error" @click="cancelarRequisicoes">
        Cancelar Carregamento
      </v-btn>
    </div>

    <CustomDataTable :row-data="currentPageData" :column-defs="baseColumnDefs" :total-items="totalOperadoras"
      :items-per-page="pagination.limit" :current-page="pagination.page" :loading="isLoading"
      @page-change="handlePageChange" @view-details="handleViewDetails" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import CustomDataTable from '@/components/CustomDataTable.vue';
import { fetchOperadoras, fetchUfs, fetchModalidades } from '@/services/apiService';
import { useRouter } from 'vue-router';

const router = useRouter();

const ufs = ref([]);
const modalidades = ref([]);
const selectedUf = ref(null);
const selectedModalidade = ref(null);

const searchFilters = ref({
  registro_operadora: '',
  cnpj: '',
  razao_social: '',
  nome_fantasia: '',
  cidade: ''
});

const totalOperadoras = ref(0);

const isLoading = ref(false);

const pagination = ref({
  limit: 20,
  page: 1,
  cursors: [null]
});
const pagesData = ref([]);

let controller = new AbortController();

const cancelarRequisicoes = () => {
  if (controller) {
    console.log('Cancelando requisições...');
    controller.abort();
    controller = new AbortController();
  }
};

const baseColumnDefs = ref([
  { headerName: 'Registro Operadora', field: 'registro_operadora', sortable: false, filter: true },
  { headerName: 'CNPJ', field: 'cnpj', sortable: false, filter: true },
  { headerName: 'Razão Social', field: 'razao_social', sortable: false, filter: true },
  { headerName: 'Nome Fantasia', field: 'nome_fantasia', sortable: false, filter: true },
  { headerName: 'Modalidade', field: 'modalidade', sortable: false, filter: true },
  { headerName: 'UF', field: 'uf', filter: true },
  { headerName: 'Cidade', field: 'cidade', sortable: false, filter: true },
  { headerName: 'Telefone', field: 'telefone', sortable: false, filter: true },
]);

const currentPageData = computed(() => {
  return pagesData.value[pagination.value.page - 1] || [];
});

const getRequestParams = () => {
  return {
    uf: selectedUf.value,
    modalidade: selectedModalidade.value,
    ...searchFilters.value,
    limit: pagination.value.limit,
  };
};

const loadPage = async (page, extraParams = {}) => {
  if (isLoading.value) return;

  if (pagesData.value[page - 1]) {
    pagination.value.page = page;
    return;
  }

  isLoading.value = true;
  try {
    while (pagesData.value.length < page) {
      const currentPageIndex = pagesData.value.length;
      const start_cursor = pagination.value.cursors[currentPageIndex] || null;

      const requestParams = {
        ...getRequestParams(),
        ...extraParams,
        start_cursor
      };

      const { data } = await fetchOperadoras(requestParams);

      if (Array.isArray(data.operadoras)) {
        pagesData.value.push(data.operadoras);
        totalOperadoras.value = data.total_elementos;
        pagination.value.cursors[currentPageIndex + 1] = data.next_cursor;
      } else {
        console.error('Dados inválidos recebidos:', data);
        break;
      }
    }
    pagination.value.page = page;
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Requisição cancelada.');
    } else {
      console.error('Erro ao carregar operadoras:', error);
    }
  } finally {
    isLoading.value = false;
  }
};

const resetAndLoad = async () => {
  pagesData.value = [];
  pagination.value.page = 1;
  pagination.value.cursors = [null];
  await loadPage(1);
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

onMounted(async () => {
  await loadFilters();
  await loadPage(1);
});

const handleViewDetails = (operadora) => {
  router.push({
    path: `/operadoras/${operadora.registro_operadora}`,
  });
};

const handlePageChange = async (payload) => {
  if (isLoading.value) return;

  if (typeof payload === 'object' && payload.itemsPerPage) {
    pagination.value.limit = payload.itemsPerPage;
    pagesData.value = [];
    pagination.value.cursors = [null];
    await loadPage(payload.page);
  } else if (typeof payload === 'number') {
    await loadPage(payload);
  }
};

const clearFilters = () => {
  selectedUf.value = null;
  selectedModalidade.value = null;

  Object.keys(searchFilters.value).forEach((key) => {
    searchFilters.value[key] = '';
  });

  resetAndLoad();
};
</script>

<style scoped>
.operacoes-page {
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