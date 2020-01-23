var randomColorGenerator = function () {
    return '#' + (Math.random().toString(16) + '0000000').slice(2, 8);
};

let data_chart = [1, 10, 5, 2, 20, 30, 45];
myData = {
    labels: ["", "", "", "", "", "", ""],
    datasets: [
        {
            data: data_chart,
            backgroundColor: [randomColorGenerator(), randomColorGenerator(), randomColorGenerator(), randomColorGenerator(), randomColorGenerator(), randomColorGenerator(), randomColorGenerator()],
            scaleLineColor: 'transparent'
        }]
};

// Default chart defined with type: 'line'
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: myData,
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    display: false
                },
                gridLines: {
                    display: false,
                },
                display: false

            }],
            xAxes: [{
                gridLines: {
                    display: false,

                },
                angleLines: {
                    display: false
                },
                display: false
            }],
        },
        legend: {
            display: false,

        }

    }

});

// Function runs on chart type select update


// Randomize data button function
function randomizeData() {
    let newdata_chart = data_chart.map(x => Math.floor(Math.random() * 50));

    myData.datasets[0].data = newdata_chart
    myChart.update();
};

