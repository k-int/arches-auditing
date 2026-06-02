import { tileChangeEdits } from "./constants.ts";
import { EditLogEntry } from "./types.ts";

const dateTimeFormatter = new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
});

export const formatTimestamp = (timestamp: string): string => {
    if (!timestamp) return "";
    return dateTimeFormatter.format(new Date(timestamp));
};


export const debounce = (fn: Function, delay: number) => {
    let timeoutId: any;
    
    return (...args: any[]) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

export const isRowInspectable = (rowData: EditLogEntry): boolean => {
    return tileChangeEdits.includes(rowData.edittype_label);
};