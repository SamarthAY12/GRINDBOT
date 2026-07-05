// ==============================
// GRINDBOT AI FITNESS COACH
// script.js PART 1
// ==============================

let weightHistory = [];
let energyHistory = [];
let sleepHistory = [];

let weightChart;
let energyChart;
let sleepChart;


// ==============================
// BMI CALCULATION
// ==============================

function calculateBMI(weight, height){

    let h = height / 100;

    return (weight / (h*h)).toFixed(1);

}


// ==============================
// GENERATE AI PLAN
// ==============================

async function generatePlan(){

    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const weight = parseFloat(document.getElementById("weight").value);
    const height = parseFloat(document.getElementById("height").value);
    const goal = document.getElementById("goal").value;
    const activity = document.getElementById("activity").value;
    const diet = document.getElementById("diet").value;

    if(!name || !age || !weight || !height){

        alert("Please fill all fields.");

        return;

    }

    const bmi = calculateBMI(weight,height);

    document.getElementById("bmi").innerHTML = bmi;

    document.getElementById("profileName").innerHTML = name;
    document.getElementById("profileAge").innerHTML = age;
    document.getElementById("profileWeight").innerHTML = weight;
    document.getElementById("profileHeight").innerHTML = height;
    document.getElementById("profileGoal").innerHTML = goal;
    document.getElementById("profileBMI").innerHTML = bmi;

    document.getElementById("result").innerHTML="Generating AI Plan...";

    try{

        const response = await fetch("/generate_plan",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                name,
                age,
                weight,
                height,
                goal,
                activity,
                diet,
                bmi

            })

        });

        const data = await response.json();

        document.getElementById("result").innerHTML = data.plan;

    }

    catch(err){

        document.getElementById("result").innerHTML="Server Error.";

        console.log(err);

    }

}// ==============================
// WEEKLY ANALYSIS
// ==============================

async function analyzeWeek(){

    const currentWeight = parseFloat(document.getElementById("currentWeight").value);
    const energy = parseInt(document.getElementById("energy").value);
    const sleep = parseInt(document.getElementById("sleep").value);
    const notes = document.getElementById("notes").value;

    if(!currentWeight){
        alert("Please enter your current weight.");
        return;
    }

    document.getElementById("weeklyResult").innerHTML="Analyzing your week...";

    try{

        const response = await fetch("/analyze_week",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                currentWeight,
                energy,
                sleep,
                notes

            })

        });

        const data = await response.json();

        document.getElementById("weeklyResult").innerHTML=data.report;

        weightHistory.push(currentWeight);
        energyHistory.push(energy);
        sleepHistory.push(sleep);

        updateCharts();

        updateComparison(currentWeight,energy,sleep);

    }

    catch(err){

        document.getElementById("weeklyResult").innerHTML="Error generating report.";

        console.log(err);

    }

}



// ==============================
// COMPARISON
// ==============================

function updateComparison(weight,energy,sleep){

    document.getElementById("comparison").innerHTML=`

<b>Your Weight:</b> ${weight} kg<br>

<b>Average User:</b> 70 kg<br><br>

<b>Your Energy:</b> ${energy}/5<br>

<b>Average User:</b> 3.5/5<br><br>

<b>Your Sleep:</b> ${sleep}/5<br>

<b>Average User:</b> 3.5/5

`;

}// ==============================
// CHARTS
// ==============================

function updateCharts(){

    const labels = [];

    for(let i=1;i<=weightHistory.length;i++){
        labels.push("Week "+i);
    }

    // Weight Chart

    if(weightChart){
        weightChart.destroy();
    }

    weightChart = new Chart(
        document.getElementById("weightChart"),
        {
            type:"line",
            data:{
                labels:labels,
                datasets:[{
                    label:"Weight (kg)",
                    data:weightHistory,
                    borderColor:"#22c55e",
                    backgroundColor:"rgba(34,197,94,0.2)",
                    fill:true,
                    tension:0.4
                }]
            },
            options:{
                responsive:true
            }
        }
    );



    // Energy Chart

    if(energyChart){
        energyChart.destroy();
    }

    energyChart = new Chart(
        document.getElementById("energyChart"),
        {
            type:"bar",
            data:{
                labels:labels,
                datasets:[{
                    label:"Energy",
                    data:energyHistory,
                    backgroundColor:"#3b82f6"
                }]
            },
            options:{
                responsive:true,
                scales:{
                    y:{
                        beginAtZero:true,
                        max:5
                    }
                }
            }
        }
    );



    // Sleep Chart

    if(sleepChart){
        sleepChart.destroy();
    }

    sleepChart = new Chart(
        document.getElementById("sleepChart"),
        {
            type:"bar",
            data:{
                labels:labels,
                datasets:[{
                    label:"Sleep",
                    data:sleepHistory,
                    backgroundColor:"#f59e0b"
                }]
            },
            options:{
                responsive:true,
                scales:{
                    y:{
                        beginAtZero:true,
                        max:5
                    }
                }
            }
        }
    );

}


// ==============================
// PAGE LOAD
// ==============================

window.onload=function(){

    document.getElementById("bmi").innerHTML="--";

    document.getElementById("result").innerHTML=
    "Generate your AI Fitness Plan.";

    document.getElementById("weeklyResult").innerHTML=
    "Analyze your week to receive an AI report.";

}
// ==============================
// AI CHATBOT
// ==============================

async function askAI(){

    const question =
    document.getElementById("chatQuestion").value;

    if(question==""){
        alert("Please enter a question.");
        return;
    }

    document.getElementById("chatAnswer").innerHTML =
    "🤖 Thinking...";

    try{

        const response = await fetch("/chat_ai",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                question:question
            })

        });

        const data = await response.json();

        document.getElementById("chatAnswer").innerHTML =
        data.answer;

    }

    catch(err){

        document.getElementById("chatAnswer").innerHTML =
        "Server Error.";

    }

}