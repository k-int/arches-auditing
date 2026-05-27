export interface EditLogEntry {
    editlogid: string;
    transactionid: string | null;
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
    old_value: Record<string, any> | null;
    new_value: Record<string, any> | null;
}

export interface FetchEditLogParams {
    offset: number;
    limit: number;
    sortField: string | null;
    sortOrder: 'asc' | 'desc' | null;
    searchUser?: string | null;
}

export interface Filters {
    resourceinstanceid:  {value: string | null};
    resource_name:  {value: string | null};
    graph_name:  {value: string | null};
    user_username:  {value: string | null};
    edittype_label:  {value: string | null};
    card_name:  {value: string | null};
    timestamp: {value: Date | null};
}

export interface ActionCounts {
    "create"?: number,
    "delete"?: number,
    "tile delete"?: number,
    "tile create"?: number,
    "tile edit"?: number,
    "bulk_create"?: number
}

import type { EDIT, VIEW } from "@/audit/constants.ts";

export type DataComponentMode = typeof EDIT | typeof VIEW;
