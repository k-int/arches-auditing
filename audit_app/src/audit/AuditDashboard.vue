<script setup lang="ts">
    import { onMounted, ref } from "vue";
    import { useGettext } from "vue3-gettext";
    import { useToast } from "primevue/usetoast";
    import DataTable, { type DataTableStateEvent } from 'primevue/datatable';
    import Column from 'primevue/column';
    import InputText from 'primevue/inputtext';
    import Select from 'primevue/select';

    import {
        fetchResourceEditLog,
    } from "@/audit/api.ts";

    import type { EditLogEntry, Filters } from "@/audit/types.ts";

    const isLoading = ref(true);
    const edits = ref([] as EditLogEntry[]);

    const sortField = ref<string | null>('timestamp');
    const sortOrder = ref<number | null>(-1);
    const first = ref(0);
    const rows = ref(5); 
    const totalRecords = ref(0);

    const filters = ref<Filters>({
        user_username: { value: null },
        edittype_label: { value: null }
    });

    const actionOptions = ref([
        { label: 'Create Resource', value: 'create' },
        { label: 'Delete Resource', value: 'delete' },
        { label: 'Delete Tile', value: 'tile delete' },
        { label: 'Create Tile', value: 'tile create' },
        { label: 'Update Tile', value: 'tile edit' },
        { label: 'Bulk Create Tile', value: 'bulk_create' },
    ]);

    const toast = useToast();
    const { $gettext } = useGettext();

    import {
        DANGER,
        DEFAULT_ERROR_TOAST_LIFE,
        DEFAULT_TOAST_LIFE,
        ERROR,
        SUCCESS,
    } from "@/audit/constants.ts";

    const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "medium",
    });

    onMounted(loadEditLog);
    
    async function loadEditLog() {

        isLoading.value = true;

        try {
            const responseData = await fetchResourceEditLog(
                {
                    offset: first.value,
                    limit: rows.value,
                    sortField: sortField.value,
                    sortOrder: sortOrder.value === 1 ? 'asc' : sortOrder.value === -1 ? 'desc' : null,
                    searchUser: filters.value.user_username.value,
                    searchAction: filters.value.edittype_label.value
                }
            );
            edits.value = responseData.edits;
            totalRecords.value = responseData.total_count;

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        } finally {
            isLoading.value = false;
        }
    }

    const formatTimestamp = (timestamp: string) => {
        return dateTimeFormatter.format(new Date(timestamp));
    }

    const onChange = (event: DataTableStateEvent) => {
        if (event.sortField === "edittype_label") {
            sortField.value = "edittype";
        }
        else {
            sortField.value = event.sortField;
        }
        
        sortOrder.value = event.sortOrder;
        first.value = event.first;
        rows.value = event.rows;

        filters.value = event.filters as Filters;

        loadEditLog();
    }

</script>

<template>

    <div class="edit-log-component">
        <DataTable 
            lazy
            filterDisplay="row"
            v-model:filters="filters"
            responsiveLayout="scroll"
            size="large"
            striped-rows
            removableSort
            :value="edits" 
            :loading="isLoading" 
            :paginator="true" 
            :rows="rows"
            :first="first"
            :totalRecords="totalRecords"
            @sort="onChange"
            @page="onChange"
            @filter="onChange"
            class="edit-log-table"
            >
            
            <Column field="resourceinstanceid" header="Resource ID" sortable>
                <template #body="slotProps">
                    <a :href="'/resource/' + slotProps.data.resourceinstanceid" target="_blank" class="resource-link">
                        {{ slotProps.data.resourceinstanceid }}
                    </a>
                </template>
            </Column>

            <Column field="resource_name" header="Resource Name" sortable></Column>

            <Column field="graph_name" header="Resource Model" sortable></Column>

            <Column field="timestamp" header="Date" sortable>
                <template #body="slotProps">
                    {{ formatTimestamp(slotProps.data.timestamp) }}
                </template>
            </Column>

            <Column field="user_username" header="User" sortable filter>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText 
                        v-model="filterModel.value" 
                        type="text" 
                        @input="filterCallback()" 
                        placeholder="Search User..." 
                        showClear
                    />
                </template>
            </Column>

            <Column field="edittype_label" header="Action" sortable filter :showFilterMenu="false">
                <template #filter="{ filterModel, filterCallback }">
                    <Select 
                        v-model="filterModel.value"
                        :options="actionOptions"
                        optionLabel="label" 
                        optionValue="value"
                        @change="filterCallback()"
                        placeholder="Select Action"
                        showClear
                    />
                </template>
            </Column>
            
            <Column field="card_name" header="Card" sortable></Column>

        </DataTable>
    </div>
</template>

<style scoped>
    .edit-log-component {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        width: 100vw;
    }
</style>