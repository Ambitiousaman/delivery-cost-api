from flask import Flask, request, jsonify

app = Flask(__name__)

# Constants for the problem
CENTERS = {
    'C1': ['A', 'B', 'C'],
    'C2': ['D', 'E', 'F'],
    'C3': ['G', 'H', 'I']
}

WEIGHTS = {
    'A': 3, 'B': 2, 'C': 8,
    'D': 12, 'E': 25, 'F': 15,
    'G': 0.5, 'H': 1, 'I': 2
}

DISTANCES = {
    'C1_L1': 3,
    'C2_L1': 2.5,
    'C3_L1': 2,
    'C1_C2': 4,
    'C2_C3': 3,
    'C1_C3': 5
}

def calculate_center_requirements(order):
    center_needs = {'C1': False, 'C2': False, 'C3': False}
    for product, quantity in order.items():
        if quantity > 0:
            if product in CENTERS['C1']:
                center_needs['C1'] = True
            elif product in CENTERS['C2']:
                center_needs['C2'] = True
            elif product in CENTERS['C3']:
                center_needs['C3'] = True
    return center_needs

def calculate_total_weight(order):
    return sum(WEIGHTS[product] * quantity for product, quantity in order.items() if quantity > 0)

def calculate_delivery_cost(centers_needed, total_weight):
    routes = {
        'C1': DISTANCES['C1_L1'] * 2,
        'C2': DISTANCES['C2_L1'] * 2,
        'C3': DISTANCES['C3_L1'] * 2,
        'C1_C2': DISTANCES['C1_C2'] + DISTANCES['C2_L1'] + DISTANCES['C1_L1'],
        'C2_C3': DISTANCES['C2_C3'] + DISTANCES['C3_L1'] + DISTANCES['C2_L1'],
        'C1_C3': DISTANCES['C1_L1'] + DISTANCES['C3_L1'] + 5,
        'C1_C2_C3': DISTANCES['C1_C2'] + DISTANCES['C2_C3'] + DISTANCES['C3_L1'] + DISTANCES['C1_L1']
    }

    needed = [center for center, needed in centers_needed.items() if needed]
    
    if len(needed) == 1:
        route_distance = routes[needed[0]]
    elif len(needed) == 2:
        if 'C1' in needed and 'C2' in needed:
            route_distance = routes['C1_C2']
        elif 'C2' in needed and 'C3' in needed:
            route_distance = routes['C2_C3']
        elif 'C1' in needed and 'C3' in needed:
            route_distance = routes['C1_C3']
    else:
        route_distance = routes['C1_C2_C3']

    if total_weight <= 5:
        cost_per_unit = 10
    elif total_weight <= 15:
        cost_per_unit = 15
    elif total_weight <= 25:
        cost_per_unit = 20
    else:
        cost_per_unit = 25

    return int(route_distance * cost_per_unit)

@app.route('/', methods=['GET'])
def home():
    return "Delivery Cost Calculator API is running!"

@app.route('/calculate-delivery-cost', methods=['POST'])
def calculate_cost():
    try:
        order = request.json
        
        if not order or not all(isinstance(v, (int, float)) for v in order.values()):
            return jsonify({'error': 'Invalid input format'}), 400

        centers_needed = calculate_center_requirements(order)
        total_weight = calculate_total_weight(order)
        minimum_cost = calculate_delivery_cost(centers_needed, total_weight)
        
        return jsonify({'minimum_cost': minimum_cost})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)