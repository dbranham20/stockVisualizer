window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    update_graph: function(msg) {
      if(!msg){return {};}  // no data, just return
      const data = JSON.parse(msg); 
      const mapped = Object.keys(data).map(key => {
        if(key !== "TIMESTAMP") {
          return { 
            y: data[key].map(val => parseFloat(val).toFixed(2)), 
            name: key, 
            type: "scatter",
            mode: "lines",
            x: data["TIMESTAMP"], 
            hovertemplate:'$%{y}' 
          };
        }}).filter(Boolean);
      
    
      return { 
        data: mapped,
        layout: { hovermode: 'x unified'}
      }
    }
  }
});
