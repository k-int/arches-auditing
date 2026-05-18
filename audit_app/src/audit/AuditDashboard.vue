<script setup lang="ts">
    import { onMounted, ref } from "vue";
    import { useGettext } from "vue3-gettext";
    import { useToast } from "primevue/usetoast";
    import DataTable, { type DataTableStateEvent } from 'primevue/datatable';
    import Column from 'primevue/column';

    import {
        fetchResourceEditLog,
    } from "@/audit/api.ts";

    import type { EditLogEntry, FetchEditLogParams } from "@/audit/types.ts";

    const isLoading = ref(true);
    const edits = ref([] as EditLogEntry[]);

    const sortField = ref<string | null>('timestamp');
    const sortOrder = ref<number | null>(-1);
    const first = ref(0);
    const rows = ref(5); 
    const totalRecords = ref(0);

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
                    sortOrder: sortOrder.value === 1 ? 'asc' : sortOrder.value === -1 ? 'desc' : null
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

        loadEditLog();
    }

</script>

<template>

    <div class="edit-log-component">
        <DataTable 
            lazy
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

            <Column field="user_username" header="User" sortable></Column>

            <Column field="edittype_label" header="Action" sortable></Column>

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