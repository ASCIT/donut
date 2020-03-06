var color_label = {
  'ASCIT':"#FFC08E",
  'Avery': "#FF9090",
  'Bechtel': "#E2E2E2",
  'Lloyd': "#FFF4A3",
  'Blacker': "#909090",
  'Page':'#92BCFF',
  'Dabney':'#93DBA5',
  'Fleming':'#FBADFF',
  'Ruddock':'#4E99D6',
  'Ricketts':'#C3A3FF',
  'Athletics':'#A3F0FF',
  'Other':'#D3FFA3',

};
function isFuture(curEvent)
{
    var timeStr = curEvent.end.dateTime || curEvent.end.date;
    var curDay = new Date();
    var curEvent = new Date(timeStr.substring(0, timeStr.length-1)+"-08:00");
    return curEvent >= curDay;
}

function showEventInfo(event)
{
  var data = event.data.data;
  var permission = event.data.permission;
  $('#eventName').text(data.summary);
  $('#eventName_edit').val(data.summary);
 
  var begin = data.start.dateTime || data.start.date;
  var end = data.end.dateTime || data.end.date;
  $('#eventStartTime').text(begin);
  $('#eventEndTime').text(end);
  
  $('#eventDescription').text(data.description);
  $('#eventDescription_edit').val(data.description);
  $('#htag').val(data.organizer.displayName);
  $('#calEventId').val(data.id);

  $('#tag').text(data.organizer.displayName);

  // We force a start time on our site but google doesn't require it
  if(begin.length > 10)
  {
    $('#start_hour').val(begin.substring(11, 13));
    $('#end_hour').val(end.substring(11, 13));
    $('#start_minute').val(end.substring(14, 16));
    $('#end_minute').val(end.substring(14, 16));
  }
  else
  {
    $('#start_hour').val(0);
    $('#end_hour').val(0);
    $('#start_minute').val(0);
    $('#end_minute').val(0); 
  }
  $('#start_date').val(begin.substring(0, 10));
  $('#end_date').val(end.substring(0, 10));
  $('#extendInfo').show();
  if (permission)
  {
    $(".deleteEvent").unbind("click").on('click',{eventID:data.id, tag:data.organizer.displayName}, deleteEvent);
    $(".editable").show();
    $(".noneditable").hide();
  }
  else{
    $(".editable").hide();
    $(".noneditable").show();
  }
  $(".close").show();
  $(".extendInfoCol").show();
}

// Returns a format in mm/dd/yy
function formatDate(datestr) {
  var curDate = datestr.substring(0, 10);
  var year = curDate.substring(0, 4).substring(2);
  var month = curDate.substring(5, 7);
  var day = curDate.substring(8, 10);
  return month + "/"+day+"/"+year;
}
// Show all searched event
function renderAll(eventList, tag, permissions)
{
    $(tag + ':not(#extendInfo)').empty();
    eventList.forEach(function(curEvent) {
    var dot = $('<label>').append($('<span>').addClass('dot').css('background-color', color_label[curEvent.organizer.displayName]));
    var eventName = $('<label>').addClass('alignleft').text(curEvent.summary);
    var eventStartDate = formatDate(curEvent.start.dateTime || curEvent.start.date);
    var eventEndDate = formatDate(curEvent.end.dateTime || curEvent.end.date);
    var eventDates = $('<label>').addClass('alignright').text(eventStartDate+" - "+eventEndDate);
    var divNode = $('<div>')
        .addClass('searchEvents rounded')
        .addClass(curEvent.organizer.displayName)
        .attr('id', curEvent.id)
        .append(dot)
        .append(eventName)
        .append(eventDates)
        .append('<hr>')
        .click({data: curEvent, div: divNode}, showEventInfo)
        $(tag).append(divNode);
        var editable = false;
        if (permissions[curEvent.organizer.displayName]) 
        {
          editable = true;
        }
        $("#"+curEvent.id).unbind("click").on('click',{data: curEvent, div:divNode, permission:editable}, showEventInfo);
    });
    if (!eventList.length)
    {
        $(tag).text('No results :(');
    }
}

function search(data, query)
{
  var possibleEventsFuture= [];
  var possibleEventsPast = [];
  data['events'].forEach(function(calEvent) {
      var name = calEvent['summary'].toLowerCase();
      var description = (calEvent.description || '').toLowerCase();
      var score = 0;
      var organizer = calEvent['organizer']['displayName'].toLowerCase();
      query.forEach(function(segment) {
        if(name.indexOf(segment)>-1)
        {
          score += 1;
        }
        else if (name.replace(/\s+/g, '').includes(segment))
        {
          score += .5;
        }
        if(description.indexOf(segment)>-1)
        {
          score += .5;
        }
        else if (description.replace(/\s+/g, '').includes(segment))
        {
          score += .25;
        }

        if(organizer.indexOf(segment)>-1)
        {
          score += 1.25;
        }
        else if (organizer.replace(/\s+/g, '').includes(segment))
        {
          score += .75;
        }
      })
      if (score)
      {
        (isFuture(calEvent) ? possibleEventsFuture : possibleEventsPast)
            .push({calEvent:calEvent, score:score});
      }
  })
  possibleEventsFuture = possibleEventsFuture.sort(function(a, b) { return b.score - a.score })
                       .map(function(eventScore) { return eventScore.calEvent });
  possibleEventsPast = possibleEventsPast.sort(function(a, b) { return b.score - a.score })
                       .map(function(eventScore) { return eventScore.calEvent });
  renderAll(possibleEventsFuture, '#future', data.permissions);
  renderAll(possibleEventsPast, '#past',  data.permissions);
}

function getData()
{
   $('#future').text('Loading...');
   $('#past').text('Loading...');
   var query = $('#query').val().trim()
		.toLowerCase()
		.split(/[ /]+/);
   var possibleEventsFuture= [];
   var possibleEventsPast = [];
   // Get all possible events...
   $.ajax({
      url: '/1/calendar_all_events_backup',
      type: 'POST',
      success: function(data){
        $('#failover_message').css('display', 'inline-table');
        search(data, query);
        $('#last_update_message').text($('#last_update_message').html().replace("{0}", data.last_update_time));
      } 
    });
}

// Delete event from our db and from the page
function deleteEvent(event)
{
    $.ajax({
      url: '/1/calendar/delete_event',
      type: 'POST',
      data:{
        id:event.data.eventID,
        tag:event.data.tag
      },
      success: function(data) {
        if(data.deleted === '')
        {
            $('#'+event.data.eventID).remove();
        }
        else{
            alert(data.deleted);
        }
      }
    });
    $('#extendInfo').hide();
}

function toggle(tag, visibility){
    $("div").each( function (){
        if ($(this).hasClass(tag))
        {
            $(this).toggle(visibility);
        }
    });
}

$(function(){
  $('.btn[value="Search"]').click(getData);
    // Fill in colors for the calendars
  for (var key in color_label) {
    $("#"+key+".dot").css("background-color", color_label[key]);
  }

  // Bind visible checkboxes. 
  $(':checkbox').change(function() {
    toggle($(this).val(), this.checked);
  });

  $(':checkbox').prop('checked', true);

  $('.close').click(function() {
        $(this).parent().hide();
  });
});
