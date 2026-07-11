const ctx = document.getElementById("riskChart");

new Chart(ctx, {

    type: "bar",

    data: {

        labels: [
            "Low Risk",
            "Medium Risk",
            "High Risk"
        ],

        datasets: [{

            label: "Students",

            data: [15,8,5],

            borderWidth: 1

        }]
    },

    options: {

        responsive:true,

        plugins:{
            legend:{
                display:false
            }
        },

        scales:{
            y:{
                beginAtZero:true
            }
        }

    }

});