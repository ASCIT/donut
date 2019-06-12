var CURRENT_DATE = new Date();
var d = new Date();

var content = 'January February March April May June July August September October November December'.split(' ');
var weekDayName = 'SUN MON TUES WED THURS FRI'.split(' ');
var events = {}
var curYear = CURRENT_DATE.getFullYear();
var colorLabel = {
  'Avery': "#ff7744",
  'Lloyd': "#ffd974",
  'Blacker': "#d3ff74",
  'Page':'#a5bcff',
  'Dabney':'#74ffa1',
  'Fleming':'#ff74df',
  'Ruddock':'#74deff',
  'Ricketts':'#b974ff',
  'Athletics':'#ff0000',
  'Other':'#868686',

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
  var eleCenter = $('#extraInfo_triangle').width()/2;
  if (event.clientX < $('#cal').width()/2)
  {
    $('#extraInfo_triangle').css("left", $('#cal').width()/2 - eleCenter);
    $('#extraInfo').css("left", $('#cal').width()/2);  
    $('#extraInfo_triangle').css({"box-shadow": "3px -3px 3px 0px rgba(0, 0, 0, 0.4)"});
    $('#extraInfo_triangle').css({"border-color": "white white transparent transparent"});
  }
  else {
    $('#extraInfo').css("left", "0px");
    $('#extraInfo_triangle').css("left", $('#cal').width()/2 - eleCenter);
    $('#extraInfo_triangle').css({"box-shadow": "-3px 3px 3px 0px rgba(0, 0, 0, 0.4)"});
    $('#extraInfo_triangle').css({"border-color": "transparent transparent white white"});
  }
  $('#extraInfo_triangle').css("top", 
        Math.min($('#extraInfo').height() -  $('#extraInfo_triangle').height(), event.clientY+ 5));
  $('#extraInfo_triangle').fadeIn();
  $('#extraInfo').fadeIn();
}

// Render the events for a month and year on our calendar. 
function renderEvents(month, year)
{
  $('div.day').each(function(){$(this).empty();});

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
        divNode.css("display", "none"); 
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
      url: '/1/calendar_events',
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
            $('#failover_message').hide();
          }
      },

      // Perhaps the timeout is too long... But this is about the time where
      // Half of the time it'll work and the other half wouldn't
      timeout:3000, 
      error: function(jqXHR, textStatus){
        if(textStatus === 'timeout')
        {     
            // Access the backup
            $.ajax({
                url: '/1/calendar_events_backup',
                type: 'POST',
                data:{
                    year:year
                },
                success:function(data){
                    if (data.err)
                    {
                        alert(data.err);
                    } else{
                      if (!window.parent.location.href.includes('sync')){
                          $('#failover_message').show();
                      }
                      process_events(data, month, year);
                    } 
                }
            });
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
    if (currentDay === 0 && (i < totalDays)) {
      $week = getCalendarRow();
      currentRow++;
    }
  }
}

// Clear generated calendar
function clearCalendar() {
  var $trs = $('#cal tbody tr:not(.calendar, .calendarHeaders)');
  $trs.remove();
  $('#extraInfo').hide();
  $('#extraInfo_triangle').hide();
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

