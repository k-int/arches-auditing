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
}

export interface FetchEditLogParams {
    offset: number;
    limit: number;
    sortField: string | null;
    sortOrder: 'asc' | 'desc' | null;
}

import type { EDIT, VIEW } from "@/audit/constants.ts";

export type DataComponentMode = typeof EDIT | typeof VIEW;
