var MIN_SEARCH_LENGTH = 3 //minimum number of characters that must be entered to execute a search
var SEARCH_TIMEOUT = 200 //ms

/**
 * Displays matching directory names when the given input's value changes
 * @param nameInput The input to attach to
 * @param resultsList A list-group to populate with search results
 * @param makeElement A function that creates an element to display given a user object
 */
function attachDirectorySearch(nameInput, resultsList, makeElement) {
	var searchToken
	nameInput.keyup(function() {
		var name = nameInput.val()
		if (name.length < MIN_SEARCH_LENGTH) return resultsList.children().remove()
		var token = {}
		searchToken = token
		setTimeout(function() {
			if (searchToken !== token) return //newer request issued
			$.ajax({
				url: '/1/users/search/' + encodeURIComponent(name),
				dataType: 'json',
				success: function(users) {
					if (searchToken !== token) return //newer request issued
					resultsList.children().remove()
					users.forEach(function(user) {
						resultsList.append(makeElement(user))
					})
					if (!users.length) {
						resultsList.append($('<li>').addClass('list-group-item').text('No users found'))
					}
				}
			})
		}, SEARCH_TIMEOUT)
	})
}