
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

