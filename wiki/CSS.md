Welcome to the Donut Style Guide™. This is here to assist you in formatting
your HTML such that it conforms to the rest of the website.

# Important Notes

For the love of all that is good in the world, wrap your content in a 
main container and then a jumbotron:

    <div class="container theme-showcase" role="main">
        <div class="jumbotron">...</div>
    </div>

If you don't do this, your HTML will break on mobile. Nobody wants that.

Also note that all of the CSS is designed to be modular so you can just
reference multiple classes in a single element to make it how you want it to
be. 

For instance:

    <div class="half-float-right medium-text">...</div>

This makes it easy to format anything you want to include in the body without
having to code your own classes!

# Color

Orange.

All links are made such that there is an orange color transition -- this is,
of course, a prominent theme of the website given that Caltech's colors are
white and orange. This is also true for buttons and, honestly, anything you
can hover. All borders are also orange. This includes forms, unhovered 
buttons, etc.

By default this orange color is what CSS has pre-defined as orange, which is
`#FFA500`. Hovered links become a darker orange, `#CD6600`. 

There are actually other colors on the website. Specifically, `#222` is used
as the navbar background, `#080808` is used as the navbar border, `#333` is
used for paragraph text, and, of course, `#FFF` is used for filler and for
text on darker background.

# Buttons

All buttons are automatically equipped with a simple opacity transition,
however to make the button fully formatted and theme compliant, make sure it 
has the `.btn` class.

    <button class="btn">Wow, what a button.</button>

# Containers

As previously mentioned, wrap all of your main content in a jumbotron. That
means the first and only child of the body should be a div with the jumbotron
class. Note that the jumbotron includes several classes that will format forms
automatically.

If you want to make a page where you have two halves, make use of 
the `.half-float-right` and `.half-float-left` classes for your divs:

    <div class="half-float-left">...</div>
    <div class="half-float-right">...</div>

Note that on mobile in a portrait orientation, this will display these in
order as though they have the block display attribute.

If you want to make a page where it is split into thirds, make use of the
`.triple-float-right`, `.triple-float-center`, and `.triple-float-left`
classes for your divs:

    <div class="triple-split-left">...</div>
    <div class="triple-split-center">...</div>
    <div class="triple-split-right">...</div>

Note that on mobile in a portrait orientation, this will display these in
order as though they have the block display attribute.

# Fonts and Text

The primary font for Caltech Donut is Google Open Sans, specifically the 300,
400, and 600 weight variants. If, for any reason, Google stops hosting fonts,
somebody will need to change this. The title font for the homepage is a custom
fonttype that is stored directly on the server as donutfont.ttf.

If you want to change the size of your text, there are three options available:

* `.large-text`
* `.medium-text`
* `.small-text` 

These should be included on your divs which contain your paragraph tags.

If you want to use a heading tag, only h1 and h2 are currently formatted and
supported on the site.

If you want to move your text -- and all objects within a div therein -- you
should include either the `.pos-center`, `.pos-left`, or `.pos-right` classes 
on your divs.

# Misc

There are IDs in the CSS setup for the header, footer, and copyright. These are
unique to those objects and should not be applied to anything else. If you
think you have to use them for something you're doing, odds are you're wrong.

# Mobile

What's great about the design of this CSS is that you should never have to worry
about what's going to happen on a mobile device. All of the classes will format
themselves quite nicely on a mobile device assuming you didn't include something
extraneous or misclassify an object by accident.