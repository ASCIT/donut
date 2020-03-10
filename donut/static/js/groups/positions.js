var groupDict = {}; // Dict of groups
var positionsDict = {}; // Dict of different types of positions
var allPositions; // Complete list of all position-group-person pairs
var controlGroupIds; // group_ids of groups that user has admin privileges for

/*
 * Initailizes all relevant fields including all groups, positions,
 * position holders and groups with admin access.
 */
function init(approvedGroupIds, approvedGroupNames, allPos) {
    allPositions = allPos;
    controlGroupIds = approvedGroupIds;
    getGroupList();
    collectPositions();
    populateTables();
    populateAdminGroups(approvedGroupIds, approvedGroupNames);
    populatePositions();
}

/*
 * Populates the groups list in the admin tab
 */
function populateAdminGroups(approvedGroupIds, approvedGroupNames) {
    for (var i = 0; i < approvedGroupIds.length; i++) {
        $('#groupCreate').append($('<option>')
            .attr('value', approvedGroupIds[i])
            .text(approvedGroupNames[i])
        );
    }
}

/*
 * Gathers all groups represented in the positions. For each group we add
 * an option to the group select.
 */
function getGroupList() {
    allPositions.forEach(function(position) {
        var id = position.group_id
        if (!(id in groupDict)) {
            groupDict[id] = position.group_name;
            $('#groupSelect').append($('<option>')
                .attr('value', id)
                .text(position.group_name)
            );
        }
    })
}

/*
 * Collects all seperate instance of a position
 */
function collectPositions() {
    allPositions.forEach(function(position) {
        var id = position.pos_id;
        if (!(id in positionsDict)) {
            positionsDict[id] = position.pos_name;
            $('#positionSelect').append($('<option>')
                .attr('value', id)
                .text(position.group_name + ' - ' + position.pos_name)
            );
        }
    })
}

/*
 * Populates the position table with each instance of a positon
 */
function populateTables() {
    allPositions.forEach(addRowToTable);
}

/*
 * adds specified position as a row on the position table
 */
function addRowToTable(pos) {
    $('#positionsTable tbody').append($('<tr>').append(
        $('<td>').append($('<a>')
            .text(pos.group_name)
            .click(function() { changeGroup(pos.group_id) })
        ),
        $('<td>').append($('<a>')
            .text(pos.pos_name)
            .click(function() { changePosition(pos.pos_id) })
        ),
        $('<td>').append(
            $('<a>').attr('href', '/1/users/' + pos.user_id).text(pos.full_name)
        )
    ));
}

/*
 * function to be called when the filter is changed
 */
function filterChange() {
    var groupIndex = parseInt($('#groupSelect').val());
    var posIndex = parseInt($('#positionSelect').val());
    $('#positionsTable tbody tr').remove();
    allPositions.forEach(function(position) {
        // If filtering by position, ignore the group filter
        if (posIndex
            ? posIndex == position.pos_id
            : (!groupIndex || groupIndex === position.group_id)
        ) {
            addRowToTable(position);
        }
    });
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
 * Finds all positions in groups that user controls,
 * and adds them to the positions dropdown.
 * Also finds all holds for those positions and adds them to the holds dropdown.
 */
function populatePositions() {
    var posSelect = $('#posIdHold');
    posSelect.children().slice(1).remove();
    $('#posHold').children().slice(1).remove();
    controlGroupIds.forEach(function(groupId) {
        $.ajax({
            url: '/1/groups/' + groupId + '/positions',
            success: function(data) {
                data.forEach(function(position) {
                    var posId = position.pos_id;
                    var posName = groupDict[groupId] + ' - ' + position.pos_name;
                    posSelect.append(
                        $('<option>').attr('value', posId).text(posName)
                    );
                    populateHolders(posId, posName);
                });
            }
        });
    });
}

function populateHolders(posId, posName) {
    $.ajax({
        url: '/1/positions/' + posId,
        success: function(data) {
            data.forEach(function(holder) {
                $('#posHold').append($('<option>')
                    .attr('value', holder.hold_id)
                    .text(posName + ': ' + holder.full_name)
                );
            });
        }
    });
}

function submitPosForm() {
    $.ajax({
        type: 'POST',
        url: '/1/positions',
        data: $("#posCreate").serialize(),
        success: function(data) {
            if (data.success) {
                alert("Position created!");
                $('#posCreate').trigger("reset");
                populatePositions();
            }
            else alert('Failed to add position: ' + data.message);
        }
    });
}

function submitHoldForm() {
    var posId = $("#posIdHold").val();
    if (isNaN(posId)) {
        alert('Please select a position to assign');
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/1/positions/' + posId,
        data: $("#holdForm").serialize(),
        success: function(data) {
            if (data.success) {
                alert("Assigned position!");
                $('#holdForm').trigger("reset");
                populatePositions();
            }
            else alert('Failed to add position holder: ' + data.message);
        }
    });
}

function submitRemoveHoldForm() {
    var holdId = $('#posHold').val();
    if (isNaN(holdId)) {
        alert('Please select a position holder to remove');
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/1/position_holds/' + holdId,
        success: function(data) {
            if (data.success) {
                alert('Removed position holder!');
                $('#removeHoldForm').trigger("reset");
                populatePositions();
            }
            else alert('Failed to remove position holder: ' + data.message);
        }
    });
}
