document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let registrationForm = document.getElementById("registration-form");
    let loginInput = document.getElementById("username");
    let peselInput = document.getElementById("pesel");
    let sexInput = document.getElementById("sex");
    let birthdateInput = document.getElementById("birthdate");
    let firstnameInput = document.getElementById("firstname");
    let lastnameInput = document.getElementById("lastname");
    let passwordInput = document.getElementById("password");
    let repeatPasswordInput = document.getElementById("repeat-password");

    loginInput.addEventListener("change", checkLoginAvailability);
    peselInput.addEventListener("change", checkPeselValidity);
    sexInput.addEventListener("change", checkSexValidity);
    birthdateInput.addEventListener("change", checkBirthdateValidity);
    firstnameInput.addEventListener("change", checkFirstnameValidity);
    lastnameInput.addEventListener("change", checkLastnameValidity);
    passwordInput.addEventListener("change", checkPasswordValidity);
    repeatPasswordInput.addEventListener("change", checkRepeatPasswordValidity);

    registrationForm.addEventListener("submit", function (event) {
        let reqiuredFields = document.querySelectorAll('#registration-form .required').length;
        let registrationForm = document.getElementById("registration-form");
        let loginInput = document.getElementById("username");
        let peselInput = document.getElementById("pesel");
        let sexInput = document.getElementById("sex");
        let birthdateInput = document.getElementById("birthdate");
        let firstnameInput = document.getElementById("firstname");
        let lastnameInput = document.getElementById("lastname");

        let n = 0;
        for (i = 0; i < reqiuredFields; i++) {
            if (event["srcElement"][i].value !== "") {
                n++;
            }
        }

        if (((n != reqiuredFields) || (document.getElementById("login_taken_error_message") != null))
            || !(checkPeselValidity() && checkBirthdateValidity() && checkSexValidity()
                && checkFirstnameValidity() && checkLastnameValidity() && checkPasswordValidity() && checkRepeatPasswordValidity())) {
            event.preventDefault();

        }
    });

    function checkLoginAvailability() {
        let loginInput = document.getElementById("username");

        let loginPattern = /^[a-z]{3,12}$/;

        if (loginInput.value != '' && loginPattern.test(loginInput.value)) {
            let baseUrl = "https://localhost:8082/user/";
            let userUrl = baseUrl + loginInput.value;

            fetch(userUrl, {method: GET}).then(function (resp) {
                console.log(resp.status);
                if (resp.status === 200) {
                    if (document.getElementById("login_taken_error_message") != null) {
                        document.getElementById("login_taken_error_message").remove()
                    }
                    loginInput.insertAdjacentHTML("afterend", "<div id='login_taken_error_message' class='text-danger'>   Login jest już zajęty. </div>");
                    return false;
                }
                if (resp.status === 400) {
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
        } else {
            if (document.getElementById("login_taken_error_message") != null) {
                document.getElementById("login_taken_error_message").remove()
            }
            loginInput.insertAdjacentHTML("afterend", "<div id='login_taken_error_message' class='text-danger'>   Login musi zawierać od 3 do 12 małych liter. </div>")
        }
    }

    function checkPeselValidity() {
        let peselInput = document.getElementById("pesel");
        let peselValue = peselInput.value;
        let controlSum = 0;
        let controlSumCoefficient = [9, 7, 3, 1];

        for (i = 0; i < peselValue.length - 1; i++) {
            controlSum += parseInt(peselValue[i]) * controlSumCoefficient[i % controlSumCoefficient.length];
        }

        controlSum = controlSum % 10;

        if (controlSum != peselValue[peselValue.length - 1]) {
            if (document.getElementById("wrong_pesel_error_message") != null) {
                document.getElementById("wrong_pesel_error_message").remove();
            }
            peselInput.insertAdjacentHTML("afterend", "<div id='wrong_pesel_error_message' class='text-danger'>   Błędny PESEL. </div>")
            return false;
        }
        if (document.getElementById("wrong_pesel_error_message") != null) {
            document.getElementById("wrong_pesel_error_message").remove();
        }
        return true;
    }

    function checkSexValidity() {
        let sexInput = document.getElementById("sex");
        if (sexInput.value !== "M" && sexInput.value !== "F") {
            if (document.getElementById("wrong_sex_error_message") != null) {
                document.getElementById("wrong_sex_error_message").remove();
            }
            sexInput.insertAdjacentHTML("afterend", "<div id='wrong_sex_error_message' class='text-danger'>   Płeć to M lub F. </div>")
            return false;
        }
        if (document.getElementById("wrong_sex_error_message") != null) {
            document.getElementById("wrong_sex_error_message").remove();
        }
        return true;
    }

    function checkBirthdateValidity() {
        let birthdateInput = document.getElementById("birthdate");
        let datePattern = /^((19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))$/g
        if (!(datePattern.test(birthdateInput.value))) {
            if (document.getElementById("wrong_birthday_error_message") != null) {
                document.getElementById("wrong_birthday_error_message").remove();
            }
            birthdateInput.insertAdjacentHTML("afterend", "<div id='wrong_birthday_error_message' class='text-danger'>  Zły format daty. </div>")
            return false;
        }
        if (document.getElementById("wrong_birthday_error_message") != null) {
            document.getElementById("wrong_birthday_error_message").remove();
        }
        return true;
    }

    function checkFirstnameValidity() {
        let nameInput = document.getElementById("firstname");
        let namePattern = /^[A-Z][a-z]{1,}$/;
        if (!(namePattern.test(nameInput.value))) {
            if (document.getElementById("wrong_firstname_error_message") != null) {
                document.getElementById("wrong_firstname_error_message").remove();
            }
            nameInput.insertAdjacentHTML("afterend", "<div id='wrong_firstname_error_message' class='text-danger'>    Imię musi posiadać co najmniej 1 wielką i jedną małą literę. </div>")
            return false;
        }
        if (document.getElementById("wrong_firstname_error_message") != null) {
            document.getElementById("wrong_firstname_error_message").remove();
        }
        return true;
    }

    function checkLastnameValidity() {
        let lastnameInput = document.getElementById("lastname");
        let namePattern = /^[A-Z][a-z]{1,}$/;
        if (!(namePattern.test(lastnameInput.value))) {
            if (document.getElementById("wrong_lastname_error_message") != null) {
                document.getElementById("wrong_lastname_error_message").remove();
            }
            lastnameInput.insertAdjacentHTML("afterend", "<div id='wrong_lastname_error_message' class='text-danger'>   Błędnie podane nazwisko. </div>")
            return false;
        }
        if (document.getElementById("wrong_lastname_error_message") != null) {
            document.getElementById("wrong_lastname_error_message").remove();
        }
        return true;
    }

    function checkPasswordValidity() {
        let passwordInput = document.getElementById("password");
        let passwordPattern = /^[A-Za-z]{8,}$/;
        if (!(passwordPattern.test(passwordInput.value))) {
            if (document.getElementById("wrong_password_error_message") != null) {
                document.getElementById("wrong_password_error_message").remove();
            }
            passwordInput.insertAdjacentHTML("afterend", "<div id='wrong_password_error_message' class='text-danger'>   Hasło musi mieć co najmniej 8 liter. </div>")
            return false;
        }
        if (document.getElementById("wrong_password_error_message") != null) {
            document.getElementById("wrong_password_error_message").remove();
        }
        return true;
    }

    function checkRepeatPasswordValidity() {
        let passwordInput = document.getElementById("password");
        let repeatPasswordInput = document.getElementById("repeat-password");
        if (!(passwordInput.value == repeatPasswordInput.value)) {
            if (document.getElementById("wrong_repeat_password_error_message") != null) {
                document.getElementById("wrong_repeat_password_error_message").remove();
            }
            repeatPasswordInput.insertAdjacentHTML("afterend", "<div id='wrong_repeat_password_error_message' class='text-danger'>   Hasło nie pokrywa się z podanym wcześniej. </div>")
            return false;
        }
        if (document.getElementById("wrong_repeat_password_error_message") != null) {
            document.getElementById("wrong_repeat_password_error_message").remove();
        }
        return true;
    }

});