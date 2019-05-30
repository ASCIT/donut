/**
 * Filename: sell_images.js
 * Author: Daniel Kong
 *
 * This script provides functions for the user to upload images directly
 * to imgur using the sell form. This requires the overlay functionality
 * found in overlay.js.
 */

//-------------------------------------------------------------------

/*
 * Display the form to upload an image.
 */
function showUploadForm(imageNum)
{
  showOverlay();

  // Create the forms to upload images.
  var uploadForm = $('<div>').addClass('panel panel-default').append(
    $('<div>').addClass('panel-heading').append(
      $('<div>').addClass('panel-title').text('Upload image')
    ),
    $('<div>').addClass('panel-body').append(
      // Used to report error messages.
      $('<div>').attr('id', 'uploadImageError'),
      $('<div>').addClass('row').append(
        // Upload from computer
        $('<div>').addClass('col-xs-6').append(
          $('<form>').append(
            $('<div>').addClass('form-group').append(
              $('<label>').attr('for', 'image_file').text('Upload from computer'),
              $('<input>').attr({type: 'file', id: 'image_file'}).addClass('form-control')
            ),
            $('<button>').attr('type', 'button').addClass('btn btn-success')
              .text('Upload')
              .click(function() { uploadFromFile(imageNum) })
          )
        ),
        // Upload from url
        $('<div>').addClass('col-xs-6').append(
          $('<form>').append(
            $('<div>').addClass('form-group').append(
              $('<label>').attr('for', 'image_url').text('Upload from URL'),
              $('<input>').addClass('form-control').attr({id: 'image_url', placeholder: 'URL'})
            ),
            $('<button>').attr('type', 'button').addClass('btn btn-success')
              .text('Upload')
              .click(function() { uploadFromURL(imageNum) })
          )
        )
      )
    )
  );

  // Display the form.
  $("#overlayWindow").append(uploadForm);

  centerOverlay();

  // Set an error handler for ajax errors. This way, we let imgur handle
  // invalid urls or files that the user may try to upload.
  $(document).ajaxError(function() {
    handleImageUploadError();
  });
}

/*
 * Use this function to handle errors by printing a message.
 */
function handleImageUploadError(message)
{
  // Since JavaScript doesn't seem to allow default values, simply don't
  // pass in a message arg for default value.
  if (!message)
  {
    message = "Oops, looks like something went wrong - try again?" +
      "<br>If problems persist, you can also upload images manually " +
      "<a href=\"http://imgur.com\">here</a> instead.";
  }

  // Hide the uploading animation. If it wasn't there in the first place, then
  // this does nothing.
  hideUploadingAnimation();

  $("#uploadImageError").html(message);
  centerOverlay();
}

/*
 * This function takes an image url and uploads the image to imgur.
 */
function uploadFromURL(imageNum)
{
  showUploadingAnimation();

  // Get the url
  var imageURL = $("#image_url").val();

  // Check that it is not empty.
  if (imageURL == "")
  {
    handleImageUploadError("You must provide a link to an image!");
    return;
  }

  // Upload to imgur
  uploadImage(imageURL, imageNum, "URL");
}

/*
 * This function takes the selected file and uploads it to imgur.
 */
function uploadFromFile(imageNum)
{
  // Check if the browser supports html5's filereader object.
  if (!window.FileReader)
  {
    handleImageUploadError(
      "Your browser does not seem to fully support HTML5, " +
      "so this feature will not work properly. However, you can " +
      "upload images manually " +
      "<a href=\"https://imgur.com\">here</a>.</p>");
    return;
  }

  showUploadingAnimation();

  var reader = new FileReader();

  // Make sure a file was selected.
  if ($("#image_file").prop("files").length === 0)
  {
    handleImageUploadError("You must select a file first.")
    return false;
  }

  var imageFile = $("#image_file").prop("files")[0];

  // Set the file reader so that it calls the upload image function when
  // the read is finished.
  reader.onload = function(e) {
    // Convert binary data to base 64 and then upload it.
    uploadImage(btoa(e.target.result), imageNum, "base64");
  };

  reader.readAsBinaryString(imageFile);
}

/*
 * This function handles the upload request.
 */
function uploadImage(imageData, imageNum, uploadType)
{
  $.ajax({
    type: "POST",
    url: "https://api.imgur.com/3/image",
    headers: {
      "Authorization": "Client-ID " + IMGUR_CLIENT_ID
    },
    data: {
      image: imageData,
      type: uploadType,
    },
    // Forces jQuery to parse the response properly.
    dataType: "json",
    success: function(response) {
      // Call the event handler with an additional argument.
      console.log(response);
      handleUploadResponse(response, imageNum);
    }
  });
}

/*
 * This function handles the response from imgur on a successful request.
 */
function handleUploadResponse(response, imageNum)
{
  // Check that the request was actually successful.
  if (response.status != 200 || response.success != true)
  {
    handleImageUploadError();
    return;
  }

  // Update the appropriate field in the sell form.
  $("#image" + imageNum).val(response.data.link);

  // Close the overlay.
  closeOverlay();
}

/*
 * This function creates a box displaying a gif to be shown when the user is
 * uploading something.
 */
function showUploadingAnimation()
{
  $("#overlayWindow").append("<div id=\"uploadingAnimation\"></div>");
  $("#uploadingAnimation").append("<div id=\"uploadingAnimationContent\"></div>");
  $("#uploadingAnimationContent").append("<img src='/static/images/marketplace/loading.gif' width=\"50\"></img>");
  $("#uploadingAnimationContent").append("<p>Processing...</p>");

  // Center the content in the middle of the box that appears.
  var width = $("#uploadingAnimationContent").width();
  var height = $("#uploadingAnimationContent").height();

  $("#uploadingAnimationContent").css({
    "top" : "50%",
    "left" : "50%",
    "margin-top" : "-" + (height / 2) + "px",
    "margin-left" : "-" + (width / 2) + "px"
  });
}

/*
 * Hides the uploading animation. This should be used in cases where the
 * uploading animation should disappear but the overlay does not; if the
 * overlay is hidden then this is also hidden.
 */
function hideUploadingAnimation()
{
  $("#uploadingAnimation").remove();
}
