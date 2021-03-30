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
}

/*
 * Populates the groups list in the admin tab
 */
function populateAdminGroups(approvedGroupIds, approvedGroupNames) {
    var selects = [$('#groupCreate'), $('#groupIdHold'), $('#groupIdHolder')];
    for (var i = 0; i < approvedGroupIds.length; i++) {
        var groupId = approvedGroupIds[i];
        var groupName = approvedGroupNames[i];
        groupDict[groupId] = groupName;
        selects.forEach(function(select) {
            select.append($('<option>').attr('value', groupId).text(groupName));
        });
    }
}

/*
 * Gathers all groups represented in the positions. For each group we add
 * an option to the group select.
 */
function getGroupList() {
    var addedGroups = {};
    allPositions.forEach(function(position) {
        var id = position.group_id;
        if (addedGroups[id]) return;

        addedGroups[id] = true;
        $('#groupSelect').append($('<option>')
            .attr('value', id)
            .text(position.group_name)
        );
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

function populatePositions(groupSelect, posSelect) {
    var children = posSelect.children();
    children.slice(1).remove();
    var groupId = groupSelect.val();
    if (isNaN(groupId)) return;

    var selectHeader = children.eq(0);
    selectHeader.text('Loading...');
    $.ajax({
        url: '/1/groups/' + groupId + '/positions',
        success: function(data) {
            data.forEach(function(position) {
                posSelect.append($('<option>')
                    .attr('value', position.pos_id)
                    .text(position.pos_name)
                );
            });
            selectHeader.text('Pick a Position');
        }
    });
}

function populateAddPositions() {
    populatePositions($('#groupIdHold'), $('#posIdHold'));
}

function populateRemovePositions() {
    populatePositions($('#groupIdHolder'), $('#posIdHolder'));
}

function populateHolders() {
    var holderSelect = $('#holdId');
    var children = holderSelect.children();
    children.slice(1).remove();
    var posId = $('#posIdHolder').val();
    if (isNaN(posId)) return;

    var selectHeader = children.eq(0);
    selectHeader.text('Loading...');
    $.ajax({
        url: '/1/positions/' + posId,
        success: function(data) {
            data.forEach(function(holder) {
                holderSelect.append($('<option>')
                    .attr('value', holder.hold_id)
                    .text(holder.full_name)
                );
            });
            selectHeader.text('Pick a Position Holder');
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
                populateAddPositions();
                populateRemovePositions();
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
                populateAddPositions();
            }
            else alert('Failed to add position holder: ' + data.message);
        }
    });
}

function submitRemoveHoldForm() {
    var holdId = $('#holdId').val();
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
                populateRemovePositions();
                populateHolders();
            }
            else alert('Failed to remove position holder: ' + data.message);
        }
    });
}
