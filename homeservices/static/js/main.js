// HomeServices – main.js

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss alerts after 4.5s ──
  document.querySelectorAll('.alert[id^=msg]').forEach(el => {
    setTimeout(() => el.style.transition = 'opacity .5s', 4000);
    setTimeout(() => el.style.opacity = '0', 4400);
    setTimeout(() => el.remove(), 4900);
  });

  // ── Mark notifications read on click ──
  const markBtn = document.getElementById('markReadBtn');
  if (markBtn) {
    markBtn.addEventListener('click', e => {
      e.preventDefault();
      fetch('/api/notifications/read/').then(() => location.reload());
    });
  }

  // ── Employee option selector highlight ──
  document.querySelectorAll('.emp-option').forEach(opt => {
    opt.addEventListener('click', () => {
      document.querySelectorAll('.emp-option').forEach(o => o.style.borderColor = 'var(--border)');
      opt.style.borderColor = 'var(--primary)';
      opt.style.background  = 'rgba(108,99,255,.1)';
    });
  });

  // ── Photo preview on file input ──
  document.querySelectorAll('input[type=file][accept*=image]').forEach(input => {
    input.addEventListener('change', () => {
      const file = input.files[0];
      if (!file) return;
      let prev = input.nextElementSibling;
      if (!prev || prev.tagName !== 'IMG') {
        prev = document.createElement('img');
        prev.style.cssText = 'max-width:100%;border-radius:10px;margin-top:.5rem;max-height:200px;object-fit:cover;';
        input.after(prev);
      }
      const reader = new FileReader();
      reader.onload = e => { prev.src = e.target.result; };
      reader.readAsDataURL(file);
    });
  });

  // ── Booking date – disable past dates ──
  const dateInput = document.querySelector('input[type=date][name=booking_date]');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
  }

});
