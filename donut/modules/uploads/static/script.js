function run(input) {
  var target = document.getElementById('content'),
      converter = new showdown.Converter(),
      html = converter.makeHtml(input);

    target.innerHTML = html;
}
