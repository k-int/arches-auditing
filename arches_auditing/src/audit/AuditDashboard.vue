<script setup lang="ts">
    import { onMounted, ref } from "vue";
    import DataTable, { type DataTableStateEvent } from 'primevue/datatable';
    import Column from 'primevue/column';
    import Card from 'primevue/card';
    import InputText from 'primevue/inputtext';
    import Select from 'primevue/select';
    import DatePicker from 'primevue/datepicker';
    import Skeleton from 'primevue/skeleton';
    import Panel from 'primevue/panel';
    import Button from 'primevue/button';
    import 'primeicons/primeicons.css';

    import {
        fetchResourceEditLog,
    } from "@/audit/api.ts";

    import { EditLogEntry, ActionCounts, Filters } from "@/audit/types.ts";

    const isLoading = ref(true);
    const edits = ref([] as EditLogEntry[]);

    const sortField = ref<string | null>('timestamp');
    const sortOrder = ref<number | null>(-1);
    const first = ref(0);
    const rows = ref(5); 
    const totalRecords = ref(0);
    const actionCounts = ref({} as ActionCounts);

    const selectedEditLogId = ref<string | null>(null);
    const selectedEditLogOldValue = ref(null as Record<string, any> | null);
    const selectedEditLogNewValue = ref(null as Record<string, any> | null);

    const filters = ref<Filters>({
        resourceinstanceid: {value: null},
        resource_name: {value: null},
        graph_name: {value: null},
        user_username: { value: null },
        edittype_label: { value: null },
        card_name: { value: null },
        timestamp: { value: null }
    });

    const actionOptions = ref([
        { label: 'Create Resource', value: 'create' },
        { label: 'Delete Resource', value: 'delete' },
        { label: 'Delete Tile', value: 'tile delete' },
        { label: 'Create Tile', value: 'tile create' },
        { label: 'Update Tile', value: 'tile edit' },
        { label: 'Bulk Create Tile', value: 'bulk_create' },
    ]);

    const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "medium",
    });

    const tileChangeEdits = ['Tile Deleted', 'Tile Created', 'Tile Updated'];

    const isRowInspectable = (rowData: EditLogEntry) => {
        return tileChangeEdits.includes(rowData.edittype_label);
    };

    const statCardsConfig = ref([
        {
            title: "Total Actions",
            getValue: () => totalRecords.value ?? 0
        },
        {
            title: "Resources Created",
            getValue: () => actionCounts.value?.create ?? 0
        },
        {
            title: "Resources Deleted",
            getValue: () => actionCounts.value?.delete ?? 0
        },
        {
            title: "Resources Edited",
            getValue: () => (
                (actionCounts.value?.["tile edit"] ?? 0) + 
                (actionCounts.value?.["tile create"] ?? 0) + 
                (actionCounts.value?.["tile delete"] ?? 0)
            )
        },
        {
            title: "Tiles Created",
            getValue: () => actionCounts.value?.["tile create"] ?? 0
        },
        {
            title: "Tiles Deleted",
            getValue: () => actionCounts.value?.["tile delete"] ?? 0
        },
        {
            title: "Tiles Edited",
            getValue: () => actionCounts.value?.["tile edit"] ?? 0
        },
    ])

    onMounted(loadEditLog);
    
    async function loadEditLog() {

        isLoading.value = true;

        try {
            const [responseData] = await Promise.all([
                fetchResourceEditLog({
                    offset: first.value,
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

            if (!responseData.ok) throw new Error("Edit log data retrieval failed.");

            edits.value = responseData.edits;
            totalRecords.value = responseData.total_count;
            actionCounts.value = responseData.action_counts;

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        } finally {
            isLoading.value = false;
        }
    }

    const debounce = (fn: Function, delay: number) => {
        let timeoutId: any;
        
        return (...args: any[]) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn(...args), delay);
        };
    }

    const debouncedFilter = debounce((callback: () => void) => {
        callback();
    }, 800);

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

        filters.value = event.filters;

        selectedEditLogId.value = null;
        selectedEditLogOldValue.value = null;
        selectedEditLogNewValue.value = null;

        loadEditLog();
    }

    const handleCheckboxChange = (event: Event, rowData: EditLogEntry) => {
        const isChecked = (event.target as HTMLInputElement).checked;

        if (isChecked) {
            selectedEditLogId.value = rowData.editlogid;
            selectedEditLogOldValue.value = rowData.old_value;
            selectedEditLogNewValue.value = rowData.new_value;
        } else {
            if (selectedEditLogId.value === rowData.editlogid) {
                selectedEditLogId.value = null;
                selectedEditLogOldValue.value = null;
                selectedEditLogNewValue.value = null;
            }
        }
    };

</script>

<template>
    <div class="audit-app-page">

        <div class="dashboard-container">

            <div class="stat-row">
                
                <template v-if="isLoading">
                    <Skeleton 
                        v-for="(card, index) in statCardsConfig" 
                        :key="'skeleton-' + index" 
                        height="150px" 
                        width="200px"
                    />
                </template>

                <template v-else>
                    <Card 
                        v-for="(card, index) in statCardsConfig" 
                        :key="'card-' + index" 
                        class="stat-card"
                    >
                        <template #title>
                            <span class="stat-title">{{ card.title }}</span>
                        </template>
                        <template #content>
                            <p class="stat-content">
                                {{ card.getValue() }}
                            </p>
                        </template>
                    </Card>
                </template>

            </div>

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
                    :first="first"
                    :totalRecords="totalRecords"
                    @sort="onChange"
                    @page="onChange"
                    @filter="onChange"
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
                    >
                    <span>Export to CSV</span>
                    <i class="pi pi-download" style="font-size: 2rem"></i>
                </Button>
            </div>

            <template v-if="selectedEditLogOldValue || selectedEditLogNewValue">
                <div class="json-value-row">
                    <Panel header="Old Value" class="json-value-container">
                        <pre v-if="selectedEditLogOldValue && Object.keys(selectedEditLogOldValue).length > 0">{{ JSON.stringify(selectedEditLogOldValue, null, 2) }}</pre>
                        <p v-else>No previous value</p>
                    </Panel>

                    <Panel header="New Value" class="json-value-container">
                        <pre v-if="selectedEditLogNewValue">{{ JSON.stringify(selectedEditLogNewValue, null, 2) }}</pre>
                        <p v-else>No new value</p>
                    </Panel>
                </div>
            </template>

        </div>
    </div>
</template>

<style scoped>

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
    
    .stat-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        /* border: 1px solid blue; */
        margin-top: 75px;
        margin-bottom: 40px;
        height: 130px;
        width: 100%;
    }
    
    .stat-row-tiles {
        justify-content: center;
        gap: 125px;
    }

    .stat-card {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 130px;
        /* border: 1px solid purple; */
        text-align: center;
    }

    .stat-title {
        font-size: 2rem;
    }

    .stat-content {
        font-size: 4rem;
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

    .json-value-row{
        display: flex;
        justify-content: space-between;
        /* border: 1px solid pink; */
        margin-top: 75px;
    }

    .json-value-container {
        /* border: 1px solid green; */
        height: 450px;
        width: 48%;
        overflow: auto;
    }

    .json-value-container :deep(.p-panel-title) {
        font-size: 2rem;
    }

    .table-checkbox {
        transform: scale(1.2);
    }

    pre {
        background-color: #f8fafc; 
    }

</style>