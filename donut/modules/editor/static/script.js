var TITLE_CUTOFF = 20;

// Creates html
function run() {
  var text = document.getElementById('source').value,
      title = document.getElementById('text_title').value,
      target = document.getElementById('preview'),
      target_title = document.getElementById('preview_title'),
      converter = new showdown.Converter({strikethrough: true}),
      html = converter.makeHtml(text);
  target.innerHTML = html;
  target_title.innerHTML = title;

}

// Changes the title of a file
function change_title(oldTitle){
  var title = document.getElementById('text_title').value;
  var input_text = document.getElementById('source').value;
  $.ajax({
    url: $SCRIPT_ROOT+'/_change_title',
    type: 'POST',
    data:{title:title, old_title:oldTitle, input_text:input_text},
    success: function(data) {
      window.alert("Title Change Sucessfully");
    },
    error: function(data) {
      window.alert("Please enter a valid title!");
    }
  });
}

//###########

function selectedString(string1, string2)
{
  var ta = document.getElementById('source');
  if (ta.value.substring(ta.selectionStart, ta.selectionEnd) == "")
  {
    insert(string2, false);
  }
  else {
    insert(string1, true);
  }
}

// All markdown related functions
function insert_heading(size){
  var string = "";
  for(var i = 0; i < size; i++)
  {
    string += "#";
  }
  selectedString(string, string + "Heading_title" + string+ "\n");
}

function insert_italic(){
  selectedString("*", "*italicText*");
}

function insert_bold(){
  selectedString("**", "**boldText**");
}

function insert_link(){
  insert("[linkTitle](example.com)", false);
}

function insert_image(){
  insert("![Alt text](url/to/image)", false);
}

function insert_ulist(){
  insert("* list \n", false);
}

function insert_olist(){
  insert("1. list \n", false);
}


function insert(string, selected){
  var ta = document.getElementById('source');
  var begin = ta.selectionStart;
  var end = ta.selectionEnd;
  if(selected)
  {
    if (document.queryCommandSupported('insertText')) {
      ta.setSelectionRange(begin, begin);
      ta.focus();
      document.execCommand('insertText', false, string);
      ta.setSelectionRange(end+string.length, end+string.length);
      ta.focus();
      document.execCommand('insertText', false, string);
    } else{
      ta.value = ta.value.substring(0, ta.selectionStart)
      + string + ta.value.substring(ta.selectionStart, ta.selectionEnd) + string
      + ta.value.substring(ta.selectionEnd);
    }
  }
  else {
    if (document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, string);
    } else{
      ta.value = ta.value.substring(0, ta.selectionStart)
      + string + ta.value.substring(ta.selectionStart);
    }
  }
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
    $.ajax({
      url: $SCRIPT_ROOT+'/pages/_check_override',
      type: 'POST',
      data:{markdown:text, title:title},
      success: function(data) {
        if (data.error === "")
        {
          $.ajax({
            url: $SCRIPT_ROOT+'/pages/_save',
            type: 'POST',
            data:{markdown:text, title:title},
            success: function(data) {
              window.location.href = data.url;
            },
            error: function(data){
              window.alert("Please enter a valid title");
            }
          });
        } else if (data.error === "Duplicate title") {
          var res = confirm("You are overriding an existing file!");
          if (res){
            $.ajax({
              url: $SCRIPT_ROOT+'/pages/_save',
              type: 'POST',
              data:{markdown:text, title:title},
              success: function(data) {
                window.location.href = data.url;
              },
              error: function(data){
                window.alert("Please enter a valid title");
              }
            });
          }
        } else {
          window.alert(data.error)
        }
      },
      error: function(data){
        window.alert("Please enter a valid title");
      }
    });
  }
}
