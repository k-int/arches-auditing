import type {
    EditLogEntry, FetchEditLogParams
} from "@/audit/types";

// import { generateArchesURL } from "@/arches/utils/generate-arches-url";

export const fetchResourceEditLog = async (
    params?: FetchEditLogParams
): Promise<{ edits: EditLogEntry[], total_count: number}> => {

    let url = "/api/audit/edit-log"
    // const url = generateArchesURL("audit_app:api-audit-edit-log", {
    //     resourceid: resourceId,
    // });

    if(params) {
        const activeParams = {} as Partial<FetchEditLogParams>;

        for (const [key, value] of Object.entries(params)) {
            if (value !== null && value !== undefined && value !== "") {
                activeParams[key] = value;
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