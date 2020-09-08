var app = new Vue({
  el: '#URI_generator',
  data: {
    URI: 'your uri model',
    key_class: "primary_key",
    Details: false,
    segments: [],
    resource_type: "plot",
    supl_data: {
      "year": ['event', 'annotation', 'plant', 'plot', 'pot', 'leaf', 'ear', 'sensor', 'vector', 'actuator', 'data', 'image'],
      "project":['plant', 'plot', 'pot', 'leaf', 'ear', 'project'],
      "relative_plant":['leaf', 'ear'] 
    }
  },
  delimiters: ['[[',']]'],
  methods:{
    GetCellValues: function() {
        var self=this
        var table = document.getElementById('mytable');
        for (var r = 1, n = table.rows.length; r < n; r++) {
            self.segments.push(table.rows[r].cells[1].innerHTML)
        }
      },
      toggleDetails: function(){
        var self = this;
        self.Details= !self.Details
        return(self.Details)
      }  
    },
  computed: {
    fill_URI: function(){
      var self=this;
      self.URI = "hostname:"+self.segments.join("/");
      return(self.URI)
    }
    
  }
})