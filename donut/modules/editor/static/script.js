var TITLE_CUTOFF = 16;

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

function insert_heading(size){
  var string = "";
  for(var i = 0; i< size; i++)
  {
    string += "#";
  }
  insert(string + "Heading_title" + string+ "\n");
}

function insert_italic(){
  insert("*italicText*");
}

function insert_bold(){
  insert("**boldText**");
}

function insert_strike_through(){
  insert("~~strikeThroughText~~");
}

function insert_link(){
  insert("[linkTitle](example.com)");
}

function insert_link(){
  insert("[linkTitle](example.com)");
}


function insert(string){
  var text = document.getElementById('source').value;
  var txt2 = text.slice(0, document.getElementById('source').selectionStart)
  + string + text.slice(document.getElementById('source').selectionStart);
  document.getElementById('source').value = txt2;
}

// Saves the page created
function save(){
  // Construct the html and get the info needed
  var text = document.getElementById('source').value,
      target = document.getElementById('preview'),
      //converter = new showdown.Converter(),
      //html = converter.makeHtml(text),
      title = document.getElementById('text_title').value;
	console.log(text_title);
	console.log(html);
  // Checking for valid titles
  if (title === '')
  {
    window.alert("Enter a title for your new page!");
  }
  else {
    // Checking for valid titles; should not have
    // anything other than numbers, characters,
    // period, front slash, and spaces.
    var valid = true;
    for(var i = 0; i<title.length; i++)
    {
      var c = title.charCodeAt(i);
      if ((c < 46 && c > 57)||(c < 65 && c > 90)||(c < 97 && c > 122)||c === 32)
      {
        continue;
      }
      else {
        valid = false;
      }
    }
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
