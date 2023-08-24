from flask import Blueprint, request, jsonify
from .extensions import db
from .models import User, Data, Plug
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/get_data', methods=['POST'])
def get_data():
    client_id = request.json.get('client_id')
    if client_id is None:
        return jsonify({'error': 'Client ID is missing in the request.'}), 400
    
    data_entries = Data.query.filter_by(client_id=client_id).all()
    data_list = [
        {
            'time': entry.time,
            'ambient_temp': entry.ambient_temp,
            'current': entry.current,
            'internal_temp': entry.internal_temp,
            'humidity': entry.humidity,
            'voltage': entry.voltage,
        }
        for entry in data_entries
    ]
    return jsonify(data_list)

@main.route('/update_relay_status', methods=['POST'])
def update_relay_status():
    status = request.json.get('status')
    if status is None:
        return jsonify({'error': 'Status value is missing in the request.'}), 400

    if status == 'on':
        status_value = 1
    elif status == 'off':
        status_value = 0
    else:
        return jsonify({'error': 'Invalid status value. It should be either "on" or "off".'}), 400

    plug = Plug.query.first()
    if plug is None:
        plug = Plug(statusOfRelay=status_value)
        db.session.add(plug)
    else:
        plug.statusOfRelay = status_value

    db.session.commit()
    return jsonify({'message': 'Relay status updated successfully.'})

@main.route('/check_plug_state', methods=['POST'])
def check_plug_state():
    data = request.get_json()
    client_id = data.get('client_id')

    if client_id is None:
        return jsonify({'error': 'Client ID is missing in the request.'}), 400

    plug = Plug.query.filter_by(client_id=client_id).first()

    if plug is None:
        # If no plug data is found for the given client_id, assume the default state as off ("0").
        return jsonify({'state': "0"})

    state = plug.stateOfRelay
    return jsonify({'state': state})

#requesting which loads can go off. they'll send you all the plug data and you'll respond with awainaa's system
@main.route('/calculate_and_control_plugs', methods=['POST'])
def calculate_and_control_plugs():
    data = request.get_json()
    total_supply = data.get('total_supply')
    plugs = data.get('plugs', {})

    # Calculate the total power demand and create a dictionary to store the calculated df for each plug
    total_demand = 0
    df_dict = {}
    power_dict  = {}
    for client_id, plug_data in plugs.items():
        voltage = plug_data.get('voltage', 0)
        current = plug_data.get('current', 0)
        internal_temp = plug_data.get('internal_temp', 0)
        ambient_temp = plug_data.get('ambient_temp', 1)  # Set a default value of 1 to avoid division by zero
        humidity = plug_data.get('humidity', 0)

        power = voltage * current
        power_dict[client_id]=power
        total_demand += power
        df = ((4 - internal_temp) * humidity) / ambient_temp
        df_dict[client_id] = df

    # Calculate the loads with df > dfref and determine which plugs to shut off
    dfref = 1  # You can adjust the threshold value as needed
    loads_to_shut_off = [client_id for client_id, df in df_dict.items() if df > dfref]
    power_to_be_taken_off = 0
    for i in loads_to_shut_off:
        power_to_be_taken_off += power_dict[i]

    # Check if shutting off high df loads can meet the supply
    remaining_supply_after_shutoff = total_demand - power_to_be_taken_off

    if remaining_supply_after_shutoff > total_supply:
        # If shutting off high df loads is not enough, try to shut off lower df loads
        loads_to_shut_off = [client_id for client_id, df in df_dict.items() if df > 0]
        remaining_supply_after_shutoff = total_supply - sum(df_dict[client_id] for client_id in loads_to_shut_off)

    # Send commands to shut off plugs and update the stateOfRelay field in the database
    shut_off_clients = []
    for client_id in loads_to_shut_off:
        plug = Plug.query.filter_by(client_id=client_id).first()
        if plug:
            plug.stateOfRelay = "off"
            db.session.commit()
            shut_off_clients.append(client_id)

    return jsonify({'shut_off_clients': shut_off_clients})

