function run() {
  var text = document.getElementById('source').value,
      target = document.getElementById('preview'),
      converter = new showdown.Converter(),
      html = converter.makeHtml(text);

    target.innerHTML = html;
}
function save(){
	
}

function change_title(){
 //var text = document.getElementById('title').value,

}
