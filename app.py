from flask import Flask, request, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_unified_time_slots(start, end, lec_duration, lab_duration, lunch_break, lab_frequency):
    slots = []
    current_time = start * 60  # Convert start time to minutes
    end_time = end * 60  # Convert end time to minutes
    lunch_start = lunch_break['start'] * 60  # Convert lunch start to minutes
    lunch_end = lunch_break['end'] * 60  # Convert lunch end to minutes

    while current_time < end_time:
        # Check if the current time is during lunch break
        if lunch_start <= current_time < lunch_end:
            current_time = lunch_end  # Skip lunch break
            continue
        
        # Check for lecture time slot
        if current_time + lec_duration <= end_time:
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_lec_minute = current_time + lec_duration
            lec_end_hour = end_lec_minute // 60
            lec_end_minute = end_lec_minute % 60
            slots.append({"type": "lecture", "slot": f"{start_hour:02}:{start_minute:02}-{lec_end_hour:02}:{lec_end_minute:02}"})
            current_time += lec_duration
        
        # Check for lab time slot
        if current_time + lab_duration <= end_time:
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_lab_minute = current_time + lab_duration
            lab_end_hour = end_lab_minute // 60
            lab_end_minute = end_lab_minute % 60
            slots.append({"type": "lab", "slot": f"{start_hour:02}:{start_minute:02}-{lab_end_hour:02}:{lab_end_minute:02}"})
            current_time += lab_duration

        # Insert a break time slot if applicable
        if current_time + 10 <= end_time and current_time < lunch_start:  # Check if we can add a break before lunch
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_break_minute = current_time + 10
            break_end_hour = end_break_minute // 60
            break_end_minute = end_break_minute % 60
            slots.append({"type": "break", "slot": f"{start_hour:02}:{start_minute:02}-{break_end_hour:02}:{break_end_minute:02}"})
            current_time += 10  # Move past the break time

    return slots
def assign_room(prefix, room_count):
    """Assign a room based on a prefix and room count."""
    return f"{prefix}-{random.randint(1, room_count)}"

def generate_random_timetable(batches, subjects, labs, theory_rooms, lab_rooms, college_start, college_end, lec_duration, lab_duration, days, lunch_break):
    unified_time_slots = generate_unified_time_slots(college_start, college_end, lec_duration, lab_duration, lunch_break, labs)

    # Initialize timetable with string keys for time slots
    timetable = {slot['slot']: {day: [] for day in days} for slot in unified_time_slots}

    # Track how many times each lab is scheduled for each batch over the week
    weekly_lab_count = {batch: {lab: 0 for lab in labs.keys()} for batch in batches}

    for day in days:
        # Track how many labs are scheduled on this particular day
        daily_lab_count = {lab: 0 for lab in labs.keys()}  # Track labs scheduled per day for the entire batch

        for slot_info in unified_time_slots:
            slot_type = slot_info['type']
            slot = slot_info['slot']

            if slot_type == 'lecture':
                subject = random.choice(list(subjects.keys()))
                teacher = subjects[subject]
                room = assign_room("A1", theory_rooms)
                
                timetable[slot][day].append({
                    "subject": subject,
                    "teacher": teacher,
                    "room": room,
                    "batches": batches,
                    "time": slot,
                    "type": slot_type
                })

            elif slot_type == 'lab':
                lab_scheduled = False  # Flag to track if a lab has been scheduled

                for lab, details in labs.items():
                    # Check if the lab has reached the frequency limit for all batches over the week
                    if daily_lab_count[lab] < 2:  # Only allow up to 2 labs per day
                        room = assign_room("A2", lab_rooms)

                        for batch in batches:
                            if weekly_lab_count[batch][lab] < details['frequency']:
                                # Schedule the lab for each batch
                                timetable[slot][day].append({
                                    "subject": lab,
                                    "teacher": details['teacher'],
                                    "room": room,
                                    "batch": batch,
                                    "time": slot,
                                    "type": slot_type
                                })

                                weekly_lab_count[batch][lab] += 1  # Increment the total count for this lab for the batch
                                lab_scheduled = True  # Lab has been scheduled for the batch
                        
                        if lab_scheduled:
                            daily_lab_count[lab] += 1  # Increment the daily count for this lab
                            break  # Move to the next slot once a lab is scheduled for all batches

                # If no lab was scheduled in this slot, try to schedule a lecture instead
                if not lab_scheduled:
                    subject = random.choice(list(subjects.keys()))
                    teacher = subjects[subject]
                    room = assign_room("A1", theory_rooms)

                    timetable[slot][day].append({
                        "subject": subject,
                        "teacher": teacher,
                        "room": room,
                        "batches": batches,
                        "time": slot,
                        "type": "lecture"
                    })

            elif slot_type == 'break':
                timetable[slot][day].append({
                    "subject": "Break",
                    "teacher": "",
                    "room": "",
                    "batch": "",
                    "time": slot,
                    "type": slot_type
                })

    return timetable



# Flask API Endpoints
@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    data = request.json
    # print("Received data:", data)

    # Validate incoming data
    required_fields = ['batches', 'theory_rooms', 'lab_rooms', 'total_faculty', 'subjects', 'lab_subjects', 'start_time', 'end_time', 'lec_duration', 'lab_duration', 'days']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Extract input values
        batches = data['batches']
        theory_rooms = int(data['theory_rooms'])
        lab_rooms = int(data['lab_rooms'])
        total_faculty = int(data['total_faculty'])
        subjects = data['subjects']
        lab_subjects = data['lab_subjects']

        # Convert time strings to minutes
        start_time = int(data['start_time'])  
        end_time = int(data['end_time']) 
        lec_duration = int(data['lec_duration']) 
        lab_duration = int(data['lab_duration']) 
        days = data['days']
        lunch_break = data.get('lunch_break', {'start': 12, 'end': 13})
        
        # Convert subjects and lab_subjects lists to dictionaries
        subject_dict = {sub['subject']: sub['teacher'] for sub in subjects}
        lab_subject_dict = {lab['subject']: {'teacher': lab['teacher'], 'frequency': lab['frequency']} for lab in lab_subjects}

        # Generate the timetable using the random generation function
        timetable = generate_random_timetable(batches, subject_dict, lab_subject_dict, theory_rooms, lab_rooms, start_time, end_time, lec_duration, lab_duration, days, lunch_break)

        print("timetable",timetable)
        return jsonify(timetable), 200
    except KeyError as ke:
        return jsonify({"error": f"Missing key: {str(ke)}"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)