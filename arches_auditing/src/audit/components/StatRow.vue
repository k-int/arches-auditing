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

        <template v-if="isLoading">
            <Skeleton 
                v-for="(card, index) in statCardsConfig" 
                :key="'skeleton-' + index" 
                height="150px" 
                width="130px"
            />
        </template>

        <template v-else>
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
                        {{ card.getValue() }}
                    </p>
                </template>
            </Card>
        </template>

    </div>

</template>

<style scoped>

    .stat-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        /* border: 1px solid blue; */
        margin-top: 75px;
        margin-bottom: 40px;
        height: 130px;
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
    }

    .stat-title {
        font-size: 2rem;
    }

    .stat-content {
        font-size: 4rem;
    }
</style>