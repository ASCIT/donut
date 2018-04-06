function convert(input) {
  var target = document.getElementById('content'),
      converter = new showdown.Converter(),
      html = converter.makeHtml(input);
  console.log(html);
  console.log(input);
	  console.log(target.innerHTML);
    target.innerHTML = html;
}

window.onload = convert;
