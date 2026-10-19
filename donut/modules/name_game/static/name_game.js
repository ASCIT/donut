/**
 * Name game: shows one face at a time and asks for the name that goes with
 * it. The roster of people to play with, and the names that are accepted as an
 * answer for each of them, come from the server, and the game itself is played
 * here in the browser.
 */
var nameGame = (function() {
  var MULTIPLE_CHOICE = 'multiple_choice'
  var NUM_CHOICES = 4
  // The keys that select a name in multiple choice mode, as key codes, which
  // is what jQuery 1 reports for them.
  var CHOICE_KEYS = {49: 0, 50: 1, 51: 2, 52: 3}

  function play(roster, mode, setupUrl) {
    var multipleChoice = mode === MULTIPLE_CHOICE
    var faces = shuffle(roster)
    var choices = []
    var missed = []
    var numCorrect = 0
    var numShown = 0
    var current = null

    function showScore() {
      $('#score').text(
        'Face ' + numShown + ' of ' + faces.length + ', ' + numCorrect +
        ' correct so far')
    }

    function setFeedback(text, className) {
      $('#feedback')
        .removeClass('text-success text-danger')
        .addClass(className)
        .text(text)
    }

    function answered(correct) {
      if (correct) {
        setFeedback('Correct!', 'text-success')
        numCorrect++
      } else {
        setFeedback('That was ' + current.name + '.', 'text-danger')
        missed.push(current)
      }
      // A face is only answered once.
      choices = []
      $('#answers').find('button, input').prop('disabled', true)
      $('#next').show()
    }

    function choose(choice) {
      answered(choice.id === current.id)
    }

    function typeName(name) {
      answered(current.answers.indexOf(normalizeName(name)) >= 0)
    }

    function showChoices() {
      // The face being shown is one of the choices, along with three other
      // people from the roster.
      var others = shuffle(faces.filter(function(person) {
        return person.id !== current.id
      })).slice(0, NUM_CHOICES - 1)
      choices = shuffle(others.concat([current]))
      var list = $('<div>').addClass('list-group')
      choices.forEach(function(choice, index) {
        list.append(
          $('<button>')
            .addClass('list-group-item name-choice')
            .append(
              $('<span>').addClass('name-choice-key').text(index + 1),
              $('<span>').addClass('name-choice-name').text(choice.name))
            .click(function() { choose(choice) }))
      })
      $('#answers').empty().append(list)
    }

    function showNameInput() {
      var input = $('<input>')
        .addClass('form-control name-answer')
        .attr('placeholder', 'Name')
      var form = $('<form>').addClass('form-inline').append(
        input,
        $('<button>').addClass('btn btn-primary').text('Answer'))
      form.submit(function(event) {
        event.preventDefault()
        typeName(input.val())
      })
      $('#answers').empty().append(form)
      input.focus()
    }

    function missedFace(face) {
      return $('<li>').addClass('list-group-item').append(
        $('<img>').addClass('missed-face').attr('src', face.image),
        $('<span>').text(face.name))
    }

    function showResults() {
      $('#score').text('')
      $('#feedback').empty()
      $('#face').empty()
      $('#answers').empty()
      $('#next').hide()
      var results = $('<div>').empty().append(
        $('<h3>').text(
          'You got ' + numCorrect + ' of ' + faces.length + ' right.'))
      if (missed.length) {
        results.append(
          $('<h4>').text('Faces to practice:'),
          $('<ul>').addClass('list-group').append(missed.map(missedFace)))
      }
      results.append(
        $('<p>').append(
          // Reloading this page plays with a different set of people that
          // match the same filters.
          $('<a>').attr('href', window.location.href)
            .addClass('btn btn-primary').text('Play again'),
          ' ',
          $('<a>').attr('href', setupUrl).text('Change the filters')))
      $('#results').show().empty().append(results)
    }

    function showRound() {
      if (numShown >= faces.length) return showResults()
      current = faces[numShown]
      numShown++
      showScore()
      $('#feedback').empty()
      $('#next').hide()
      $('#face').empty().append(
        $('<img>').addClass('img-responsive').attr('src', current.image))
      if (multipleChoice) showChoices()
      else showNameInput()
    }

    function nextRound() {
      $('#face').empty()
      $('#answers').empty()
      showRound()
    }

    // The number keys pick a name in multiple choice mode.
    $(document).on('keydown', function(event) {
      if (event.altKey || event.ctrlKey || event.metaKey) return
      var index = CHOICE_KEYS[event.which]
      if (index === undefined || !choices[index]) return
      event.preventDefault()
      choose(choices[index])
    })

    $('#next').click(nextRound)
    showRound()
  }

  /** Returns the name in a form that can be compared case insensitively. */
  function normalizeName(name) {
    return name.toLowerCase().replace(/[.,'’]/g, '').split(/\s+/).filter(
      function(word) { return word.length > 0 }).join(' ')
  }

  /** Returns the given list in random order. */
  function shuffle(list) {
    for (var i = list.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1))
      var swap = list[i]
      list[i] = list[j]
      list[j] = swap
    }
    return list
  }

  return {'play': play}
})()