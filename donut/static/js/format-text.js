var URL_REGEX = /(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g
function formatText(text, textType) {
  textType = textType || 'p'
  textType = '<' + textType + '>'
  function makeText(text) {
    return $(textType).css('display', 'inline').text(text)
  }
  var lines = text.split('\n')
  var result = $('<div>')
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim()
    var formattedLine = $('<div>')
    var searchIndex = 0, match
    while (match = URL_REGEX.exec(line)) {
      if (match.index > searchIndex) {
        formattedLine.append(makeText(line.substring(searchIndex, match.index)))
      }
      var link = match[0]
      var linkPrefix = link.startsWith('http') ? '' : '//'
      formattedLine.append($('<a>').attr('href', linkPrefix + link).append(makeText(link)))
      searchIndex = match.index + link.length
    }
    if (searchIndex < line.length) {
      formattedLine.append(makeText(line.substring(searchIndex, line.length)))
    }
    result.append(formattedLine)
  }
  return result
}