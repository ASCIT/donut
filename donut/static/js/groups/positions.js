var groupDict = {}; // Dict of groups
var positionsDict = {}; // Dict of different types of positions
var allPositions; // Complete list of all position-group-person pairs
var controlGroupIds; // group_ids of groups that user has admin privileges for
var adminPositionsData = {}; // Stores position data for admin table: {posId: {group_id, group_name, pos_name, holders: []}}

/*
 * Format a date string for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '—';
    var date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return months[date.getMonth()] + ' ' + date.getDate() + ', ' + date.getFullYear();
}

/*
 * Format a Date object as YYYY-MM-DD for date input fields
 */
function formatDateForInput(date) {
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    return year + '-' + month + '-' + day;
}

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
    if (approvedGroupIds.length > 0) {
        loadAdminPositionsTable();
    }
}

/*
 * Populates the groups list in the admin tab
 */
function populateAdminGroups(approvedGroupIds, approvedGroupNames) {
    var adminFilterSelect = $('#adminGroupFilter');
    for (var i = 0; i < approvedGroupIds.length; i++) {
        var groupId = approvedGroupIds[i];
        var groupName = approvedGroupNames[i];
        groupDict[groupId] = groupName;
        adminFilterSelect.append($('<option>').attr('value', groupId).text(groupName));
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


/*
 * Load all positions for admin table (single API call)
 */
function loadAdminPositionsTable(callback) {
    adminPositionsData = {};

    if (controlGroupIds.length === 0) {
        renderAdminTable();
        return;
    }

    $.ajax({
        url: '/1/admin/positions?group_ids=' + controlGroupIds.join(','),
        success: function(data) {
            data.positions.forEach(function(pos) {
                adminPositionsData[pos.pos_id] = {
                    group_id: pos.group_id,
                    group_name: pos.group_name,
                    pos_name: pos.pos_name,
                    pos_id: pos.pos_id,
                    send: pos.send,
                    control: pos.control,
                    receive: pos.receive,
                    holders: pos.holders || []
                };
            });
            renderAdminTable();
            if (callback) callback();
        }
    });
}

/*
 * Reload holders for a specific position after add/remove
 */
function reloadPositionHolders(posId, callback) {
    $.ajax({
        url: '/1/positions/' + posId,
        success: function(holders) {
            if (adminPositionsData[posId]) {
                adminPositionsData[posId].holders = holders;
            }
            if (callback) callback();
        }
    });
}

/*
 * Render the admin positions table
 */
function renderAdminTable() {
    var tbody = $('#adminPositionsTable tbody');
    tbody.empty();

    var filterGroupId = parseInt($('#adminGroupFilter').val());

    // Sort positions by group name then position name
    var sortedPositions = Object.values(adminPositionsData).sort(function(a, b) {
        if (a.group_name !== b.group_name) {
            return a.group_name.localeCompare(b.group_name);
        }
        return a.pos_name.localeCompare(b.pos_name);
    });

    // Group positions by group_id
    var positionsByGroup = {};
    var groupInfo = {};
    sortedPositions.forEach(function(pos) {
        if (filterGroupId && pos.group_id !== filterGroupId) {
            return;
        }
        if (!positionsByGroup[pos.group_id]) {
            positionsByGroup[pos.group_id] = [];
            groupInfo[pos.group_id] = { name: pos.group_name, id: pos.group_id };
        }
        positionsByGroup[pos.group_id].push(pos);
    });

    // Render each group's positions
    Object.keys(positionsByGroup).forEach(function(groupId) {
        var positions = positionsByGroup[groupId];
        var group = groupInfo[groupId];
        var isFirstRow = true;

        positions.forEach(function(pos) {
            var row = $('<tr>').attr('data-pos-id', pos.pos_id).attr('data-group-id', pos.group_id);

            // Group name cell with delete button (only on first row)
            var groupCell = $('<td>');
            if (isFirstRow) {
                groupCell.text(pos.group_name);
                groupCell.append(
                    $('<button>')
                        .addClass('btn-delete-group')
                        .attr('title', 'Delete group (only works if empty)')
                        .text('×')
                        .click(function(e) {
                            e.stopPropagation();
                            deleteGroup(pos.group_id, pos.group_name);
                        })
                );
                isFirstRow = false;
            }
            row.append(groupCell);

            // Position name cell with delete button (only if no holders)
            var posCell = $('<td>').text(pos.pos_name);
            if (!pos.holders || pos.holders.length === 0) {
                posCell.append(
                    $('<button>')
                        .addClass('btn-delete-position')
                        .attr('title', 'Delete position')
                        .text('×')
                        .click(function(e) {
                            e.stopPropagation();
                            deletePosition(pos.pos_id, pos.pos_name);
                        })
                );
            }
            row.append(posCell);

            // Settings cell with checkboxes
            var settingsCell = $('<td>').addClass('settings-cell');
            settingsCell.append(createSettingsCheckboxes(pos));
            row.append(settingsCell);

            var holdersCell = $('<td>').addClass('holders-cell');

            if (pos.holders && pos.holders.length > 0) {
                pos.holders.forEach(function(holder) {
                    var chip = $('<span>').addClass('holder-chip');
                    var nameLink = $('<a>')
                        .addClass('holder-name')
                        .text(holder.full_name)
                        .click(function(e) {
                            e.preventDefault();
                            chip.toggleClass('expanded');
                            chip.find('.holder-dates').toggle();
                        });
                    chip.append(nameLink);
                    chip.append(
                        $('<button>')
                            .addClass('btn-remove')
                            .attr('data-hold-id', holder.hold_id)
                            .attr('title', 'Remove holder')
                            .text('×')
                            .click(function(e) {
                                e.stopPropagation();
                                removeHolder(holder.hold_id, holder.full_name, pos.pos_id);
                            })
                    );
                    var dates = $('<div>').addClass('holder-dates').css('display', 'none');
                    dates.append(
                        $('<div>').addClass('date-row').append(
                            $('<span>').addClass('date-label').text('Start:'),
                            $('<span>').addClass('date-value').text(formatDate(holder.start_date))
                        )
                    );
                    dates.append(
                        $('<div>').addClass('date-row').append(
                            $('<span>').addClass('date-label').text('End:'),
                            $('<span>').addClass('date-value').text(formatDate(holder.end_date))
                        )
                    );
                    dates.append(
                        $('<a>').addClass('profile-link').attr('href', '/1/users/' + holder.user_id).text('View Profile')
                    );
                    chip.append(dates);
                    holdersCell.append(chip);
                });
            } else {
                holdersCell.append($('<span>').addClass('no-holders').text('(none)'));
            }

            // Add holder button
            holdersCell.append(
                $('<button>')
                    .addClass('btn-add-holder')
                    .text('+ Add')
                    .click(function() { showAddHolderForm(pos.pos_id, $(this).closest('tr')); })
            );

            // Hidden add holder form
            var addForm = createAddHolderForm(pos.pos_id);
            holdersCell.append(addForm);

            row.append(holdersCell);
            tbody.append(row);
        });

        // Add "+ Add Position" row for this group
        var addPosRow = $('<tr>').addClass('add-position-row').attr('data-group-id', groupId);
        addPosRow.append($('<td>')); // Empty group cell
        addPosRow.append(
            $('<td>').attr('colspan', '3').append(
                $('<button>')
                    .addClass('btn-add-position')
                    .text('+ Add Position')
                    .click(function() { showAddPositionForm(group.id, group.name, $(this).closest('tr')); }),
                createAddPositionForm(group.id)
            )
        );
        tbody.append(addPosRow);
    });
}

// Tooltip descriptions for position settings
var SETTING_TOOLTIPS = {
    receive: 'Receive emails: When someone sends an email to this group\'s mailing list, holders of this position will receive it in their inbox (unless they personally unsubscribe).',
    send: 'Send emails: Holders of this position can send emails to the group\'s mailing list. The email will appear as "Position Name (Person\'s Name)" so recipients know who sent it.',
    control: 'Manage group: Holders of this position can create/edit/delete positions, add/remove position holders, and view applications to the group.'
};

/*
 * Create settings checkboxes for a position
 */
function createSettingsCheckboxes(pos) {
    var container = $('<span>').addClass('pos-settings');

    var receiveLabel = $('<label>')
        .addClass('setting-checkbox')
        .attr('title', SETTING_TOOLTIPS.receive);
    var receiveCheckbox = $('<input>')
        .attr('type', 'checkbox')
        .prop('checked', pos.receive)
        .change(function() { updatePositionSetting(pos.pos_id, container); });
    receiveLabel.append(receiveCheckbox, ' R');
    container.append(receiveLabel);

    var sendLabel = $('<label>')
        .addClass('setting-checkbox')
        .attr('title', SETTING_TOOLTIPS.send);
    var sendCheckbox = $('<input>')
        .attr('type', 'checkbox')
        .prop('checked', pos.send)
        .change(function() { updatePositionSetting(pos.pos_id, container); });
    sendLabel.append(sendCheckbox, ' S');
    container.append(sendLabel);

    var controlLabel = $('<label>')
        .addClass('setting-checkbox')
        .attr('title', SETTING_TOOLTIPS.control);
    var controlCheckbox = $('<input>')
        .attr('type', 'checkbox')
        .prop('checked', pos.control)
        .change(function() { updatePositionSetting(pos.pos_id, container); });
    controlLabel.append(controlCheckbox, ' M');
    container.append(controlLabel);

    // Store references for easy access
    container.data('receive', receiveCheckbox);
    container.data('send', sendCheckbox);
    container.data('control', controlCheckbox);

    return container;
}

/*
 * Update position settings via API
 */
function updatePositionSetting(posId, container) {
    var receive = container.data('receive').is(':checked') ? '1' : '0';
    var send = container.data('send').is(':checked') ? '1' : '0';
    var control = container.data('control').is(':checked') ? '1' : '0';

    $.ajax({
        type: 'PUT',
        url: '/1/positions/' + posId,
        data: {
            receive: receive,
            send: send,
            control: control
        },
        success: function(data) {
            if (!data.success) {
                alert('Failed to update position: ' + data.message);
                // Reload to reset checkboxes
                loadAdminPositionsTable();
            }
        },
        error: function() {
            alert('Failed to update position');
            loadAdminPositionsTable();
        }
    });
}

/*
 * Create inline add position form
 */
function createAddPositionForm(groupId) {
    var form = $('<div>').addClass('add-position-form').css('display', 'none');

    var nameField = $('<div>').addClass('form-field').css('display', 'inline-block').css('margin-right', '10px');
    nameField.append($('<label>').text('Position Name: '));
    var nameInput = $('<input>')
        .addClass('pos-name-input')
        .attr('placeholder', 'e.g. Secretary')
        .css('width', '150px');
    nameField.append(nameInput);

    var checkboxes = $('<span>').addClass('pos-checkboxes');
    checkboxes.append(
        $('<label>').css('margin-right', '10px').attr('title', SETTING_TOOLTIPS.receive).append(
            $('<input>').attr('type', 'checkbox').addClass('pos-receive').prop('checked', true),
            ' Receive'
        )
    );
    checkboxes.append(
        $('<label>').css('margin-right', '10px').attr('title', SETTING_TOOLTIPS.send).append(
            $('<input>').attr('type', 'checkbox').addClass('pos-send'),
            ' Send'
        )
    );
    checkboxes.append(
        $('<label>').css('margin-right', '10px').attr('title', SETTING_TOOLTIPS.control).append(
            $('<input>').attr('type', 'checkbox').addClass('pos-control'),
            ' Manage'
        )
    );

    var buttons = $('<span>').addClass('pos-buttons');
    buttons.append(
        $('<button>').addClass('btn btn-success btn-sm').text('Create').click(function() {
            submitInlinePositionForm(groupId, form);
        })
    );
    buttons.append(' ');
    buttons.append(
        $('<button>').addClass('btn btn-default btn-sm').text('Cancel').click(function() {
            hideAddPositionForm(form);
        })
    );

    form.append(nameField, checkboxes, buttons);
    return form;
}

/*
 * Show inline add position form
 */
function showAddPositionForm(groupId, groupName, row) {
    $('.add-position-form').hide();
    $('.btn-add-position').show();

    var form = row.find('.add-position-form');
    row.find('.btn-add-position').hide();
    form.show();
    form.find('.pos-name-input').focus();
}

/*
 * Hide inline add position form
 */
function hideAddPositionForm(form) {
    form.hide();
    form.find('.pos-name-input').val('');
    form.find('.pos-receive').prop('checked', true);
    form.find('.pos-send').prop('checked', false);
    form.find('.pos-control').prop('checked', false);
    form.closest('tr').find('.btn-add-position').show();
}

/*
 * Submit inline position form
 */
function submitInlinePositionForm(groupId, form) {
    var posName = form.find('.pos-name-input').val().trim();
    if (!posName) {
        alert('Please enter a position name');
        return;
    }

    var data = {
        group_id: groupId,
        pos_name: posName
    };
    if (form.find('.pos-receive').is(':checked')) data.receive = 'on';
    if (form.find('.pos-send').is(':checked')) data.send = 'on';
    if (form.find('.pos-control').is(':checked')) data.control = 'on';

    $.ajax({
        type: 'POST',
        url: '/1/positions',
        data: data,
        success: function(response) {
            if (response.success) {
                hideAddPositionForm(form);
                loadAdminPositionsTable();
                refreshViewAllTable();
            } else {
                alert('Failed to create position: ' + response.message);
            }
        }
    });
}

/*
 * Create the inline add holder form
 */
function createAddHolderForm(posId) {
    var form = $('<div>').addClass('add-holder-form').css('display', 'none');
    var formRow = $('<div>').addClass('form-row');

    // Name field
    var nameField = $('<div>').addClass('form-field').css('position', 'relative');
    nameField.append($('<label>').text('Person'));
    var nameInput = $('<input>')
        .addClass('name-search')
        .attr('placeholder', 'Search by name...')
        .attr('autocomplete', 'off')
        .css('width', '180px');
    var searchResults = $('<ul>').addClass('name-search-results');
    var userIdInput = $('<input>').attr('type', 'hidden').addClass('user-id-input');
    nameField.append(nameInput, searchResults, userIdInput);

    // Start date field
    var startField = $('<div>').addClass('form-field');
    startField.append($('<label>').text('Start Date'));
    var today = new Date();
    var nextYear = new Date();
    nextYear.setFullYear(nextYear.getFullYear() + 1);

    var startDate = $('<input>')
        .attr('type', 'date')
        .addClass('start-date')
        .css('width', '140px')
        .val(formatDateForInput(today));
    startField.append(startDate);

    // End date field
    var endField = $('<div>').addClass('form-field');
    endField.append($('<label>').text('End Date'));
    var endDate = $('<input>')
        .attr('type', 'date')
        .addClass('end-date')
        .css('width', '140px')
        .val(formatDateForInput(nextYear));
    endField.append(endDate);

    // Buttons
    var btnGroup = $('<div>').addClass('btn-group');
    var saveBtn = $('<button>')
        .addClass('btn btn-success')
        .text('Save')
        .click(function() { saveHolder(posId, form); });
    var cancelBtn = $('<button>')
        .addClass('btn btn-default')
        .text('Cancel')
        .click(function() { hideAddHolderForm(form); });
    btnGroup.append(saveBtn, cancelBtn);

    formRow.append(nameField, startField, endField, btnGroup);
    form.append(formRow);

    // Attach directory search
    attachDirectorySearch(nameInput, searchResults, function(user) {
        return $('<li>').append($('<a>')
            .text(user.full_name)
            .click(function() {
                nameInput.val(user.full_name);
                searchResults.children().remove();
                userIdInput.val(user.user_id);
            })
        );
    });

    return form;
}

/*
 * Show the add holder form for a row
 */
function showAddHolderForm(posId, row) {
    // Hide any other open forms
    $('.add-holder-form').hide();
    $('.btn-add-holder').show();

    var form = row.find('.add-holder-form');
    var addBtn = row.find('.btn-add-holder');
    addBtn.hide();
    form.show();
    form.find('.name-search').focus();
}

/*
 * Hide the add holder form
 */
function hideAddHolderForm(form) {
    form.hide();
    form.find('.name-search').val('');
    form.find('.user-id-input').val('');
    form.find('.start-date').val('');
    form.find('.end-date').val('');
    form.find('.name-search-results').empty();
    form.closest('tr').find('.btn-add-holder').show();
}

/*
 * Save a new holder
 */
function saveHolder(posId, form) {
    var userId = form.find('.user-id-input').val();
    var startDate = form.find('.start-date').val();
    var endDate = form.find('.end-date').val();

    if (!userId) {
        alert('Please select a person from the search results');
        return;
    }
    if (!startDate || !endDate) {
        alert('Please enter both start and end dates');
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/1/positions/' + posId,
        data: {
            user_id: userId,
            start_date: startDate,
            end_date: endDate
        },
        success: function(data) {
            if (data.success) {
                hideAddHolderForm(form);
                reloadPositionHolders(posId, renderAdminTable);
                refreshViewAllTable();
            } else {
                alert('Failed to add position holder: ' + data.message);
            }
        }
    });
}

/*
 * Remove a holder with confirmation
 */
function removeHolder(holdId, holderName, posId) {
    if (!confirm('Remove ' + holderName + ' from this position?')) {
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/1/position_holds/' + holdId,
        success: function(data) {
            if (data.success) {
                reloadPositionHolders(posId, renderAdminTable);
                refreshViewAllTable();
            } else {
                alert('Failed to remove position holder: ' + data.message);
            }
        }
    });
}

