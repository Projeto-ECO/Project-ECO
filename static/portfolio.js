function loadUserData(id) {    
    // Load user data from file
    const userId = id; // Replace with user ID
    console.log(userId);
    const userFile = `/data/${userId}`;
    console.log(userFile)
    fetch(userFile).then(response => response.json()).then(userData => {
            // Define the coins and their values
            console.log(userData);
            const coins = userData.coins;

            // Define the number of each coin owned and sort by value
            const coinAmounts = userData.coinAmounts;
            const sortedCoinAmounts = Object.keys(coinAmounts).sort((a, b) => parseFloat(a) - parseFloat(b)).reduce((obj, key) => {
                obj[key] = coinAmounts[key];
                return obj;
            }, {});

            // Calculate the value of each coin and the total balance
            let totalBalance = 0;
            for (const coinValue in sortedCoinAmounts) {
                const amountOwned = sortedCoinAmounts[coinValue];
                const coin = coins.find(c => c.value == coinValue);
                const coinName = parseFloat(coinValue);
                const coinValueInEuros = coin ? coin.value : parseFloat(coinValue);
                const coinValueTotal = amountOwned * coinValueInEuros;
                totalBalance += coinValueTotal;

                // Add a row to the table for this coin
                const tr = document.createElement("tr");
                const nameTd = document.createElement("td");
                nameTd.innerText = coinName.toLocaleString("pt-PT", { style: "currency", currency: "EUR" });
                const amountTd = document.createElement("td");
                amountTd.innerText = amountOwned;
                const valueTd = document.createElement("td");
                valueTd.innerText = coinValueTotal.toLocaleString("pt-PT", { style: "currency", currency: "EUR" });
                tr.appendChild(nameTd);
                tr.appendChild(amountTd);
                tr.appendChild(valueTd);
                document.getElementById("coin-table").appendChild(tr);
            }

            // Set the total balance in the table footer
            document.getElementById("total-balance").innerText = totalBalance.toLocaleString("pt-PT", { style: "currency", currency: "EUR" });
        });
}

var depositButton = document.getElementById("deposit-button");
var modal = document.getElementById("deposit-modal");
var closeButton = document.getElementsByClassName("close")[0];

depositButton.onclick = function() {
    modal.style.display = "block";
}

closeButton.onclick = function() {
    modal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}


$(function() {
    $('#deposit-form').submit(function(event) {
        // Prevent default form submission behavior
        event.preventDefault();
    
        // Get form data
        var formData = {
            'coin': $('#coin').val(),
            'amount': $('#amount').val()
        };
    
        // Send AJAX request to server
        $.ajax({
            type: 'POST',
            url: '/deposit',
            data: formData,
            success: function(response) {
                // Refresh the page
                location.reload();
            },
            error: function(xhr, status, error) {
                // Handle error response
                location.reload();
            }
        });
    });
});