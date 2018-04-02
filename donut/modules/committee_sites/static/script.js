

function edit_section(title, id) {
  var text = document.getElementById(id).value;
  $.ajax({
        url: '/editor',
        type: 'POST',
        data:{markdown:text, title:title}
  });
}
