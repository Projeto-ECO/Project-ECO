// Get the logout button element
const logoutButton = document.querySelector("#logout-button");

// Add event listener for logout button click
logoutButton.addEventListener("click", (event) => {
    event.preventDefault();

  // Send a POST request to the server to logout the user
    fetch("/logout", {
    method: "POST",
    })
    .then((response) => {
        if (response.ok) {
        // Redirect to the home page after successful logout
        window.location.href = "/";
        } else {
        throw new Error("Failed to logout");
        }
    })
    .catch((error) => {
        console.error(error);
      // Handle the error in a meaningful way, e.g. display an error message to the user
    });
});

function logout() {
    fetch('/logout', {
        method: 'POST'
        }).then(function(response) {
        if (response.redirected) {
            window.location.href = response.url;
        }
        }).catch(function(error) {
        console.log(error);
        });
    }
    
    document.querySelector('a[href="/logout"]').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });


