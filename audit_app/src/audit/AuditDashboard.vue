<script setup lang="ts">
    import { computed, inject, onMounted, ref } from "vue";
    import { useGettext } from "vue3-gettext";
    import { useToast } from "primevue/usetoast";
    import DataTable from 'primevue/datatable';
    import Column from 'primevue/column';

    import {
        fetchResourceEditLog,
    } from "@/audit/api.ts";

    import type { EditLogEntry } from "@/audit/types.ts";

    const isLoading = ref(true);
    const edits = ref([] as EditLogEntry[]);

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
        console.log("LOAD!!!!")

        isLoading.value = true;

        try {
            const responseData = await fetchResourceEditLog();
                edits.value = responseData.edits;
            console.log("EDITS", edits)

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        } finally {
            isLoading.value = false;
        }
    
    }

    const formatLabel = (label: any) => {
        return $gettext(label._proxy____args[0]);
    };

    const formatTimestamp = (timestamp: string) => {
        return dateTimeFormatter.format(new Date(timestamp));
    }

</script>

<template>

    <div class="edit-log-component">
        <DataTable 
            responsiveLayout="scroll"
            size="large"
            striped-rows
            removableSort
            :value="edits" 
            :loading="isLoading" 
            :paginator="true" 
            :rows="5"
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

            <Column field="edittype_label" header="Action" sortable>
                <template #body="slotProps">
                    {{ formatLabel(slotProps.data.edittype_label) }}
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