
var colors = ['255, 0, 0', '0, 255, 0', '0, 0, 255',
              '255, 255, 0', '255, 0, 255', '0, 255, 255',
              '255, 128, 0', '255, 0, 128', '0, 255, 128',
              '128, 255, 0', '128, 0, 255', '0, 128, 255'];
var allCourses = {};
var savedCourses = {};
var totalUnits = 0;
var courseBoxes = {'M': [], 'T': [], 'W': [], 'R': [], 'F': []};

function Course(id, course_id, name, text, units) {
    this.id = id;
    this.course_id = course_id;
    this.name = name;
    this.text = text;
    this.units = units;
    this.color = courseColor(name);
}
function CourseBox(course, day, start, end, om) {
    this.id = 'calendar_course_'
        + course.id + day.toString() + start.toString() + om.toString();
    this.course = course;
    this.day = day;
    this.start = start;
    this.end = end;
    this.index = 0;
    this.index_width = 1;
}
function courseBoxSort(a, b) {
    var diff = a.start - b.start;
    if (diff == 0) {
        diff = a.course.name.localeCompare(b.course.name);
    }
    return diff;
}
function hashString(string) {
    var sum = 0;
    for (var i = 0; i < string.length; i++) {
        sum += string.charCodeAt(i);
    }
    return sum % 100;
}
function courseColor(name) {
    if (name == null) return colors[0];
    var sum = 0;
    for (var i = 0; i < name.length; i++) {
        sum += name.charCodeAt(i);
    }
    return colors[sum % colors.length];
}

function clearAll() {
    for (var id in allCourses) {
        removeCourse(id, false);
    }
    totalUnits = 0;
}

var timer = null;
function save() {

    savedCourses = {};

    jQuery.extend(savedCourses, allCourses);

    updateSaveButton();

    var courses = '';
    var firstCourse = true;
    for (var id in allCourses) {
        if (firstCourse)
        {
            firstCourse = false;
        }
        else
        {
            courses += ',';
        }

        courses += id;
    }
    var link = window.location.href.split('?')[0] + '?courses=' + courses;
    $('#link_box').val(link);

    /*clearTimeout(timer);
    timer = setTimeout(function() {
        $.get('update.php', {'courses': courses});
    }, 1000);*/
    $.get("update.php", {'courses': courses});
}

function addCourse(id, course_id, name, text, units, times, doSave, loadingFromDatabase) {

    if (typeof(units) === "string")
    {
        units = parseUnitsString(units);
    }

    if (typeof(loadingFromDatabase) === "undefined")
    {
        loadingFromDatabase = false;
    }

    var course = new Course(id, course_id, name, text, units);
    allCourses[id] = course;

    if (loadingFromDatabase)
    {
        savedCourses[id] = course;
    }
    for (var day in times) {
        for (var i = 0; i < times[day].length; i++) {
            var start = convertTime(times[day][i][0]);
            var end = convertTime(times[day][i][1]);
            var om = times[day][i][2];
            addCourseBox(course, day, start, end, om);
        }
    }

    updateSaveButton();
    updateClearAllButton();

    totalUnits += units;
    document.getElementById('calendar_corner_content').innerHTML = totalUnits;
}

function removeCourse(id, doSave) {

    // remove check from list (if it exists)
    var checkbox = $('input#section_' + id + '_checkbox');
    if (checkbox.length > 0) {
        checkbox.attr('checked', false);
    }
    totalUnits -= allCourses[id].units;
    document.getElementById('calendar_corner_content').innerHTML = totalUnits;

    // remove from calendar
    delete allCourses[id];
    for (var day in courseBoxes) {
        var newList = [];
        var needsReflow = false;
        for (var i = 0; i < courseBoxes[day].length; i++) {
            if (courseBoxes[day][i].course.id == id) {
                var boxId = courseBoxes[day][i].id;
                $('#' + boxId).remove();
                needsReflow = true;
            }
            else {
                newList.push(courseBoxes[day][i]);
            }
        }
        courseBoxes[day] = newList;
        if (needsReflow) {
            reflowCourses(day);
        }
    }

    updateSaveButton();
    updateClearAllButton();
}

