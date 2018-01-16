var groupDict = {}; // Dict of groups
var positionsDict = {}; // Dict of different types of positions
var allPositions = []; // Complete list of all position-group-person pairs
var counter = 0;

/*
 * Gathers the total list of groups from the groups endpoint.
 * for each group, it calls the collectPositions method on it
 */
function getGroupList() {
    coutner = 0;
    $.getJSON('/1/groups/', function(groups) {
        for (var i = 0; i < groups.length; i++) {
            var newOption = '<option value="' + groups[i].group_id + '">' 
                                            + groups[i].group_name + '</option>';
            $('#groupSelect option:last').after(newOption);
            groupDict[groups[i].group_id] = groups[i].group_name;
        }
        collectPositions(groups);
    });
}

/*
 * Takes in a list of groups and for each looks through the positions of
 * each and adds it to a list.
 * @param {List<Groups>} List of groups
 */
function collectPositions(groups) {
    for (var i = 0; i < groups.length; i++) {
        collectPositionFromGroup(groups[i]);
    }
}

/*
 * Collects all positions from a single group
 */
function collectPositionFromGroup(group) {
    $.getJSON('/1/groups/' + group.group_id + '/positions/', function(positions) {
        for (var j = 0; j < positions.length; j++) {
            var temp = positions[j].pos_name in positionsDict;
            if (!temp) {
                positionsDict[positions[j].pos_name] = counter;
                var newOption = '<option value=' + counter + '>' 
                                                + positions[j].pos_name + '</option>';
                $('#positionSelect option:last').after(newOption);
                counter++;
            }
        }
    });
}

/*
 * This function takes in a position id, group id, pos name, looks up all
 * students associated with the position and adds each student as a row
 * to the table
 */
function collectStudentsFromPosition(pos_id, group_id, pos_nam) {
    $.getJSON('/1/positions/'+pos_id, function(people){
        for (var i = 0; i < people.length; i++) {
            var firstName = people[i].first_name;
            var lastName = people[i].last_name;
            var name = firstName + ' ' + lastName;
            var userId = people[i].user_id;
            var text = '{ "groupId":' + group.group_id + ',' +
                        '"positionName":"' + positions[j].pos_name + '",' +
                        '"studentName":"' + name +'",' +
                        '"studentId":' + userId + '}';
            var json = JSON.parse(text);
            allPositions.push(json);
            addRowToTable(json);
     
        }
    });
}

/*
 * adds specified position as a row on the position table 
 * @param {JSON} json specfiying a position
 */
function addRowToTable(pos) {
    var newRow = '<tr>'  
           + '<td> <a onclick=changeGroup(' + pos.groupId + ')>' 
                            + groupDict[pos.groupId] + '</a> </td>'
           + '<td> <a onclick=changePosition(' + positionsDict[pos.positionName] + ')>' 
                            + pos.positionName + '</a> </td>'
           + '<td>' + pos.studentName + '</td>' 
                + '</tr>';
    $('#positionsTable tbody').append(newRow);
}

/*
 * function to be called when the filter is changed
 */
function filterChange() {
    var groupIndex = $('#groupSelect').prop('selectedIndex');
    var posIndex = $('#positionSelect').prop('selectedIndex');
    var groupName = $('#groupSelect').find(":selected").text();
    var posName = $('#positionSelect').find(":selected").text();
    $('#positionsTable tbody > tr').remove();
    for (var i = 0; i < allPositions.length; i++) {
        if (groupIndex !== 0 && groupName !== groupDict[allPositions[i].groupId]) {
            continue;
        }
        if (posIndex !== 0 && posName !== allPositions[i].positionName) {
            continue;
        }
        addRowToTable(allPositions[i]);
    }
}

function changeGroup(groupId) {
    $('#groupSelect').val(groupId);
    filterChange();
}

function changePosition(posName) {
    $('#positionSelect').val(posName);
    filterChange();
}
