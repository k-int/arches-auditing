import ko from 'knockout';
import createVueApplication from 'arches/arches/app/media/js/utils/create-vue-application'
import AuditTemplate from 'templates/views/components/plugins/audit.htm'
import AuditDashboard from '@/audit/AuditDashboard.vue';

export default ko.components.register('audit', {
    viewModel: function(){
        createVueApplication(AuditDashboard)
        .then(vueApp => {
            vueApp.mount('#audit-container')
        })
        .catch(err => {
            console.error('Vue integration failed:', err);
        });
    },
    template: AuditTemplate
});