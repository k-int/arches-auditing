<script setup lang="ts">
    import { onMounted, ref, computed } from "vue";

    import { 
        type DataTableSortEvent, 
        type DataTablePageEvent, 
        type DataTableFilterEvent 
    } from 'primevue/datatable';

    import Button from 'primevue/button';
    import { FilterMatchMode } from '@primevue/core/api';

    import { debounce } from "./utils.ts";
    import {
        fetchResourceEditLog,
    } from "./api.ts";

    import { EditLogEntry, ActionCounts, Filters } from "./types.ts";

    import EditLogComparison from "./components/EditLogComparison.vue";
    import StatRow from "./components/StatRow.vue";
    import EditLogTable from "./components/EditLogTable.vue";

    const isLoading = ref(true);

    const edits = ref<EditLogEntry[]>([])
    const actionCounts = ref<ActionCounts>({});
    const totalRecords = ref(0);

    const sortField = ref<string | null>('timestamp');
    const sortOrder = ref<number | null>(-1);
    const firstRow = ref(0);
    const rows = ref(5); 

    const selectedEditLogId = ref<string | null>(null);
    const selectedEditLogOldValue = ref<string | null>(null);
    const selectedEditLogNewValue = ref<string | null>(null);

    const filters = ref<Filters>({
        resourceinstanceid: {value: null, matchMode: FilterMatchMode.CONTAINS},
        resource_name: {value: null, matchMode: FilterMatchMode.CONTAINS},
        graph_name: {value: null, matchMode: FilterMatchMode.CONTAINS},
        user_username: { value: null, matchMode: FilterMatchMode.CONTAINS},
        edittype_label: { value: null, matchMode: FilterMatchMode.CONTAINS},
        card_name: { value: null, matchMode: FilterMatchMode.CONTAINS},
        timestamp: { value: null, matchMode: FilterMatchMode.CONTAINS}
    });

    const statCardsConfig = computed(() => [
        {
            title: "Total Actions",
            value: totalRecords.value ?? 0
        },
        {
            title: "Resources Created",
            value: actionCounts.value?.create ?? 0
        },
        {
            title: "Resources Deleted",
            value: actionCounts.value?.delete ?? 0
        },
        {
            title: "Resources Edited",
            value: (
                (actionCounts.value?.["tile edit"] ?? 0) + 
                (actionCounts.value?.["tile create"] ?? 0) + 
                (actionCounts.value?.["tile delete"] ?? 0)
            )
        },
        {
            title: "Tiles Created",
            value: actionCounts.value?.["tile create"] ?? 0
        },
        {
            title: "Tiles Deleted",
            value: actionCounts.value?.["tile delete"] ?? 0
        },
        {
            title: "Tiles Edited",
            value: actionCounts.value?.["tile edit"] ?? 0
        },
    ]);

    const debouncedFilter = debounce((callback: () => void) => {
        callback();
    }, 800);

    onMounted(loadEditLog);
    
    async function loadEditLog() {

        isLoading.value = true;

        try {
            const [responseData] = await Promise.all([
                fetchResourceEditLog({
                    export: false,
                    offset: firstRow.value,
                    limit: rows.value,
                    sortField: sortField.value,
                    sortOrder: sortOrder.value === 1 ? 'asc' : sortOrder.value === -1 ? 'desc' : null,
                    userFilter: filters.value.user_username.value,
                    actionFilter: filters.value.edittype_label.value,
                    resourceidFilter: filters.value.resourceinstanceid.value,
                    resourceNameFilter: filters.value.resource_name.value,
                    graphNameFilter: filters.value.graph_name.value,
                    cardNameFilter: filters.value.card_name.value
                }),
                new Promise(resolve => setTimeout(resolve, 600))
            ]);

            edits.value = responseData.edits;
            totalRecords.value = responseData.total_count;
            actionCounts.value = responseData.action_counts;

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        } finally {
            isLoading.value = false;
        }
    }

    const handleTableChange = (event: DataTableSortEvent | DataTablePageEvent | DataTableFilterEvent) => {
        if (event.sortField === "edittype_label") {
            sortField.value = "edittype";
        }
        else {
            sortField.value = event.sortField ? String(event.sortField) : null;
        }
        
        sortOrder.value = event.sortOrder ?? -1;
        firstRow.value = event.first ?? 0;
        rows.value = event.rows ?? 5;

        filters.value = event.filters as any;

        selectedEditLogId.value = null;
        selectedEditLogOldValue.value = null;
        selectedEditLogNewValue.value = null;

        loadEditLog();
    }

    const handleCheckboxChange = (event: Event, rowData: EditLogEntry) => {
        const isChecked = (event.target as HTMLInputElement).checked;

        if (isChecked) {
            selectedEditLogId.value = rowData.editlogid;
            selectedEditLogOldValue.value = JSON.stringify(rowData.old_value, null, 2);
            selectedEditLogNewValue.value = JSON.stringify(rowData.new_value, null, 2);
        } else {
            if (selectedEditLogId.value === rowData.editlogid) {
                selectedEditLogId.value = null;
                selectedEditLogOldValue.value = null;
                selectedEditLogNewValue.value = null;
            }
        }
    };

    const handleExport = async () => {

        try {
            const params = new URLSearchParams({
                export: 'true',
                sortField: sortField.value || 'timestamp',
                sortOrder: sortOrder.value === 1 ? 'asc' : 'desc',
                userFilter: filters.value.user_username.value || '',
                actionFilter: filters.value.edittype_label.value || '',
                resourceidFilter: filters.value.resourceinstanceid.value || '',
                resourceNameFilter: filters.value.resource_name.value || '',
                graphNameFilter: filters.value.graph_name.value || '',
                cardNameFilter: filters.value.card_name.value || ''
            });

            const response = await fetch(`/api/audit/edit-log?${params.toString()}`, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) throw new Error("Export download request failed.");

            const csvBlob = await response.blob();
            const blobUrl = window.URL.createObjectURL(csvBlob);

            const downloadLink = document.createElement('a');
            downloadLink.href = blobUrl;
            downloadLink.setAttribute('download', `audit_log_export_${new Date().toISOString().split('T')[0]}.csv`);
            downloadLink.style.display = 'none';
            
            document.body.appendChild(downloadLink);
            downloadLink.click();
            
            document.body.removeChild(downloadLink);
            window.URL.revokeObjectURL(blobUrl);

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        }

    }

