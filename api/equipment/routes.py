import pandas as pd
from . import equipment
from db import db
from db.models import Equipment
from flask import request, jsonify, render_template
from datetime import datetime
from .equipment_utils import *

@equipment.route('/', methods=['POST'])
def add_equipment():

    json_data = request.json

    error_response = validate_json_data(json_data)
    if error_response:
        return error_response

    timestamp = parse_timestamp(json_data['timestamp'])
    if not timestamp:
        return jsonify({'error': 'Invalid timestamp format'}), 400

    error_response = check_existing_equipment(json_data['equipmentId'], timestamp, json_data['value'])
    if error_response:
        return error_response

    new_equipment = create_new_equipment(json_data['equipmentId'], timestamp, json_data['value'])
    db.session.add(new_equipment)
    db.session.commit()

    return jsonify({'message': 'Equipment added successfully'}), 201


@equipment.route('/upload_csv', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        df = pd.read_csv(file, sep=',', skipinitialspace=True)
        validate_csv(df)

        existing_equipment_list, new_equipment_list = process_csv_data(df)

        db.session.commit()

        response = {
            'message': 'CSV data uploaded successfully',
            'existing_equipment': existing_equipment_list,
            'new_equipment': new_equipment_list
        }

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@equipment.route('/home', methods=['GET'])
def index():
    equipment_ids = db.session.query(Equipment.equipment_id).distinct()
    print(equipment_ids)
    return render_template('index.html', equipment_ids=equipment_ids)


@equipment.route('/equipment-records', methods=['GET'])
def get_equipment_records():
    try:
        equipment_id = request.args.get('equipment_id')
        if not equipment_id:
            return jsonify({'error': 'No equipment ID provided'}), 400

        now = datetime.now()

        records = Equipment.query.filter_by(equipment_id=equipment_id).all()
        if not records:
            return jsonify({'error': 'No records found for the provided equipment ID'}), 404

        averages = calculate_averages(records)

        return jsonify({
            'equipment_id': equipment_id,
            **averages,
            'timestamp': now.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500