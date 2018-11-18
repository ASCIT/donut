var BOUNDARY_CHARS = {
	' ': true,
	'/': true,
	undefined: true
}

/**
 * Filters a list of courses by whether they match a query string.
 * Sorts courses from highest matching score to lowest.
 */
function searchCourses(courses, query) {
	query = query.trim()
		.toLowerCase()
		.split(/[ /]+/)
	var matches = []
	courses.forEach(function(course) {
		var number = course.number.toLowerCase(),
			name = course.name.toLowerCase()
		var score = 0
		query.forEach(function(segment) {
			var numberIndex = number.indexOf(segment)
			if (numberIndex > -1) {
				score += segment.length
				if (BOUNDARY_CHARS[number[numberIndex - 1]]) score++
				if (BOUNDARY_CHARS[number[numberIndex + segment.length]]) score++
			}
			else if (name.indexOf(segment) > -1) score += segment.length * 0.1
		})
		if (score) matches.push({course: course, score: score})
	})
	return matches
		.sort(function(a, b) { return b.score - a.score })
		.map(function(courseScore) { return courseScore.course })
}