function isEqual(list1, list2)
{
    var length1 = Object.keys(list1).length;
    var length2 = Object.keys(list2).length;

    if (length1 !== length2)
    {
        return false;
    }

    for (var id in allCourses)
    {
        if (!(id in savedCourses))
        {
            return false;
        }
    }

    return true;
}

function updateSaveButton()
{
    var saveButton = document.getElementById("save_button");

    if (!isEqual(allCourses, savedCourses))
    {
        $(saveButton).removeClass("button_disabled");
        $(saveButton).attr("href", "javascript:save()");
    }

    else
    {
        $(saveButton).addClass("button_disabled");
        $(saveButton).removeAttr("href");
    }
}

function updateClearAllButton()
{
    var clearButton = document.getElementById("clear_button");

    var numberOfCourses = Object.keys(allCourses).length;

    if (numberOfCourses != 0)
    {
        $(clearButton).removeClass("button_disabled");
        $(clearButton).attr("href", "javascript:clearAll()");
    }

    else
    {
        $(clearButton).addClass("button_disabled");
        $(clearButton).removeAttr("href");
    }
}

function parseTimeString(time_string) {
    if (time_string == 'A') return {};
    times = {}
    strings = time_string.split('<br>');
    for (var i = 0; i < strings.length; i++) {
        var split = strings[i].split(' ');
        var days = split[0];
        var start = parseInt(split[1].replace(':', ''), 10);
        var end = parseInt(split[3].replace(':', ''), 10);
        var om = false;
        if (days.indexOf('OM,') != -1) {
            om = true;
            days = days.split(',')[1];
        }
        for (var j = 0; j < days.length; j++) {
            var day = days.charAt(j);
            if (!(day in times)) {
                times[day] = []
            }
            times[day].push([start, end, om]);
        }
    }
    return times;
}

function parseUnitsString(units_string) {
    units = 0;

    if (units_string === "+")
    {
        return units;
    }
    strings = units_string.split('-');
    for (var i=0; i< strings.length; i++) {
        units += parseInt(strings[i])
    }
    return units;
}

function convertTime(time) {
    return Math.floor(time/100)*100 + Math.floor((time%100)/60 * 100);
}

function addCourseBox(course, day, start, end, om) {
    if (!(day in courseBoxes)) return;

    var courseBox = new CourseBox(course, day, start, end, om);
    courseBoxes[day].push(courseBox);
    courseBoxes[day].sort(courseBoxSort);

    var id = courseBox.id;
    $('#day_grid_' + day).append(
        '<div class="calendar_course_box" id="' + id + '"></div>');
    var box = $('#' + id);
    if (om) {
        box.append('[OM] ');
    }
    box.append('<div class="calendar_course_box_x"></div>');
    box.append(course.text);
    box.addClass('calendar_course_' + course.id + '_' + course.course_id);
    box.css('height', (end - start)*0.5 + 'px');
    box.css('top', (start - 800)/100*50 + 25 + 'px');
    box.css('background-color', 'rgba(' + course.color + ', 0.25)');
    box.css('border-color', 'rgb(' + course.color + ')');

    reflowCourses(day);
}

function timeSort(time1, time2){
    var diff = time1[0] - time2[0];
    if(diff == 0){
        diff = time1[1] - time2[1];
    }
    return diff;
}

