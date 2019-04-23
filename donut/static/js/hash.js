function hashString(str) {
	var hash = 0
	for (var i = 0; i < str.length; i++) {
		hash = ((hash << 5) - hash) ^ str.charCodeAt(i)
	}
	return hash
}