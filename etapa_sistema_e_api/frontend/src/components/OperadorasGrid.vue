<template>
    <v-data-table :items="props.rowData" :headers="finalHeaders" :loading="loading"
        :no-data-text="'Nenhum dado encontrado.'" :no-results-text="'Nenhum resultado encontrado.'" :search="search"
        :options="options" @update:options="options = $event">
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
    </v-data-table>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { VDataTable } from 'vuetify/components/VDataTable'
import { VTextField } from 'vuetify/components/VTextField';
import { VBtn } from 'vuetify/components/VBtn';
import { VSpacer } from 'vuetify/components';

// --- Props e Emits ---
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
});

const emit = defineEmits(['view-details']);

// --- State ---
const search = ref('');
const loading = ref(false); // Você pode usar isso para indicar carregamento de dados
const options = ref({
    page: 1,
    itemsPerPage: 20,
    sortBy: [],
    sortDesc: [],
});

// --- Computed ---

// Converte columnDefs do formato do AG Grid para o formato do Vuetify
const headers = computed(() => {
    return props.columnDefs.map((colDef) => ({
        key: colDef.field,
        title: colDef.headerName,
        sortable: colDef.sortable !== false, // Vuetify torna as colunas ordenáveis por padrão
    }));
});

// Adiciona a coluna de ações.  Inclui verificação para evitar duplicação.
const finalHeaders = computed(() => {
    const baseHeaders = headers.value;
    const actionsHeader = { key: 'actions', title: 'Ações', sortable: false };
    // Verifica se 'actions' já existe para não duplicar
    if (!baseHeaders.some(header => header.key === 'actions')) {
        return [...baseHeaders, actionsHeader];
    }
    return baseHeaders;
});


// --- Watchers ---
watch(
    () => props.rowData,
    () => {
        loading.value = false;
    }
);

// --- Methods ---
const clearSearch = () => {
    search.value = '';
};

</script>

<style scoped>
/* Você pode adicionar estilos específicos do componente aqui */
.v-data-table {
    width: 100%;
}
</style>
