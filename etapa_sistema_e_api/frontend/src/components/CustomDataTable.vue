<template>
    <v-data-table :items="props.rowData" :headers="finalHeaders" :loading="loading"
        :no-data-text="'Nenhum dado encontrado.'" :no-results-text="'Nenhum resultado encontrado.'" :search="search"
        :server-options="{
            page: localPage,
            itemsPerPage: localItemsPerPage,
        }" :items-length="totalItems" @update:options="handleOptionsUpdate">
        <template #top>
            <v-text-field v-model="search" label="Buscar" class="mx-4" hide-details />
            <v-spacer />
            <v-btn variant="text" :disabled="!search" class="mr-4" @click="clearSearch">
                Limpar Busca
            </v-btn>
        </template>
        <template #[`item.actions`]="{ item }">
            <v-btn size="small" class="mr-2" variant="outlined" @click="emit('view-details', item)">
                Visualizar
            </v-btn>
        </template>
        <template #bottom>
            <div class="d-flex align-center justify-end flex-wrap">
                <span class="mr-2 text-caption">
                    Página {{ localPage }} de {{ totalPagesDisplay }}
                </span>
                <v-pagination v-model="localPage" :length="totalPagesDisplay"
                    :total-visible="Math.min(totalPagesDisplay, 7)" :disabled="loading"
                    class="mt-2" @update:model-value="handlePageChange" />
                <v-select v-model="localItemsPerPage" :items="[10, 20, 50, 100]" label="Itens por página"
                    class="ml-4 mt-2" dense @update:model-value="handleItemsPerPageChange" />
            </div>
        </template>
    </v-data-table>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { VDataTable } from 'vuetify/components/VDataTable';
import { VTextField } from 'vuetify/components/VTextField';
import { VBtn } from 'vuetify/components/VBtn';
import { VSpacer } from 'vuetify/components';
import { VPagination } from 'vuetify/components/VPagination';
import { VSelect } from 'vuetify/components/VSelect';

const props = defineProps({
    rowData: {
        type: Array,
        required: true,
        default: () => [],
    },
    columnDefs: {
        type: Array,
        required: true,
        default: () => [],
    },
    totalItems: {
        type: Number,
        required: true,
    },
    itemsPerPage: {
        type: Number,
        default: 20,
    },
    currentPage: {
        type: Number,
        default: 1,
    }
});

const emit = defineEmits(['view-details', 'page-change']);

const search = ref('');
const loading = ref(false);
const localPage = ref(props.currentPage);
const localItemsPerPage = ref(props.itemsPerPage);
const internalTotalPages = ref(1);

const headers = computed(() => {
    return props.columnDefs.map((colDef) => ({
        key: colDef.field,
        title: colDef.headerName,
        sortable: colDef.sortable !== false,
    }));
});

const finalHeaders = computed(() => {
    const baseHeaders = headers.value;
    const actionsHeader = { key: 'actions', title: 'Ações', sortable: false };
    if (!baseHeaders.some(header => header.key === 'actions')) {
        return [...baseHeaders, actionsHeader];
    }
    return baseHeaders;
});

const totalPagesDisplay = computed(() => internalTotalPages.value);

watch(() => props.rowData, () => {
    loading.value = false;
});

watch(() => props.currentPage, (newPage) => {
    localPage.value = newPage;
});

watch(() => props.itemsPerPage, (newItemsPerPage) => {
    localItemsPerPage.value = newItemsPerPage;
});

const clearSearch = () => {
    search.value = '';
};

const handleOptionsUpdate = (options) => {
    // Se a página ou os itens por página mudaram, emite eventos padronizados
    if (options.page !== localPage.value) {
        localPage.value = options.page;
        emit('page-change', options.page);
    }
    if (options.itemsPerPage !== localItemsPerPage.value) {
        localItemsPerPage.value = options.itemsPerPage;
        // Ao alterar o número de itens, resetamos para a primeira página
        localPage.value = 1;
        emit('page-change', { page: 1, itemsPerPage: options.itemsPerPage });
        internalTotalPages.value = Math.ceil(props.totalItems / options.itemsPerPage);
    }
};

const handlePageChange = (newPage) => {
    console.log("Página alterada para:", newPage);
    localPage.value = newPage;
    emit('page-change', newPage);
};

const handleItemsPerPageChange = (newItemsPerPage) => {
    localItemsPerPage.value = newItemsPerPage;
    // Reseta para a página 1 ao alterar itens por página
    localPage.value = 1;
    emit('page-change', { page: 1, itemsPerPage: newItemsPerPage });
    internalTotalPages.value = Math.ceil(props.totalItems / newItemsPerPage);
};

onMounted(() => {
    internalTotalPages.value = Math.ceil(props.totalItems / props.itemsPerPage);
});
</script>

<style scoped>
.v-data-table {
    width: 100%;
}

.v-pagination {
    margin-top: 1rem;
}
</style>