function reflowCourses(day){
    courseBoxes[day].sort(courseBoxSort);
    var allTimes = new Array();
    /* [time, +/-1]
     * if it's a start time, +1
     * otherwise -1
    */
    for (var i = 0; i < courseBoxes[day].length; i++){
        allTimes.push([courseBoxes[day][i].start, 1, i]);
        allTimes.push([courseBoxes[day][i].end, -1, i]);
    }
    allTimes.sort(timeSort);
    var count = 0;
    while (count < allTimes.length){
        var max = 1;
        var sum = 0;
        var start = count;
        while (true) {
            sum = sum + allTimes[count][1];
            if (sum > max) {
                max = sum;
            }
            if (sum == 0) {
                break;
            }
            else {
                count++;
            }
        }
        /* now that max is found, add in the positions (index and index_width)*/
        var width = 100 / max;
        var isIndexUsed = new Array(max);
        for (var i = 0; i < max; i++) {
            isIndexUsed[i] = false;
        }
        /* addedCourse is to check if expansion is possible (it's actually the course index)*/
        var addedCourse = -1;
        for (var i = start; i <= count; i++) {
            var courseBox = courseBoxes[day][allTimes[i][2]];
            if (allTimes[i][1] == 1) {
                for (var findIndex = 0; findIndex < max; findIndex++) {
                    if (!isIndexUsed[findIndex]) {
                        isIndexUsed[findIndex] = true;
                        courseBox.index = findIndex;
                        break;
                    }
                }

                if (addedCourse < 0 ||
                        courseBox.index > courseBoxes[day][addedCourse].index) {
                    // if cannot expand, reset to rightmost
                    addedCourse = allTimes[i][2];
                }
                var id = courseBox.id;
                $('#' + id).css('width', "" + courseBox.index_width * width + "%");
                $('#' + id).css('left', "" + courseBox.index * width + "%");
            }
            else{
                if (addedCourse == allTimes[i][2]) {
                    // check if can expand
                    var extra = 1;
                    while (courseBox.index + extra < max) {
                        if (!isIndexUsed[courseBox.index + extra]) {
                            extra += 1;
                        }
                        else {
                            break;
                        }
                    }
                    var id = courseBoxes[day][addedCourse].id;
                    $('#' + id).css('width', "" + courseBox.index_width * extra * width + "%");
                }
                if (addedCourse >= 0 && courseBoxes[day][allTimes[i][2]].index
                        >= courseBoxes[day][addedCourse].index){
                    addedCourse = -1;
                }
                isIndexUsed[courseBox.index] = false;
            }
        }
        count++;
    }
}

function reflowAll() {
    for (var day in courses) {
        reflowCourses(day);
    }
}

var courseHtmlQueue = [];

function loadCourseHtml() {
    var i = 2;
    while (courseHtmlQueue.length > 0 && i > 0) {
        var html = courseHtmlQueue.shift();
        var courseBox = $(html).hide();
        $('#course_list').append(courseBox);

        var courseTitle = courseBox.children('.course_title');
        var color = courseColor(courseTitle.html());
        courseTitle.css('background-color', 'rgba(' + color + ', 0.25)');
        courseTitle.css('border-color', 'rgb(' + color + ')');
        courseBox.find('.section').each(function() {
            var id = parseInt($(this).attr('id').split('_')[1]);

            if (id in allCourses) {
                $(this).children('input').attr('checked', true);
                $(this).children('.section_image').css('background-image', "url('x.png')");
            } else {
                $(this).children('.section_image').css('background-image', "url('plus.png')");
            }
        });

        courseBox.fadeIn();
        i--;
    }
    if (courseHtmlQueue.length > 0) {
        window.setTimeout(loadCourseHtml, 10);
    }
}

function courseHover(id, hover) {
    var box = $('#course_list #course_' + id);
    if (box.length > 0) {
        var title = box.children('.course_title');
        var color = courseColor(title.html());
        if (hover) {
            box.addClass('course_box_hover');
            title.css('background-color', 'rgba(' + color + ', 0.75)');
            title.css('border-color', '#000');
        }
        else {
            box.removeClass('course_box_hover');
            title.css('background-color', 'rgba(' + color + ', 0.25)');
            title.css('border-color', 'rgb(' + color + ')');
        }
    }
}

