var CURRENT_DATE = new Date();
var d = new Date();

var content = 'January February March April May June July August September October November December'.split(' ');
var weekDayName = 'SUN MON TUES WED THURS FRI'.split(' ');
var events = {}
var curYear = CURRENT_DATE.getFullYear();
var colorLabel = {
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

function toggle(tag, visibility){
    $("div").each( function (){
        if ($(this).hasClass(tag))
        {
            $(this).toggle(visibility);
        }
    });
}


// Returns the day of week which month starts (eg 0 for Sunday, 1 for Monday, etc.)
function getCalendarStart(dayOfWeek, currentDate) {
  var date = currentDate - 1;
  var startOffset = (date % 7) - dayOfWeek;
  if (startOffset > 0) {
    startOffset -= 7;
  }
  return Math.abs(startOffset);
}

function showEventInfo(event)
{
  data = event.data.data;
  $('#eventName').text(data.summary);
  $('#eventName_edit').val(data.summary);
 
  var begin = data.start.dateTime || data.start.date;
  var end = data.end.dateTime || data.end.date;
  $('#eventStartTime').text(begin);
  $('#eventEndTime').text(end);
  
  $('#eventDescription').text(data.description);
  $('#eventDescription_edit').val(data.description);


  $('#eventLocation').text(data.location);
  $('#eventLocation_edit').val(data.location);

  $('#tag').text(data.organizer.displayName);
  $('#htag').val(data.organizer.displayName);
  $('#calEventId').val(data.id);
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
  $(".deleteEvent").off("click").click({eventID:data.id, tag:data.organizer.displayName}, deleteEvent);
  


  // Rendering fun....
  var eleCenter = $('#cal').width()/2;
  var offset = $('#cal').width() * 1/7;
  if (event.clientX - offset < $('#cal').width()/2)
  {
    $('#extraInfo').css("left", "auto");
    $('#extraInfo').css("right", "0px");  
  }
  else {
     $('#extraInfo').css("right", "auto");
    $('#extraInfo').css("left", offset+"px");
  }
  $('#extraInfo').fadeIn();
}

// Render the events for a month and year on our calendar. 
function renderEvents(month, year)
{
  $('div.day').empty();

  events[month].forEach(function(curEvent) 
  {
        
    var checked = $(':checkbox').filter(
     function() {
        return $(this).val() === curEvent.organizer.displayName;});

    var begin = curEvent.start.dateTime || curEvent.start.date;
    var end = curEvent.end.dateTime || curEvent.end.date;
            
    var startDay = parseInt(begin.substring(8, 10), 10);
    var endDay = parseInt(end.substring(8, 10), 10);
    var startMonth = parseInt(begin.substring(5, 7), 10);
    var endMonth = parseInt(end.substring(5, 7), 10);

    var indexOneMonth = month + 1;
    startDay = indexOneMonth > startMonth || year > Number(begin.substring(0, 4)) ? 1 : startDay;
    endDay = indexOneMonth < endMonth || year < Number(end.substring(0, 4)) ? new Date(year, indexOneMonth, 0).getDate() : endDay;
    for(var j = startDay; j <= endDay; j++)
    {
      var divNode = $("<div>");
      divNode.css("background-color", colorLabel[curEvent.organizer.displayName]);
      divNode.addClass('events ' + curEvent.organizer.displayName + ' rounded-circle ' + curEvent.id);
      divNode.attr("id", curEvent.id + j);
      var eventName = $("<label>").text(curEvent.summary);
      divNode.append(eventName);
      if (month === d.getMonth())
      {
        $('#day' + j).append(divNode);
        $("#"+curEvent.id+j).click({data: curEvent}, showEventInfo);
      }
      
      if(!checked[0].checked){
        divNode.hide(); 
      }
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
            $('.'+event.data.eventID).remove();
            $('#extraInfo_triangle').hide();
            $('#extraInfo').hide();
        }
        else{
            alert(data.deleted);
        }
      }
    });
}

// Cache the events locally for an entire year. 
function process_events(data, month, year)
{
  var cal_events = data.events || [];
  cal_events.forEach(function(curEvent)
  {
    var beginStr = curEvent.start.dateTime || curEvent.start.date;
    var beginMonth = parseInt(beginStr.substring(5, 7));
    var endStr = curEvent.end.dateTime || curEvent.end.date;
    var endMonth = parseInt(endStr.substring(5, 7));

    // If the current year and the end year are not the same, then 
    // for whatever ungodly reason the event spans a year
    endMonth = (new Date(endStr).getFullYear() === year) ? endMonth : 12;

    // Same but with beginning months
    beginMonth =  (new Date(beginStr).getFullYear() === year) ? beginMonth : 1;
    while(beginMonth <= endMonth)
    {
      events[beginMonth-1].push(curEvent);
      beginMonth += 1;
    }
  });
  renderEvents(month, year);
}

