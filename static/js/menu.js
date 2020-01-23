const toggle = document.getElementById("customSwitches");
const mlbtn = document.getElementById("dropdownMenuButton");
const modelselect = document.getElementById("model_select");
const uploadcode = document.getElementById("upload_code");
const choosemodel = document.getElementById("choose_model");
modelselect.hidden = true;
customCodeBtn.hidden = false;
mlbtn.hidden = true;
customCodeBtn.hidden = false;
choosemodel.hidden = true;

var togglebool = false;


toggle.addEventListener("click", function () {
    if (togglebool) {
        togglebool = false;
        mlbtn.hidden = true;
        customCodeBtn.hidden = false;
        modelselect.hidden = true;
        uploadcode.hidden = false;
        choosemodel.hidden = true;

    } else {
        togglebool = true;
        mlbtn.hidden = false;
        customCodeBtn.hidden = true;
        modelselect.hidden = false;
        uploadcode.hidden = true;
        choosemodel.hidden = false;
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "http://127.0.0.1:5000/api/toggle", true);
    xhttp.send(togglebool);


})
