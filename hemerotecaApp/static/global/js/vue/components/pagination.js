//component to control pagination
Vue.component('pagination',{
  props: {
    objectpagination: undefined
  },
  data: function(){
      return {
      }
  },
  methods:{
    checkPage(page) {
      return page==this.objectpagination.current;
    },  
    giveMePage(page) {
      this.$emit("eventPagination", page)
    },
    giveMeNextPage() {
      this.$emit("eventPagination", this.objectpagination.current+1)
    },
    giveMePreviousPage(page) {
      this.$emit("eventPagination", this.objectpagination.current-1)
    }  
  },
  template:
  `
           <nav aria-label="Paginación">
              <ul class="pagination">
                    <li v-if="this.objectpagination.current!=1" class="page-item"><a class="page-link" href="#" v-on:click="giveMePreviousPage()">&laquo;</a></li>
             
                    <template v-for="page in this.objectpagination.pages">
                    <li class="page-item" v-if="!checkPage(page)">
                      <a class="page-link" href="#" v-on:click="giveMePage(page)">{{page}}</a>
                    </li>
                    <li class="page-item active" aria-current="page" v-else>
                      <a class="page-link" href="#" v-on:click="giveMePage(page)">{{page}} <span class="sr-only">(current)</span></a>
                    </li>
                    </template>
                   
                    <li v-if="this.objectpagination.current!=this.objectpagination.pages" class="page-item"><a class="page-link" v-on:click="giveMeNextPage()" href="#">&raquo;</a></li>
              </ul>
            </nav>
           
      </div>
  
  `
});