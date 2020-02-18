document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let loginInput = document.getElementById("username");
    let loginForm = document.getElementById("login-form");


    loginInput.addEventListener("change", checkLoginAvailability);

    loginForm.addEventListener("submit", function (event) {
        let reqiuredFields = document.querySelectorAll('#login-form .required').length;

        let n = 0;
        for (i = 0; i < reqiuredFields; i++) {
            if (event["srcElement"][i].value !== "") {
                n++;
            }
        }

        if ((n != reqiuredFields) || (document.getElementById("login_taken_error_message") != null)) {
            event.preventDefault();
        }

    });


    function checkLoginAvailability() {
        let loginInput = document.getElementById("username");

        let loginPattern = /^[a-z]{3,12}$/;

        if (loginInput.value != '' && loginPattern.test(loginInput.value)) {
            let baseUrl = "https://localhost:8082/user/";
            let userUrl = baseUrl + loginInput.value;

            fetch(userUrl, {method: GET, mode: "cors"}).then(function (resp) {
                console.log(resp.status);
                if (resp.status == 400) {
                    if (document.getElementById("login_taken_error_message") != null) {
                        document.getElementById("login_taken_error_message").remove()
                    }
                    loginInput.insertAdjacentHTML("afterend", "<div id='login_taken_error_message' class='text-danger'>   Taki użytkownik nie istnieje. </div>");
                    return false;
                }
                if (resp.status == 200) {
                    if (document.getElementById("login_taken_error_message") != null) {
                        document.getElementById("login_taken_error_message").remove()
                    }
                    return true;
                }
                return false;

            }).catch(function (err) {
                console.log(err);
                return false;
            });
        }
    }

});