</script>

<template>
    <div class="audit-app-page">

        <div class="dashboard-container">

            <StatRow
                :is-loading="isLoading"
                :stat-cards-config="statCardsConfig"
            />

            <div class="edit-log-table-container">
                <EditLogTable
                    :is-loading="isLoading"
                    :edits="edits"
                    :total-records="totalRecords"
                    :rows="rows"
                    :selected-edit-log-id="selectedEditLogId"
                    :handle-table-change="handleTableChange"
                    :handle-checkbox-change="handleCheckboxChange"
                    :debounced-filter="debouncedFilter"
                    v-model:filters="filters"
                    v-model:firstRow="firstRow"
                />
            </div>

            <div class="table-actions-bar">
                <Button 
                    raised
                    size="large"
                    severity="secondary"
                    class="export-csv-btn"
                    @click=handleExport
                    >
                    <span>Export to CSV</span>
                    <i class="pi pi-download" style="font-size: 2rem"></i>
                </Button>
            </div>

            <EditLogComparison  v-if="selectedEditLogOldValue || selectedEditLogNewValue"
                :old-value="selectedEditLogOldValue"
                :new-value="selectedEditLogNewValue"
            />

        </div>
    </div>
</template>

<style scoped>

    @import 'primeicons/primeicons.css';

    .audit-app-page {
        background-color: white;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        flex-direction: column;
        height: 100vh;
        overflow-y: auto;
        font-size: 1.5rem;
        box-sizing: border-box;
        margin: 0px;
        width: calc(100vw - 3%);
    }

    .dashboard-container {
        width: 85%;
        padding-bottom: 100px;
    }

    .table-actions-bar{
        display: flex;
        justify-content: end;
        margin-bottom: 15px;
    }

    .export-csv-btn {
        padding: 12px 24px;
        font-size: 1.6rem;
        margin-top: 20px;
    }

    .edit-log-table-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }

</style>