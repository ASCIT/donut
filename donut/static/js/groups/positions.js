var groupDict = {}; // Dict of groups
var positionsDict = {}; // Dict of different types of positions
var allPositions = []; // Complete list of all position-group-person pairs
var counter = 0;

/*
 * Initailizes all relevant fields including all groups, positions,
 * position holders and groups with admin access.
 */
function init(approvedGroupIds, approvedGroupNames,
        allPos) {
    filterPositions(allPos);
    getGroupList();
    collectPositions();
    populateTables();
    populateAdminGroups(approvedGroupIds, approvedGroupNames);
}

/*
 * Populates the groups list in the admin tab
 */
function populateAdminGroups(approvedGroupIds, approvedGroupNames) {
    for (var i = 0; i < approvedGroupIds.length; i++) {
        var newOption = '<option value=' + approvedGroupIds[i] + '>' +
            approvedGroupNames[i] + '</option>'
        $('#groupCreate option:last').after(newOption);
        $('#groupDel option:last').after(newOption);
        $('#groupPosHold option:last').after(newOption);
    }
}

/*
 * filters out all positions that have expired/havent happened yet
 */
function filterPositions(allPos) {
    var today = new Date();
    for (var i = 0; i < allPos.length; i++) {
        var s = Date.parse(allPos[i].start_date);
        var e = Date.parse(allPos[i].end_date);
        if (s < today && today < e) {
                allPositions.push(allPos[i])
        }
    }
}

/*
 * Gathers all groups represented in the positions. For each group we add
 * an option to the group select.
 */
function getGroupList() {
    for (var i = 0; i < allPositions.length; i++) {
        var id = allPositions[i].group_id
        if (groupDict[id] === undefined) {
            groupDict[id] = allPositions[i].group_name;
            var newOption = '<option value="' + id + '">'
                                + allPositions[i].group_name + '</option>';
            $('#groupSelect option:last').after(newOption);

        }
    }
}

/*
 * Collects all seperate instance of a position
 */
function collectPositions() {
    for (var j = 0; j < allPositions.length; j++) {
        var id = allPositions[j].pos_id;
        if (positionsDict[id] === undefined) {
            positionsDict[id] = allPositions[j].pos_name;
            var newOption = '<option value=' + id + '>'
                        + allPositions[j].pos_name + '</option>';
            $('#positionSelect option:last').after(newOption);
        }
    }
}

/*
 * Populates the position table with each instance of a positon
 */
function populateTables() {
    for (var i = 0; i < allPositions.length; i++) {
        addRowToTable(allPositions[i]);
    }
}

/*
 * adds specified position as a row on the position table
 * @param {JSON} json specfiying a position
 */
function addRowToTable(pos) {
    var groupId = pos.group_id;
    var posId =  pos.pos_id;
    var studentName = pos.first_name + " " + pos.last_name;
    var userId = pos.user_id;
    var newRow = '<tr>'
        + '<td> <a onclick=changeGroup(' + groupId + ')>'
                            + groupDict[groupId] + '</a> </td>'
        + '<td> <a onclick=changePosition(' + posId + ')>'
                            + positionsDict[posId] + '</a> </td>'
        + '<td> <a href=/1/users/' + userId + ">" + studentName + '</a> </td>'
                + '</tr>';
    $('#positionsTable tbody').append(newRow);
}

/*
 * function to be called when the filter is changed
 */
function filterChange() {
    var groupIndex = parseInt($('#groupSelect').val());
    var posIndex = parseInt($('#positionSelect').val());
    $('#positionsTable tbody > tr').remove();
    for (var i = 0; i < allPositions.length; i++) {
        if (groupIndex !== 0 && groupIndex !== allPositions[i].group_id) {
            continue;
        }
        if (posIndex !== 0 && posIndex !== allPositions[i].pos_id) {
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

/*
 * Called when a group is selected for the "delete position" tab.
 * Queries for all positions associated with the group
 */
function groupDelChange() {
    var groupIndex = $('#groupDel').val();
    $('#position').find('option').remove();
    populateListOfPositions(groupIndex, '#position');
}

/*
 * Called when a group is selected for the "assign position holder" tab.
 * Queries for all positions associated with the group
 */
function groupPosHoldChange() {
    var groupIndex = $('#groupPosHold').val();
    $('#posIdHold').find('option').remove();
    populateListOfPositions(groupIndex, '#posIdHold');
}

/*
 * This method takes in a group id and a select element id and populates
 * the select element with a list of options representing all positions
 * associated with the group
 */
function populateListOfPositions(groupIndex, posSelectId) {
    var url = '/1/groups/' + groupIndex + '/positions/';
    $.ajax({
        url: url,
        success: function(data){
            for (var i = 0; i < data.length; i++) {
                var newOption = '<option value=' + data[i].pos_id + '>' +
                    data[i].pos_name + '</option>';
                $(posSelectId).append(newOption);
            }
        }
    });
}

$(document).ready(function() {
    // Setting up triggers for administration tasks
    $('#submitPosBtn').click(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/1/positions/',
            data: $("#posCreate").serialize(),
            success: function(data) {
                if(data.success) {
                    $('#posCreate').trigger("reset");
                    alert("Position created!");
                }
            }
        });
    });
    $('#delPosBtn').click(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/1/positions/delete/',
            data: $("#posDelete").serialize(),
            success: function(data) {
                if(data.success) {
                    setUpForms();
                    alert("Position Deleted");
                }
            }
        });
    });
    $('#submitPosHoldBtn').click(function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/1/positions/' + $("#posIdHold").val() + '/',
            data: $("#holdForm").serialize(),
            success: function(data) {
                if(data.success) {
                    setUpForms();
                    alert("Assigned Position!")
                }
            }
        });
    });
});

/*
 * Function to be called to reset forms to default
 */
function setUpForms() {
    $('#posDelete').trigger("reset");
    $('#holdForm').trigger("reset")
    $('#position').find('option')
                  .remove()
                  .end()
                  .append('<option>Select a Position</option>');
    $('#posIdHold').find('option')
                    .remove()
                    .end()
                    .append('<option>Select a Position</option>');

}
