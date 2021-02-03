# how and where, if applicable, to compile, configure, and use your project.
# Hold our hand with this documentation; be sure to answer in your documentation any questions that you think we might have while testing your work.

Harvard House Hunting

This project is a Python-Flask web application that allows users to search for homes near Harvard in the Cambridge-Boston area based on a variety of factors.
Users will be able to create their own profiles and connect with other users for group home searching to find potential roommates and/or split expenses.
Harvard House Hunting (HHH) is designed to be run within the CS50 IDE using a flask app, after which the user can then begin using the website.


Upon opening up the homepage, users will be greeted with a landing page and a short blurb describing the purpose of the website.
From there, users can either register or log in using the two links in the top right.

In the register page, users will enter a username and password (with confirmation) and will be redirected to the landing page, where they can then login with their newly
created accounts.
In the log in page, users will enter their preestablished username and password, and will be directed to their personal page.




Once at the user's personal page, the user is presented with a list of houses that they have previously viewed, and has several new options left open to them.

In the check page, the user has the option to search for houses with a variety of different filters that cater to the user preferences. Any fields left blank will be given no preference when
houses are searched for. Clicking on the search button will return a table of all houses that match the user preferences.

In the find friends page, users can enter a comma separated list of preferences for roommates, and the web app will query for other users based on the preferences. Clicking
on the search button will return a table of all users that match any of the preferences, and more information about each user is provided. The user information
for each user can be updated/viewed in the user's profile tab.

In the profile page, a user will be able to see their own username, contact information, personal description, and roommate preferences. Initially, all of these fields except
for the username will be blank. The user can update any of these fields by clicking on the update profile button, which takes the user to another page and allows them to fill in
as much or as little as they want. The information can be searched for, so users should take care with their privacy on the webpage.



At any point, the user can click on the title Harvard House Hunting (HHH) to return to either the personal page if logged in, or the landing page if not.

Finally, the logout page returns the user to the home screen and ready to register/log in to a different account.

