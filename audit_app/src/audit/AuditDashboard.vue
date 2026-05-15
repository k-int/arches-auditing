<script setup lang="ts">
    import { computed, inject, onMounted, ref } from "vue";
    import { useGettext } from "vue3-gettext";
    import { useToast } from "primevue/usetoast";

    import {
        fetchResourceEditLog,
    } from "@/audit/api.ts";

    import type { EditLogEntry } from "@/audit/types.ts";

    const isLoading = ref(true);
    const edits = ref([] as EditLogEntry[]);

    const toast = useToast();
    const { $gettext } = useGettext();

    import {
        DANGER,
        DEFAULT_ERROR_TOAST_LIFE,
        DEFAULT_TOAST_LIFE,
        ERROR,
        SUCCESS,
    } from "@/audit/constants.ts";

    onMounted(loadEditLog);
    
    async function loadEditLog() {
        console.log("LOAD!!!!")

        isLoading.value = true;

        try {
            const responseData = await fetchResourceEditLog();
                edits.value = responseData.edits;
            console.log("EDITS", edits)

        } catch (caughtError) {
            console.log("Unable to fetch edit history: ", caughtError)

        } finally {
            isLoading.value = false;
        }
    
        }

</script>

<template>
    <p>Hello world</p>    
</template>