import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Helper functions
def generate_unified_time_slots(start, end, lec_duration, lab_duration, lunch_break):
    slots = []
    current_time = start * 60  # Convert start time to minutes
    end_time = end * 60  # Convert end time to minutes
    lunch_start = lunch_break['start'] * 60  # Convert lunch start to minutes
    lunch_end = lunch_break['end'] * 60  # Convert lunch end to minutes

    while current_time < end_time:
        # Skip lunch break
        if lunch_start <= current_time < lunch_end:
            # If within lunch break, add a lunch break slot
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_hour = lunch_end // 60
            end_minute = lunch_end % 60
            slots.append({
                "type": "lunch_break", 
                "slot": f"{start_hour:02}:{start_minute:02}-{end_hour:02}:{end_minute:02}"
            })
            current_time = lunch_end  # Move current time past the lunch break
            continue

        # Add lecture slot
        if current_time + lec_duration <= end_time:
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_lec_minute = current_time + lec_duration
            lec_end_hour = end_lec_minute // 60
            lec_end_minute = end_lec_minute % 60
            slots.append({
                "type": "lecture", 
                "slot": f"{start_hour:02}:{start_minute:02}-{lec_end_hour:02}:{lec_end_minute:02}"
            })
            current_time += lec_duration

        # Add lab slot
        if current_time + lab_duration <= end_time:
            start_hour = current_time // 60
            start_minute = current_time % 60
            end_lab_minute = current_time + lab_duration
            lab_end_hour = end_lab_minute // 60
            lab_end_minute = end_lab_minute % 60
            slots.append({
                "type": "lab", 
                "slot": f"{start_hour:02}:{start_minute:02}-{lab_end_hour:02}:{lab_end_minute:02}"
            })
            current_time += lab_duration

    return slots

def assign_room(prefix, room_count):
    return f"{prefix}-{random.randint(1, room_count)}"

# Main timetable generation function
def generate_random_timetable(batches, subjects, labs, theory_rooms, lab_rooms, college_start, college_end, lec_duration, lab_duration, days, lunch_break):
    unified_time_slots = generate_unified_time_slots(college_start, college_end, lec_duration, lab_duration, lunch_break)

    # Shuffle the days and slots to ensure randomness
    random.shuffle(days)
    random.shuffle(unified_time_slots)

    timetable = {slot['slot']: {day: [] for day in days} for slot in unified_time_slots}

    # Track lab count for each batch and each lab per week
    weekly_lab_count = {batch: {lab: 0 for lab in labs.keys()} for batch in batches}

    # Track lecture count for each subject per day to ensure no subject is scheduled more than twice
    daily_lecture_count = {day: {subject: 0 for subject in subjects.keys()} for day in days}

    for day in days:
        daily_lab_count = {lab: 0 for lab in labs.keys()}  # Track labs scheduled for the day

        for slot_info in unified_time_slots:
            slot_type = slot_info['type']
            slot = slot_info['slot']

            if slot_type == 'lecture':
                # Select a subject that hasn't exceeded the limit of 2 lectures per day
                available_subjects = [subject for subject in subjects.keys() if daily_lecture_count[day][subject] < 2]

                if available_subjects:
                    subject = random.choice(available_subjects)  # Randomly choose a subject
                    teacher = subjects[subject]
                    room = assign_room("A1", theory_rooms)

                    # Schedule the lecture
                    timetable[slot][day].append({
                        "subject": subject,
                        "teacher": teacher,
                        "room": room,
                        "batches": batches,
                        "time": slot,
                        "type": slot_type
                    })

                    # Update the lecture count for the selected subject
                    daily_lecture_count[day][subject] += 1

            elif slot_type == 'lab':
                lab_scheduled = False

                # Schedule the same lab for all batches, but each batch gets a different room
                for lab, details in labs.items():
                    if daily_lab_count[lab] < 2:  # Max 2 labs per day
                        # Assign different rooms for each batch
                        for i, batch in enumerate(batches):
                            if weekly_lab_count[batch][lab] < details['frequency']:
                                room = f"A2-{(i % lab_rooms) + 1}"  # Assign a different room to each batch
                                
                                timetable[slot][day].append({
                                    "subject": lab,
                                    "teacher": details['teacher'],
                                    "room": room,
                                    "batch": batch,
                                    "time": slot,
                                    "type": slot_type
                                })
                                weekly_lab_count[batch][lab] += 1
                                lab_scheduled = True

                        if lab_scheduled:
                            daily_lab_count[lab] += 1
                            break
            

                # If no lab was scheduled, assign a lecture in that slot
                if not lab_scheduled:
                    available_subjects = [subject for subject in subjects.keys() if daily_lecture_count[day][subject] < 2]
                    if available_subjects:
                        subject = random.choice(available_subjects)
                        teacher = subjects[subject]
                        room = assign_room("A1", theory_rooms)

                        # Schedule the lecture
                        timetable[slot][day].append({
                            "subject": subject,
                            "teacher": teacher,
                            "room": room,
                            "batches": batches,
                            "time": slot,
                            "type": "lecture"
                        })

                        # Update the lecture count for the selected subject
                        daily_lecture_count[day][subject] += 1


            elif slot_type == 'lunch_break':
                timetable[slot][day].append({
                    "slot_type": "lunch_break",  # Use the same key as in your React component
                    "slot": slot  # You can include slot time or any other details if needed
                })
                
        

    return timetable


# Flask API Endpoints
@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    data = request.json

    # Extract input values
    batches = data['batches']
    theory_rooms = int(data['theory_rooms'])
    lab_rooms = int(data['lab_rooms'])
    subjects = data['subjects']
    lab_subjects = data['lab_subjects']
    start_time = int(data['start_time'])
    end_time = int(data['end_time'])
    lec_duration = int(data['lec_duration'])
    lab_duration = int(data['lab_duration'])
    days = data['days']
    lunch_break = data.get('lunch_break', {'start': 12, 'end': 13})

    # Convert subjects and lab_subjects to dicts
    subject_dict = {sub['subject']: sub['teacher'] for sub in subjects}
    lab_subject_dict = {lab['subject']: {'teacher': lab['teacher'], 'frequency': lab['frequency']} for lab in lab_subjects}

    # Generate timetable
    timetable = generate_random_timetable(
        batches, subject_dict, lab_subject_dict, theory_rooms, lab_rooms, 
        start_time, end_time, lec_duration, lab_duration, days, lunch_break
    )

    print("tiemtable",timetable)

    return jsonify(timetable), 200

if __name__ == "__main__":
    app.run(debug=True)
