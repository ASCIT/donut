This is the section of the wiki dedicated to teaching you how to make 
a simple page with HTML and CSS.

# Humble Beginnings

Let's start with a blank HTML file. Now, because literally everything 
on Donut is modular, we need to add the  following to include the 
navbar and head:

    {% extends "layout.html" %}
    
    {% block page %}
    ...
    {% endblock %}

Those fancy things inside the curly braces are doing a couple of things: 
(1) The extension of the layout.html page is retrieving the navbar and header
which includes references to the JS libraries and the CSS that we use on Donut,
(2) The block page is what is going to contain the HTML that you want on the
page. This tells the server, at runtime, to construct the body of the page
using whatever you happened to put in this block.

Now, let's get started actually making the body of the page. First and
foremost, put in the container and jumbotron div into the page block -- these
are what will wrap all of the page's actual content. To see why this is
necessary, go to the section of the wiki dedicated to explaining how the CSS
for Donut works.

Okay, great. You should have something that looks like this now:

    {% extends "layout.html" %}

    {% block page %}
        <div class="container theme-showcase" role="main">
            <div class="jumbotron">...</div>
        </div>
    {% endblock %}

This is the very minimum that you should have in your HTML file.

# A Two-Column Page Example

For this example, we're going to make a simple two-column webpage. 
Let's start by wrapping everything in a div implying that the text 
will be medium in size.

    {% extends "layout.html" %}

    {% block page %}
        <div class="container theme-showcase" role="main">
            <div class="jumbotron">
                <div class="medium-text">
                ...
                </div>
            </div>
        </div>
    {% endblock %}

Great! Now we need the two columns. We can make these using the half-
float-right and half-float-left classes and a couple of div tags:

    {% extends "layout.html" %}

    {% block page %}
        <div class="container theme-showcase" role="main">
            <div class="jumbotron">
                <div class="medium-text">
                    <div class="half-float-left">
                    </div>
                    <div class="half-float-right">
                    </div>
                </div>
            </div>
        </div>
    {% endblock %}

Fantastic. Now, we can fill these with just about whatever we want. Let's
add in some text to the left-hand column and a picture to the right-hand
column.

    {% extends "layout.html" %}

    {% block page %}
        <div class="container theme-showcase" role="main">
            <div class="jumbotron">
                <div class="medium-text">
                    <div class="half-float-left">
                        <p>I love making websites. Huzzah!</p>
                    </div>
                    <div class="half-float-right">
                        <img src="https://goo.gl/L1HVuZ"/>
                    </div>
                </div>
            </div>
        </div>
    {% endblock %}

And now you have a really basic webpage! Feel free to mix and match classes
as you need to -- using anything described in the part of this wiki about the
CSS on Donut -- and add whatever content your heart desires. Good luck!