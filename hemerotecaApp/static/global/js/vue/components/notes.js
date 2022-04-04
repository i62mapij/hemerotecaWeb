//component that displays the note management screen
Vue.component('notes',{
    props: {
        publicationEdit: undefined,
        time:0,
        readonly:''
    },
    data: function(){
        return {
            notes: [],
            clientToken: '',
            error:'',
            errorDetail:'',
            ftext:''
        }
    },
    methods:{
        closeWindow: function () {
          $("#modalNotes").modal("hide")
        },
        callServerForNotes: function(){
            //function that calls rest to get a token and call the getnotes function
            fetch('/api/getToken')
            .then(res => res.json())
            .then(res => {
              if(res.code == 200){
                this.clientToken=res.data.token;
                this.getNotes();
              }else{
                  this.error = 'Error de seguridad al obtener los datos. No se pudo obtener un token para la sesión actual.'
              }
            }) 

        },
        showError:function(res){
          this.error=res.msj.split('#')[0]
          if (res.msj.split('#').length>1){
              this.errorDetail=res.msj.split('#')[1]
          }
          $('#errorID').show()
        },
        callDelete(idNote){
          //function that calls the rest api to delete a note
          let headers = new Headers()
          headers.set('Authorization', 'Bearer '+this.clientToken)
          fetch('/api/notes/'+idNote+'/'+this.publicationEdit.id, {
              method: 'DELETE',
              headers:headers
            }).then(res => res.json())
            .then(res => {
                if(res.code == 200){
                  this.getNotes();
                }else{
                  this.showError(res);
                }
              })          
        },
        callAddNote(){
          //function that calls the rest api to add a note
          let headers = new Headers()
          var formData = new FormData()
          formData.append("idPublication", this.publicationEdit.id)
          formData.append("text", this.ftext)

          if(this.ftext.trim()==''){
            this.error='Introduzca un texto para la nota'
            $('#errorID').show()
            return
          }

          headers.set('Authorization', 'Bearer '+this.clientToken)
          fetch('/api/notes/', {
              method: 'PUT',
              headers:headers,
              body: formData
            }).then(res => res.json())
            .then(res => {
                if(res.code == 200){
                  this.ftext=''
                  this.getNotes();
                }else{
                  this.showError(res);
                }
              })          
        },
        getNotes: function(){
            //function that calls the rest api to get the notes
            let headers = new Headers()
            headers.set('Authorization', 'Bearer '+this.clientToken)
            fetch('/api/notes/'+this.publicationEdit.id, { headers:headers })
            .then(res => res.json())
            .then(res => {
              if(res.code == 200){
               this.notes = res
               
               this.$emit("eventShowLoading", false)
               $("#modalNotes").modal("show")
              }
              else{
                this.error=res.msj.split('#')[0]
                if (res.msj.split('#').length>1){
                 this.errorDetail=res.msj.split('#')[1]
                }
                setTimeout(()=> {this.$emit("eventShowLoading", false)},1000)
                setTimeout(()=> {$("#modalNotes").modal("show")},1000)
              }
            })
        },
        showDetailError: function(inputindex){
          alert(this.errorDetail)
        },
        noteDelete: function(index){
          if(confirm('¿Borrar la nota?')){
           idNote=this.notes.data[index].id
           this.callDelete(idNote)
          }
        },
        checkReadOnly:function(){
          let returnValue;
          
          if(this.readonly=='S'){
            returnValue=false;
          }
          else{
            returnValue=true;
          }

          return returnValue;
        }
    },
    watch: {
     time: function (newValue, oldValue) {
      this.error = ""
      this.errorDetail = ""

      $("#modalNotes").modal("show")
      this.callServerForNotes();
    }
  },
  template:
    `
    <div class="modal fade" id="modalNotes" tabindex="-1" role="dialog" aria-labelledby="modalNotesLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 v-if="this.publicationEdit!=undefined" class="modal-title" id="notesModalLabel">Notas referentes a la publicación: "{{ publicationEdit.title }}"</h5>
          
         <button type="button" v-on:click="closeWindow" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
         </button>
          </div>
            <div class="modal-body"> 
              <div v-if="error" class="alert alert-danger fade show mt-3" id="errorID">
              {{ error }}
              <button type="button" v-if="this.errorDetail!=''" v-on:click="showDetailError()" aria-label="Ver detalle">
                <span aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                </svg></span>
              </button>
              <button type="button" class="close" onclick="$('#errorID').hide()" aria-label="Cerrar">
                  <span aria-hidden="true">&times;</span>
              </button>
             
            </div>
            <div v-if="notes.data!=undefined && notes.data.length == 0">
             <h1>NO se encontraron notas</h1>
            </div>
          
           <div v-for="(note, index) in this.notes.data" class="jumbotron pb-2 pt-3 espaciadoJumbo" >
                <div>
                  <span>&nbsp;{{ note.text }}
                     <button v-if="checkReadOnly()" type="button" class="close" v-on:click="noteDelete(index)" aria-label="Borrar nota">
                       <span aria-hidden="true" title="Borrar nota">&times;</span>
                     </button>
                  </span>
                </div>
           </div>
           
        </div>
       
        <div class="modal-footer" v-if="this.readonly=='N'">
        <div class="form-group" style="width:90%;align:right!important">
        <label for="notes">Nueva nota</label> 
        <textarea class="form-control form-control-sm" v-model="ftext" type="text" value="" rows="2"></textarea>  
       </div>
       <br>
       <div v-if="this.readonly=='N'">
         <a v-on:click="callAddNote()" data-toggle="tooltip" data-placement="top" title="Añadir nota" class="btn btn-success btn-sm" href="#"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clipboard-plus" viewBox="0 0 16 16">
         <path fill-rule="evenodd" d="M8 7a.5.5 0 0 1 .5.5V9H10a.5.5 0 0 1 0 1H8.5v1.5a.5.5 0 0 1-1 0V10H6a.5.5 0 0 1 0-1h1.5V7.5A.5.5 0 0 1 8 7z"/>
         <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
         <path d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5h3zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3z"/>
         </svg></a>
        </div> 
        </div>
      </div>
    </div>
  </div>
    
    `
});