// Actually requests for the events from the server. 
function getEvents(month, year){
  // We don't always need to send a request. 
  {
    curYear = year;
    $('div').filter($('.day')).each(function(){$(this).text('loading')});
    for (var i = 0; i < 12; i++)
    {
        events[i] = [];
    }
    $.ajax({
      url: '/1/calendar_events_backup',
      type: 'POST',
      data:{
        year:year
      },
      success:function(res){
          if (res.err)
          {
              alert(res.err);
          } else {
            process_events(res, month, year);
            if (!window.parent.location.href.includes('sync')){
              $('#failover_message').show();
            }
            $('#last_update_message').text($('#last_update_message').html().replace("{0}", res.last_update_time));
          }
      }
    });

  }
}

// Render Calendar
function renderCalendar(startDay, totalDays, currentDate) {
  var currentRow = 1;
  var currentDay = startDay;
  var $table = $('#cal');
  var $week = getCalendarRow();
  var $day;
  var render_date = new Date(d.setDate(1));
  for (var i = 0; i <= totalDays; i++) {

    $day = $week.find('td').eq(currentDay);
    $day.text(i);
    if (i === currentDate) {
      $day.addClass('today');
    }
    $day.append("<br>");
    var wrapper = $('<div>').attr('id', 'day'+i).addClass('day');
    $day.append(wrapper);

    currentDay = render_date.getDay();
    render_date.setDate(render_date.getDate() + 1);

    // Generate new row when day is Saturday, but only if there are
    // additional days to render
    if (currentDay === 0 && (i < totalDays) && i !== 0) {
      $week = getCalendarRow();
      currentRow++;
    }
  }
  // If we are not viewing on a mobile device
  if ($(window).width() > 900)
  {
    $("#cal td").css("height", String(90/currentRow)+"%");
  }
}

// Clear generated calendar
function clearCalendar() {
  var $trs = $('#cal tbody tr:not(.calendar, .calendarHeaders)');
  $trs.remove();
  $('#extraInfo').hide();
  $('.month-year').empty();
}

// Generates table row used when rendering Calendar
function getCalendarRow() {
  var $table = $('#cal');
  var $tr = $('<tr>');
  for (var i = 0; i < 7; i++) {
    $tr.append($('<td>'));
  }
  $table.append($tr);
  return $tr;
}

function myCalendar() {
  var month = d.getMonth();
  var day = d.getDay();
  var year = d.getFullYear();
  var date = d.getDate();
  var totalDaysOfMonth = new Date(year, month+1, 0).getDate();
  var counter = 1;

  var $ym = $('<h3>');
  
  $ym.text(content[month] + ' ' + year);
  $ym.appendTo('.month-year');

  var dateToHighlight = 0;

  // Determine if Month && Year are current for Date Highlight
  if (CURRENT_DATE.getMonth() === month && CURRENT_DATE.getFullYear() === year) {
    dateToHighlight = date;
  }

  // Get Start Day
  renderCalendar(getCalendarStart(day, date), totalDaysOfMonth, dateToHighlight);
  if (curYear != year ||$.isEmptyObject(events))
  {
    curYear = year;
    getEvents(month, year);
  }
  else
  {
    renderEvents(month, year);
  }
};

function navigationHandler(dir) {
  d.setMonth(d.getMonth() + dir);
  clearCalendar();
  myCalendar();
}

function jumptodate(){
  if ($('.jumpto_month').val() === "" || $('.jumpto_year').val() === "")
  {
    return;
  }
  // Indexed by 0 but humans index by 1
  d.setMonth($('.jumpto_month').val() - 1);
  // But year isn't...
  d.setFullYear($('.jumpto_year').val());
  clearCalendar();
  myCalendar();
}
$(document).ready(function() {
  // Bind Events
  $('.prev-month').click(function() {
    navigationHandler(-1);
  });
  $('.next-month').click(function() {
    navigationHandler(1);
  });

  $('.jumpto').click(function() {
    jumptodate();
  });
  // Generate Calendar
  myCalendar();

  // Fill in colors for the calendars
  for (var key in colorLabel) {
  $("#"+key+".dot").css("background-color", colorLabel[key]);

  }

  // Bind visible checkboxes. 
  $(':checkbox').change(function() {
    toggle($(this).val(), this.checked);
  });  

  // Bind the little x button
  $('.close').click(function() {
        $(this).parent().hide();
        $('#extraInfo_triangle').hide();
  });
  $(':checkbox').prop('checked', true);
});

