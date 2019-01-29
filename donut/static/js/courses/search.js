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
				// 1 point if occurs at the start of a word in the course number
				if (BOUNDARY_CHARS[number[numberIndex - 1]]) score++
				var nextChar = number[numberIndex + segment.length]
				// 1 point if occurs at the end of a word in the course number,
				// or is followed by a course's term letter (e.g. Ma 1a)
				if (
					BOUNDARY_CHARS[nextChar] ||
					/[a-z]/.test(nextChar) && /\d/.test(number[numberIndex + segment.length - 1])
				) score++
			}
			// 0.1 points per matched letter in course title
			else if (name.indexOf(segment) > -1) score += segment.length * 0.1
		})
		if (score) matches.push({course: course, score: score})
	})
	return matches
		.sort(function(a, b) { return b.score - a.score })
		.map(function(courseScore) { return courseScore.course })
}