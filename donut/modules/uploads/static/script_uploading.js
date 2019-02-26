function upload(){
  var form_data = new FormData($('#upload-file')[0]);
  $.ajax({
      url: '/uploads/_check_valid_file',
      type: 'POST',
      data:form_data,
      processData: false,
      contentType: false,
      success: function(data) {
        if(data.error === "" || data.error === 'Duplicate title') {
          if (data.error === 'Duplicate title') {
            res =  confirm("You are replacing an existing file! If you choose to override, you may need to refresh the page");
          }
          else {
            res = true;
          }
          if (res) {
            $.ajax({
              url: '/uploads/_upload_file',
              type: 'POST',
              data:form_data,
              processData: false,
              contentType: false,
              success: function(data) {
                window.location.href = data.url;
               },
              error: function(data){
                window.alert("Please enter a valid title");
              }
            });
          } else {
            return false;
          } 
        } else {
          window.alert(data.error);
        }
      },
      error: function(data) {
        window.alert("Invalid file");
      }
  });
  return false;
}
                               
