var color_label = {
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
function isFuture(curEvent)
{

    var timeStr = curEvent['end']['dateTime'] || curEvent['end']['date'];
    var year = parseInt(timeStr.substring(0, 4), 10);
    var day = parseInt(timeStr.substring(8, 10), 10);
    var month = parseInt(timeStr.substring(5, 7), 10);    
    var curDay = new Date();
    if (year > curDay.getFullYear()){ return true};
    if (year < curDay.getFullYear()){ return false};
    if (month-1 > curDay.getMonth()){ return true};
    if (month-1 <  curDay.getMonth()){ return false};
    if (day >= curDay.getDate()){ return true};
    return false;
}

function showEventInfo(event)
{
    var data = event.data.data;
  data = event.data.data;
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
  //$('#'+data.id).append($('#extendInfo'));
  $('#extendInfo').show();
}

// Show all searched event
function renderAll(eventList, tag)
{
    $(tag).not($('#extendInfo')).empty();
    eventList.forEach(function(curEvent) {
        var divNode = document.createElement('div');        
        divNode.style.backgroundColor = color_label[curEvent['organizer']['displayName']];
        divNode.className = 'searchEvents';
        divNode.className +=  ' rounded';
        divNode.setAttribute("id", curEvent['id']);
        var eventName = document.createElement('Label');
        eventName.innerHTML = curEvent['summary'];
        divNode.appendChild(eventName);
        $(tag).append(divNode);
        $("#"+curEvent.id).on('click',{data: curEvent, div:divNode}, showEventInfo);
    });
    if ($.isEmptyObject(eventList))
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
      var description = '';
      if (typeof(calEvent['description']) !== 'undefined')
      {
        description = calEvent['description'].toLowerCase();
      }
      var score = 0;
      query.forEach(function(segment) {
        if(name.includes(segment))
        {
          score += 1;
        }
        else if (name.replace(/\s+/g, '').includes(segment))
        {
          score += .5;
        }
        if(description.includes(segment))
        {
          score += .5;
        }
        else if (description.replace(/\s+/g, '').includes(segment))
        {
          score += .25;
        }
      })
      if (score)
      {
        if (isFuture(calEvent))
          {
            possibleEventsFuture.push({calEvent:calEvent, score:score});
          }
          else{
            possibleEventsPast.push({calEvent:calEvent, score:score});
          }
       }
  })
  possibleEventsFuture = possibleEventsFuture.sort(function(a, b) { return b.score - a.score })
                       .map(function(eventScore) { return eventScore.calEvent });
  possibleEventsPast = possibleEventsPast.sort(function(a, b) { return b.score - a.score })
                       .map(function(eventScore) { return eventScore.calEvent });
  renderAll(possibleEventsFuture, '#future');
  renderAll(possibleEventsPast, '#past');
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
      url: '/1/calendar_all_events',
      type: 'POST',
      data:{
      },
      success: function(data){
        $('#failover_message').hide();
        search(data, query);
      }, 
      timeout:1000,
      error: function(jqXHR, textStatus){
        if(textStatus === 'timeout')
        { 
          $.ajax({
              url: '/1/calendar_all_events_backup',
              type: 'POST',
              data:{
              },
              success:function(data){
                if (!window.parent.location.href.includes('sync')){
                    $('#failover_message').show();
                }
                search(data, query); 
              }
          });
        }
      }
    });
}
$(function(){
    $('.btn[value="Submit"]').click(getData);
});
