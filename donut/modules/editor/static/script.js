var TITLE_CUTOFF = 16;

function run() {
  var text = document.getElementById('source').value,
      target = document.getElementById('preview'),
      converter = new showdown.Converter({strikethrough: true}),
      html = converter.makeHtml(text);

    target.innerHTML = html;
}

function change_title(){
 //var text = document.getElementById('title').value,

}

function insert_heading(size){
  var string = "";
  for(var i = 0; i< size; i++)
  {
    string += "#";
  }
  if (window.getSelection().toString() != "")
  {
    var text = document.getElementById('source').value;
    document.getElementById('source').value =
    text.slice(0, window.getSelection().selectionStart) +
    "*" + window.getSelection().toString() + "*"
    text.slice(window.getSelection().selectionEnd);
  }
  else {
    insert(string + "Heading_title" + string+ "\n");
  }
}

function insert_italic(){
  if (window.getSelection().toString() != "")
  {
    insert("*", false);
  }
  else {
    insert("*italicText*");
  }
}

function insert_bold(){
  if (window.getSelection().toString() != "")
  {
    insert("**", false);
  }
  else {
    insert("**boldText**");
  }
}

function insert_strike_through(){
  if (window.getSelection().toString() != "")
  {
    insert("~~", false);
  }
  else {
    insert("~~strikeThroughText~~", true);
  }

}

function insert_link(){
  insert("[linkTitle](example.com)");
}


function insert_image(){
  insert("![Alt text](url/to/image");
}
function insert(string, bool){
  var text = document.getElementById('source').value;
  if(!bool)
  {
    var txt2 = text.slice(0, document.getElementById('source').selectionStart)
  + string + text.slice(document.getElementById('source').selectionStart,
  document.getElementById('source').selectionEnd) + string
  + text.slice(document.getElementById('source').selectionEnd);
  }
  else {
    var txt2 = text.slice(0, document.getElementById('source').selectionStart)
  + string + text.slice(document.getElementById('source').selectionStart);
  }
  document.getElementById('source').value = txt2;
}

// Saves the page created
function save(){
  // Construct the html and get the info needed
  var text = document.getElementById('source').value;
  var target = document.getElementById('preview');
      //converter = new showdown.Converter(),
      //html = converter.makeHtml(text),
  var title = document.getElementById("text_title").value;
  //title = title.substring(38, title.length - 12);
	console.log(typeof(title));
	console.log(title);
	//console.log(html);
  // Checking for valid titles
  if (title === '')
  {
    window.alert("Enter a title for your new page!");
  }
  else {
    // Checking for valid titles; should not have
    // anything other than numbers, characters,
    // period, front slash, and spaces.
    var valid = /^[0-9a-zA-Z.\/ ]*$/.test(title);
    if (valid && title.length < TITLE_CUTOFF)
    {
      $.ajax({
            url: $SCRIPT_ROOT+'/_save',
            type: 'POST',
            data:{markdown:text, title:title}
      });
    }
    else {
      window.alert("Please enter a valid title!");
    }
  }
}