/*
 * Admin group filter change handler
 */
function adminFilterChange() {
    renderAdminTable();
}

/*
 * Refresh the view all positions table via AJAX (no page reload)
 */
function refreshViewAllTable() {
    $.ajax({
        url: '/1/positions',
        success: function(data) {
            allPositions = data;
            filterChange(); // Re-renders with current filter applied
        }
    });
}


/*
 * Toggle the create group form visibility
 */
function toggleCreateGroupForm() {
    $('#createGroupForm').toggle();
}

/*
 * Submit the create group form
 */
function submitGroupForm() {
    $.ajax({
        type: 'POST',
        url: '/1/groups',
        data: $('#groupCreateForm').serialize(),
        success: function(data) {
            if (data.success) {
                alert('Group created!');
                $('#groupCreateForm').trigger('reset');
                toggleCreateGroupForm();
                // Reload the page to get updated group list
                location.reload();
            } else {
                alert('Failed to create group: ' + data.message);
            }
        }
    });
}

/*
 * Delete a group (only if empty)
 */
function deleteGroup(groupId, groupName) {
    if (!confirm('Are you sure you want to delete the group "' + groupName + '"?\n\nThis can only succeed if the group has no members.')) {
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/1/groups/' + groupId,
        success: function(data) {
            if (data.success) {
                alert('Group deleted!');
                location.reload();
            } else {
                alert('Failed to delete group: ' + data.message);
            }
        }
    });
}

/*
 * Delete a position (only if no holders)
 */
function deletePosition(posId, posName) {
    if (!confirm('Are you sure you want to delete the position "' + posName + '"?')) {
        return;
    }

    $.ajax({
        type: 'DELETE',
        url: '/1/positions/' + posId,
        success: function(data) {
            if (data.success) {
                // Remove from local data immediately
                delete adminPositionsData[posId];
                renderAdminTable();
                refreshViewAllTable();
            } else {
                alert('Failed to delete position: ' + data.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Error deleting position: ' + error);
        }
    });
}
