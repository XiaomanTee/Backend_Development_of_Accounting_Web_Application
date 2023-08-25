from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__, template_folder='template', static_folder='static')

stock_level = 0
account_balance = 0.0
warehouse = {}
history = []

def write_history(data):
    with open("history.txt", "a") as file:
        file.write(data + "\n")

@app.route('/', methods=["GET"])
def main_page():
    return render_template("index.html", stock_level=stock_level, account_balance=account_balance)

@app.route('/balance_change_form.html', methods=["GET"])
def balance_change_form():
    return render_template("balance_change_form.html")

@app.route('/change_balance', methods=["GET", "POST"])
def balance_change():
    global account_balance
    amount = float(request.form["amount"])
    operation = request.form.get("operation")

    if operation == "add":
        account_balance += amount
        message = f"Success: Add the {amount} to account. Account Balance: {account_balance}"
        history.append(f"Added {amount} to account. Balance: {account_balance}")
        write_history(f"Added {amount} to account. Balance: {account_balance}")
        return render_template("/balance_change_form.html", message=message)
    elif operation == "subtract":
        if account_balance - amount < 0:
            error_message = "Error: Insufficient balance!"
            return render_template("/balance_change_form.html", error_message=error_message)
        else:
            account_balance -= amount
            message = f"Success: Subtract  the {amount} to account. Account Balance: {account_balance}"
            history.append(f"Subtract {amount} to account. Balance: {account_balance}")
            write_history(f"Subtract {amount} to account. Balance: {account_balance}")
            return render_template("/balance_change_form.html", message=message)
    else:
        error_message = "Error: Invalid operation!"
        return render_template("/balance_change_form.html", error_message=error_message)

    return redirect(url_for("balance_change_page"))

@app.route('/purchase_form.html', methods=["GET"])
def purchase_form():
    return render_template("purchase_form.html")

@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    global stock_level, account_balance
    quantity = int(request.form["number_of_pieces"])
    price = float(request.form["unit_price"])
    product_name = request.form["product_name"]

    total_price = price * quantity

    if product_name in warehouse and warehouse[product_name]['price'] != price and warehouse[product_name]['quantity'] > 0:
        error_message = f"Purchase error: {product_name} already exists with different prices and quantities"
        return render_template("/purchase_form.html", error_message=error_message)
    else:
        if account_balance - total_price < 0:
            error_message = "Purchase error: Insufficient balance!"
            return render_template("/purchase_form.html", error_message=error_message)
        else:
            account_balance -= total_price

            if product_name in warehouse:
                if warehouse[product_name]['price'] == price:
                    warehouse[product_name]['quantity'] += quantity
                elif warehouse[product_name]['quantity'] == 0:
                    warehouse[product_name].update({"price": price, "quantity": quantity})
            elif product_name not in warehouse:
                warehouse[product_name] = {"price": price, "quantity": quantity}
        
        stock_level += quantity
        
        message = f"Successful purchase {quantity} of {product_name} with {total_price}. Balance: {account_balance}"
        history.append(f"Purchased {quantity} of {product_name} with {total_price}. Balance: {account_balance}")
        write_history(f"Purchased {quantity} of {product_name} with {total_price}. Balance: {account_balance}")
        return render_template("/purchase_form.html", message=message)

    return redirect(url_for("purchase_form"))

@app.route('/sale_form.html', methods=["GET"])
def sale_form():
    return render_template("/sale_form.html", warehouse=warehouse)

@app.route('/sale', methods=["GET", "POST"])
def sale():
    global stock_level, account_balance
    quantity = int(request.form["number_of_pieces"])
    price = float(request.form["unit_price"])
    product_name = request.form.get("sale_list")

    if product_name in warehouse and warehouse[product_name]['quantity'] >= quantity:
        total_price = price * quantity

        account_balance += total_price
        warehouse[product_name]['quantity'] -= quantity
        
        stock_level -= quantity

        message = f"Successful sales {quantity} of {product_name} with {total_price}. Balance: {account_balance}"
        history.append(f"Sold {quantity} of {product_name} with {total_price}. Balance: {account_balance}")
        write_history(f"Sold {quantity} of {product_name} with {total_price}. Balance: {account_balance}")
        return render_template("/sale_form.html", message=message, warehouse=warehouse)
    elif product_name not in warehouse:
        error_message = f"Sales error: {product_name} is not in the warehouse."
        return render_template("/sale_form.html", error_message=error_message, warehouse=warehouse)
    else:
        error_message = f"Sales error: Not enought quantity for {product_name}. Only {warehouse[product_name]['quantity']} left."
        return render_template("/sale_form.html", error_message=error_message, warehouse=warehouse)

    return redirect(url_for("sale_form"))

@app.route('/history.html', methods=["GET"])
def history_page():
    return render_template("/history.html", history=history)

@app.route('/history', methods=["GET", "POST"])
def review():
    from_indices = request.form["from"]
    to_indices = request.form["to"]

    if from_indices == "" or from_indices is None:
        from_indices = 0
    else:
        from_indices = int(from_indices)

    if to_indices == "" or to_indices is None:
        to_indices = len(history)
    else:
        to_indices = int(to_indices)

    if from_indices < 0 or from_indices > to_indices or to_indices > len(history):
        error_message = f"Error: Invalid range! Please enter between From: 0; To: {len(history)}"
        return render_template("/history.html", error_message=error_message)
    elif not history:
        error_message = f"No history can be review"
        return render_template("/history.html", error_message=error_message)
    else:
        review_history = history[from_indices:to_indices]
        return render_template("/history.html", review_history=review_history)
    
    return redirect(url_for("history_page"))
    
if __name__ == '__main__':
    app.run()
