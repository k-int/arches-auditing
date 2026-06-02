<script setup lang="ts">
    import { onMounted, ref, computed } from "vue";

    import DataTable, { 
        type DataTableSortEvent, 
        type DataTablePageEvent, 
        type DataTableFilterEvent 
    } from 'primevue/datatable';

    import Column from 'primevue/column';
    import InputText from 'primevue/inputtext';
    import Select from 'primevue/select';
    import DatePicker from 'primevue/datepicker';
    import Button from 'primevue/button';
    import { FilterMatchMode } from '@primevue/core/api';

    import { formatTimestamp, debounce, isRowInspectable } from "./utils.ts";
    import {
        fetchResourceEditLog,
    } from "./api.ts";

    import { EditLogEntry, ActionCounts, Filters } from "./types.ts";
    import { actionOptions } from "./constants.ts";

    import EditLogComparison from "./components/EditLogComparison.vue";
    import StatRow from "./components/StatRow.vue";

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
                    :first="firstRow"
                    :totalRecords="totalRecords"
                    @sort="handleTableChange"
                    @page="handleTableChange"
                    @filter="handleTableChange"
                    class="edit-log-table"
                    >
                    
                    <Column field="resourceinstanceid" header="Resource ID" sortable filter :showFilterMenu="false">
                        <template #body="slotProps">
                            <a :href="'/resource/' + slotProps.data.resourceinstanceid" target="_blank" class="resource-link">
                                {{ slotProps.data.resourceinstanceid }}
                            </a>
                        </template>

                        <template #filter="{ filterModel, filterCallback }">
                            <InputText 
                            v-model="filterModel.value" 
                            type="text" 
                            @input="debouncedFilter(filterCallback)"
                            placeholder="Search by resource ID..." 
                            class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column field="resource_name" header="Resource Name" sortable filter :showFilterMenu="false">
                        <template #filter="{ filterModel, filterCallback }">
                            <InputText 
                                v-model="filterModel.value" 
                                type="text" 
                                @input="debouncedFilter(filterCallback)"
                                placeholder="Search Resource Name..." 
                                class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column field="graph_name" header="Graph Name" sortable filter :showFilterMenu="false">
                        <template #filter="{ filterModel, filterCallback }">
                            <InputText 
                                v-model="filterModel.value" 
                                type="text" 
                                @input="debouncedFilter(filterCallback)"
                                placeholder="Search Graph Name..." 
                                class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column field="timestamp" header="Date" sortable filter :showFilterMenu="false">
                        <template #body="slotProps">
                            {{ formatTimestamp(slotProps.data.timestamp) }}
                        </template>

                        <template #filter="{ filterModel, filterCallback }">
                            <DatePicker 
                                :modelValue="filterModel ? filterModel.value : null"
                                :manualInput="true"
                                @update:modelValue="(val) => { if (filterModel) filterModel.value = val; }"
                                @date-select="filterCallback()"
                                @clear="filterCallback()"
                                selectionMode="range" 
                                dateFormat="yy-mm-dd"
                                placeholder="Select Date Range"
                                showClear
                                class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column field="user_username" header="User" sortable filter :showFilterMenu="false">
                        <template #filter="{ filterModel, filterCallback }">
                            <InputText 
                                v-model="filterModel.value" 
                                type="text" 
                                @input="debouncedFilter(filterCallback)"
                                placeholder="Search User..." 
                                class="filter-box"
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
                                class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column field="card_name" header="Card Name" sortable filter :showFilterMenu="false">
                        <template #filter="{ filterModel, filterCallback }">
                            <InputText 
                                v-model="filterModel.value" 
                                type="text" 
                                @input="debouncedFilter(filterCallback)"
                                placeholder="Search Card Name..." 
                                class="filter-box"
                            />
                        </template>
                    </Column>

                    <Column header="View Change" :sortable="false" :filter="false" bodyClass="text-center">
                        <template #body="slotProps">
                            <div class="checkbox-container">
                                <input 
                                    v-if="isRowInspectable(slotProps.data)"
                                    type="checkbox"
                                    :checked="selectedEditLogId === slotProps.data.editlogid"
                                    @change="handleCheckboxChange($event, slotProps.data)"
                                    class="table-checkbox"
                                />
                            </div>
                        </template>
                    </Column>
                    
                </DataTable>
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
        width: 100vw;
        height: 100vh;
        overflow-y: scroll;
        font-size: 1.5rem;
    }

    .dashboard-container {
        width: 85%;
        padding-bottom: 100px;
        /* border: 1px solid orange; */
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
        /* border: 1px solid red; */
    }
    
    .p-datatable {
        /* border: 1px solid lightgrey; */
        width: 100%;
    }

    .checkbox-container {
        text-align: center;
    }

    .filter-box {
        width: 100%;
        font-size: 1.3rem;
    }

    .filter-box :deep(.p-datepicker-input) {
        font-size: 1.3rem;
    }

    .filter-box :deep(.p-select-label) {
        font-size: 1.3rem;
    }

    .table-checkbox {
        transform: scale(1.2);
    }

</style>