const realBtn = document.getElementById("real-file");
const customCSVBtn = document.getElementById("custom-csvbtn");
const customCodeBtn = document.getElementById("custom-codebtn");

const realBtn2 = document.getElementById("real-file2");
const realSubBtn2 = document.getElementById("sub-file2");


const realSubBtn = document.getElementById("sub-file");

customCSVBtn.addEventListener("click", function () {
    realBtn.click();
});

customCodeBtn.addEventListener("click", function () {
    realBtn2.click();
});

realBtn.addEventListener("change", function () {
    if (realBtn.value) {
        realSubBtn.click()
    }
});
realBtn2.addEventListener("change", function () {
    if (realBtn2.value) {
        realSubBtn2.click()
    }
});