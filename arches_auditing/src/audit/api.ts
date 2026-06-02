import type {
    ActionCounts, EditLogEntry, FetchEditLogParams
} from "./types";

// import { generateArchesURL } from "@/arches/utils/generate-arches-url";

export const fetchResourceEditLog = async (
    params?: FetchEditLogParams
): Promise<{ edits: EditLogEntry[], total_count: number, action_counts: ActionCounts}> => {

    let url = "/api/audit/edit-log"
    // const url = generateArchesURL("arches_auditing:api-audit-edit-log", {
    //     resourceid: resourceId,
    // });

    if(params) {
        const activeParams: Record<string, string> = {};

        for (const [key, value] of Object.entries(params)) {
            if (value !== null && value !== undefined && value !== "") {
                activeParams[key] = String(value);
            }
        }

        const queryString = new URLSearchParams(activeParams).toString();

        if (queryString) url += `?${queryString}`;
    }

    const response = await fetch(url);
    const parsed = await response.json();

    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};