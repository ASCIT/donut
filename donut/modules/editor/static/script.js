var old_title;
// In milli
let KEEP_PAGE_ALIVE_TIME = 60*1000;
$(function() {	
  old_title = $('#text_title').val();
  $('#runBtn').click(preview);
  $('#change_title').click(change_title);
  for (var i = 1; i<7; i++) {
    $('#heading'+String(i)).click({size:i}, insert_heading);
  }
  $('#italicize').click(insert_italic);
  $('#bold').click(insert_bold);
  $('#link').click(insert_link);
  $('#image').click(insert_image);
  $('#ulist').click(insert_ulist);
  $('#olist').click(insert_olist);
  $('#save').click(save);
});

// Creates html
function preview() {
  var text = $('#source').val(),
      title = $('#text_title').val(),
      target = $('#preview'),
      target_title = $('#preview_title'),
      converter = new showdown.Converter({strikethrough: true}),
      html = converter.makeHtml(text);
  target.html(html);
  target_title.html(title);
}

// Changes the title of a file
function change_title(){
  var title = $('#text_title').val();
  var text = $('#source').val();
  console.log(old_title);
  $.ajax({
    url: '/pages/_change_title',
    type: 'POST',
    data:{title:title, 
          old_title:old_title, 
          input_text:text},
    success: function(data) {
      window.alert("Title Change Sucessfully");
      old_title = title;
    },
    error: function(data) {
      window.alert("Please enter a valid title!");
    }
  });
}

//###########

function modHighlightedString(string1, string2)
{
  var ta = $('#source')[0];
  if (ta.selectionStart === ta.selectionEnd)
  {
    insert(string2, false);
  }
  else {
    insert(string1, true);
  }
}

// All markdown related functions
function insert_heading(event){
  var size = event.data.size;
  var string = "";
  for(var i = 0; i < size; i++)
  {
    string += "#";
  }
  modHighlightedString(string, string + "Heading_title" + string+ "\n");
}

function insert_italic(){
  modHighlightedString("*", "*italicText*");
}

function insert_bold(){
  modHighlightedString("**", "**boldText**");
}

function insert_link(){
  insert("[Link title](example.com)", false);
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
  var ta = $("#source")[0];
  var begin = ta.selectionStart;
  var end = ta.selectionEnd;
  if(selected)
  {
    if (document.queryCommandSupported('insertText')) {
      ta.setSelectionRange(begin, begin);
      ta.focus();
      document.execCommand('insertText', false, string);
      ta.setSelectionRange(end + string.length, end + string.length);
      ta.focus();
      document.execCommand('insertText', false, string);
    } else{
      ta.value = ta.value.substring(0, begin)
      + string + ta.value.substring(begin, end) + string
      + ta.value.substring(end);
    }
  }
  else {
    if (document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, string);
    } else{
      ta.value = ta.value.substring(0, begin)
      + string + ta.value.substring(begin);
    }
  }
}

// Saves the page created
function save(){
  // Construct the html and get the info needed
  var text = $("#source").val();
  var title = $('#text_title').val();
  // Checking for valid titles
  if (title === '')
  {
    window.alert("Enter a title for your new page!");
    return;
  }
  $.ajax({
    url: '/pages/_check_errors',
    type: 'POST',
    data:{markdown:text, title:title},
    success: function(data) {
      if (data.error === "Duplicate title" || data.error === "")
      {
        if (data.error === "Duplicate title") {
          var res = confirm("You are overriding an existing file!");
        }
        else {
          var res = true;
        }
        if (res){
          $.ajax({
            url: '/pages/_save',
            type: 'POST',
            data:{markdown:text, title:title},
            success: function(data) {
              window.location.href = data.url;
            },
            error: function(data){
              window.alert("Invalid permissions");
            }
          });
        }
      } else {
        window.alert(data.error);
      }
    },
    error: function(data){
      window.alert("Unknown error occurred");
    }
  });
}

// Sends a request to the server to keep the lock alive every minute. 
setInterval(function(){
 var title = $('#text_title').val();
  $.ajax({
    url: '/pages/_keep_alive_page',
    type: 'POST',
    data:{title:title},
 });
}, KEEP_PAGE_ALIVE_TIME);

window.addEventListener("beforeunload", function (e) {
  var title = $('#text_title').val();
  var url = "{{ url_for('editor.close_page') }}";
  $.ajax({
    url: "/pages/_close_page",
    type: 'POST',
    data:{title:title},
  });
});
