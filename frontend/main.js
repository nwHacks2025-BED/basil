var localShortlist = [];

function onSkip() {
    document.getElementById('job-application-content').classList.add('hidden');
    showLoading();
    fetch('http://localhost:3000/skip', {
        method: 'POST',
        mode: 'cors'
    })
        .then(() => {
            getBestPosting();
        })
        .catch(error => console.error('Error during skip:', error));
}

let loadingTimeout;

function showLoadingWithDelay() {
    loadingTimeout = setTimeout(() => {
        document.getElementById('finding-jobs').style.display = 'block';
    }, 1500);
}

function showLoading() {
    document.querySelector('.loader').style.display = 'inline-block';
    document.getElementById('loader-box').style.display = 'flex';
    showLoadingWithDelay();
}

function hideLoading() {
    clearTimeout(loadingTimeout);
    document.querySelector('.loader').style.display = 'none';
    document.getElementById('loader-box').style.display = 'none';
    document.getElementById('finding-jobs').style.display = 'none';
}

function onShortlist() {
    document.getElementById('job-application-content').classList.add('hidden');
    showLoading();
    fetch('http://localhost:3000/shortlist', {
        method: 'POST',
        mode: 'cors'
    }).then((shortlist) => {
            shortlist.json().then(data => {
                updateShortlist(data['shortlisted']);
            });
            getBestPosting();
        })
        .catch(error => console.error('Error during shortlist:', error));
}

function getShortlist() {
    fetch('http://localhost:3000/shortlist', {
        mode: 'cors'
    })
        .then(response => response.json())
        .then(data => {
            setShortlist(data);
        })
        .catch(() => {
            document.getElementById('shortlist-jobs').innerHTML = '';
        });
}

function setShortlist(shortlist) {
    localShortlist = shortlist;
    var shortlistTable = document.getElementById('shortlist-jobs');
    shortlistTable.innerHTML = '';
    shortlist.forEach(posting => {
        var li = document.createElement('li');
        var title = document.createElement('div');
        title.className = 'shortlist-title';
        title.textContent = posting.job_title_;
        title.addEventListener('click', () => {
            createPane('<h2>Dynamic Pane</h2><p>This is a dynamically created pane that covers part of the webpage!</p>');
        });

        var company = document.createElement('div');
        company.className = 'shortlist-company';
       
        var companyHeading = document.createElement('strong');
        companyHeading.className = 'shortlist-heading';
        companyHeading.textContent = 'Company: ';
        company.appendChild(companyHeading);

        var companyText = document.createElement('span');
        companyText.textContent = posting.company;
        company.appendChild(companyText);

        var location = document.createElement('div');
        location.className = 'shortlist-location';

        var locationHeading = document.createElement('strong');
        locationHeading.className = 'shortlist-heading';
        locationHeading.textContent = 'Location: ';
        location.appendChild(locationHeading);

        var locationText = document.createElement('span');
        locationText.textContent = posting.job_location;
        location.appendChild(locationText);
        
        var removeButton = document.createElement('span');
        removeButton.className = 'shortlist-remove';
        removeButton.textContent = '✓';
        removeButton.onclick = function() {
            removeShortlistEntry(posting, shortlistTable, li);
        };
        li.appendChild(removeButton);

        var link = document.createElement('a');
        link.className = 'shortlist-link';
        link.target = "_blank";

        if (posting.important_urls) {
            link.textContent = "Apply here";
            link.href = posting.important_urls.split(',')[0];
        } else {
            link.textContent = "Apply on SCOPE using ID: " + posting.job_id;
            link.href="https://scope.sciencecoop.ubc.ca/students/cwl-current-student-login.htm";
        }

        li.appendChild(title);
        li.appendChild(company);
        li.appendChild(location);
        li.appendChild(link);
        shortlistTable.appendChild(li);
    });
}

function removeShortlistEntry(posting, shortlistTable, li) {
    // remove from UI display
    shortlistTable.removeChild(li);

    const indexToDelete = localShortlist.findIndex(item => item.job_id === posting.job_id);
    if (indexToDelete === -1) {
        console.error('Error: Shortlist item not found');
    } else {
        // update local shortlist array
        localShortlist.splice(indexToDelete, 1);
    }

    // console.log('job_id: ', posting.job_id);
    fetch('http://localhost:3000/shortlist/' + posting.job_id, {
        method: 'DELETE',
        mode: 'cors',
    }).then((response) => {
        if (response.status !== 204) {
            console.error('Error during shortlist delete:', response);
        }
    }).catch(error => console.error('Error during shortlist:', error));
};

function updateShortlist(job) {
    if (!localShortlist) {
        updateShortlist([job]);
    } else {
        localShortlist.push(job);
        var shortlistTable = document.getElementById('shortlist-jobs');
        var li = document.createElement('li');
        var title = document.createElement('div');
        title.className = 'shortlist-title';
        title.textContent = job.job_title_;

        var company = document.createElement('div');
        company.className = 'shortlist-company';
       
        var companyHeading = document.createElement('strong');
        companyHeading.className = 'shortlist-heading';
        companyHeading.textContent = 'Company: ';
        company.appendChild(companyHeading);

        var companyText = document.createElement('span');
        companyText.textContent = job.company;
        company.appendChild(companyText);

        var location = document.createElement('div');
        location.className = 'shortlist-location';

        var locationHeading = document.createElement('strong');
        locationHeading.className = 'shortlist-heading';
        locationHeading.textContent = 'Location: ';
        location.appendChild(locationHeading);

        var locationText = document.createElement('span');
        locationText.textContent = job.job_location;
        location.appendChild(locationText);

        var removeButton = document.createElement('span');
        removeButton.className = 'shortlist-remove';
        removeButton.textContent = '✓';
        removeButton.onclick = function() {
            shortlistTable.removeChild(li);
            localShortlist = localShortlist.filter(item => item.job_id !== posting.job_id);
        };
        li.appendChild(removeButton);


        var link = document.createElement('a');
        link.className = 'shortlist-link';
        link.target = "_blank";

        if (job.important_urls) {
            link.textContent = "Apply here";
            link.href = job.important_urls.split(',')[0];
        } else {
            link.textContent = "Apply on SCOPE using ID: " + job.job_id;
            link.href="https://scope.sciencecoop.ubc.ca/students/cwl-current-student-login.htm";
        }

        li.appendChild(title);
        li.appendChild(company);
        li.appendChild(location);
        li.appendChild(link);
        shortlistTable.appendChild(li);
    }
}

function getBestPosting() {
    fetch('http://localhost:3000/best-posting', {
        mode: 'cors'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('job-application-content').classList.remove('hidden');
            hideLoading();

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

function createPane(content) {
    let existingPane = document.querySelector('.pane-overlay');
    if (existingPane) {
        existingPane.remove();
    }

    const paneOverlay = document.createElement('div');
    paneOverlay.className = 'pane-overlay';
    paneOverlay

    const pane = document.createElement('div');
    pane.className = 'pane';

    if (typeof content === 'string') {
        pane.innerHTML = content;
    } else {
        pane.appendChild(content);
    }

    const closeButton = document.createElement('button');
    closeButton.className = 'pane-close';
    closeButton.textContent = '×';
    closeButton.onclick = () => {
        paneOverlay.style.display = 'none';
    };

    pane.appendChild(closeButton);

    paneOverlay.appendChild(pane);

    document.body.appendChild(paneOverlay);

    paneOverlay.style.display = 'flex';
}

document.addEventListener("DOMContentLoaded", getBestPosting());
document.addEventListener("DOMContentLoaded", getShortlist());
