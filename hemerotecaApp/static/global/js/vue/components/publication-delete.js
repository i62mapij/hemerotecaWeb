//component that shows the delete screen of a publication
Vue.component('publication-delete',{
    props:['publication','time'],
    data: function(){
        return {
            publications: []
        }
    },
    methods:{
        publicationDelete: function(){ 
          $("#deleteModal").modal("hide")
          this.$emit("eventPublicationDelete")
        },
        closeWindow: function () {
          $("#deleteModal").modal("hide")
        }
    },
    watch: {
        time: function(newValue, oldValue){
            $("#deleteModal").modal("show")
        }
    },
    template:
    `
    <div class="modal fade" id="deleteModal" tabindex="-1" role="dialog" aria-labelledby="modalScreen" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div v-if="publication"  class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="modalScreen">Borrar: {{ publication.title}}</h5>
          <button type="button" v-on:click="closeWindow" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          ¿Seguro que desea borrar el registro seleccionado?
        </div>
        <div class="modal-footer">
          <button type="button"  v-on:click="closeWindow" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
          <button v-on:click="publicationDelete" class="btn btn-danger" data-dismiss="modal">Borrar</button>
        </div>
      </div>
    </div>
  </div>
    
    `
});