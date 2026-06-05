<script setup lang="ts">
    import Card from 'primevue/card';
    import Skeleton from 'primevue/skeleton';

    defineProps<{
        statCardsConfig: any;
        isLoading: boolean;
    }>();

</script>

<template>
        
    <div class="stat-row">

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
                    {{ card.value }}
                </p>
            </template>
        </Card>

        <div v-if="isLoading" class="stat-row-mask" aria-hidden="true">
            <i class="pi pi-spin pi-spinner stat-row-mask-spinner"></i>
        </div>

    </div>

</template>

<style scoped>

    .stat-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 75px;
        margin-bottom: 40px;
        height: 130px;
        width: 100%;
        position: relative;
        width: 100%;
    }
    .stat-row-tiles {
        justify-content: center;
        gap: 125px;
    }

    .stat-card {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 130px;
        text-align: center;
        background-color: #f7fafd;
    }

    .stat-title {
        font-size: 2rem;
    }

    .stat-content {
        font-size: 4rem;
    }

    .stat-row-mask {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.4);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2;
        border-radius: 6px;
    }

    .stat-row-mask-spinner {
        font-size: 1.9rem;
        font-weight: 50;
        color: #E8E8E8;
    }
</style>