from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Import CORS
import os

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# Define class fees with group categories
CLASS_FEES = {
    "Sow & Grow Nurture": {
        "Introduction to The Arts": 50  # Nurture class
    },
    "Sow & Grow Progression": {
        "Breakdance Elites": 80,
        "Street Dance": 50,
        "Junior Elites": 60,
        "Musical Theatre + Commercial": 50,
        "Body Conditioning": 50,
        "Ballet, Jazz and Contemporary": 40,
        "Junior Industry Workshops": 15
    },
    "Inters & Teens": {
        "Contemporary": 70,
        "Body Conditioning": 50,
        "Ballet": 40,
        "Commercial Street (45 mins)": 40,
        "Drama and Musical Theatre": 70,
        "Inter & Senior Industry Workshop": 25
    },
    "Elite Inters": {
        "Elite Training": 80
    }
}

# Discount structure based on class count
CLASS_DISCOUNTS = {
    2: 0.05,  # 5% for second class
    3: 0.10,  # 10% for third class
    4: 0.15   # 15% for fourth class
}

# Sibling discount rules
SIBLING_DISCOUNT = 0.05  # 5% discount on the second class for siblings

# Agency fee (inclusive of training)
AGENCY_FEE = 25  # Updated to £25 per month
ELITE_AGENCY_FEE = 25  # Updated Elite Agency Fee to £25 per month

@app.route('/')
def home():
    return "Welcome to The Rose Arts London Class Calculator API!"

@app.route('/calculate_fee', methods=['POST'])
def calculate_fee():
    data = request.json
    students = data.get("students", [])
    discretionary_discount = data.get("discretionary_discount", 0)  # Manual override discount
    include_agency = data.get("include_agency", False)  # Include standard agency fee
    include_elite_agency = data.get("include_elite_agency", False)  # Include elite agency fee
    include_sibling_discount = data.get("include_sibling_discount", False)  # ✅ New sibling discount flag
    
    all_classes = []
    student_discounts = []
    
    # Flatten the CLASS_FEES dictionary for easier access
    class_fees_flat = {class_name: fee for group in CLASS_FEES.values() for class_name, fee in group.items()}
    
    for student in students:
        student_classes = student.get("classes", [])
        all_classes.extend(student_classes)
        
        # Determine discount based on number of classes
        num_classes = len(student_classes)
        discount_rate = CLASS_DISCOUNTS.get(num_classes, 0)
        student_discounts.append((student_classes, discount_rate))
    
    # Calculate total monthly cost before discount
    monthly_cost_before_discount = sum(class_fees_flat.get(cls, 0) for cls in all_classes)
    
    total_discount = 0
    
    # ✅ Ensure discounts apply to a single student with multiple classes
    sibling_discount_amount = 0
    if include_sibling_discount and len(students) > 1:
        sibling_discount_amount = total_discount
    elif len(students) == 1 and len(students[0]["classes"]) > 1:
    # ✅ Apply discount even if only one student has multiple classes
        cheapest_class = min(students[0]["classes"], key=lambda cls: class_fees_flat.get(cls, 0))
        sibling_discount_amount = class_fees_flat.get(cheapest_class, 0) * 0.05  # 5% discount

    
    # ✅ Apply sibling discount **only if selected**
    sibling_discount_amount = 0
    if include_sibling_discount and len(students) > 1:
        sibling_discount_amount = total_discount  # Apply calculated sibling discount
    
    # Apply discretionary discount (manual override)
    discretionary_discount_amount = monthly_cost_before_discount * (discretionary_discount / 100)
    total_discount += discretionary_discount_amount
    
    # Calculate final costs
    monthly_total = monthly_cost_before_discount - total_discount - sibling_discount_amount
    term_total = (monthly_total / 3) * 12  # Adjusted for a 12-week term
    
    # Annual payment: Total term cost x 3 x 3, then divided by 12 months
    annual_total = (term_total * 3 * 3) / 12
    
    # Add agency fees if applicable
    if include_agency:
        monthly_total += AGENCY_FEE  # £25 per month
    if include_elite_agency:
        monthly_total += ELITE_AGENCY_FEE  # £25 per month
    
    # Payment schedule (9-month term roll)
    payment_schedule = {
        "Spring": ["Jan", "Feb", "March"],
        "Summer": ["May", "June", "July"],
        "Autumn": ["Sept", "Oct", "Nov", "Dec"]
    }
    
    return jsonify({
        "monthly_total": round(monthly_total, 2),
        "term_total": round(term_total, 2),
        "annual_total": round(annual_total, 2),
        "discretionary_discount_applied": round(discretionary_discount_amount, 2),
        "sibling_discount_applied": round(sibling_discount_amount, 2) if include_sibling_discount else 0,  # ✅ Only show discount if applied
        "payment_schedule": payment_schedule
    })

# 🚀 Corrected Run Block for Deployment 🚀
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Get port from Render
    app.run(host="0.0.0.0", port=port, debug=False)  # Ensure Flask binds to all interfaces
