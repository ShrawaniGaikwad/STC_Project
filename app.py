from flask import Flask, request, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock data structure to hold the timetable information
timetables = {}

def generate_timetable(divisions, batches, theory_rooms, lab_rooms, teachers, subjects, practical_subjects, start_time, end_time, lec_duration, lab_duration, days, total_faculty):
    generated_timetables = {}
    print("Inside the generated timetable function")
    iteration_count = 0  # Debug counter
    max_iterations = 1000  # Set a maximum iteration limit

    for division in range(1, divisions + 1):
        timetable = {"theory": {}, "practical": {}}
        
        for day in days:
            day_schedule = []
            current_time = start_time
            
            assigned_rooms = set()  # Reset for each day
            assigned_teachers = set()  # Reset for each day
            
            while current_time < end_time:
    # If there are no subjects, break the loop
                if len(subjects) == 0:
                    break

                # Select a random subject
                subject = random.choice(subjects)

                # Track if a valid schedule was found
                session_scheduled = False

                for _ in range(len(teachers) * len(theory_rooms)):  # Try multiple combinations
                    teacher = random.choice(teachers)
                    room = random.choice(theory_rooms)

                    # Ensure no conflicts in theory sessions
                    if teacher in assigned_teachers or room in assigned_rooms:
                        continue  # Skip this iteration if conflict found

                    # If there's no conflict, assign the teacher and room
                    assigned_teachers.add(teacher)
                    assigned_rooms.add(room)

                    day_schedule.append({
                        "subject": subject,
                        "teacher": teacher,
                        "room": room,
                        "time": f"{current_time}:00 - {current_time + lec_duration}:00"
                    })

                    current_time += lec_duration  # Increment time
                    session_scheduled = True  # Mark that a session was successfully scheduled
                    print(f"Assigned: {subject}, {teacher}, Room: {room}, Time: {current_time - lec_duration}:00 - {current_time}:00")
                    
                    # Check if current time has reached or exceeded end time
                    if current_time >= end_time:
                        break  # End of the day, stop lab sessions

                # If no valid session was scheduled after trying all combinations
                if not session_scheduled:
                    print(f"No valid session could be scheduled for {subject}. Ending session generation.")
                    break

                # Increment iteration count
                iteration_count += 1
                if iteration_count > max_iterations:
                    print("Breaking out of the loop for debugging")
                    break
            
            # Assign theory schedule for the day
            timetable["theory"][day] = day_schedule

            # Generate practical sessions divided by batches for each division
            batch_schedule = []
            for batch in batches:
                lab_schedule = []
                current_time = start_time
                assigned_rooms = set()  # Reset for each batch
                assigned_teachers = set()  # Reset for each batch

                for practical_subject in practical_subjects:
                    lab_teacher = random.choice(teachers)
                    lab_room = random.choice(lab_rooms)

                    # Ensure no conflicts in practical sessions (teacher and lab room)
                    if lab_teacher in assigned_teachers or lab_room in assigned_rooms:
                        continue  # Skip this iteration if conflict found
                        
                    assigned_teachers.add(lab_teacher)
                    assigned_rooms.add(lab_room)

                    lab_schedule.append({
                        "subject": practical_subject,
                        "teacher": lab_teacher,
                        "room": lab_room,
                        "time": f"{current_time}:00 - {current_time + lab_duration}:00"
                    })

                    current_time += lab_duration  # Increment time
                    if current_time >= end_time:
                        break  # End of the day, stop lab sessions

                    # Debug iteration count
                    iteration_count += 1
                    if iteration_count > max_iterations:
                        print("Breaking out of the loop for debugging")
                        break

                batch_schedule.append({batch: lab_schedule})
            
            timetable["practical"][day] = batch_schedule
        
        generated_timetables[f"Division-{division}"] = timetable
    
    print("Outside the for loop")  # This should now be printed
    # Log the generated timetable before returning
    print("Generated Timetable:", generated_timetables)
    
    return generated_timetables

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable_endpoint():
    data = request.json
    print(data)  # Log the incoming request data
    divisions = data['divisions']
    batches = data['batches']
    theory_rooms = list(range(1, data['theory_rooms'] + 1))
    lab_rooms = list(range(1, data['lab_rooms'] + 1))
    teachers = data['teachers']
    subjects = data['subjects']
    practical_subjects = data['practical_subjects']
    start_time = data['start_time']
    end_time = data['end_time']
    lec_duration = data['lec_duration']
    lab_duration = data['lab_duration']
    days = data['days']
    total_faculty = data['total_faculty']

    generated_timetable = generate_timetable(divisions, batches, theory_rooms, lab_rooms, teachers, subjects, practical_subjects, start_time, end_time, lec_duration, lab_duration, days, total_faculty)
    
    if not generated_timetable:  # Check for empty result
        return jsonify({"error": "Unable to generate timetable due to conflicts or invalid data."}), 400
    else:
        print("Final Generated Timetable:", generated_timetable)  # Log the final result
        return jsonify(generated_timetable)

if __name__ == '__main__':
    app.run(debug=True)
