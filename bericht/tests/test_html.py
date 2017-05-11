from unittest import TestCase
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter

from bericht.html import *
from bericht.text import *
from bericht.style import *


class TestHtmlParagraphs(TestCase):

    def test_bold_italic(self):
        result = parse_html('<p><b>hello</b> <i>world</i></p>', BlockStyle.default())
        self.assertIsInstance(result[0], Paragraph)
        words = result[0].words
        self.assertEqual(len(words), 2)
        hello, world = (w.parts[0] for w in words)
        self.assertEqual(hello.style.bold, True)
        self.assertEqual(hello.style.italic, False)
        self.assertEqual(world.style.bold, False)
        self.assertEqual(world.style.italic, True)


class TestAllTheThings(TestCase):

    def test_build_elon_musk_quotes(self):
        doc = SimpleDocTemplate('elon_musk_quotes.pdf', pagesize=letter)
        doc.build(parse_html(
            """
            <table>
              <tr>
                <td>
                    <p><i>Some <b>people</b> don't like change, but you need to
                    embrace change if the alternative is <b>disaster</b>.</i></p>
                </td>
                <td>
                    <p>People <b>work</b> better when they know what the goal is
                    and why. It is important that people look forward
                    to coming to <b>work</b> in the morning and enjoy <b>work</b>ing.</p>
                </td>
              </tr>
            </table>
            <p>
            Alright, thank you. <br/>
            So, I’ve got about apparently I’ve got about five to six minutes to say the most useful things I can think of. <br/>
            I’m gonna do my best. <br/>
            It was suggested that I distill things down to 3 items. <br/>
            I think I’ll go with four. <br/>
            And I’ll try, I think, I think these are pretty important ones. <br/>
            Some of it may kinda sound like, well you’ve heard them before. <br/>
            But, you know, worth reemphasizing. <br/>
            <br/>
            I think the first is, you need to <b>work</b>, if you, depending on how well you want to do, <br/>
            particularly if you want to start a company, you need to <b>work</b> super <i>hard</i>. <br/>
            So what is super <i>hard</i> mean? <br/>
            Well, when my brother and I were starting our first company, instead of getting an apartment, <br/>
            we just rented a small office and we slept on the couch and we showered in the YMCA. <br/>
            We’re so <i>hard</i> up that we had just one computer. <br/>
            So the website was up during the day, and I was coding at night. <br/>
            7 days a week, all the time. <br/>
            And I, sort of briefly had a girlfriend in that period and in order to be with me, <br/>
            she had to sleep in the office. <br/>
            So, <b>work</b> <i>hard</i>, like, every waking hour. <br/>
            That’s the thing I would say, particularly if you’re starting a company. <br/>
            And I mean, if you do the simple math, you say like somebody else is <b>work</b>ing 50 hours a week and <br/>
            you’re <b>work</b>ing 100, you’ll get twice as done, as much done, in the course of the year as the other company. <br/>
            <br/>
            The other thing I’d say is that if you’re creating a company, or if you’re joining a company, <br/>
            the most important thing is to attract great people. <br/>
            So either be with, join a group that’s amazing, that you really respect. <br/>
            Or, if you’re building a company, you’ve got to gather great people. <br/>
            I mean, all a company is is a group of people that have gathered together to create a product or service. <br/>
            So depending upon how talented and <i>hard</i> <b>work</b>ing that group is, <br/>
            and to the degree in which they are focused cohesively in a good direction, <br/>
            that will determine the success of the company. <br/>
            So, do everything you can to gather great people, if you’re creating a company. <br/>
            <br/>
            Then, I’d say focus on signal over noise. <br/>
            A lot of companies get confused. <br/>
            They spend a lot of money on things that don’t actually make the product better. <br/>
            So, for example, at Tesla, we’ve never spent any money on advertising. <br/>
            We’ve put all the money into R and D and manufacturing and design to try and make the car as good as possible. <br/>
            And, I think that’s the way to go. For any given company, keep thinking about, <br/>
            “Are, these efforts that people are expending, are they resulting in a better product or service?"<br/>
            And if they’re not, stop those efforts. <br/>
            And then the final thing is, is to sort of, don’t just follow the trend. <br/>
            So, you may have heard me say that it’s good to thinking terms of the physics approach, the first principles. <br/>
            With is, rather than reasoning by analogy, <br/>
            you boil things down to the most fundamental truths you can imagine, and then you reason up from there. <br/>
            And this is a good way to figure out if something really makes sense, or is it just what everybody else is doing. <br/>
            It’s <i>hard</i> to think that way, you can’t think that way about everything. <br/>
            It takes a lot of effort. But if you’re trying to do something new, it’s the best way to thing. <br/>
            And that frame<b>work</b> was developed by physicists to figure out counter intuitive things, like quantum mechanics. <br/>
            It’s really a powerful, powerful method. <br/>
            <br/>
            And anyways, so that’s, and then the final thing I would encourage you to do is now is the time to take risks. <br/>
            You don’t have kids, you’re obligations, well! Some of you… Hahaha, you probably don’t have kids. <br/>
            But as you get older, your obligations start to increase. <br/>
            So, and, once you have a family, you start taking risks not just for yourself, but for your family as well. <br/>
            It gets <i>harder</i> to do things that might not <b>work</b> out. So now is the time to do that. <br/>
            Before you have those obligations. So I would encourage you to take risks now, and to do something bold. <br/>
            You won’t regret it. Thank you....<br/>
            <br/>
            ...I don’t know if it was helpful. Great.<br/>
            </p>""")
        )
