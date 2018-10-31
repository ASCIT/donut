function convert(input) {
  var target = document.getElementById('content'),
      converter = new showdown.Converter(),
      html = converter.makeHtml(input);
  target.innerHTML = html;
}

$(function() {
  $('#submit_btn').on('click', function(){
    var form_data = new FormData($('#upload-file')[0]);
    $.ajax({
      url: $SCRIPT_ROOT+'/_check_valid_file',
      type: 'POST',
      data:form_data,
  	  processData: false,
      contentType: false,
      success: function(data) {
        if(data.error === "")
        {
          $.ajax({
            url: $SCRIPT_ROOT+'/_upload_file',
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
        } else if (data.error === 'Duplicate title') {
          var res = confirm("You are replacing an existing file! If you choose to override, you may need to refresh the page");
          if (res) {
            $.ajax({
              url: $SCRIPT_ROOT+'/_upload_file',
              type: 'POST',
              data:form_data,
              processData: false,
              contentType: false,
  	      success: function(data) {
                window.location.href = data.url;
  	      },
              error: function(data) {
                window.alert("Please enter a valid title");
              }
            });
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
  })
})

function load(url) {
  $.getJSON($SCRIPT_ROOT + '/_send_page', {
    url: url
  },
  function(data) {
    convert(data.result)
  });
}
