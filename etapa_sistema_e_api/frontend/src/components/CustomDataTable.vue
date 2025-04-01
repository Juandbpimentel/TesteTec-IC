<template>
    <v-data-table :items-per-page="localItemsPerPage" :page="localPage" :items="props.rowData" :headers="finalHeaders"
        :loading="props.loading" :server-items-length="props.totalItems" @update:options="handleOptionsUpdate">
        <!-- Botão "Visualizar" nas ações, controlado pela propriedade hideActions -->
        <template #[`item.actions`]="{ item }" v-if="!props.hideActions">
            <v-btn size="small" class="mr-2" variant="outlined" @click="emit('view-details', item)">
                Visualizar
            </v-btn>
        </template>

        <template #bottom>
            <div class="pagination-container">
                <span class="mr-2 text-caption">
                    Página {{ localPage }} de {{ totalPagesDisplay }}
                </span>
                <v-pagination v-model="localPage" :length="totalPagesDisplay"
                    :total-visible="Math.min(totalPagesDisplay, 7)" :disabled="props.loading"
                    class="pagination-fixed-width" @update:model-value="handlePageChange" />
                <v-select v-model="localItemsPerPage" :items="[10, 20, 50, 100]" label="Itens por página"
                    class="items-per-page-select" dense @update:model-value="handleItemsPerPageChange" />
            </div>
        </template>
    </v-data-table>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { VDataTable } from 'vuetify/components/VDataTable';
import { VBtn } from 'vuetify/components/VBtn';
import { VPagination } from 'vuetify/components/VPagination';
import { VSelect } from 'vuetify/components/VSelect';

const props = defineProps({
    rowData: {
        type: Array,
        required: true,
        default: () => []
    },
    columnDefs: {
        type: Array,
        required: true,
        default: () => []
    },
    totalItems: {
        type: Number,
        required: true
    },
    itemsPerPage: {
        type: Number,
        default: 20
    },
    currentPage: {
        type: Number,
        default: 1
    },
    loading: {
        type: Boolean,
        default: false
    },
    hideActions: {
        type: Boolean,
        default: false // Por padrão, o botão "Visualizar" será exibido
    }
});
const emit = defineEmits(['view-details', 'page-change']);

const localPage = ref(props.currentPage);
const localItemsPerPage = ref(props.itemsPerPage);

const headers = computed(() => {
    return props.columnDefs.map((colDef) => ({
        key: colDef.field,
        title: colDef.headerName,
        sortable: false,
        align: colDef.align || 'start',
    }));
});

const finalHeaders = computed(() => {
    const baseHeaders = headers.value;
    const actionsHeader = { key: 'actions', title: 'Ações', sortable: false };
    if (!props.hideActions && !baseHeaders.some((header) => header.key === 'actions')) {
        return [...baseHeaders, actionsHeader];
    }
    return baseHeaders;
});

// Cálculo do total de páginas
const totalPagesDisplay = computed(() => {
    return Math.ceil(props.totalItems / localItemsPerPage.value) || 1;
});

watch(() => props.currentPage, (newPage) => {
    localPage.value = newPage;
});
watch(() => props.itemsPerPage, (newLimit) => {
    localItemsPerPage.value = newLimit;
});

const handleOptionsUpdate = (options) => {
    if (options.page !== localPage.value) {
        localPage.value = options.page;
        emit('page-change', options.page);
    }
    if (options.itemsPerPage !== localItemsPerPage.value) {
        localItemsPerPage.value = options.itemsPerPage;
        localPage.value = 1;
        emit('page-change', { page: 1, itemsPerPage: options.itemsPerPage });
    }
};

const handlePageChange = (newPage) => {
    localPage.value = newPage;
    emit('page-change', newPage);
};

const handleItemsPerPageChange = (newItemsPerPage) => {
    localItemsPerPage.value = newItemsPerPage;
    localPage.value = 1;
    emit('page-change', { page: 1, itemsPerPage: newItemsPerPage });
};

onMounted(() => {
    // Inicializações se necessárias
});
</script>

<style scoped>
.v-data-table {
    width: 100%;
}

.pagination-container {
    display: flex;
    justify-content: center;
    /* Alinha à direita */
    align-items: center;
    gap: 1rem;
    /* Espaçamento entre os elementos */
    margin-top: 1rem;
}

.pagination-fixed-width {
    width: 90%;
    /* Define o tamanho fixo de 90% */
}

.items-per-page-select {
    width: 20%;
    /* Define o tamanho fixo de 20% */
}
</style>