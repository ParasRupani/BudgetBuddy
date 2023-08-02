from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from helpers import login_required
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
import matplotlib.pyplot as plt

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///budgetbuddy.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # default page is the dashboard
    return redirect("/dashboard")


@app.route("/register", methods=["POST"])
def register():
    # grab all the user details
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    currency = request.form.get("currency")


    # error handling
    if not username:
        alert = "Enter Username!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    user_query = db.execute("SELECT username FROM users WHERE username = ?;", username)

    if user_query:
        alert = "Username already taken!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    if not password:
        alert = "Enter Password!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    if len(password)<4:
        alert = "Not Strong Password!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    if password != confirmation:
        alert = "Passwords do not match!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    if not currency:
        alert = "Choose your Currency!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)


    hash_pass = generate_password_hash(password)

    # updating the database with new user
    db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hash_pass)
    user_data = db.execute("SELECT * FROM users WHERE username = ?", username)
    db.execute("UPDATE users SET currency = ? WHERE username = ?", currency, username)

    user_id = user_data[0]["user_id"]

    default_categories = [
        {"name": "Salary", "type": "Income"},
        {"name": "Business", "type": "Income"},
        {"name": "Investment", "type": "Income"},
        {"name": "Passive", "type": "Income"},

        {"name": "Groceries", "type": "Expense"},
        {"name": "Entertainment", "type": "Expense"},
        {"name": "Transportation", "type": "Expense"},
        {"name": "Utilities", "type": "Expense"}
    ]

    # inserting default categories for every new user
    for category_data in default_categories:
        category_name = category_data["name"]
        category_type = category_data["type"]
        db.execute("INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)", user_id, category_name, category_type)

    # custom greeting possible
    default_greeting = "Welcome to your Dashboard,"
    db.execute("INSERT INTO greetings (user_id, greeting_message) VALUES (?, ?)", user_id, default_greeting)

    session["user_id"] = user_id
    session["username"] = username

    alert = "Registration successful!"
    session["alert"] = alert

    return redirect("/dashboard")


@app.route("/login", methods=["POST"])
def login():
    session.clear()

    # error handling
    if not request.form.get("username"):
        alert = "Enter Username!"
        session["alert"] = alert

        return render_template("welcome.html", alert=alert)

    elif not request.form.get("password"):
        alert = "Enter Password!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        alert = "INVALID CREDENTIALS!"
        session["alert"] = alert
        return render_template("welcome.html", alert=alert)

    session["user_id"] = rows[0]["user_id"]
    session["username"] = rows[0]["username"]

    alert = "Login successful!"
    session["alert"] = alert

    return redirect("/dashboard")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = session["user_id"]


    # Extracting user's data to display
    greeting_data = db.execute("SELECT greeting_message FROM greetings WHERE user_id = ?", user_id)
    greeting = greeting_data[0]["greeting_message"]

    categories = db.execute("SELECT * FROM categories WHERE user_id = ?;", user_id)

    user_data = db.execute("SELECT currency FROM users WHERE user_id = ?", user_id)
    currency = user_data[0]["currency"] if user_data else None

    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transaction_id DESC limit 5", user_id)

    budget_data = db.execute("SELECT * FROM budget WHERE user_id = ?", user_id)
    budget = budget_data[0] if budget_data else None

    amount = 0.0
    alloted = 0

    if request.method == "POST":

        # When submitting the budget amount
        amount = float(request.form.get("amount"))
        if amount < 0:
            alert = "Not Valid !"
            session["alert"] = alert
            return redirect("/dashboard")

        if budget:
            db.execute("UPDATE budget SET amount = ?, currency = ?, remaining = ? WHERE user_id = ?", amount, currency, amount, user_id)
        else:
            db.execute("INSERT INTO budget (user_id, amount, currency, remaining) VALUES (?, ?, ?, ?)", user_id, amount, currency, amount)

    # when visiting the dashboard directly
    budget_data = db.execute("SELECT * FROM budget WHERE user_id = ?", user_id)
    budget = budget_data[0] if budget_data else None

    if budget_data:
        alloted = budget_data[0]["amount"]

    alert = session.pop("alert", None)

    return render_template("dashboard.html",active_page="dashboard", greeting=greeting, currency=currency, transactions=transactions, budget=budget, alloted=alloted, amount=amount, categories = categories, alert=alert)


@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    alert = session.pop("alert", None)
    user_id = session["user_id"]

    if request.method == "POST":
        # addition of new categories
        category_name = request.form.get("add-category")
        category_type = request.form.get("type")

        if not category_name:
            alert = "Name Required!"
            session["alert"] = alert

            return redirect("/categories")

        if not category_type:
            alert = "Type Required!"
            session["alert"] = alert
            return redirect("/categories")


        existing_category = db.execute("SELECT * FROM categories WHERE user_id = ? AND name = ?", user_id, category_name)

        if existing_category:
            alert = "Already Exists!"
            session["alert"] = alert
            return redirect("/categories")

        db.execute("INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)", user_id, category_name, category_type)

        alert = "Category added successfully!"
        session["alert"] = alert
        return redirect("/categories")

    categories = db.execute("SELECT * FROM categories WHERE user_id = ?", user_id)

    return render_template("categories.html", categories=categories, active_page="categories", alert=alert)