function sectionHover(id, hover, fromCalendar) {
    var sectionBox = $('#course_list #section_' + id);
    if (sectionBox.length > 0) {
        if (fromCalendar) {
            var courseBox = sectionBox.parents('.course_box');
            if (courseBox.length > 0) {
                var courseId = parseInt(courseBox.attr('id').split('_')[1]); // course_#
                courseHover(courseId, hover);
            }
        }
        if (hover) {
            sectionBox.addClass('section_hover');
            sectionBox.children('.section_image').show();
        }
        else {
            sectionBox.removeClass('section_hover');
            sectionBox.children('.section_image').hide();
        }
    }
    var calendarBoxes = $('#calendar_body .calendar_course_' + id);
    if (calendarBoxes.length > 0) {
        var course = allCourses[id];
        if (hover) {
            calendarBoxes.css('background-color', 'rgba(' + course.color + ', 0.75)');
            calendarBoxes.css('border-color', '#000');
        }
        else {
            calendarBoxes.css('background-color', 'rgba(' + course.color + ', 0.25)');
            calendarBoxes.css('border-color', 'rgb(' + course.color + ')');
        }
    }
}

var searchTimer = null;
var lastQuery = null;

function search() {
    var data = $('#search_form').serialize();
    if (data != lastQuery) {
        lastQuery = data;
        $('#course_list_loading').stop().fadeIn();
        $.get('search.php', data)
            .success(function(result) {
                $('#course_list').empty();
                if ($.trim(result) == '') {
                    $('#course_list').html(
                        '<div id="course_list_message">No matches found ):</div>');
                    courseHtmlQueue = [];
                } else {
                    courseHtmlQueue = result.split('\t');
                    loadCourseHtml();
                }
                $('#course_list_loading').stop().hide();
            })
            .error(function() {
                $('#course_list_loading').stop().hide();
            });
    }
}

function getTotalUnits()
{
    return totalUnits;
}

window.onbeforeunload = function() {
    if (!isEqual(allCourses, savedCourses))
    {
          return "You have unsaved changes to your schedule.";
    }
}

