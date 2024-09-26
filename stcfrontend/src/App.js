import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

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
    <div className="container mt-5">
      <h1 className="text-center mb-4">Timetable Generator</h1>
      <form>
        <div className="form-group">
          <label>Divisions:</label>
          <input
            type="number"
            className="form-control"
            value={divisions}
            onChange={(e) => setDivisions(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Batches (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={batches}
            onChange={(e) => setBatches(e.target.value.split(','))}
          />
        </div>
        <div className="form-group">
          <label>Total Theory Rooms:</label>
          <input
            type="number"
            className="form-control"
            value={theoryRooms}
            onChange={(e) => setTheoryRooms(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Total Lab Rooms:</label>
          <input
            type="number"
            className="form-control"
            value={labRooms}
            onChange={(e) => setLabRooms(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Total Faculty:</label>
          <input
            type="number"
            className="form-control"
            value={totalFaculty}
            onChange={(e) => setTotalFaculty(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Teachers (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={teachers}
            onChange={(e) => setTeachers(e.target.value.split(','))}
          />
        </div>
        <div className="form-group">
          <label>Subjects (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={subjects}
            onChange={(e) => setSubjects(e.target.value.split(','))}
          />
        </div>
        <div className="form-group">
          <label>Practical Subjects (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={practicalSubjects}
            onChange={(e) => setPracticalSubjects(e.target.value.split(','))}
          />
        </div>
        <div className="form-group">
          <label>Start Time:</label>
          <input
            type="number"
            className="form-control"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>End Time:</label>
          <input
            type="number"
            className="form-control"
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Lecture Duration (hours):</label>
          <input
            type="number"
            className="form-control"
            value={lecDuration}
            onChange={(e) => setLecDuration(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Lab Duration (hours):</label>
          <input
            type="number"
            className="form-control"
            value={labDuration}
            onChange={(e) => setLabDuration(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Days (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={days.join(',')}
            onChange={(e) => setDays(e.target.value.split(','))}
          />
        </div>
        <button type="button" className="btn btn-primary btn-block" onClick={handleSubmit}>
          Generate Timetable
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {timetable && (
        <div className="container mt-5">
        <h2 className="text-center mb-4">Generated Timetable</h2>
        <div className="table-responsive">
          <table className="table table-bordered">
            <thead className="thead-dark">
              <tr>
                <th>Division</th>
                <th>Day</th>
                <th>Subject</th>
                <th>Teacher</th>
                <th>Room</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(timetable).map(([division, days]) =>
                Object.entries(days.theory).map(([day, sessions]) =>
                  sessions.map((session, index) => (
                    <tr key={`${division}-${day}-${index}`}>
                      <td>{division}</td>
                      <td>{day}</td>
                      <td>{session.subject}</td>
                      <td>{session.teacher}</td>
                      <td>{session.room}</td>
                      <td>{session.time}</td>
                    </tr>
                  ))
                )
              )}
              {Object.entries(timetable).map(([division, days]) =>
                Object.entries(days.practical).map(([day, batches]) =>
                  batches.map((batch) => (
                    batch[Object.keys(batch)[0]].map((session, index) => (
                      <tr key={`${division}-${day}-practical-${index}`}>
                        <td>{division}</td>
                        <td>{day}</td>
                        <td>{session.subject}</td>
                        <td>{session.teacher}</td>
                        <td>{session.room}</td>
                        <td>{session.time}</td>
                      </tr>
                    ))
                  ))
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
      )}
    </div>
  );
}

export default App;
