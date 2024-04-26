from flask import jsonify
from datetime import datetime
from db.models import Equipment
from db import db
from io import StringIO
from datetime import datetime, timezone, timedelta

def validate_json_data(json_data):
    if not isinstance(json_data, dict):
        return jsonify({"error": "Invalid JSON format. Expected a dictionary."}), 400

    if json_data['value'] is None:
        return jsonify({'error': 'Value cannot be null. Please, upload csv.'}), 400

    required_fields = ['equipmentId', 'timestamp', 'value']
    if not all(field in json_data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

def parse_timestamp(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
        return None

def check_existing_equipment(equipment_id, timestamp, value):
    existing_equipment = Equipment.query.filter_by(
        equipment_id=equipment_id,
        timestamp=timestamp,
        value=value
    ).first()

    if existing_equipment:
        return jsonify({'error': f'Equipment already exists'}), 400

def create_new_equipment(equipment_id, timestamp, value):
    return Equipment(
        equipment_id=equipment_id,
        timestamp=timestamp,
        value=value
    )

def validate_csv(df):
    expected_columns = ['equipmentId', 'timestamp', 'value']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError('CSV file is missing required columns: "equipmentId", "timestamp", "value"')

def process_csv_data(df):
    existing_equipment_list = []
    new_equipment_list = []

    for _, row in df.iterrows():
        equipment_id, timestamp_str, value = row['equipmentId'], row['timestamp'], row['value']

        timestamp = parse_timestamp(timestamp_str)

        existing_equipment, new_equipment = find_or_create_equipment(equipment_id, timestamp, value)

        if existing_equipment:
            existing_equipment_list.append(format_equipment(existing_equipment))
        else:
            new_equipment_list.append(format_equipment(new_equipment))

    return existing_equipment_list, new_equipment_list

def parse_timestamp(timestamp_str):
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.000%z')
    except ValueError:
        raise ValueError(f'Invalid timestamp format: {timestamp_str}')

def find_or_create_equipment(equipment_id, timestamp, value):
    existing_equipment = Equipment.query.filter_by(equipment_id=equipment_id, timestamp=timestamp).first()

    if existing_equipment:
        return existing_equipment, None
    else:
        new_equipment = Equipment(equipment_id=equipment_id, timestamp=timestamp, value=value)
        db.session.add(new_equipment)
        return None, new_equipment

def format_equipment(equipment):
    return {
        'equipmentId': equipment.equipment_id,
        'timestamp': equipment.timestamp.strftime('%Y-%m-%dT%H:%M:%S.000%z'),
        'value': equipment.value
    }


def calculate_averages(records):
    intervals = {
        '24h': timedelta(hours=24),
        '48h': timedelta(hours=48),
        'week': timedelta(weeks=1),
        'month': timedelta(days=30)
    }

    averages = {}
    for interval, delta in intervals.items():
        filtered_records = [record.value for record in records if record.timestamp >= datetime.now() - delta]
        averages[f'average_{interval}'] = sum(filtered_records) / len(filtered_records) if filtered_records else 0

    return averages