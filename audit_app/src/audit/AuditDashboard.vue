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
    <p>Hello world</p>    

    <div class="card">
        <DataTable 
            :value="edits" 
            :loading="isLoading" responsiveLayout="scroll"
            striped-rows
            >
            
            <Column header="Resource ID">
                <template #body="slotProps">
                    <a :href="'/resource/' + slotProps.data.resourceinstanceid" target="_blank" class="resource-link">
                        {{ slotProps.data.resourceinstanceid }}
                    </a>
                </template>
            </Column>

            <Column field="resourceName" header="Resource Name"></Column>

            <Column header="Date">
                <template #body="slotProps">
                    {{ formatTimestamp(slotProps.data.timestamp) }}
                </template>
            </Column>

            <Column field="user_username" header="User"></Column>

            <Column header="Action">
                <template #body="slotProps">
                    {{ formatLabel(slotProps.data.edittype_label) }}
                </template>
            </Column>
        </DataTable>
    </div>
</template>