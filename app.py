from flask import Flask, request, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_unified_time_slots(start, end, lec_duration, lab_duration, lunch_break):
    """Generate a unified time slot list for lectures and labs without exceeding the end time and respecting lunch breaks."""
    slots = []
    current_time = start * 60  # Convert start time to minutes
    end_time = end * 60  # Convert end time to minutes
    lunch_start = lunch_break['start'] * 60  # Convert lunch start to minutes
    lunch_end = lunch_break['end'] * 60  # Convert lunch end to minutes

    while current_time + lec_duration <= end_time:
        # Check if the current time is during lunch break
        if lunch_start <= current_time < lunch_end:
            current_time = lunch_end  # Skip lunch break
        
        start_hour = current_time // 60
        start_minute = current_time % 60
        end_lec_minute = current_time + lec_duration

        lec_end_hour = end_lec_minute // 60
        lec_end_minute = end_lec_minute % 60

        # Lecture time slot as string "start-end"
        lec_time_slot = f"{start_hour:02}:{start_minute:02}-{lec_end_hour:02}:{lec_end_minute:02}"
        slots.append({"type": "lecture", "slot": lec_time_slot})

        current_time += lec_duration  # Move to next lecture slot

        if current_time + lab_duration <= end_time:
            # Check if the current time is during lunch break
            if lunch_start <= current_time < lunch_end:
                current_time = lunch_end  # Skip lunch break
            
            # Lab time slot as string "start-end"
            end_lab_minute = current_time + lab_duration
            lab_end_hour = end_lab_minute // 60
            lab_end_minute = end_lab_minute % 60

            lab_time_slot = f"{start_hour:02}:{start_minute:02}-{lab_end_hour:02}:{lab_end_minute:02}"
            slots.append({"type": "lab", "slot": lab_time_slot})

            current_time += lab_duration  # Move to next lab slot

    return slots

def assign_room(prefix, room_count):
    """Assign a room based on a prefix and room count."""
    return f"{prefix}-{random.randint(1, room_count)}"

def generate_random_timetable(batches, subjects, labs, theory_rooms, lab_rooms, college_start, college_end, lec_duration, lab_duration, days, lunch_break):
    """Generates a random timetable for each batch based on the provided inputs."""
    unified_time_slots = generate_unified_time_slots(college_start, college_end, lec_duration, lab_duration, lunch_break)

    if not unified_time_slots:
        raise ValueError("No valid time slots generated.")

    # Initialize timetable with string keys for time slots
    timetable = {slot['slot']: {day: [] for day in days} for slot in unified_time_slots}

    for day in days:
        scheduled_labs = set()  # Track labs that have been scheduled for the day

        # Assign lectures and labs based on unified time slots
        for slot_info in unified_time_slots:
            slot_type = slot_info['type']
            slot = slot_info['slot']

            if slot_type == 'lecture':
                # Lectures are common to all batches
                subject = random.choice(list(subjects.keys()))
                teacher = subjects[subject]
                room = assign_room("A1", theory_rooms)
                
                # Only one lecture per time slot for all batches
                if not timetable[slot][day]:
                    timetable[slot][day].append({
                        "subject": subject,
                        "teacher": teacher,
                        "room": room,
                        "batches": batches,  # Assign all batches to the same lecture
                        "time": slot,  # Use the string time slot directly
                        "type": slot_type
                    })
            else:
                # Labs are per batch, ensure all batches are assigned labs
                remaining_batches = list(batches)  # Keep track of batches that still need a lab assignment
                
                for room in range(1, lab_rooms + 1):
                    if remaining_batches:
                        for batch in remaining_batches:
                            if not remaining_batches:
                                break

                            # If all labs have been scheduled, start rotating through the labs again
                            if len(scheduled_labs) == len(labs):
                                scheduled_labs.clear()  # Clear the set to allow reassigning labs

                            # Select a lab subject that hasn't been scheduled yet for this round
                            available_labs = [lab for lab in labs.keys() if lab not in scheduled_labs]
                            
                            if available_labs:
                                subject = random.choice(available_labs)
                                teacher = labs[subject]
                                assigned_room = f"A2-{room}"  # Lab room

                                # Check if the room is free in the timetable slot
                                if not any(class_info['room'] == assigned_room for class_info in timetable[slot][day]):
                                    timetable[slot][day].append({
                                        "subject": subject,
                                        "teacher": teacher,
                                        "room": assigned_room,
                                        "batch": batch,
                                        "time": slot,  # Use the string time slot directly
                                        "type": slot_type
                                    })

                                    scheduled_labs.add(subject)  # Mark this lab as scheduled for the round
                                    remaining_batches.remove(batch)  # Batch is assigned, remove from list
                                    
                            if not remaining_batches:
                                break

    return timetable

# Flask API Endpoints
@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    data = request.json
    print("Received data:", data)

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
        lab_subject_dict = {lab['subject']: lab['teacher'] for lab in lab_subjects}

        # Generate the timetable using the random generation function
        timetable = generate_random_timetable(batches, subject_dict, lab_subject_dict, theory_rooms, lab_rooms, start_time, end_time, lec_duration, lab_duration, days, lunch_break)

        print(timetable)
        return jsonify(timetable), 200
    except KeyError as ke:
        return jsonify({"error": f"Missing key: {str(ke)}"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
