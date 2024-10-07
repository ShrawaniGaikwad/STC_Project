from flask import Flask, request, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Utility Functions
def generate_time_slots(start, end, duration):
    """Generate time slots based on start time (in hours), end time (in hours),
    and duration (in minutes).
    """
    time_slots = []
    current_time = start * 60  # Convert start time to minutes
    end_time = end * 60  # Convert end time to minutes

    while current_time + duration <= end_time:  # Ensure the time doesn't exceed the end
        start_hour = current_time // 60
        start_minute = current_time % 60
        end_time_slot = current_time + duration
        end_hour = end_time_slot // 60
        end_minute = end_time_slot % 60

        # Format time slots as "HH:MM-HH:MM"
        time_slot = f"{start_hour:02d}:{start_minute:02d}-{end_hour:02d}:{end_minute:02d}"
        time_slots.append(time_slot)
        current_time += duration  # Move to the next slot

    return time_slots
def assign_room(room_type, total_rooms):
    """Assign a room based on type and total available rooms."""
    room_number = random.randint(1, total_rooms)
    return f"{room_type}-{room_number + 300}"  # Example: A1-301

def generate_random_timetable(batches, subjects, labs, theory_rooms, lab_rooms, college_start, college_end, lecture_duration, lab_duration, days):
    """Generates a random timetable for each batch based on the provided inputs."""
    lecture_time_slots = generate_time_slots(college_start, college_end, lecture_duration)
    lab_time_slots = generate_time_slots(college_start, college_end, lab_duration)

    if not lecture_time_slots or not lab_time_slots:
        raise ValueError("No valid time slots generated.")

    timetable = {slot: {day: [] for day in days} for slot in lecture_time_slots + lab_time_slots}
    
    for day in days:
        assigned_subjects = set()  
        for slot in lecture_time_slots:
            subject = random.choice(list(subjects.keys()))
            if subject in assigned_subjects: 
                continue
            assigned_subjects.add(subject)
            teacher = subjects[subject]
            room = assign_room("A1", theory_rooms)  
            timetable[slot][day].append({
                "subject": subject,
                "teacher": teacher,
                "room": room,
                "batch": "All"
            })

    for batch in batches:
        for day in days:
            available_lab_slots = random.sample(lab_time_slots, len(lab_time_slots))
            for lab_slot in available_lab_slots:
                subject = random.choice(list(labs.keys()))
                teacher = labs[subject]
                room = assign_room("A2", lab_rooms) 

                if lab_slot in timetable and all(
                    not (class_info['teacher'] == teacher or class_info['room'] == room) 
                    for class_info in timetable[lab_slot][day]
                ):
                    timetable[lab_slot][day].append({
                        "subject": subject,
                        "teacher": teacher,
                        "room": room,
                        "batch": batch
                    })

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

        # Convert subjects and lab_subjects lists to dictionaries
        subject_dict = {sub['subject']: sub['teacher'] for sub in subjects}
        lab_subject_dict = {lab['subject']: lab['teacher'] for lab in lab_subjects}

        # Generate the timetable using the random generation function
        timetable = generate_random_timetable(batches, subject_dict, lab_subject_dict, theory_rooms, lab_rooms, start_time, end_time, lec_duration, lab_duration, days)
        
        return jsonify(timetable), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
