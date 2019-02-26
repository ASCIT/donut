function convert(input) {
  var target = $("#content"),
      converter = new showdown.Converter(),
      html = converter.makeHtml(input);
  target.html(html);
}

function load() {
  url = $("#title").html();
  $.ajax({
    url: '/uploads/_send_page',
    type: 'GET',
    data:{url:url},
    success: function(data) {
    convert(data)
    }
  });
}

$(function() {
  load();
})
