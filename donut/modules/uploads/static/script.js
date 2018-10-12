function convert(input) {
  var target = document.getElementById('content'),
      converter = new showdown.Converter(),
      html = converter.makeHtml(input);
  target.innerHTML = html;
}

$(function() {
  $('#submit_btn').on('click', function(){
 // var inputt = document.querySelector('form');
 // console.log(inputt);
//var formData = new FormData(inputt);
//	console.log(formData);
var form_data = new FormData($('#upload-file')[0]);
$.ajax({
    url: $SCRIPT_ROOT+'/_check_valid_file',
    type: 'POST',
    data:form_data,
	processData: false, contentType: false, 
    success: function(data) {
      console.log(data);
      if(data.error === "None")
      {
        $.ajax({
          url: $SCRIPT_ROOT+'/_upload_file',
          type: 'POST',
	data:form_data,
		processData: false, contentType: false,
	 success: function(data)
		{
			console.log(data);
			window.location.href = data.url
		}, 
          error: function(data){
            window.alert("Please enter a valid title");
          }
        });
      }
      else if (data.error === 'Duplicate title')
	    {
		    var r = confirm("You are replacing an existing file!");
			if (r == true) {
    $.ajax({
          url: $SCRIPT_ROOT+'/_upload_file',
          type: 'POST',
        data:form_data,
                processData: false, contentType: false,
	    success: function(data)
	    {
		    window.location.href = data.url
	    },
          error: function(data){
            window.alert("Please enter a valid title");
          }
        });

		}
	   }
      else
      {
        window.alert(data.error);
      }
    },
    error: function(data){
            console.log(data);
      window.alert("Invalid file");

    }
 });
return false;
  })
})

function load(url)
{
console.log(url);
$.getJSON($SCRIPT_ROOT + '/_send_page', {
  url: url
}
, function(data) {
convert(data.result)
});
}
