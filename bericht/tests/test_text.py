from unittest import TestCase
import textwrap
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.pagesizes import letter

from bericht.text import *


class TestText(TestCase):

    def test_split(self):
        text = Paragraph.from_string(
            "Some people don't like change, but you need to "
            "embrace change if the alternative is disaster."
        )
        self.assertEqual(text.wrap(20, 10), (20, 238))

    def test_build_elon_musk_quotes(self):
        doc = SimpleDocTemplate('elon_musk_quotes.pdf', pagesize=letter)
        doc.build([
            Paragraph.from_string(
                "Some people don't like change, but you need to "
                "embrace change if the alternative is disaster."
            ),
            Paragraph.from_string(
                "People work better when they know what the goal is "
                "and why. It is important that people look forward "
                "to coming to work in the morning and enjoy working. "
            ),
            Paragraph.from_string(textwrap.dedent("""
                Alright, thank you. 
                So, I’ve got about apparently I’ve got about five to six minutes to say the most useful things I can think of. 
                I’m gonna do my best. 
                It was suggested that I distill things down to 3 items. 
                I think I’ll go with four. 
                And I’ll try, I think, I think these are pretty important ones. 
                Some of it may kinda sound like, well you’ve heard them before. 
                But, you know, worth reemphasizing. 

                I think the first is, you need to work, if you, depending on how well you want to do, 
                particularly if you want to start a company, you need to work super hard. 
                So what is super hard mean? 
                Well, when my brother and I were starting our first company, instead of getting an apartment, 
                we just rented a small office and we slept on the couch and we showered in the YMCA. 
                We’re so hard up that we had just one computer. 
                So the website was up during the day, and I was coding at night. 
                7 days a week, all the time. 
                And I, sort of briefly had a girlfriend in that period and in order to be with me, 
                she had to sleep in the office. 
                So, work hard, like, every waking hour. 
                That’s the thing I would say, particularly if you’re starting a company. 
                And I mean, if you do the simple math, you say like somebody else is working 50 hours a week and 
                you’re working 100, you’ll get twice as done, as much done, in the course of the year as the other company. 

                The other thing I’d say is that if you’re creating a company, or if you’re joining a company, 
                the most important thing is to attract great people. 
                So either be with, join a group that’s amazing, that you really respect. 
                Or, if you’re building a company, you’ve got to gather great people. 
                I mean, all a company is is a group of people that have gathered together to create a product or service. 
                So depending upon how talented and hard working that group is, 
                and to the degree in which they are focused cohesively in a good direction, 
                that will determine the success of the company. 
                So, do everything you can to gather great people, if you’re creating a company. 

                Then, I’d say focus on signal over noise. 
                A lot of companies get confused. 
                They spend a lot of money on things that don’t actually make the product better. 
                So, for example, at Tesla, we’ve never spent any money on advertising. 
                We’ve put all the money into R and D and manufacturing and design to try and make the car as good as possible. 
                And, I think that’s the way to go. For any given company, keep thinking about, 
                “Are, these efforts that people are expending, are they resulting in a better product or service?"
                And if they’re not, stop those efforts. 
                And then the final thing is, is to sort of, don’t just follow the trend. 
                So, you may have heard me say that it’s good to thinking terms of the physics approach, the first principles. 
                With is, rather than reasoning by analogy, 
                you boil things down to the most fundamental truths you can imagine, and then you reason up from there. 
                And this is a good way to figure out if something really makes sense, or is it just what everybody else is doing. 
                It’s hard to think that way, you can’t think that way about everything. 
                It takes a lot of effort. But if you’re trying to do something new, it’s the best way to thing. 
                And that framework was developed by physicists to figure out counter intuitive things, like quantum mechanics. 
                It’s really a powerful, powerful method. 

                And anyways, so that’s, and then the final thing I would encourage you to do is now is the time to take risks. 
                You don’t have kids, you’re obligations, well! Some of you… Hahaha, you probably don’t have kids. 
                But as you get older, your obligations start to increase. 
                So, and, once you have a family, you start taking risks not just for yourself, but for your family as well. 
                It gets harder to do things that might not work out. So now is the time to do that. 
                Before you have those obligations. So I would encourage you to take risks now, and to do something bold. 
                You won’t regret it. Thank you....

                ...I don’t know if it was helpful. Great.
                """))
        ])
