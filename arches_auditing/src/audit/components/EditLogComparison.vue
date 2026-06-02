<script setup lang="ts">
import Panel from 'primevue/panel';

defineProps<{
    oldValue: string | null;
    newValue: string | null;
}>();

</script>

<template>
    <div class="json-value-row">
        <Panel header="Old Value" class="json-value-container">
            <pre v-if="oldValue && oldValue !== '{}'">{{ oldValue }}</pre>
            <p v-else>No previous value</p>
        </Panel>

        <Panel header="New Value" class="json-value-container">
            <pre v-if="newValue && newValue !== 'null'">{{ newValue }}</pre>
            <p v-else>No new value</p>
        </Panel>
    </div>
</template>

<style scoped>
    .json-value-row{
        display: flex;
        justify-content: space-between;
        margin-top: 75px;
    }

    .json-value-container {
        height: 450px;
        width: 48%;
        overflow: auto;
    }

    .json-value-container :deep(.p-panel-title) {
        font-size: 2rem;
    }

    pre {
        background-color: #f8fafc; 
    }
</style>