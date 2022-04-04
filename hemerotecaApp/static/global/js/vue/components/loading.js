//wait layer component
Vue.component('loading',{
    props: {
        showLayer:false,
        time:0
    },
    data: function(){
        return {      
        }
    },
    mounted(){
        $('#loadingID').hide()
    },
    methods:{
    },
    watch: {
        time: function (newValue, oldValue) {
        if(!this.showLayer){
          setTimeout(()=> {$("#modalWait").modal("hide")},1000)
        }
        else{
            $("#modalWait").modal("show")
        }
     }
    },
    template:
    `
    <div class="modal fade" id="modalWait" tabindex="-1" role="dialog" aria-labelledby="waitModalLabel" aria-hidden="true">
  
    <div class="modal-dialog modal-lg" role="document" id="modalWaitDialog">
     <div class="modal-content">
       <div class="modal-header">
         <h5 class="modal-title" id="webCatchModalLabel">Espere por favor</h5>
       </div>
       <div class="modal-body">

       <div class="d-flex justify-content-center">
       <div class="spinner-border" role="status">
         <span class="visually-hidden"></span>
       </div>
     </div>
          
       </div>
       <div class="modal-footer">
       </div>
     </div>
   </div>
 </div>
  
    `
});