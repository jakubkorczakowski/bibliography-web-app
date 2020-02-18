document.addEventListener('DOMContentLoaded', function (event) {

    const GET = "GET";
    const POST = "POST";

    let bibInput = document.getElementById("username");
    let bibForm = document.getElementById("bib-form");


    bibForm.addEventListener("submit", function (event) {
        let reqiuredFields = document.querySelectorAll('#bib-form .required').length;

        let n = 0;
        for (i = 0; i < reqiuredFields; i++) {
            if (event["srcElement"][i].value !== "") {
                n++;
            }
        }

        if (n != reqiuredFields) {
            event.preventDefault();
        }

    });

});