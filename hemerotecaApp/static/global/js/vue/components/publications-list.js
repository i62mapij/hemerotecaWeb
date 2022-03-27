//component that displays the list of publications
Vue.component('publications-list',{
  props: {
      publication_type: '',
      publicationsearch: '',
      firstpage:'',
      notauth:''
  },
  data: function(){
      return {
          publications: [],
          publicationSelected:undefined,
          publicationIndexSelected:0,
          timeShow:0,
          timePre:0,
          timeDelete:0,
          timeUpdate:0,
          timeSave:0,
          timeTuits:0,
          clientToken: '',
          screen_name:'',
          objectPagination: undefined,
          page:1,
          error:'',
          errorDetail:'',
          timeNotes:0
      }
  },
  mounted(){
      this.callServerForPublications();
  },
  methods:{
      callServerForPublications: function(){
          //function that calls the rest api to get a token and call the publications listing function
          fetch('/api/getToken')
          .then(res => res.json())
          .then(res => {
            if(res.code == 200){
              this.clientToken=res.data.token;
              this.getPublications();
            }
            else{
              this.error = 'Error de seguridad al obtener los datos. No se pudo obtener un token para la sesión actual.'
            }
          }) 

      },
      getPublications: function(){
          //function that calls the rest api to get the list of publications that meet the filter criteria  
          let headers = new Headers()
          var formData = new FormData()
          var searchObject=JSON.parse(this.publicationsearch);
          formData.append("type", searchObject.type)
          formData.append("title", searchObject.title)
          formData.append("text", searchObject.text)
          formData.append("fromDate", searchObject.fromDate)
          formData.append("toDate", searchObject.toDate)
          formData.append("fromWebDate", searchObject.fromWebDate)
          formData.append("toWebDate", searchObject.toWebDate)
          formData.append("hasImage", searchObject.hasImage)
          formData.append("automatic", searchObject.automatic)
          formData.append("tag", searchObject.tag)

          headers.set('Authorization', 'Bearer '+this.clientToken)
          fetch('/api/publications/'+this.page, { method: 'POST', headers:headers, body: formData })
          .then(res => res.json())
          .then(res => { 
            if(res.code == 200){
             this.publications = res
             this.objectPagination= this.publications.data[this.publications.data.length-1]
             this.$delete(this.publications.data,this.publications.data.length-1)
            }
            else{
              this.error=res.msj.split('#')[0]
              if (res.msj.split('#').length>1){
                this.errorDetail=res.msj.split('#')[1]
              }
            }
          })         

      },
      callDelete(formData){
        //function that calls the rest api to delete a publication
        let headers = new Headers()
        headers.set('Authorization', 'Bearer '+this.clientToken)
        fetch('/api/publication/', {
            method: 'DELETE',
            headers:headers,
            body: formData
          }).then(res => res.json())
          .then(res => {
              if(res.code == 200){
                this.callServerForPublications();
              }else{
                this.error=res.msj.split('#')[0]
                if (res.msj.split('#').length>1){
                  this.errorDetail=res.msj.split('#')[1]
                }
                $('#errorID').show()
              }
            })          
    },
    showDetailError: function(inputindex){
      alert(this.errorDetail)
    },
    publicationDelete: function(publication,index){
        this.timeDelete = new Date().getTime()
        this.publicationSelected = publication
        this.publicationIndexSelected = index
    },
      returnBack: function(){
        window.history.back();
      },
      publicationShow: function(publication,index){
        this.publicationSelected = publication
        this.publicationIndexSelected = index
        this.timeShow = new Date().getTime()
      },
      publicationUpdate: function(publication,index){
            this.publicationSelected = publication
            this.publicationIndexSelected = index
            this.timePre = new Date().getTime()
           
        },
        eventPublicationDelete: function(){
            var formData = new FormData()
            
            formData.append("id",this.publicationSelected.id)
            this.callDelete(formData)
            
        },
        eventPublicationUpdate: function(publication){
            this.publications.data[this.publicationIndexSelected].title = publication.title
            this.publications.data[this.publicationIndexSelected].summary = publication.summary
            this.publications.data[this.publicationIndexSelected].text = publication.text
            this.publications.data[this.publicationIndexSelected].webDate = publication.webDate
            this.publications.data[this.publicationIndexSelected].notes = publication.notes
            this.publications.data[this.publicationIndexSelected].image = publication.image
            this.publications.data[this.publicationIndexSelected].type = publication.type
            this.publications.data[this.publicationIndexSelected].screen_name = publication.screen_name
            this.publications.data[this.publicationIndexSelected].id = publication.id
            this.publications.data[this.publicationIndexSelected].draft = 'N'
        },
      eventPagination: function(page){
        this.page=page
        this.callServerForPublications()
      },
      eventShowLoading: function(showLayer){
         this.timeLoading = new Date().getTime()
         this.showLayer = showLayer
      },
      showNotes: function(publication,index){
            this.publicationSelected = publication
            this.publicationIndexSelected = index
            this.timeNotes = new Date().getTime()
      },
  },
  template:
  `
      <div>
            
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
       <div align="right" v-if="this.firstpage=='N'"><button class="btn btn-success" v-on:click="returnBack">Volver</button></div>
         
           <div v-if="publications.length == 0">
              <h1>NO hay publicaciones con esos criterios</h1>
          </div>
          
          <div v-else>
            <h2 v-if="this.firstpage=='N'">Resultados de la búsqueda</h2>
            <h2 v-else>Últimas publicaciones registradas</h2>
          </div>
          <pagination  v-on:eventPagination="eventPagination" :objectpagination="this.objectPagination"></pagination>
     
          <div class="scrollPanelList">
          <div v-for="(publication, index) in publications.data" class="jumbotron pb-2 pt-3"> 
                  <h6>
                      <a :href="publication.url" target="_blank">
                      <img v-if="publication.image"  v-bind:src="publication.image"  alt="..." class="float-left" width="10%" height="10%">
                      <span>&nbsp;{{ publication.title }}</span>
                      </a>
                  </h6>
                  <h6>
                    <span>&nbsp;{{ publication.summary }}</span>
                    <span v-else>&nbsp;{{ publication.text }}</span>  
                  </h6>
                  <div align="right">
                   <h6><label>Publicada el:</label> {{ publication.webDate }}</h6>
                   <h6><label>Capturada el:</label> {{ publication.date }}</h6>
                  
                   <a v-on:click="showNotes(publication,index)" data-toggle="tooltip" data-placement="top" title="Notas" class="btn btn btn-info btn-sm" href="#"><i class="fa fa-edit"></i></a> 
                   <a v-on:click="publicationUpdate(publication,index)" data-toggle="tooltip" data-placement="top" title="Editar" class="btn btn-success btn-sm" href="#"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-receipt" viewBox="0 0 16 16">
                   <path d="M1.92.506a.5.5 0 0 1 .434.14L3 1.293l.646-.647a.5.5 0 0 1 .708 0L5 1.293l.646-.647a.5.5 0 0 1 .708 0L7 1.293l.646-.647a.5.5 0 0 1 .708 0L9 1.293l.646-.647a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .708 0l.646.647.646-.647a.5.5 0 0 1 .801.13l.5 1A.5.5 0 0 1 15 2v12a.5.5 0 0 1-.053.224l-.5 1a.5.5 0 0 1-.8.13L13 14.707l-.646.647a.5.5 0 0 1-.708 0L11 14.707l-.646.647a.5.5 0 0 1-.708 0L9 14.707l-.646.647a.5.5 0 0 1-.708 0L7 14.707l-.646.647a.5.5 0 0 1-.708 0L5 14.707l-.646.647a.5.5 0 0 1-.708 0L3 14.707l-.646.647a.5.5 0 0 1-.801-.13l-.5-1A.5.5 0 0 1 1 14V2a.5.5 0 0 1 .053-.224l.5-1a.5.5 0 0 1 .367-.27zm.217 1.338L2 2.118v11.764l.137.274.51-.51a.5.5 0 0 1 .707 0l.646.647.646-.646a.5.5 0 0 1 .708 0l.646.646.646-.646a.5.5 0 0 1 .708 0l.646.646.646-.646a.5.5 0 0 1 .708 0l.646.646.646-.646a.5.5 0 0 1 .708 0l.646.646.646-.646a.5.5 0 0 1 .708 0l.509.509.137-.274V2.118l-.137-.274-.51.51a.5.5 0 0 1-.707 0L12 1.707l-.646.647a.5.5 0 0 1-.708 0L10 1.707l-.646.647a.5.5 0 0 1-.708 0L8 1.707l-.646.647a.5.5 0 0 1-.708 0L6 1.707l-.646.647a.5.5 0 0 1-.708 0L4 1.707l-.646.647a.5.5 0 0 1-.708 0l-.509-.51z"/>
                   <path d="M3 4.5a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 1 1 0 1h-6a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5zm8-6a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5zm0 2a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 0 1h-1a.5.5 0 0 1-.5-.5z"/>
                   </svg></i></a>
                   <span v-if="notauth=='N'">
                   <button v-on:click="publicationDelete(publication,index)" :data-name="publication.title" :data-id="publication.id" class="btn btn-danger btn-sm"><i  data-toggle="tooltip"  :title="'Eliminar publicación '+publication.title" data-placement="top"class="fa fa-trash"></i></button>
                   </span>
                   </div> 
                  
                  <div v-if="publication.type=='web'"><i class="fab fa-google" title="Publicación de Google"></i></div>
                  <div v-if="publication.type=='Twitter'"><i class="fab fa-twitter" title="Publicación de Twitter"></i>{{publication.screen_name}}</div>  
                  <div v-if="publication.type=='Telegram'"><i class="fab fa-telegram" title="Publicación de Telegram"></i>{{publication.channel}}</div>  
                
                  <div align="left" v-if="publication.draft=='S'"> 
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-alarm" viewBox="0 0 16 16">
                    <title>Pendiente de guardar</title>
                     <path d="M8.5 5.5a.5.5 0 0 0-1 0v3.362l-1.429 2.38a.5.5 0 1 0 .858.515l1.5-2.5A.5.5 0 0 0 8.5 9V5.5z"/>
                     <path d="M6.5 0a.5.5 0 0 0 0 1H7v1.07a7.001 7.001 0 0 0-3.273 12.474l-.602.602a.5.5 0 0 0 .707.708l.746-.746A6.97 6.97 0 0 0 8 16a6.97 6.97 0 0 0 3.422-.892l.746.746a.5.5 0 0 0 .707-.708l-.601-.602A7.001 7.001 0 0 0 9 2.07V1h.5a.5.5 0 0 0 0-1h-3zm1.038 3.018a6.093 6.093 0 0 1 .924 0 6 6 0 1 1-.924 0zM0 3.5c0 .753.333 1.429.86 1.887A8.035 8.035 0 0 1 4.387 1.86 2.5 2.5 0 0 0 0 3.5zM13.5 1c-.753 0-1.429.333-1.887.86a8.035 8.035 0 0 1 3.527 3.527A2.5 2.5 0 0 0 13.5 1z"/>
                  </svg>
                 </div>  
              </div>
             </div>
            
              <publication-delete v-on:eventPublicationDelete="eventPublicationDelete" :time="timeDelete" :publication="publicationSelected" ></publication-delete>
              <pre-publication v-on:eventPublicationUpdate="eventPublicationUpdate" :publicationEdit="publicationSelected" :time="timePre" :publication_type=this.publication_type :notauth=this.notauth></pre-publication>
              <notes :readonly="this.notauth" v-on:eventShowLoading="eventShowLoading" :time="timeNotes" :publicationEdit="publicationSelected"></notes>
               
      </div>
  
  `
});