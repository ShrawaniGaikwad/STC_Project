import React, { useState } from 'react';

function App() {
  const [divisions, setDivisions] = useState(1);
  const [batches, setBatches] = useState(['K4', 'L4', 'M4', 'N4']);
  const [theoryRooms, setTheoryRooms] = useState(4);
  const [labRooms, setLabRooms] = useState(5);
  const [teachers, setTeachers] = useState(["Teacher1","Teacher2","Teacher3","Teacher4","Teacher5","Teacher6","Teacher7","Teacher8",]);
  const [subjects, setSubjects] = useState(["CNS","TOC","SPOS","HCI","DBMS"]);
  const [practicalSubjects, setPracticalSubjects] = useState(["DBMSL","LP1","CNSL"]);
  const [startTime, setStartTime] = useState(8);
  const [endTime, setEndTime] = useState(15);
  const [lecDuration, setLecDuration] = useState(1);
  const [labDuration, setLabDuration] = useState(2);
  const [days, setDays] = useState(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]);
  const [totalFaculty, setTotalFaculty] = useState(10);
  const [timetable, setTimetable] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:5000/generate-timetable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            divisions: Number(divisions),
            batches,
            theory_rooms: Number(theoryRooms),
            lab_rooms: Number(labRooms),
            teachers,
            subjects,
            practical_subjects: practicalSubjects,
            start_time: Number(startTime),
            end_time: Number(endTime),
            lec_duration: Number(lecDuration),
            lab_duration: Number(labDuration),
            days,
            total_faculty: Number(totalFaculty)
        }),
    });
    
    const data = await response.json();

    if (response.status === 200) {
        setTimetable(data);
        setError('');
    } else {
        setTimetable(null);
        setError(data.error);
    }
};

  return (
    <div>
      <h1>Timetable Generator</h1>
      <div>
        <label>Divisions: </label>
        <input type="number" value={divisions} onChange={e => setDivisions(Number(e.target.value))} />
      </div>
      <div>
        <label>Batches (comma separated): </label>
        <input type="text" value={batches} onChange={e => setBatches(e.target.value.split(','))} />
      </div>
      <div>
        <label>Total Theory Rooms: </label>
        <input type="number" value={theoryRooms} onChange={e => setTheoryRooms(Number(e.target.value))} />
      </div>
      <div>
        <label>Total Lab Rooms: </label>
        <input type="number" value={labRooms} onChange={e => setLabRooms(Number(e.target.value))} />
      </div>
      <div>
        <label>Total Faculty: </label>
        <input type="number" value={totalFaculty} onChange={e => setTotalFaculty(Number(e.target.value))} />
      </div>
      <div>
        <label>Teachers (comma separated): </label>
        <input type="text" value={teachers} onChange={e => setTeachers(e.target.value.split(','))} />
      </div>
      <div>
        <label>Subjects (comma separated): </label>
        <input type="text" value={subjects} onChange={e => setSubjects(e.target.value.split(','))} />
      </div>
      <div>
        <label>Practical Subjects (comma separated): </label>
        <input type="text" value={practicalSubjects} onChange={e => setPracticalSubjects(e.target.value.split(','))} />
      </div>
      <div>
        <label>Start Time: </label>
        <input type="number" value={startTime} onChange={e => setStartTime(e.target.value)} />
      </div>
      <div>
        <label>End Time: </label>
        <input type="number" value={endTime} onChange={e => setEndTime(e.target.value)} />
      </div>
      <div>
        <label>Lecture Duration (hours): </label>
        <input type="number" value={lecDuration} onChange={e => setLecDuration(e.target.value)} />
      </div>
      <div>
        <label>Lab Duration (hours): </label>
        <input type="number" value={labDuration} onChange={e => setLabDuration(e.target.value)} />
      </div>
      <div>
        <label>Days (comma separated): </label>
        <input type="text" value={days.join(',')} onChange={e => setDays(e.target.value.split(','))} />
      </div>
      <button onClick={handleSubmit}>Generate Timetable</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {timetable && (
        <div>
          <h2>Generated Timetable</h2>
          <pre>{JSON.stringify(timetable, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
