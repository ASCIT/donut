groupInt = {'bod': 1, 'arc': 2, 'donut': 3}
groupName = {
    'arc': 'Academics and Research Committee (ARC)',
    'bod': 'ASCIT',
    'donut': 'Devteam'
}

msg1 = """ This is the {0} anonymous feedback form.
Ever wanted to suggest something to the {0}, but didn't want to say it directly? Ever wanted to comment about how an event was run, or are curious about how to get involved? Well then, simply fill out the form below. The {0} would love to hear all of your suggestions

Fill in your name and email address if you are willing to have the {0} contact you with follow up questions; this will obviously make your comment non-anonymous, but we do promise to keep comments strictly confidential.
"""
msg2 = """ This is the Donut anonymous feedback form.

Notice a bug on the website? Ever wanted to suggest a new feature for Donut, but didn't want to say it directly? Well then, simply fill out the form below. The Donut Devteam would love to hear all of your suggestions

Fill in your name and email address if you are willing to have the Donut Devteam contact you with follow up questions; this will obviously make your comment non-anonymous, but we do promise to keep comments strictly confidential.
"""
Groups = {'bod': msg1.format('BoD'), 'arc': msg1.format('ARC'), 'donut': msg2}
