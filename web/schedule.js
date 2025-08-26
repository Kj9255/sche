const SHIFT_CYCLE = ['D','N','O','O'];

function parseCSV(text){
  const rows = text.trim().split(/\r?\n/).map(r=>r.split(','));
  const header = rows[0];
  const days = header.slice(2);
  const teams = {};
  rows.slice(1).forEach(row=>{
    if(!row[0]) return;
    const team = row[0].trim();
    const name = row[1].trim();
    if(!teams[team]) teams[team]=[];
    teams[team].push({name, schedule:Array(days.length).fill(''), total:0, nights:0});
  });
  return {days, teams};
}

function generate(days, teams, startOffset){
  const teamNames = Object.keys(teams).sort();
  teamNames.forEach((team, idx)=>{
    const offset = (startOffset + idx) % SHIFT_CYCLE.length;
    for(let day=0; day<days.length; day++){
      let shift = SHIFT_CYCLE[(offset + day) % SHIFT_CYCLE.length];
      let valid = true;
      if(shift === 'D' || shift === 'N'){
        for(const emp of teams[team]){
          if(emp.total >= 15){ valid=false; break; }
          if(shift === 'N' && (emp.nights >=4 || emp.name.includes('[D]'))){ valid=false; break; }
        }
      }
      if(!valid) shift = 'O';
      for(const emp of teams[team]){
        emp.schedule[day] = shift;
        if(shift === 'D' || shift === 'N'){
          emp.total++;
          if(shift === 'N') emp.nights++;
        }
      }
    }
  });
}

function teamsToCSV(days, teams){
  let lines = [["TEAM","Full Name",...days].join(',')];
  Object.keys(teams).sort().forEach(team=>{
    teams[team].forEach(emp=>{
      lines.push([team, emp.name, ...emp.schedule].join(','));
    });
  });
  return lines.join('\n');
}

document.getElementById('generateBtn').addEventListener('click', ()=>{
  const fileInput = document.getElementById('csvFile');
  const offset = parseInt(document.getElementById('offset').value,10) || 0;
  if(!fileInput.files.length){ alert('Please choose a CSV file'); return; }
  const file = fileInput.files[0];
  const reader = new FileReader();
  reader.onload = e => {
    const text = e.target.result;
    const {days, teams} = parseCSV(text);
    generate(days, teams, offset);
    const csvOut = teamsToCSV(days, teams);
    const outputDiv = document.getElementById('output');
    let html = '<table><tr><th>TEAM</th><th>Full Name</th>';
    days.forEach(d=> html += `<th>${d}</th>`);
    html += '</tr>';
    Object.keys(teams).sort().forEach(team=>{
      teams[team].forEach(emp=>{
        html += `<tr><td>${team}</td><td>${emp.name}</td>`;
        emp.schedule.forEach(s=> html += `<td>${s}</td>`);
        html += '</tr>';
      });
    });
    html += '</table>';
    outputDiv.innerHTML = html;
    const link = document.getElementById('downloadLink');
    const blob = new Blob([csvOut], {type:'text/csv'});
    link.href = URL.createObjectURL(blob);
    link.download = 'schedule.csv';
    link.style.display = 'inline';
  };
  reader.readAsText(file);
});
