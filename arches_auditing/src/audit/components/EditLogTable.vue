<script setup lang="ts">

    import DataTable from 'primevue/datatable';

    import Column from 'primevue/column';
    import InputText from 'primevue/inputtext';
    import Select from 'primevue/select';
    import DatePicker from 'primevue/datepicker';
    import IconField from 'primevue/iconfield';
    import InputIcon from 'primevue/inputicon';
    import Skeleton from 'primevue/skeleton';

    import { formatTimestamp, isRowInspectable } from "../utils.ts";

    import { actionOptions } from "../constants.ts";
    import { EditLogEntry, Filters } from "../types.ts";


    defineProps<{
        isLoading: boolean;
        edits: EditLogEntry[];
        totalRecords: number;
        rows: number;
        selectedEditLogId: string | null;
        isGraphsLoading: boolean;
        graphOptions: string[];

        handleTableChange: (event: any) => void;
        handleCheckboxChange: (event: Event, rowData: EditLogEntry) => void;
        debouncedFilter: (callback: () => void) => void;
    }>();

    const filters = defineModel<Filters>('filters', { required: true });
    const firstRow = defineModel<number>('firstRow', { required: true });

    const emit = defineEmits(['update:rows', 'update:firstRow', 'page-change']);

</script>

<template>
    <div class="edit-log-table-container">

        <Skeleton v-if="isLoading"
            width="100%" 
            height="342px" 
        />
                
        <DataTable v-else
            lazy
            filterDisplay="row"
            v-model:filters="filters"
            :first="firstRow"
            responsiveLayout="scroll"
            size="large"
            striped-rows
            removableSort
            :value="edits" 
            :paginator="true" 
            :rows="rows"
            :totalRecords="totalRecords"
            @sort="handleTableChange"
            @page="handleTableChange"
            @filter="handleTableChange"
            resizableColumns
            columnResizeMode="fit"
            class="edit-log-table"
            >
            
            <Column field="resourceinstanceid" header="Resource ID" sortable filter :showFilterMenu="false">
                <template #body="slotProps">
                    <a :href="'/resource/' + slotProps.data.resourceinstanceid" target="_blank" class="resource-link">
                        {{ slotProps.data.resourceinstanceid }}
                    </a>
                </template>

                <template #filter="{ filterModel, filterCallback }">
                    <IconField iconPosition="right">
                        <InputText 
                            v-model="filterModel.value" 
                            type="text" 
                            @input="debouncedFilter(filterCallback)"
                            placeholder="Search by resource ID..." 
                            class="filter-box"
                            showClear
                        />
                        <InputIcon 
                            v-show="filterModel.value" 
                            class="pi pi-times clear-filter-icon" 
                            @click="filterModel.value = null; filterCallback();"
                        />
                    </IconField>
                </template>
            </Column>

            <Column field="resource_name" header="Resource Name" sortable filter :showFilterMenu="false">
                <template #filter="{ filterModel, filterCallback }">
                    <IconField iconPosition="right">
                        <InputText 
                            v-model="filterModel.value" 
                            type="text" 
                            @input="debouncedFilter(filterCallback)"
                            placeholder="Search Resource Name..." 
                            class="filter-box"
                        />
                        <InputIcon 
                            v-show="filterModel.value" 
                            class="pi pi-times clear-filter-icon" 
                            @click="filterModel.value = null; filterCallback();"
                        />
                    </IconField>
                </template>
            </Column>

            <Column field="graph_name" header="Graph Name" sortable filter :showFilterMenu="false">
                <template #filter="{ filterModel, filterCallback }">
                    <Select
                        v-model="filterModel.value" 
                        :options="graphOptions"
                        filter
                        placeholder="Search Graph Name..." 
                        class="filter-box"
                        @change="filterCallback()"
                        showClear
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
                        @update:modelValue="(val) => { if (filterModel) filterModel.value = val;}"
                        @date-select="filterCallback()"
                        @clear-click="() => {if (filterModel) filterModel.value = null; filterCallback();}"
                        selectionMode="range" 
                        dateFormat="yy-mm-dd"
                        placeholder="Select Date Range"
                        showClear
                        showButtonBar
                        class="filter-box"
                    />
                </template>
            </Column>

            <Column field="user_username" header="User" sortable filter :showFilterMenu="false">
                <template #filter="{ filterModel, filterCallback }">
                    <IconField iconPosition="right">
                        <InputText 
                            v-model="filterModel.value" 
                            type="text" 
                            @input="debouncedFilter(filterCallback)"
                            placeholder="Search User..." 
                            class="filter-box"
                        />
                        <InputIcon 
                            v-show="filterModel.value" 
                            class="pi pi-times clear-filter-icon" 
                            @click="filterModel.value = null; filterCallback();"
                        />
                    </IconField>
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
                    <IconField iconPosition="right">
                        <InputText 
                            v-model="filterModel.value" 
                            type="text" 
                            @input="debouncedFilter(filterCallback)"
                            placeholder="Search Card Name..." 
                            class="filter-box"
                        />
                        <InputIcon 
                            v-show="filterModel.value" 
                            class="pi pi-times clear-filter-icon" 
                            @click="filterModel.value = null; filterCallback();"
                        />
                    </IconField>
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
</template>

<style scoped>

    .edit-log-table-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
    }

    .edit-log-table {
        width: 100%;
    }

    .filter-box :deep(.p-datepicker-input) {
        font-size: 1.3rem;
    }

    .filter-box :deep(.p-select-label) {
        font-size: 1.3rem;
    }

    .filter-box {
        width: 100%;
        font-size: 1.3rem;
    }

    .table-checkbox {
        transform: scale(1.2);
    }

    .checkbox-container {
        text-align: center;
    }

    .clear-filter-icon {
        cursor: pointer;
    }

    .resource-link {
        color: #579ddb;
        transition: color 0.15s ease
    }

    .resource-link:hover {
        color: #4a85ba;
        text-decoration: underline;
    }

</style>