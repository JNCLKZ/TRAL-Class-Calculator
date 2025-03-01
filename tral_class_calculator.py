<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRAL Class Fee Calculator</title>
    <style>
        #calculator-container { 
            font-family: Arial, sans-serif; 
            max-width: 600px; 
            margin: auto; 
            padding: 20px; 
        }
        #calculator-container h2, #calculator-container h3 { margin-bottom: 10px; }
        #calculator-container form, #result-container { 
            border: 1px solid #ccc; 
            padding: 15px; 
            border-radius: 8px; 
            background: #f9f9f9; 
        }
        .student { 
            margin-bottom: 10px; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            background: #fff; 
        }
        #calculator-container label { font-weight: bold; display: block; margin-top: 8px; }
        #calculator-container select, #calculator-container input { width: 100%; padding: 5px; margin-top: 5px; }
        #calculator-container button { 
            margin-top: 10px; 
            padding: 8px; 
            border: none; 
            background: #007BFF; 
            color: white; 
            border-radius: 5px; 
            cursor: pointer; 
        }
        #calculator-container button.remove-student { background: #DC3545; }
        #calculator-container button.clear-results { background: #6c757d; }
        #calculator-container ul { padding-left: 15px; }
        .checkbox-container, .input-container {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
        }
        .checkbox-container label, .input-container label {
            flex-grow: 1;
        }
    </style>
</head>
<body>

<div id="calculator-container">
    <h2>TRAL Class Fee Calculator</h2>
    
    <form id="classCalculatorForm">
        <h3>Select Classes for Each Student</h3>
        
        <div id="students-container">
            <div class="student">
                <label>Student Name:</label>
                <input type="text" class="student-name" placeholder="Enter name" required>

                <label>Select Classes:</label>
                <select multiple class="student-classes">
                    <option value="Ballet">Ballet (£40)</option>
                    <option value="Contemporary">Contemporary (£70)</option>
                    <option value="Breakdance Elites">Breakdance Elites (£80)</option>
                    <option value="Body Conditioning">Body Conditioning (£50)</option>
                    <option value="Street Dance">Street Dance (£50)</option>
                    <option value="Junior Elites">Junior Elites (£60)</option>
                    <option value="Musical Theatre + Commercial">Musical Theatre + Commercial (£50)</option>
                    <option value="Junior Industry Workshops">Junior Industry Workshops (£15)</option>
                    <option value="Drama and Musical Theatre">Drama and Musical Theatre (£70)</option>
                    <option value="Commercial Street (45 mins)">Commercial Street (45 mins) (£40)</option>
                </select>

                <button type="button" class="remove-student">Remove</button>
            </div>
        </div>

        <div class="checkbox-container">
            <input type="checkbox" id="includeSiblingDiscount">
            <label for="includeSiblingDiscount">Apply Sibling Discount</label>
        </div>
        
        <div class="checkbox-container">
            <input type="checkbox" id="includeAgency">
            <label for="includeAgency">Include Standard Agency Fee (£25/month)</label>
        </div>

        <div class="checkbox-container">
            <input type="checkbox" id="includeEliteAgency">
            <label for="includeEliteAgency">Include Elite Agency Fee (£25/month)</label>
        </div>

        <div class="input-container">
            <label for="discretionaryDiscount">Discretionary Discount (%):</label>
            <input type="number" id="discretionaryDiscount" min="0" max="100" value="0">
        </div>

        <button type="button" id="addStudent">+ Add Another Student</button>
        <button type="button" id="calculateFees">Calculate Fees</button>
        <button type="button" id="clearResults" class="clear-results">Clear Results</button>
    </form>

    <h3>Results:</h3>
    <div id="result-container">
        <div id="result"></div>
    </div>
</div>

<script>
    document.getElementById("calculateFees").addEventListener("click", async function () {
        let students = [];

        document.querySelectorAll(".student").forEach(studentDiv => {
            let name = studentDiv.querySelector(".student-name").value;
            let classes = Array.from(studentDiv.querySelector(".student-classes").selectedOptions).map(option => option.value);

            if (name && classes.length > 0) {
                students.push({ name: name, classes: classes });
            }
        });

        if (students.length === 0) {
            document.getElementById("result").textContent = "Error: Please add at least one student and select classes.";
            return;
        }

        let includeSiblingDiscount = document.getElementById("includeSiblingDiscount").checked;
        let includeAgency = document.getElementById("includeAgency").checked;
        let includeEliteAgency = document.getElementById("includeEliteAgency").checked;
        let discretionaryDiscount = parseFloat(document.getElementById("discretionaryDiscount").value) || 0;

        try {
            const response = await fetch("https://tral-class-calculator-27ku.onrender.com/calculate_fee", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    students: students, 
                    include_sibling_discount: includeSiblingDiscount,
                    include_agency: includeAgency,
                    include_elite_agency: includeEliteAgency,
                    discretionary_discount: discretionaryDiscount 
                })
            });

            const result = await response.json();
            document.getElementById("result").innerHTML = `<h3>Payment Breakdown:</h3>
                ${students.map(student => `<p><strong>${student.name}:</strong> ${student.classes.join(", ")}</p>`).join("")}
                <p><strong>Annual Total:</strong> £${result.annual_total}</p>
                <p><strong>Term Total:</strong> £${result.term_total}</p>
                <p><strong>Monthly Total:</strong> £${result.monthly_total}</p>`;
        } catch (error) {
            document.getElementById("result").textContent = "Error: " + error.message;
        }
    });
</script>
</body>
</html>
