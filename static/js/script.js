window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

document.getElementById('delete').addEventListener('click', function(e){
  console.log('deleting');
  console.log = e.target.dataset['idn'];
  let venue_id = e.target.dataset['idn'];
  fetch(`/venues/${venue_id}`, {
    method: 'DELETE'
  })

})