window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// Handle Enter key in search forms to trigger submission
document.addEventListener('DOMContentLoaded', function() {
  const venueForm = document.getElementById('venue-search-form');
  const artistForm = document.getElementById('artist-search-form');
  
  const setupFormEnter = (form) => {
    if (form) {
      const inputs = form.querySelectorAll('input, select');
      inputs.forEach(function(input) {
        input.addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            form.submit();
          }
        });
      });
    }
  };
  
  setupFormEnter(venueForm);
  setupFormEnter(artistForm);
});
