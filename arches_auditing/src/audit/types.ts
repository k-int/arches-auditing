export interface EditLogEntry {
    editlogid: string;
    transactionid: string;
    edittype: string;
    edittype_label: string;
    timestamp: string;
    userid: string;
    user_firstname: string;
    user_lastname: string;
    user_username: string;
    user_email: string;
    nodegroupid: string | null;
    tileinstanceid: string | null;
    card_name: string | null;
    note: string | null;
    old_value: string | null;
    new_value: string | null;
}

export interface FetchEditLogParams {
    export: boolean;
    offset: number;
    limit: number;
    sortField: string | null;
    sortOrder: 'asc' | 'desc' | null;
    searchUser?: string | null;
    userFilter?: string | null;
    actionFilter?: string | null;
    resourceidFilter?: string | null;
    resourceNameFilter?: string | null;
    graphNameFilter?: string | null;
    cardNameFilter?: string | null;
    dateTimeFromFilter?: string | null;
    dateTimeToFilter?: string | null;
}

import type { DataTableFilterMetaData } from 'primevue/datatable';

export interface Filters {
    resourceinstanceid: { value: string | null; matchMode: string };
    resource_name:      { value: string | null; matchMode: string };
    graph_name:         { value: string | null; matchMode: string };
    user_username:      { value: string | null; matchMode: string };
    edittype_label:     { value: string | null; matchMode: string };
    card_name:          { value: string | null; matchMode: string };
    timestamp:          { value: Date[] | null;   matchMode: string };
    [key: string]: DataTableFilterMetaData | any;
}

export interface ActionCounts {
    "create"?: number,
    "delete"?: number,
    "tile delete"?: number,
    "tile create"?: number,
    "tile edit"?: number,
    "bulk_create"?: number
}
