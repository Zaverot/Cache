# discusses, technically, how you implemented your project and why you made the design decisions you did.
# your opportunity to give the staff a technical tour of your project underneath its hood.

We wanted to create a website that would allow students to query for apartments and houses for rent in the area, in case Harvard restricted the number of students on campus
(which they did). The best way for us to implement this was with Python-Flask web application that could allow users to go in between different pages on a website that would allow them to
look for houses with various criteria, find relevant information about these houses by querying our SQLite database, and track their search history using a history of search table.

Our website color scheme was actually generated using a website called coolors.com that generated aesthetic combinations of colors and gave the hexadecimal pixel values for them
so that we could more easily implement them into the layout theme of our website. The grey, pink, yellow scheme was an unexpected gem that we eventually realized fit the topic
of our project really well since these are colors that people often see a lot in the streets of Cambridge.

We decided to create a separate landing page with register and login requirements for each user so that each user would be able to track their searches and see the houses they had
looked at previously. We made the landing page look nice with a nice photo of an upscale apartment in Cambridge, just to give the user a glimpse at what kind of places they could
find in Cambridge.

We wanted to display a short history of past searchers on the index page after the user logged in so that the user would be able to more easily reference some of the houses they
were looking at earlier. This would appear right as the user logged in or if they clicked the header "Harvard House Hunting (HHH)" for easy access.

In searches, we allowed for users to filter for houses based on preferences for bathrooms, prices, walking times and distances to Harvard, etc. These were designed so that fields
left blank would not impact the search and allow for a broader scope of finds, all for the users' convenience.

Additionally, for the social aspect, we created a Profile section, where users could add information about themselves and their roommate preferences. We created larger text boxes
for users to enter info about themselves so that they could be more descriptive and thorough. Users could also leave their phone numbers/emails to allow other people to contact them,
which leads us to the finding friends function.

In finding friends, users could search with keywords and find potential roommates, as our back end commands would scrape the other users' intros in order to find similar users
with similar interests. Finding friends would allow a user to see the description of their potential friends based on the interests that the user entered, and it would also provide
the other users' roommate preferences and contacts.

Overall, this website is designed to help Harvard students look for nearby houses (manually) aggregated from various websites like Zillow, Airbnb, and Harvard Off Campus Housing
and also find suitable roommates to room with. Useful information like the cost of splitting these apartments and houses were also given, along with the walking distance to
Harvard square, another important factor for students when purchasing a place in Cambridge.



