async function generatePlan() {
let weeklyHistory = JSON.parse(localStorage.getItem("weeklyHistory")) || [];
    const name = document.getElementById("name").value;
    const age = parseInt(document.getElementById("age").value);
    const weight = parseFloat(document.getElementById("weight").value);
    const height = parseFloat(document.getElementById("height").value);
    const goal = document.getElementById("goal").value;
    const activity = document.getElementById("activity").value;
    const diet = document.getElementById("diet").value;

    if (!name || !age || !weight || !height) {
        alert("Please fill all fields.");
        return;
    }

    document.getElementById("result").innerText = "Generating AI Plan... Please wait...";
    window.scrollTo({

top:document.body.scrollHeight,

behavior:"smooth"

});

    const response = await fetch("/generate_plan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
             name,
             age,
             weight,
             height,
             goal,
             activity,
             diet
         })
    });

    const data = await response.json();

    document.getElementById("bmi").innerText = data.bmi;

document.getElementById("profileName").innerText = name;
document.getElementById("profileAge").innerText = age;
document.getElementById("profileWeight").innerText = weight;
document.getElementById("profileHeight").innerText = height;
document.getElementById("profileGoal").innerText = goal;
document.getElementById("profileBMI").innerText = data.bmi;

document.getElementById("result").innerText = data.plan;
}
async function analyzeWeek() {

    const currentWeight = parseFloat(document.getElementById("currentWeight").value);
    const energy = document.getElementById("energy").value;
    const sleep = document.getElementById("sleep").value;
    const notes = document.getElementById("notes").value;

    if (!currentWeight) {
        alert("Please enter your current weight.");
        return;
    }

    document.getElementById("weeklyResult").innerText =
        "Analyzing your progress... Please wait...";
        window.scrollTo({

top:document.body.scrollHeight,

behavior:"smooth"

});

    const response = await fetch("/analyze_week", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            currentWeight,
            energy,
            sleep,
            notes
        })

    });

    const data = await response.json();

    document.getElementById("weeklyResult").innerText = data.report;
    weeklyHistory.push({
    weight: currentWeight,
    energy: parseInt(energy),
    sleep: parseInt(sleep)
});

localStorage.setItem(
    "weeklyHistory",
    JSON.stringify(weeklyHistory)
);

drawCharts();    drawCharts(currentWeight, energy, sleep);

}
// ---------------- Charts ----------------

let weightChart;
let energyChart;
let sleepChart;

function drawCharts(){

    const labels = weeklyHistory.map((_, index) => "Week " + (index + 1));

    const weights = weeklyHistory.map(item => item.weight);
    const energies = weeklyHistory.map(item => item.energy);
    const sleeps = weeklyHistory.map(item => item.sleep);

    if(weightChart){
        weightChart.destroy();
        energyChart.destroy();
        sleepChart.destroy();
    }

    weightChart = new Chart(
        document.getElementById("weightChart"),
        {
            type:'line',
            data:{
                labels:labels,
                datasets:[{
                    label:"Weight",
                    data:weights
                }]
            }
        }
    );

    energyChart = new Chart(
        document.getElementById("energyChart"),
        {
            type:'line',
            data:{
                labels:labels,
                datasets:[{
                    label:"Energy",
                    data:energies
                }]
            }
        }
    );

    sleepChart = new Chart(
        document.getElementById("sleepChart"),
        {
            type:'line',
            data:{
                labels:labels,
                datasets:[{
                    label:"Sleep",
                    data:sleeps
                }]
            }
        }
    );

}
window.onload = function(){

    if(weeklyHistory.length > 0){

        drawCharts();
        document.getElementById("comparison").innerHTML = `
<h3>Your Stats</h3>

<p><b>Weight:</b> ${currentWeight} kg</p>

<p><b>Energy:</b> ${energy}/5</p>

<p><b>Sleep:</b> ${sleep}/5</p>

<hr>

<h3>Average User</h3>

<p><b>Weight:</b> 72 kg</p>

<p><b>Energy:</b> 3/5</p>

<p><b>Sleep:</b> 3/5</p>
`;

    }

}