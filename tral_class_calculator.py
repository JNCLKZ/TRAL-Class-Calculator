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
    2: 0.05,  # 5% discount for second class
    3: 0.10,  # 10% discount for third class
    4: 0.15   # 15% discount for fourth class
}

# Sibling discount rules
SIBLING_DISCOUNT = 0.05  # 5% discount per class when siblings enroll

# Agency fees
AGENCY_FEE = 25  
ELITE_AGENCY_FEE = 25  

@app.route('/')
def home():
    return "Welcome to The Rose Arts London Class Calculator API!"

@app.route('/calculate_fee', methods=['POST'])
def calculate_fee():
    data = request.json
    students = data.get("students", [])
    discretionary_discount = data.get("discretionary_discount", 0)
    include_agency = data.get("include_agency", False)
    include_elite_agency = data.get("include_elite_agency", False)
    include_sibling_discount = data.get("include_sibling_discount", False)

    class_fees_flat = {class_name: fee for group in CLASS_FEES.values() for class_name, fee in group.items()}
    all_classes = []
    student_discounts = []
    class_discount_breakdown = []

    # Calculate class costs before discounts
    for student in students:
        student_classes = student.get("classes", [])
        all_classes.extend(student_classes)

        # Apply class count discount
        num_classes = len(student_classes)
        discount_rate = CLASS_DISCOUNTS.get(num_classes, 0)

        if num_classes > 1:
            cheapest_class = min(student_classes, key=lambda cls: class_fees_flat.get(cls, 0))
            discount_amount = class_fees_flat.get(cheapest_class, 0) * discount_rate
            student_discounts.append(discount_amount)
            class_discount_breakdown.append({"class": cheapest_class, "discount": round(discount_amount, 2)})

    monthly_cost_before_discount = sum(class_fees_flat.get(cls, 0) for cls in all_classes)
    total_discount = sum(student_discounts)

    # ✅ Apply sibling discount **only if selected** and **if multiple students exist**
    sibling_discount_amount = 0
    if include_sibling_discount and len(students) > 1:
        sibling_discount_amount = sum(class_fees_flat.get(cls, 0) * SIBLING_DISCOUNT for cls in all_classes)
        total_discount += sibling_discount_amount

    # Apply discretionary discount
    discretionary_discount_amount = monthly_cost_before_discount * (discretionary_discount / 100)
    total_discount += discretionary_discount_amount

    # Final cost calculations
    monthly_total = monthly_cost_before_discount - total_discount
    term_total = monthly_total * 3  # ✅ Each term is 3 months
    annual_total = term_total * 3  # ✅ 3 terms in a year
    monthly_installment = annual_total / 12  # ✅ Monthly breakdown over 12 months

    # Add agency fees
    if include_agency:
        monthly_total += AGENCY_FEE
    if include_elite_agency:
        monthly_total += ELITE_AGENCY_FEE

    # Payment schedule
    payment_schedule = {
        "Spring": ["Jan", "Feb", "March"],
        "Summer": ["May", "June", "July"],
        "Autumn": ["Sept", "Oct", "Nov", "Dec"]
    }

    return jsonify({
        "monthly_total": round(monthly_total, 2),
        "term_total": round(term_total, 2),  # ✅ Now correctly calculated
        "annual_total": round(annual_total, 2),  # ✅ Now correctly calculated
        "monthly_installment": round(monthly_installment, 2),  # ✅ Now included
        "discretionary_discount_applied": round(discretionary_discount_amount, 2),
        "sibling_discount_applied": round(sibling_discount_amount, 2) if include_sibling_discount else 0,
        "class_discounts": class_discount_breakdown,  # ✅ Shows discounts applied to each class
        "payment_schedule": payment_schedule
    })

# 🚀 Corrected Run Block for Deployment 🚀
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
