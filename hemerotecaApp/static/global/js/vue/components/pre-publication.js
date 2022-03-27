//component to present the data of the obtained publications, modify them and save them
Vue.component('pre-publication', {
  props: {
    time: Number,
    notauth:'',
    publication_type: '',
    publicationEdit: {
      type: Object,
      default: undefined
    }
  },
  data: function () {
    return {
      publications: [],
      ftitle: "",
      fsummary: "",
      ftext: "",
      furl: "",
      ftype: "",
      fid: "",
      fscreen_name: "",
      fchannel: "",
      fimage: undefined,
      fnotes: "",
      fwebDate: "",
      error:"",
      errorDetail:""
    }
  },
  mounted(){
    this.setDisabledMode()
  },
  methods: {
    setDisabledMode(){
      //disable the form
      if(this.notauth=='S'){
        $("input[type='text']").prop("disabled", true);
        $("textarea").prop("disabled", true);
      }
    },
    uploadImage(e){
      //function to load image
      const image = e.target.files[0];
      const reader = new FileReader();
      reader.readAsDataURL(image);
      reader.onload = e =>{
          this.fimage = e.target.result;
      };
    },
    publicationSave: function () {
      //function that saves the publication data in a FormData object
      //and call the save publication function
      var formData = new FormData()
      formData.append("title", this.ftitle)
      formData.append("summary", this.fsummary)
      formData.append("text", this.ftext)
      formData.append("notes", this.fnotes)
      formData.append("url", this.furl)
      formData.append("draft", "N")
      
      if(this.fid!=undefined){
       formData.append("id", this.fid)
      }
      else{
       formData.append("id", "")
      }
      formData.append("image", this.fimage)
      if(this.publication_type==undefined){
       formData.append("type", this.ftype)
      }
      else{
       formData.append("type", this.publication_type)
      }
      formData.append("type", this.publication_type)
      formData.append("screen_name", this.fscreen_name)
      formData.append("date", this.fdate)
      formData.append("webDate", this.fwebDate)
      this.error = ""
      this.publicationInsert(formData)
    },
    publicationSaveDraft: function () {
      //function that saves the publication data in a FormData object
      //and call the save draft publication function
      var formData = new FormData()
      formData.append("title", this.ftitle)
      formData.append("summary", this.fsummary)
      formData.append("text", this.ftext)
      formData.append("notes", this.fnotes)
      formData.append("url", this.furl)
      formData.append("date", this.fdate)
      formData.append("webDate", this.fwebDate)
      formData.append("type", this.publication_type)
      formData.append("image", this.fimage)
      formData.append("screen_name", this.fscreen_name)
      formData.append("channel", "")
      formData.append("draft", "S")
      this.error = ""
      this.publicationDraft(formData)
    },
    closeWindow: function () {
      $("#modalWebCatch").modal("hide")
      $("#modalPrePublication").modal("hide")
    },
    showPrePublication(formData) {
      $("#modalWebCatch").modal("hide")
      $("#modalPrePublication").modal("show")
    },
    formValidations: function () {
      if (this.publication_type!='Twitter' && (!this.ftitle || !this.fsummary || !this.ftext )) {
        this.error='Complete los campos Título, Resumen y Texto';
        return false;
      }
      
      if (this.publication_type=='Twitter' && !this.ftext) {
        this.error='Complete el campo Texto';
        return false;
      }
      
      if(this.fwebDate!=''){
       var regex = /^\d{2}\/\d{2}\/\d{4}$/
       if(regex.test(this.fwebDate)){
        this.error='';
       }
       else{
        $('#scrollDiv').scrollTop(0);
        this.error='La fecha debe tener formato DD/MM/YYYY';
        $('#errorID').show();
        return false;
       }
      } 

      if(this.fwebDate==''){
        this.error='Debe rellenar la fecha en formato DD/MM/YYYY';
        $('#errorID').show();
        return false;
      }

      return true;
    },
    publicationInsert(formData) {
      //function that calls the rest api to get a token and call the function that saves publications
      //validations
      if(!this.formValidations()){
        $('#scrollDiv').scrollTop(0);
        return false;
      }
      
      fetch('/api/getToken')
      .then(res => res.json())
      .then(res => {
        if(res.code == 200){
          this.clientToken=res.data.token;
          this.callInsert(formData)
        }
        else{
          this.error = 'Error de seguridad al obtener los datos. No se pudo obtener un token para la sesión actual.'
          $('#scrollDiv').scrollTop(0);
        }
      }) 

  },
  showDetailError: function(inputindex){
      alert(this.errorDetail)
  },
  publicationDraft(formData) {   
    //function that saves a publication as a draft
    if (this.publication_type=='Twitter') {
      res={title:formData.get("title"),date:new Date().toLocaleDateString(),summary:formData.get("summary"),text:formData.get("text"),notes:formData.get("notes"),draft:formData.get("draft"),image:formData.get("image"),type:this.publication_type,screen_name:this.fscreen_name,webDate:formData.get("webDate")}
    }
    else{
     res={title:formData.get("title"),date:new Date().toLocaleDateString(),summary:formData.get("summary"),text:formData.get("text"),notes:formData.get("notes"),draft:formData.get("draft"),image:formData.get("image"),type:this.publication_type,screen_name:'',url:formData.get("url"),webDate:formData.get("webDate")}
    }
    this.publication = res
    
    this.$emit("eventPublicationInsert", this.publication)
    $("#modalPrePublication").modal("hide")
  },
  cleanImage(){
   this.fimage=''
  },
  showError: function(res){
    this.error=res.msj.split('#')[0]
    if (res.msj.split('#').length>1){
              this.errorDetail=res.msj.split('#')[1]
    }
    $('#scrollDiv').scrollTop(0);
  },
  callInsert(formData){
    //function that calls the rest api to insert/update a publication
    let headers = new Headers()
    headers.set('Authorization', 'Bearer '+this.clientToken)

    fetch('/api/publication/', {
        method: 'PUT',
        headers:headers,
        body: formData
      }).then(res => res.json())
      .then(res => {
          if(res.code == 200){
            this.publication = res
            if (this.publicationEdit.id!=undefined && this.publicationEdit.id!=0) {
              this.$emit("eventPublicationUpdate", this.publication.data)
            }
            else{
              this.$emit("eventPublicationInsert", this.publication.data)
            }
            $("#modalPrePublication").modal("hide")

          }else{
            this.showError(res);
          }
        })          
      }
  },
  watch: {
    time: function (newValue, oldValue) {
      this.error = ""
      $("#modalPrePublication").modal("show")
      if (this.publicationEdit) {
        this.ftitle = this.publicationEdit.title
        this.furl = this.publicationEdit.url
        this.ftype = this.publicationEdit.type
        this.fsummary = this.publicationEdit.summary
        this.ftext = this.publicationEdit.text
        this.fwebDate = this.publicationEdit.webDate
        this.fscreen_name = this.publicationEdit.screen_name 
        this.fchannel = this.publicationEdit.channel 
        if(this.publicationEdit.notes!=undefined){
         this.fnotes = this.publicationEdit.notes
        }
        this.fimage = this.publicationEdit.image 
        this.fid=this.publicationEdit.id 
      } 
    }
  },
  template:
    `
  <div class="modal fade bd-example-modal-lg" id="modalPrePublication" tabindex="-1" role="dialog" aria-labelledby="prePublicationModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document" >
    <div class="modal-content">
      <div class="modal-header">
        <h5 v-if="this.publicationEdit==undefined || this.publicationEdit.id==undefined" class="modal-title" id="preCatchModalLabel">Previsualización de la captura</h5>
        <h5 v-else class="modal-title" id="preCatchModalLabel">Editar publicación</h5>  
        <button type="button" v-on:click="closeWindow" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body" id="scrollDiv">
         <div v-if="error" class="alert alert-danger fade show mt-3" id="errorID">
            {{ error }}
            <button type="button"  v-if="this.errorDetail!=''" v-on:click="showDetailError()" aria-label="Ver detalle">
            <span aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
            </svg></span>
            </button>
            <button type="button" class="close" onclick="$('#errorID').hide()" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div>
           <span>
           <label for="image">Imagen</label> 
           <img v-if="fimage" :src="fimage" alt="..." class="img-fluid" style="display:flex;" width="20%" length="20%"/>
           </span>
           <span v-if="this.notauth=='N'">
           <label>
           <input id="Image" type="file" class="form-control-image"  name="image_reference" accept="image/*" @change="uploadImage($event)">
           <svg  style="cursor:pointer" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
           <title>Cambiar imagen</title> 
           <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
           <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
          </svg>   
         </label>
         <label>
         <svg  style="cursor:pointer" v-if="this.fimage!=''" v-on:click="cleanImage(publication,index)" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
         <title>Borrar imagen</title> 
         <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
         <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
        </svg>  
        </label>
           </span>
          </div>
          <div>
           <br/>
          </div>
          <div class="form-group">
            <label for="title">Título</label> 
            <input class="form-control form-control-sm" v-model="ftitle" type="text" value="" >
          </div>   
          <div class="form-group">
           <label for="summary">Resumen</label> 
           <textarea class="form-control form-control-sm" v-model="fsummary" type="text" value="" rows="10"></textarea>
          </div>
          <div class="form-group" v-if="!this.fid">
           <label for="notes">Nota a incluir</label> 
           <textarea class="form-control form-control-sm" v-model="fnotes" type="text" value="" rows="2"></textarea>
          </div>
          <div v-if="ftype=='Twitter'" class="form-group">
          <label for="text">Cuenta de Twitter</label> 
           <input class="form-control form-control-sm" v-model="fscreen_name" type="text" value="" disabled=true>
         </div>
         <div v-if="ftype=='Telegram'" class="form-group">
         <label for="text">Canal de Telegram</label> 
          <input class="form-control form-control-sm" v-model="fchannel" type="text" value="" disabled=true>
        </div>
        <div class="form-group">
        <label for="webDate">Fecha obtenida</label> 
        <input class="form-control form-control-sm" v-model="fwebDate" type="text" value="">
       </div>
       <div class="form-group">
       <label for="text">Texto</label> 
       <textarea class="form-control form-control-sm" v-model="ftext" type="text" value="" rows="40"></textarea>
      </div>
      </div>
      <div class="modal-footer">
        <button v-on:click="closeWindow" type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
        <button v-if="this.notauth=='N'" v-on:click="publicationSave" class="btn btn-success">Grabar</button>
        <button v-if="!this.fid" v-on:click="publicationSaveDraft" class="btn btn-info">Borrador</button>
      </div>
    </div>
  </div>
</div>

    `
});