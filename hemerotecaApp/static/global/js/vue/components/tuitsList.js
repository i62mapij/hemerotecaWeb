//component that displays the tweet listing screen
Vue.component('tuits-list',{
    props: {
        screen_name: '',
        time:0
    },
    data: function(){
        return {
            tuits: [],
            tuitSelected:undefined,
            tuitIndexSelected:-1,
            clientToken: '',
            error:'',
            errorDetail:''
        }
    },
    methods:{
        closeWindow: function () {
          $("#modalPrePublicationTuits").modal("hide")
        },
        callServerForTuits: function(){
           //function that calls the server to get a token and call the function that gets the tweets
            fetch('/api/getToken')
            .then(res => res.json())
            .then(res => {
              if(res.code == 200){
                this.clientToken=res.data.token;
                this.getTuits();
              }else{
                  this.error = 'Error de seguridad al obtener los datos. No se pudo obtener un token para la sesión actual.'
              }
            }) 

        },
        getTuits: function(){
            //function that calls the rest api to get the list of tweets from a user
            let headers = new Headers()
     
            headers.set('Authorization', 'Bearer '+this.clientToken)
            fetch('/api/tuits/'+this.screen_name, { headers:headers })
            .then(res => res.json())
            .then(res => {
              if(res.code == 200){
               this.tuits = res
               this.$emit("eventShowLoading", false)
               $("#modalPrePublicationTuits").modal("show")
              }
              else{
                this.error=res.msj.split('#')[0]
                if (res.msj.split('#').length>1){
                 this.errorDetail=res.msj.split('#')[1]
                }
                setTimeout(()=> {this.$emit("eventShowLoading", false)},1000)
                setTimeout(()=> {$("#modalPrePublicationTuits").modal("show")},1000)
              }
            })

        },
        tuitSelection: function(){
          //function to select a tweet from which to capture publication
          const URLMatcher = /(?:(?:https?):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])/igm
          
          if(this.tuits.data.length>0 && this.tuitIndexSelected!=-1){
           if(URLMatcher.test(this.tuits.data[this.tuitIndexSelected].text)){
            $("#modalPrePublicationTuits").modal("hide")
            this.$emit("eventPrePublicationTweet", this.tuits.data[this.tuitIndexSelected])
           }
           else{
            this.error="El tuit no tiene URLs que capturar"
           }
          }else{
            this.error='No se ha seleccionado ningún tuit'
            $('#errorID').show()
          } 
        },
        selectTuit: function(inputindex){
          $($('input:radio[name=radioTuit]').get(inputindex)).attr('checked', true);
          this.tuitIndexSelected=inputindex
        },
        showDetailError: function(inputindex){
          alert(this.errorDetail)
        }
    },
    watch: {
     time: function (newValue, oldValue) {
      this.error = ""
      this.tuitIndexSelected = -1
      this.errorDetail=''
      this.tuits=[]
      $('input:radio[name=radioTuit]').attr('checked',false)
      this.$emit("eventShowLoading", true)
      this.callServerForTuits();
    }
  },
  template:
    `
    <div class="modal fade" id="modalPrePublicationTuits" tabindex="-1" role="dialog" aria-labelledby="prePublicationModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title" id="preCatchTuitsModalLabel">Seleccionar tuit del que capturar publicación</h2>
          
          <button type="button"  v-if="this.errorDetail!=''" v-on:click="closeWindow" class="close" data-dismiss="modal" aria-label="Close">
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
            <div v-if="tuits.length == 0 && this.error==''">
             <h3>NO se encontraron tuits de {{screen_name}}</h3>
            </div>
            <div v-else>
             <h5 v-if="this.error==''">Últimos tuits de @{{screen_name}}</h5>
           </div>
           <div v-for="(tuit, index) in tuits.data" class="jumbotron pb-2 pt-3 espaciadoJumbo" v-on:click="selectTuit(index)">
                <div>
                 <input class="form-check-input" type="radio" name="radioTuit" id="" v-on:click="selectTuit(index)">
                 <img v-if="tuit.image" v-bind:src="tuit.image"  alt="..."  width="10%" height="10%">
                </div>
                <div>
                  <span>&nbsp;{{ tuit.text }}</span>
                </div>
                <div align="right">  
                  <span align="right">&nbsp;{{ tuit.date }}</span>
                </div>
           </div>

        </div>
        <div class="modal-footer">
          <button v-on:click="closeWindow" type="button" class="btn btn-secondary" data-dismiss="modal">Cerrar</button>
          <button v-on:click="tuitSelection" class="btn btn-success">Seleccionar</button>
        </div>
      </div>
    </div>
    
  </div>
    
    `
});
