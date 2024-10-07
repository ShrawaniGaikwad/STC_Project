import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [batches, setBatches] = useState(['K4', 'L4', 'M4', 'N4']);
  const [theoryRooms, setTheoryRooms] = useState(3);
  const [labRooms, setLabRooms] = useState(2);
  const [totalFaculty, setTotalFaculty] = useState(5);
  const [subjects, setSubjects] = useState([{ subject: 'CNS', teacher: 'mr. xyz' },{ subject: 'SPOS', teacher: 'mr. abc' },{ subject: 'DBMS', teacher: 'mr. hfb'},{ subject: 'HCI', teacher: 'mr. yrb'},{ subject: 'TOC', teacher: 'mr. apn'}]);
  const [labSubjects, setLabSubjects] = useState([{ subject: 'CNS LAb', teacher: 'hdc' },{ subject: 'LP Lab', teacher: 'ydbd' },{ subject: 'DBMS Lab', teacher: 'tdbjc' }]);
  const [startTime, setStartTime] = useState(9); // 9 AM
  const [endTime, setEndTime] = useState(17); // 5 PM
  const [lecDuration, setLecDuration] = useState(60);
  const [labDuration, setLabDuration] = useState(120);
  const [days, setDays] = useState(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]);
  const [timetable, setTimetable] = useState([]);
  const [error, setError] = useState('');


  const handleSubmit = async () => {
    const response = await fetch('http://localhost:5000/generate_timetable', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            batches,
            theory_rooms: Number(theoryRooms),
            lab_rooms: Number(labRooms),
            total_faculty: Number(totalFaculty),
            subjects,
            lab_subjects: labSubjects,
            start_time: Number(startTime),
            end_time: Number(endTime),
            lec_duration: Number(lecDuration),
            lab_duration: Number(labDuration),
            days,
        }),
    });

    console.log("Response Status:", response.status);  // Log status
    const data = await response.json();
    console.log("Response Data:", data);  // Log response data
    console.log(typeof(data));

    if (response.status === 200) {
      setTimetable(data); // Update with the correct key based on your response structure
      console.log("timetable" + timetable);

    setError('');
    } else {
        setTimetable([]);
        setError(data.error || 'An error occurred while generating the timetable.');
    }
};

  const handleSubjectChange = (index, field, value) => {
    const newSubjects = [...subjects];
    newSubjects[index][field] = value;
    setSubjects(newSubjects);
  };

  const handleLabSubjectChange = (index, field, value) => {
    const newLabSubjects = [...labSubjects];
    newLabSubjects[index][field] = value;
    setLabSubjects(newLabSubjects);
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Timetable Generator</h1>
      <form>
        <div className="form-group">
          <label>Batches (comma separated):</label>
          <input
            type="text"
            className="form-control"
            value={batches.join(', ')}
            onChange={(e) => setBatches(e.target.value.split(',').map(batch => batch.trim()))}
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
          <label>Subjects and Teachers:</label>
          {subjects.map((subject, index) => (
            <div key={index} className="d-flex mb-2">
              <input
                type="text"
                className="form-control mr-2"
                placeholder="Subject"
                value={subject.subject}
                onChange={(e) => handleSubjectChange(index, 'subject', e.target.value)}
              />
              <input
                type="text"
                className="form-control"
                placeholder="Teacher"
                value={subject.teacher}
                onChange={(e) => handleSubjectChange(index, 'teacher', e.target.value)}
              />
            </div>
          ))}
          <button
            type="button"
            className="btn btn-secondary mb-3"
            onClick={() => setSubjects([...subjects, { subject: '', teacher: '' }])}
          >
            Add Subject
          </button>
        </div>

        <div className="form-group">
          <label>Lab Subjects and Teachers:</label>
          {labSubjects.map((subject, index) => (
            <div key={index} className="d-flex mb-2">
              <input
                type="text"
                className="form-control mr-2"
                placeholder="Lab Subject"
                value={subject.subject}
                onChange={(e) => handleLabSubjectChange(index, 'subject', e.target.value)}
              />
              <input
                type="text"
                className="form-control"
                placeholder="Teacher"
                value={subject.teacher}
                onChange={(e) => handleLabSubjectChange(index, 'teacher', e.target.value)}
              />
            </div>
          ))}
          <button
            type="button"
            className="btn btn-secondary mb-3"
            onClick={() => setLabSubjects([...labSubjects, { subject: '', teacher: '' }])}
          >
            Add Lab Subject
          </button>
        </div>

        <div className="form-group">
          <label>Start Time:</label>
          <input
            type="number"
            className="form-control"
            value={startTime}
            onChange={(e) => setStartTime(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>End Time:</label>
          <input
            type="number"
            className="form-control"
            value={endTime}
            onChange={(e) => setEndTime(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>Lecture Duration (hours):</label>
          <input
            type="number"
            className="form-control"
            value={lecDuration}
            onChange={(e) => setLecDuration(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>Lab Duration (hours):</label>
          <input
            type="number"
            className="form-control"
            value={labDuration}
            onChange={(e) => setLabDuration(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>Days:</label>
          <select
            className="form-control"
            value={days.join(', ')}
            onChange={(e) => setDays(e.target.value.split(',').map(day => day.trim()))}
          >
            <option value="Monday, Tuesday, Wednesday, Thursday, Friday">Monday - Friday</option>
            <option value="Monday, Tuesday, Wednesday, Thursday, Friday, Saturday">Monday - Saturday</option>
          </select>
        </div>

        <button type="button" className="btn btn-primary btn-block" onClick={handleSubmit}>
          Generate Timetable
        </button>
      </form>
      <div style={{marginTop:'100px'}}>
  {error && <p style={{ color: 'red' }}>{error}</p>}

  {Object.keys(timetable).length > 0 && (
    <table className="table table-bordered">
      <thead>
        <tr>
          <th style={{backgroundColor:'gray'}}>Time</th>
          {days.map((day) => (
            <th key={day} style={{backgroundColor:'gray'}}>{day}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {Object.entries(timetable).map(([timeSlot, entries]) => (
          <tr key={timeSlot}>
            <td >{timeSlot}</td>
            {days.map((day) => {
              const lessons = entries[day] || []; // Access lessons for each day
              return (
                <td key={day}>
                  {lessons.map((entry, index) => (
                    <div key={index}>
                      <strong>{entry.subject}</strong> ({entry.teacher}) - {entry.room}<br />
                      <small>{entry.batch}</small>
                    </div>
                  ))}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  )}
</div>
    </div>
  );
}

export default App;
