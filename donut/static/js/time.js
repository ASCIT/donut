function timezoneName(timezoneOffset) {
	var timezoneName = 'GMT'
	if (timezoneOffset) {
		timezoneName += timezoneOffset < 0 ? '-' : '+'
		var absoluteTimezoneOffset = Math.abs(timezoneOffset)
		timezoneName += String(Math.floor(absoluteTimezoneOffset / 60))
		timezoneName += ':'
		var offsetMinutes = absoluteTimezoneOffset % 60
		if (offsetMinutes < 10) timezoneName += '0'
		timezoneName += String(offsetMinutes)
	}
	return timezoneName
}
