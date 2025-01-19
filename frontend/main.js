function onSkip() {
    fetch('http://localhost:3000/skip', {
        method: 'POST',
        mode: 'cors'
    })
        .then(() => {
            getBestPosting();
        })
        .catch(error => console.error('Error during skip:', error));
}

function getTopPostings(limit) {
    fetch(`http://localhost:3000/top-postings?limit=${limit}`, {
        method: 'GET',
        mode: 'cors'
    }).then(response => console.log(response)).then(()=> {
            getBestPosting();
        })
        .catch(error => console.error('Error during shortlist:', error));
}


function getBestPosting() {
    fetch('http://localhost:3000/best-posting', {
        mode: 'cors'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('job-id-value').textContent = data.job_id;
            document.getElementById('company-value').textContent = data.company;
            document.getElementById('job-title-value').textContent = data.job_title_;
            document.getElementById('duration-value').textContent = data.duration;
            document.getElementById('location-value').textContent = data.job_location;
            document.getElementById('job-description-value').textContent = data.job_description;
            document.getElementById('cover-letter-value').textContent = data['cover_letter_required?'];
            document.getElementById('application-link-value').href = data.application_link;

        })
        .catch(() => {
            document.getElementById('job-application-box').classList.add('hidden');
            document.getElementById('no-jobs-box').classList.remove('hidden');
        });
}

document.addEventListener("DOMContentLoaded", getTopPostings(10));