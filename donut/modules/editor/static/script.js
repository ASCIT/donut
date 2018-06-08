var TITLE_CUTOFF = 16;

// Creates html
function run() {
  var text = document.getElementById('source').value,
      target = document.getElementById('preview'),
      converter = new showdown.Converter({strikethrough: true}),
      html = converter.makeHtml(text);

    target.innerHTML = html;
}

// Changes the title of a file
function change_title(){
 var title = document.getElementById('title').value,
 var valid = /^[0-9a-zA-Z.\/_\- ]*$/.test(title);

 if (valid && title.length < TITLE_CUTOFF)
 {
   $.ajax({
         url: $SCRIPT_ROOT+'/_change_title',
         type: 'POST',
         data:{title:title},
  success: function(data) {
        document.getElementById("chang_title").innerHTML = "Title Change Sucessfully";
     }
   });
 }
 else {
   window.alert("Please enter a valid title!");
 }
}

//###########
// All markdown related functions
function insert_heading(size){
  var string = "";
  console.log("headings???");
  for(var i = 0; i< size; i++)
  {
    string += "#";
  }
  var ta = document.getElementById('source')
  if ((ta.value.substring(ta.selectionStart, ta.selectionEnd)) != "")
  {
    insert(string, false);
  }
  else {
    insert(string + "Heading_title" + string+ "\n", true);
  }
}

function insert_italic(){
  var ta = document.getElementById("source");
  if (ta.value.substring(ta.selectionStart, ta.selectionEnd) != "")
  {
    insert("*", false);
  }
  else {
    insert("*italicText*", true);
  }
}

function insert_bold(){
  var ta = document.getElementById("source");
  if ((ta.value.substring(ta.selectionStart, ta.selectionEnd)) != "")
  {
    insert("**", false);
  }
  else {
    insert("**boldText**", true);
  }
}

function insert_strike_through(){
  var ta = document.getElementById("source");
  if ((ta.value.substring(ta.selectionStart, ta.selectionEnd)) != "")
  {
    insert("~~", false);
  }
  else {
    insert("~~strikeThroughText~~", true);
  }

}

function insert_link(){
  insert("[linkTitle](example.com)", true);
}


function insert_image(){
  insert("![Alt text](url/to/image", true);
}

function insert_ulist(){
  insert("* ", true);
}

function insert_olist(){
  var number = 1;
  var ta = document.getElementById("source");
  while(ta.includes(number+"."))
  {
    number = number + 1;
  }
  insert(number+". ", true);
}


function insert(string, bool){
  var ta = document.getElementById('source');
  if(!bool)
  {
    var txt2 = ta.value.substring(0, ta.selectionStart)
  + string + ta.value.substring(ta.selectionStart, ta.selectionEnd) + string
  + ta.value.substring(ta.selectionEnd);
  }
  else {
    var txt2 = ta.value.substring(0, ta.selectionStart)
  + string + ta.value.substring(ta.selectionStart);
  }
  ta.value = txt2;
}

// Saves the page created
function save(){
  // Construct the html and get the info needed
  var text = document.getElementById('source').value;
  var target = document.getElementById('preview');
  var title = document.getElementById("text_title").value;

  // Checking for valid titles
  if (title === '')
  {
    window.alert("Enter a title for your new page!");
  }
  else {
    // Checking for valid titles; should not have
    // anything other than numbers, characters, underscore,
    // period, front slash, hyphen, and spaces.
    var valid = /^[0-9a-zA-Z.\/_\- ]*$/.test(title);

    if (valid && title.length < TITLE_CUTOFF)
    {
      $.ajax({
            url: $SCRIPT_ROOT+'/_save',
            type: 'POST',
            data:{markdown:text, title:title},
	    success: function(data) {
            window.location.href = data['url']
        }
      });
    }
    else {
      window.alert("Please enter a valid title!");
    }
  }
}
