// component that show the page to enter the url or Twitter user from which to capture
Vue.component('get-source', {
  props: {
    time: Number,
    timePreTweet:Number,
    publication_type: '',
    url: '',
    screen_name: ''
  },
  data: function () {
    return {
      furl: "",
      error:"",
      clientToken: '',
      type:"",
      errorDetail:''
    }
  },
  mounted: function(){
    //initialize capture type
    this.type=this.publication_type
    this.furl=""
    this.getToken()
  },
  methods: {
    formValidations:function (){
      valid=true;
      if (!this.furl) {
        if(this.type=='Twitter'){
         this.error='La cuenta de Twitter es obligatoria.';
        }
        else{
         this.error='La url es obligatoria.';
        }
        valid=false;
      }

      return valid;
    },
    catchPublication: function () {
      //function to collect the data and call catches
      //validations
      if(!this.formValidations()){
        return false;
      }

      var formData = new FormData()
      formData.append("url", this.furl)
      formData.append("type", this.publication_type)
      //if it is a capture of type Twitter it calls the function that obtains the tweets
      if(this.type=='Twitter'){   
        this.showTuitsList(formData)
      }
      else{
        //if it is a web capture, the get web elements function is called
        $("#modalWebCatch").modal("hide")  
        this.$emit("eventShowLoading", true)
        this.callCatchPublication(formData)
      }
          
      this.error = ""
      this.furl = ""
    },
    getToken: function(){
      //function that calls rest api to get a token
      fetch('/api/getToken')
      .then(res => res.json())
      .then(res => {
        if(res.code == 200){
          //obtained token
          this.clientToken=res.data.token;
        }
        else{
          this.error = 'Error de seguridad al obtener los datos. No se pudo obtener un token para la sesión actual.'
        }
      }) 

   },
   getError: function(res){
           this.error = this.error=res.msj.split('#')[0]

            if (res.msj.split('#').length>1){
              this.errorDetail=res.msj.split('#')[1]
            }
            setTimeout(()=> {this.$emit("eventShowLoading", false)},1000)
            setTimeout(()=> {$("#modalWebCatch").modal("show")},1000)
   },
   callCatchPublication: function(formData){
      //function that calls api rest to get the elements of the web page or the list of tweets
      let headers = new Headers()
      headers.set('Authorization', 'Bearer '+this.clientToken)
      fetch('/api/catchPublication', {method: 'POST', headers:headers, body: formData})
      .then(res => res.json())
      .then(res => 
        { 
          if(res.code == 200){
            //the list of tweets was obtained. 
            if(this.type=='Twitter'){
              this.showTuitsList(formData)
            }
            else{  
              //a function is called that shows the preview of the capture
              this.showPrePublication(res.data[0])
              this.$emit("eventShowLoading", false)
            }
          }else{
            this.getError(res);
          }
      }) 
    },
    closeWindow: function () {
      $("#modalWebCatch").modal("hide")
      $("#modalPrePublication").modal("hide")
    },
    showPrePublication(res) {
     
      this.$emit("eventPrePublication", res)
    },
    showTuitsList(formData) {
      $("#modalWebCatch").modal("hide")
      this.$emit("eventTuitsList", this.furl)
    },
    changeUrl:function(e){
      if(this.publication_type!='Twitter'){
       const url = e.target.value
       this.isURLValid(url);
      }
  },
  showDetailError: function(inputindex){
    alert(this.errorDetail)
  },
  isURLValid: function(inputUrl) {  
      //validate URL expression
      var regex = new RegExp("^(http[s]?:\\/\\/(www\\.)?|ftp:\\/\\/(www\\.)?|www\\.){1}([0-9A-Za-z-\\.@:%_\+~#=]+)+((\\.[a-zA-Z]{2,3})+)(/(.)*)?(\\?(.)*)?");
      if(regex.test(inputUrl)){
        this.error='';
      }
      else{
        this.error='URL no válida'
        $('#errorID').show()
      }
  }
  },
  watch: {
    time: function (newValue, oldValue) {
      $("#modalWebCatch").modal("show")
      
      this.error = ""
      this.furl = ""
      this.type=this.publication_type
    },
    timePreTweet: function (newValue, oldValue) {
      var formData = new FormData()
      formData.append("url", this.url)
      formData.append("type", this.publication_type)
      formData.append("screen_name", this.screen_name)
      this.type=''
      this.callCatchPublication(formData)
    }
  },
  template:
    `
    <div class="modal fade" id="modalWebCatch" tabindex="-1" role="dialog" aria-labelledby="webCatchModalLabel" aria-hidden="true">
  
     <div class="modal-dialog modal-lg" role="document" id="modalWebCatchDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="webCatchModalLabel">Capturar publicación desde {{this.publication_type}}</h5>
          <button type="button" v-on:click="closeWindow" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">

            <div v-if="error" class="alert alert-danger" id="errorID">
              {{ error }}
              <button v-if="errorDetail!=''" type="button" v-on:click="showDetailError()" aria-label="Ver detalle">
                <span aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                </svg></span>
              </button>
              <button  type="button" class="close" onclick="$('#errorID').hide()" aria-label="Close">
              <span aria-hidden="true">&times;</span>
             </button>
            </div>
           
            <div class="form-group">
                <label for="furl" v-if="this.publication_type=='web'">Introduzca la URL de la publicación web</label> 
                <label for="furl" v-if="this.publication_type=='Twitter'">Introduzca la cuenta de Twitter: </label> 
     
                <input v-if="this.publication_type=='Twitter'" id="urlField" class="form-control-sm" v-model="furl" type="url" @input="changeUrl($event)" @change="changeUrl($event)" value="this.furl">
                <input v-else id="urlField" class="form-control" v-model="furl" type="url" @input="changeUrl($event)" @change="changeUrl($event)" value="this.furl">
            </div>
        </div>
        <div class="modal-footer">
          <button v-on:click="closeWindow" type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
          <button v-on:click="catchPublication" class="btn btn-success">Aceptar</button>
        </div>
       
      </div>
    </div>
    
  </div>

    `
});