$(document).ready(function() {

    var widthString = window.getComputedStyle($("#scheduler")[0]).width;
    var widthSub = widthString.substring(0, widthString.length - 2);
    var width = parseInt(widthSub);
    var fontSize = (width - 144.5) / 59.5;
    $("#scheduler").css("fontSize", "" + fontSize + "px");

    $("#calendar_body").scroll(function(event) {
        $("#day_row").css("margin-left", -$("#calendar_body").scrollLeft());
        $("#time_column").scrollTop($("#calendar_body").scrollTop());
    });

    $(window).resize(function(event) {
        var widthString = window.getComputedStyle($("#scheduler")[0]).width;
        var widthSub = widthString.substring(0, widthString.length - 2);
        var width = parseInt(widthSub);
        var fontSize = (width - 144.5) / 59.5;
        $("#scheduler").css("fontSize", "" + fontSize + "px");
    });

    // calendar hover
    $('#calendar_body').on('mouseover mouseout', '.calendar_course_box',
        function(event) {
            var box_id = $(this).attr('class').split(' ')[1];
            var id = parseInt(box_id.split('_')[2]); // calendar_course_#
            sectionHover(id, event.type == 'mouseover', true);
            if (event.type == 'mouseover') {
                $(this).children('.calendar_course_box_x').show();
            } else {
                $(this).children('.calendar_course_box_x').hide();
            }
        }
    );

    // calendar click
    $('#calendar_body').on('click', '.calendar_course_box', function(event) {
        var box_id = $(this).attr('class').split(' ')[1];
        var course_id = parseInt(box_id.split('_')[3]); // calendar_course_#

        var elementId = "course_" + course_id;

        $("#course_list_box").animate({"scrollTop": $("#course_list_box").scrollTop() + $("#" + elementId).position().top}, "slow");
    });

    // search course hover
    $('#course_list').on('mouseover mouseout', '.course_box',
        function(event) {
            var id = parseInt($(this).attr('id').split('_')[1]);  // course_#
            courseHover(id, event.type == 'mouseover');
        }
    );
    // section hover
    $('#course_list').on('mouseover mouseout', '.section',
        function(event) {
            var id = parseInt($(this).attr('id').split('_')[1]);
            sectionHover(id, event.type == 'mouseover', false);
        }
    );

    // calendar click
    $('#calendar_body').on('click', '.calendar_course_box_x',
        function(event) {
            event.stopPropagation();
            var classList = $(this).parent().attr('class').split(/\s+/);
            var id = parseInt(classList[1].split('_')[2]); // calendar_course_#
            sectionHover(id, false, true);
            removeCourse(id, true);
        }
    );

    $('#stale_sections_box_x').on('click',
        function(event) {
            document.getElementById('stale_sections').style.display = "none";
        }
    );

    // add or remove course on click
    $('#course_list').on('click', '.section',
        function(event) {
            event.stopPropagation();
            var section = $(this);
            var id = parseInt(section.attr('id').split('_')[1]);
            if (!(id in allCourses)) {
                var checkBoxId = section.children('input').attr('id');
                document.getElementById(checkBoxId).checked = "true";
                var course_box = section.parents('.course_box');
                var name = course_box.children('.course_title').html()
                var text = name + '<br>'
                    + section.children('.section_number').html();
                var times = parseTimeString(section.children('.section_times').html());
                var units = parseUnitsString(course_box.children('.course_units').text());

                var courseIdString = course_box.attr('id');
                var courseIdArray = courseIdString.split('_');
                var courseId = parseInt(courseIdArray[1]);

                addCourse(id, courseId, name, text, units, times, true);
                sectionHover(id, true, false);
                section.children('.section_image').css('background-image', "url('x.png')");
            }
            else {
                removeCourse(id, true);
                section.children('input').attr('checked', false);
                section.children('.section_image').css('background-image', "url('plus.png')");
            }
        }
    );

    $('#course_list').on('click', '.course_box', function(event) {
        var course_box = $(this);
        var link = course_box.find('.more_sections_link');
        var sectionsPreview = link.siblings('.more_sections_preview');
        var sections = link.siblings('.more_sections');

        if (!(sections.is(':visible')))
        {
            sectionsPreview.slideDown('fast');
            link.html('&#9650;');
            sectionsPreview.slideUp('fast');
            link.html('&#9660;');
        }

    });



    // show hidden sections
    $('#course_list').on('click', '.more_sections_link',
        function(event) {
            event.stopPropagation();
            var link = $(this);
            var sections = link.siblings('.more_sections');
            var sectionsPreview = link.siblings('.more_sections_preview');

            if (sectionsPreview.is(':visible'))
            {
                sectionsPreview.slideUp();
            }
            if (sections.is(':visible')) {
                sections.slideUp();
                link.html('&#9660;');
            }
            else {
                sections.slideDown();
                link.html('&#9650;');
            }
        }
    );

    // search options toggle
    var sb_height = $('#search_box').height() + 30;
    $("#search_box").css({marginTop: (-sb_height + 30) + 'px'});
    $("#search_box_button").toggle(
        function () {
            $("#search_box").stop().animate({marginTop: '0px'}, 200);
            $("#course_list_box").stop().animate({marginTop: sb_height + 'px'}, 200);
            $("#search_box_button_text").text('Hide advanced options');
        },
        function () {
            $("#search_box").stop().animate({marginTop: (-sb_height + 30) + 'px'}, 200);
            //$("#course_list_box").stop().animate({marginTop: '30px'}, 200);
            $("#search_box_button_text").text('Show advanced options');
        }
    );

    // search result updating
    $('#search_form').submit(function(event) {
        search();
        return false;
    });

    $('#search_form').on('keyup', function(event) {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function() {
            search();
        }, 200);
        return true;
    });

    $('#search_form').submit();
});
