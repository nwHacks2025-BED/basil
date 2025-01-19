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

function onShortlist() {
    fetch('http://localhost:3000/shortlist', {
        method: 'POST',
        mode: 'cors'
    }).then((shortlist) => {
            shortlist.json().then(data => {
                updateShortlist(data);
            });
            getBestPosting();
        })
        .catch(error => console.error('Error during shortlist:', error));
}

function updateShortlist(shortlist) {
    console.log(shortlist)
    var shortlistTable = document.getElementById('shortlist-jobs');
    shortlistTable.innerHTML = '';
    shortlist.forEach(posting => {
        var li = document.createElement('li');
        var title = document.createElement('div');
        title.className = 'shortlist-title';
        title.textContent = posting.job_title_;

        var data = null;
        
        if (posting.important_urls) {
            data = document.createElement('a');
            data.textContent = "Apply here";
            data.href = posting.important_urls.split(',')[0];
            data.target = '_blank';
        } else {
            data = document.createElement('a');
            data.textContent = "Apply on SCOPE using ID: " + posting.job_id;
        }
        data.className = 'posting-data';

        li.appendChild(title);
        li.appendChild(data);
        shortlistTable.appendChild(li);
    });

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
            if (data['cover_letter_required?'] != 'Yes') {
                document.getElementById('cover-letter').classList.add('hidden');
            }
            document.getElementById('application-link-value').href = data.application_link;
            document.getElementById('job-description-trunc').textContent = data.job_description.substring(0, 1000) + '...';
            if (data.job_description.length > 1000) {
                document.getElementById('readMoreButton').classList.remove('hidden');
                document.getElementById('job-description-value').classList.add('hidden');
            } else {
                document.getElementById('readMoreButton').classList.add('hidden');
                document.getElementById('job-description-value').classList.remove('hidden');
            }

        })
        .catch(() => {
            document.getElementById('job-application-box').classList.add('hidden');
            document.getElementById('no-jobs-box').classList.remove('hidden');
        });
}

function toggleDescription() {
    var description = document.getElementById('job-description-value');
    var button = document.getElementById('readMoreButton');
    if (description.classList.contains('hidden')) {
        description.classList.remove('hidden');
        button.textContent = 'read less';
    } else {
        description.classList.add('hidden');
        button.textContent = 'read more';
    }
}



document.addEventListener("DOMContentLoaded", getBestPosting());