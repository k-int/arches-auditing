<script setup lang="ts">
    import { onMounted, ref } from "vue";
    import DataTable, { type DataTableStateEvent } from 'primevue/datatable';
    import Column from 'primevue/column';
    import Card from 'primevue/card';
    import InputText from 'primevue/inputtext';
    import Select from 'primevue/select';
    import DatePicker from 'primevue/datepicker';
    import Skeleton from 'primevue/skeleton';

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
        }
    ]);

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
                    userFilter: filters.value.user_username.value,
                    actionFilter: filters.value.edittype_label.value,
                    resourceidFilter: filters.value.resourceinstanceid.value,
                    resourceNameFilter: filters.value.resource_name.value,
                    graphNameFilter: filters.value.graph_name.value,
                    cardNameFilter: filters.value.card_name.value
                }
            );
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

        loadEditLog();
    }

</script>

<template>
    <div class="edit-log-page">

        <div class="dashboard-container">

            <div class = "edit-log-stats-row">
                
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

            <template v-if="isLoading">
                <Skeleton class="edit-log-table-skeleton" height="325px";></Skeleton>
            </template>

            <div v-else class="edit-log-table-container">
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
                                @update:modelValue="(val) => { if (filterModel) filterModel.value = val; }"
                                @date-select="filterCallback()"
                                @clear="filterCallback()"
                                selectionMode="range" :manualInput="false"  dateFormat="yy-mm-dd"
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
                    
                </DataTable>
            </div>

        </div>
    </div>
</template>

<style scoped>

    .dashboard-container {
        width: 80%;
        /* border: 1px solid orange; */
    }

    .edit-log-page {
        background-color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        min-height: 100vh;
        width: 100vw;
    }

    .edit-log-stats-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        /* border: 1px solid blue; */
        height: 150px;
        margin-bottom: 150px;
    }

    .edit-log-table-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;
        /* border: 1px solid red; */
    }
    
    .p-datatable {
        border: 1px solid lightgrey;
        width: 100%;
    }

    .filter-box {
        width: 100%;
    }

    .stat-card {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 200px;
        /* border: 1px solid purple; */
        text-align: center;
    }

    .stat-title {
        font-size: 2rem;
    }

    .stat-content {
        font-size: 4rem;
    }
</style>