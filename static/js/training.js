   function reset() {
            $("#model_finised").hide();
            $("#show_results").hide();
            $("#button_results").hide();
            $("#model_trains").show();
            $("#container").show();


        }

        function drop(id) {
            const mlbtn = document.getElementById("dropdownMenuButton");
            const selectedbtn = document.getElementById(id);
            mlbtn.firstChild.data = selectedbtn.firstChild.data;
            $(selectedbtn).removeClass("card").addClass("card bg-primary text-white ");

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "http://127.0.0.1:5000/api/mlalg", true);
            xhttp.send(id);

        }

        $("#model_finised").hide();
        $("#show_results").hide();
        $("#button_results").hide();

        function start_training() {
            window.setInterval(function () {
                    randomizeData();
                }
                , 700);

            resetTimer();
            startTimer();
            axios
                .get('http://127.0.0.1:5000/api/training')
                .then(function (response) {
                    pauseTimer();
                    $("#model_trains").hide(400);
                    $('#model_finised').show(400);
                    $("#show_results").show(400);
                    $("#button_results").show(400);
                    $("#container").hide(400);
                    document.getElementById("p_training_time").innerHTML = "Training Time: " + (response.data.train_time).toFixed(5) + " s";
                    document.getElementById("p_testing_time").innerHTML = "Testing Time: " + (response.data.test_time).toFixed(5) + " s";
                    document.getElementById("p_complete_time").innerHTML = "Overall Time: " + timerDisplay.innerHTML;
                    document.getElementById("p_accuracy").innerHTML = "R2_SCORE: " + response.data.result;

                    if (response.data.f1 != null) {
                        document.getElementById("p_accuracy2").innerHTML = "F1 SCORE: " + response.data.f1;
                    } else {
                        document.getElementById("p_accuracy2").innerHTML = "F1 SCORE: No Score, because of Regression";
                    }
                    // display and evaluate js,html
                    document.getElementById("plot1").innerHTML = response.data.htmls[0].html;
                    eval(response.data.htmls[0].js);
                    document.getElementById("plot2").innerHTML = response.data.htmls[1].html;
                    eval(response.data.htmls[1].js);
                    document.getElementById("plot3").innerHTML = response.data.htmls[2].html;
                    eval(response.data.htmls[2].js);


                    let r2 = parseFloat(response.data.result);
                    if (r2 < 0) {
                        document.getElementById("pasteprogressbar").innerHTML = "<div class=\"progress\">\n" +
                            "                <div class=\"progress-bar bg-danger  role=\"progressbar\"\n" +
                            "                     aria-valuenow=\"0.5\" aria-valuemin=\"0\" aria-valuemax=\"1\" style=\"width: 33%\">poor</div>\n" +
                            "            </div>"
                        document.getElementById("descrprogress").innerHTML = "Any negative R squared value means that the model definition is poor."

                    } else if (r2 == 0) {
                        document.getElementById("pasteprogressbar").innerHTML = "<div class=\"progress\">\n" +
                            "                <div class=\"progress-bar bg-info   role=\"progressbar\"\n" +
                            "                     aria-valuenow=\"0.5\" aria-valuemin=\"0\" aria-valuemax=\"1\" style=\"width: 66%\">mediocre</div>\n" +
                            "            </div>"
                        document.getElementById("descrprogress").innerHTML = "Any R squared value equal to zero means that the regression analysis is a horizontal line through the mean value."
                    } else {
                        document.getElementById("pasteprogressbar").innerHTML = "<div class=\"progress\">\n" +
                            "                <div class=\"progress-bar   role=\"progressbar\"\n" +
                            "                     aria-valuenow=\"0.5\" aria-valuemin=\"0\" aria-valuemax=\"1\" style=\"width: 100%\">good</div>\n" +
                            "            </div>"
                        document.getElementById("descrprogress").innerHTML = "Any R squared value greater than zero means that the regression analysis did better than just using a horizontal line through the mean value."
                    }
                }).catch(error => {
                console.log(error.response)
                alert("Error Strings not supported in Csv");
                pauseTimer();
                $("#model_trains").hide(400);
                $('#model_finised').show(400);
                $("#show_results").show(400);
                $("#button_results").show(400);
                $("#container").hide(400);
            });
        }

        function define_start() {
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "http://127.0.0.1:5000/api/def", false);
            xhttp.send();
            start_training();
        }