# BudgetBuddy
## Demo:
Video: <https://youtu.be/VomclQsMnxc>

![Budget Buddgy Demo](https://github.com/ParasRupani/budget-buddy/blob/main/Budget-Buddy-Demo.png)

### Description:

The idea of developing an expense tracker was of interest to me as I was looking for various available tools to help me with this and I did find a few but they were not appealing to me, so I decided to make my own which I can incorporate in my daily life and benefit from it.

BudgetBuddy is a user-friendly expense tracker and budget manager web application. it tracks users' expenses, and incomes across various categories and provides insights towards their expenses.

After deciding on the project I started to look at other similar budget tools which gave me a new perspective to look at things. Initially, quite a lot of time went into deciding what features to be included, it was not difficult to find various features to implement, in this process, I forgot that I wanted to keep this minimal with only the essentials. I then started planning and dividing the features into separate sections and completing them individually. Bootstrap came in handy as it allowed me to get a majority of the styling done easily and required me to just tweak it wherever necessary. Initially, I took helpers.py from CS50 to do the error handling then changed them to actual alerts on the page itself.

Browsing through the internet and various forums was beneficial as they allowed me to not just get to the solution I needed but also a few more ways to make the code more efficient.

All the data gathered such as username, password, currency, budget, transactions and much more is stored in the budgetbuddy.db which has the following tables: users, budget, transactions, greetings, and categories. All these tables reference user_id to link them together which is then tracked throughout as a session_id of the user.


`welcome.html`:

The default landing page is set to the dashboard which requires the user to be logged in to have complete access to the web app. So if the user is not logged in they are prompted with the page to either register or login! Similarly, all the other pages do require the user to be logged in, in case they directly visit from the search bar.

`dashboard.html`:

On the Dashboard, they are greeted with a welcome message, which they can personalize from the settings. Then they are required to set their budget amount until then they are not allowed to log any of the transactions. This way the remaining amount left in the budget is tracked accurately. The transactions can be the user's various sources of income and expenses according to the category. After entering the transactions, they will be able to view the recent 5 transactions on their dashboard.

`categories.html`:

There are a few categories set by default for each user under expenses and incomes if they would like to include more they can head to the Categories page where they can specify the type of category they want to add and the name of it.

`transactions.html`, `edit_transactions.html`:

If the user happens to make an incorrect transaction or accidentally submit it, they have the complete freedom to edit or delete it from the logs, this improves the user experience and also when the transactions are edited the remaining budget gets updated accordingly.

`ananlysis.html`:

The app also provides analytical insights towards the expenses such as the total percentage of budget used and graphically represents the amount being spent among the various categories. It also mentions the total income and expenses which were logged. The pie-chart representation is achieved through matplotlib.pyplot which was interesting and had to learn the basics of interacting with it as I had never tried such representations in Python.

`settings.html`:

There are a few settings which the user can interact with to update their details. These include their username, password, preferred currency symbol, budget allotted and personalized greeting which is displayed on their dashboard. If they want to reset all the transactions and budget allotted they will have the ability to do that as well.