#Open Relay
@main.route('/turn_plug_off', methods=['POST'])
def turn_plug_off():
    data = request.get_json()
    client_id = data.get('client_id')

    if client_id is None:
        return jsonify({'error': 'Client ID is missing in the request.'}), 400

    plug = Plug.query.filter_by(client_id=client_id).first()
    print(plug)

    if plug is None:
        return jsonify({'error': 'Plug data not found for the given client_id.'}), 404

    # Update the state of the relay field to off ("0").
    plug.stateOfRelay = "0"

    try:
        db.session.commit()
        return jsonify({'message': 'Plug state updated to off.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update plug state.'}), 500

#Close Relay
@main.route('/turn_plug_on', methods=['POST'])
def turn_plug_on():
    data = request.get_json()
    client_id = data.get('client_id')

    if client_id is None:
        return jsonify({'error': 'Client ID is missing in the request.'}), 400

    plug = Plug.query.filter_by(client_id=client_id).first()

    if plug is None:
        return jsonify({'error': 'Plug data not found for the given client_id.'}), 404

    # Update the state of the relay field to on ("1").
    plug.stateOfRelay = "1"

    try:
        db.session.commit()
        return jsonify({'message': 'Plug state updated to on.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update plug state.'}), 500

#Return Average ambTemp value
# Route for calculating average ambient temperature
@main.route('/average_ambient_temp', methods=['GET'])
def average_ambient_temp():
    try:
        total_ambient_temp = db.session.query(db.func.avg(Data.ambient_temp)).scalar()
        return jsonify({'average_ambient_temp': total_ambient_temp})
    except Exception as e:
        return jsonify({'error': 'Failed to calculate average ambient temperature.'}), 500

#Return list of datapoints for Average ambTemp value
@main.route('/average_ambient_temp_graph_data', methods=['GET'])
def average_ambient_temp_graph_data():
    try:
        # Query to get unique timestamps and their corresponding average ambient temperature
        avg_temp_query = db.session.query(Data.time, func.avg(Data.ambient_temp)) \
            .group_by(Data.time) \
            .order_by(Data.time.asc()) \
            .all()

        # Format data for D3.js
        graph_data = [{'time': str(row[0])[11:][:-10], 'average_ambient_temp': row[1]} for row in avg_temp_query]

        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve graph data.'}), 500

#Return Average intTemp value
# Route for calculating average internal temperature
@main.route('/average_internal_temp', methods=['GET'])
def average_internal_temp():
    try:
        total_internal_temp = db.session.query(db.func.avg(Data.internal_temp)).scalar()
        return jsonify({'average_internal_temp': total_internal_temp})
    except Exception as e:
        return jsonify({'error': 'Failed to calculate average internal temperature.'}), 500

#Return list of datapoints for Average intTemp value
@main.route('/average_internal_temp_graph_data', methods=['GET'])
def average_internal_temp_graph_data():
    try:
        # Query to get unique timestamps and their corresponding average internal temperature
        avg_temp_query = db.session.query(Data.time, func.avg(Data.internal_temp)) \
            .group_by(Data.time) \
            .order_by(Data.time.asc()) \
            .all()
        
        # Format data for D3.js
        graph_data = [{'time': str(row[0])[11:][:-10], 'average_internal_temp': row[1]} for row in avg_temp_query]

        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve graph data.'}), 500

#Return total power value
# Route for calculating total power consumption
@main.route('/total_power_consumption', methods=['GET'])
def total_power_consumption():
    try:
        total_power_queried = 0
        for x in range(1,11):
            data = Data.query.filter_by(client_id=x).first()
            total_power_queried += data.voltage * data.current

        total_power = db.session.query(db.func.sum(Data.voltage * Data.current)).scalar()
        return jsonify({'total_power_consumption': total_power_queried})
    except Exception as e:
        return jsonify({'error': 'Failed to calculate total power consumption.'}), 500

#Return list of datapoints for total power value
@main.route('/total_power_graph_data', methods=['GET'])
def total_power_graph_data():
    try:
        # Query to get unique timestamps and their corresponding total power consumption
        total_power_query = db.session.query(Data.time, func.sum(Data.voltage * Data.current)) \
            .group_by(Data.time) \
            .order_by(Data.time.asc()) \
            .all()

        # Format data for D3.js
        graph_data = [{'time': str(row[0])[11:][:-10], 'total_power': row[1]} for row in total_power_query]

        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve graph data.'}), 500