@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    alert = session.pop("alert", None)
    user_id = session["user_id"]

    if request.method == "POST":

        # extracting details of new transaction
        date = request.form.get("date")
        amount = float(request.form.get("amount"))
        if amount < 0:
            alert = "Not Valid !"
            session["alert"] = alert
            return redirect("/dashboard")

        currency_data = db.execute("SELECT currency FROM users WHERE user_id = ?", user_id)
        currency = currency_data[0]["currency"]
        type = request.form.get("type")
        category_name = request.form.get("category")
        category_data = db.execute("SELECT category_id FROM categories WHERE name = ?", category_name)

        if not category_data:
            alert = "Invalid Category!"
            session["alert"] = alert
            return redirect("/dashboard")

        category_id = category_data[0]["category_id"]

        db.execute("INSERT INTO transactions (user_id, category_id, date, amount, currency, category, type) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_id, category_id, date, amount, currency, category_name, type)

        budget_data = db.execute("SELECT amount, remaining FROM budget WHERE user_id = ?;", user_id)
        if budget_data:
            budget_amount = 0
            budget_amount = budget_data[0]["amount"]
            remaining_budget = float(budget_data[0]["remaining"])

        if type == "Expense":
            remaining_budget -= amount

        db.execute("UPDATE budget SET remaining = ?, amount = ?  WHERE user_id = ?", remaining_budget, budget_amount, user_id)

        alert = "Transaction Added!"
        session["alert"] = alert
        return redirect("/dashboard")

    else:
        # delete doesn't use post method
        if "delete" in request.args:


            transaction_id = int(request.args["delete"])
            transaction_data = db.execute("SELECT amount FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)

            deleted_amount = transaction_data[0]["amount"]
            budget_data = db.execute("SELECT amount, remaining FROM budget WHERE user_id = ?;", user_id)

            type_data = db.execute("SELECT type FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
            type = type_data[0]["type"]

            # updating the remaining budget
            if budget_data:
                budget_amount = 0
                budget_amount = budget_data[0]["amount"]
                remaining_budget = float(budget_data[0]["remaining"])
                if type=="Expense":
                    remaining_budget += deleted_amount
                db.execute("UPDATE budget SET remaining = ? WHERE user_id = ?", remaining_budget, user_id)


            db.execute("DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)

            alert = "Transaction deleted!"
            session["alert"] = alert
            return redirect("/transactions")

        elif "edit" in request.args:
            # extracting the details of the selected transaction to edit
            transaction_id = int(request.args["edit"])
            transaction = db.execute("SELECT * FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
            categories = db.execute("SELECT * FROM categories WHERE user_id = ?", user_id)

            alert = "Edit Successful!"
            session["alert"] = alert

            # transferring to the page to edit.
            return render_template("edit_transactions.html", transaction=transaction[0], categories=categories)

        else:
            transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transaction_id DESC", user_id)
            return render_template("transactions.html", transactions=transactions, active_page="transactions", alert=alert)


@app.route("/edit_transaction", methods=["POST"])
@login_required
def edit_transaction():

    # extracting all the details related to the transaction
    user_id = session["user_id"]
    transaction_id = int(request.form.get("transaction_id"))
    date = request.form.get("date")
    amount = float(request.form.get("new-amount"))
    currency_data = db.execute("SELECT currency FROM users WHERE user_id = ?;", user_id)
    currency = currency_data[0]["currency"]
    type = request.form.get("type")
    category_name = (request.form.get("category"))

    category_data = db.execute("SELECT category_id FROM categories WHERE user_id = ? AND name = ?;", user_id, category_name)
    category_id = category_data[0]["category_id"] if category_data else None

    budget_data = db.execute("SELECT amount, remaining FROM budget WHERE user_id = ?;", user_id)
    if budget_data:
        remaining_budget = budget_data[0]["remaining"]

    prev_amount_data = db.execute("SELECT amount from transactions WHERE transaction_id = ? AND user_id = ? ;", transaction_id, user_id)
    prev_amount = 0
    prev_amount = prev_amount_data[0]["amount"]

    # updating the remaining budget
    if type=="Expense":
        remaining_budget -= (amount - prev_amount)
    db.execute("UPDATE budget SET remaining = ?  WHERE user_id = ?;", remaining_budget, user_id)
    db.execute("UPDATE transactions SET date = ?, amount = ?, currency = ?, type = ?, category_id = ? WHERE transaction_id = ? AND user_id = ?;",
               date, amount, currency, type, category_id, transaction_id, user_id)

    return redirect("/transactions")


@app.route("/analysis")
@login_required
def analysis():

    # extracting the user's budget and transactions
    user_id = session["user_id"]
    alert = session.pop("alert", None)

    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)

    budget_data = db.execute("SELECT * FROM budget WHERE user_id = ?", user_id)
    budget = budget_data[0] if budget_data else None

    amount = budget_data[0]["amount"] if budget_data else 0

    if amount != 0:
        # calculating: income, expenses, remaining budget, percentage
        total_expenses = sum(transaction["amount"] for transaction in transactions if transaction["type"] == "Expense")
        total_income = sum(transaction["amount"] for transaction in transactions if transaction["type"] == "Income")

        remaining_budget = budget["remaining"]
        budget_used_percentage = round((total_expenses / budget["amount"]) * 100, 1)

        expense_categories = db.execute("SELECT category, SUM(amount) as total_amount FROM transactions WHERE user_id = ? AND type = 'Expense' GROUP BY category", user_id)
        expense_category_names = [category['category'] for category in expense_categories]
        expense_category_amounts = [category['total_amount'] for category in expense_categories]

        # displaying the expenses according to the categories
        plt.figure(figsize=(8, 6))
        plt.pie(expense_category_amounts, labels=expense_category_names, autopct='%1.1f%%', startangle=140)
        plt.title('Expenses')
        plt.savefig('static/pie_chart.png')
    else:

        # when the budget is reset or not set
        total_expenses = 0
        total_income = 0
        remaining_budget = 0
        budget_used_percentage = 0
        expense_category_names = []
        expense_category_amounts = []

        alert = "No Data Available"

        session["alert"] = alert
        alert = session.pop("alert", None)

    return render_template("analysis.html", transactions=transactions, budget=budget, total_expenses=total_expenses, total_income=total_income, remaining_budget=remaining_budget, budget_used_percentage=budget_used_percentage, expense_category_names=expense_category_names, expense_category_amounts=expense_category_amounts, active_page="analysis", alert=alert)


@app.route("/settings")
@login_required
def settings():
    # extracting the current details of the user.
    user_id = session["user_id"]

    new_greeting = request.form.get("greeting")
    session["greeting"] = new_greeting

    user_data = db.execute("SELECT currency FROM users WHERE user_id = ?", user_id)
    currency = user_data[0]["currency"] if user_data else None

    budget_data = db.execute("SELECT * FROM budget WHERE user_id = ?", user_id)
    budget = budget_data[0] if budget_data else None

    greeting_data = db.execute("SELECT greeting_message FROM greetings WHERE user_id = ?", user_id)
    greeting = greeting_data[0]["greeting_message"]

    user = db.execute("SELECT username FROM users WHERE user_id = ?", user_id)
    username = user[0]["username"] if user else None

    alert = session.pop("alert", None)

    return render_template("settings.html", currency=currency, budget=budget, username=username, greeting=greeting, active_page="settings", alert=alert)


@app.route("/update_currency", methods=["POST"])
@login_required
def update_currency():
    # updating the currency from settings.
    user_id = session["user_id"]
    currency = request.form.get("currency")
    db.execute("UPDATE users SET currency = ? WHERE user_id = ?", currency, user_id)

    alert = "Currency Updated!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/update_budget", methods=["POST"])
@login_required
def update_budget():
    # updating the budget from settings.
    user_id = session["user_id"]
    total_budget = float(request.form.get("new-budget-amount"))
    budget_data = db.execute("SELECT * FROM budget WHERE user_id = ?", user_id)

    if budget_data:
        # modifying the remaining budget
        amount = budget_data[0]["amount"]
        remaining_budget = budget_data[0]["remaining"]
        remaining_budget += (total_budget - amount)
        db.execute("UPDATE budget SET remaining = ?  WHERE user_id = ?;", remaining_budget, user_id)

    if budget_data:
        db.execute("UPDATE budget SET amount = ? WHERE user_id = ?", total_budget, user_id)
    else:
        db.execute("INSERT INTO budget (user_id, amount) VALUES (?, ?)", user_id, total_budget)

    alert = "Budget Updated!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/update_username", methods=["POST"])
@login_required
def update_username():
    # updating the username from settings.
    user_id = session["user_id"]
    new_username = request.form.get("username")
    db.execute("UPDATE users SET username = ? WHERE user_id = ?", new_username, user_id)

    session["username"] = new_username

    alert = "Username Updated!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/update_password", methods=["POST"])
@login_required
def update_password():
    # updating the user's password from settings.
    user_id = session["user_id"]
    new_password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if new_password != confirmation:
        alert = "Passwords do not match!"
        session["alert"] = alert
        return redirect("/settings")

    hash_pass = generate_password_hash(new_password)

    db.execute("UPDATE users SET hash = ? WHERE user_id = ?", hash_pass, user_id)

    alert = "Password Updated!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/reset_budget", methods=["POST"])
@login_required
def reset_budget():
    # resetting the budget to 0
    # deleting all the transactions
    user_id = session["user_id"]

    db.execute("UPDATE budget SET amount = 0, remaining = 0 WHERE user_id = ?", user_id)
    db.execute("DELETE FROM transactions WHERE user_id = ?", user_id)

    alert = "Reset Successful!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/greeting", methods=["POST"])
@login_required
def greeting():
    # modifying the greeting
    user_id = session["user_id"]
    new_greeting = request.form.get("greeting")

    db.execute("UPDATE greetings SET greeting_message = ? WHERE user_id = ?;", new_greeting, user_id)
    alert = "Greeting Updated!"
    session["alert"] = alert

    return redirect("/settings")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")