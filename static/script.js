function removeAlert() {
    const alertDiv = document.getElementById("alert-div");
    if (alertDiv) {
        alertDiv.classList.add("fade-out");
        setTimeout(() => {
            alertDiv.style.display = "none";
        }, 1000); 
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(removeAlert, 2000); 
});

const transactionTypeSelect = document.getElementById("transactionType");
const categorySelect = document.getElementById("categorySelect");
const expenseOptions = categorySelect.getElementsByClassName("expense");
const incomeOptions = categorySelect.getElementsByClassName("income");

// Function to show expense categories
function showExpenseCategories() {
    for (const option of expenseOptions) {
        option.style.display = "block";
    }
    for (const option of incomeOptions) {
        option.style.display = "none";
    }
}

function showIncomeCategories() {
    for (const option of expenseOptions) {
        option.style.display = "none";
    }
    for (const option of incomeOptions) {
        option.style.display = "block";
    }
}

transactionTypeSelect.addEventListener("change", function () {
    const selectedType = transactionTypeSelect.value;
    if (selectedType === "Expense") {
        showExpenseCategories();
    } else if (selectedType === "Income") {
        showIncomeCategories();
    } else {
        for (const option of expenseOptions) {
            option.style.display = "block";
        }
        for (const option of incomeOptions) {
            option.style.display = "block";
        }
    }
});

    const initialType = transactionTypeSelect.value;
if (initialType === "Expense") {
    showExpenseCategories();
} else if (initialType === "Income") {
    showIncomeCategories();
} else {
    for (const option of expenseOptions) {
        option.style.display = "block";
    }
    for (const option of incomeOptions) {
        option.style.display = "block";
    }
}
