import type {
    EditLogEntry,
} from "@/audit/types";

// import { generateArchesURL } from "@/arches/utils/generate-arches-url";

export const fetchResourceEditLog = async (
    resourceId: string,
): Promise<EditLogEntry[]> => {
    const url = "/api/audit/edit-log"
    // const url = generateArchesURL("audit_app:api-audit-edit-log", {
    //     resourceid: resourceId,
    // });
    const response = await fetch(url);
    const parsed = await response.json();

    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};