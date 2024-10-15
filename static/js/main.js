document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            height: 'auto',
            events: function(fetchInfo, successCallback, failureCallback) {
                fetch(`/get_sponsors?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`)
                    .then(response => {
                        if (!response.ok) {
                            if (response.status === 401) {
                                window.location.href = '/login';
                                throw new Error('Unauthorized');
                            }
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        var events = data.map(sponsor => ({
                            title: sponsor.name,
                            start: sponsor.date,
                            extendedProps: sponsor
                        }));
                        successCallback(events);
                    })
                    .catch(error => {
                        console.error('Error fetching sponsors:', error);
                        failureCallback(error);
                    });
            },
            eventClick: function(info) {
                var sponsor = info.event.extendedProps;
                var modalBody = document.getElementById('sponsorModalBody');
                if (modalBody) {
                    var content = `
                        <p><strong>Name:</strong> ${info.event.title}</p>
                        <p><strong>Date:</strong> ${info.event.startStr}</p>
                    `;
                    if (isSuperuser()) {
                        content += `
                            <p><strong>Phone:</strong> ${sponsor.phone || 'N/A'}</p>
                            <p><strong>Email:</strong> ${sponsor.email || 'N/A'}</p>
                        `;
                    }
                    modalBody.innerHTML = content;
                    var sponsorModal = new bootstrap.Modal(document.getElementById('sponsorModal'));
                    sponsorModal.show();
                }
            }
        });
        calendar.render();
    }

    function isSuperuser() {
        var superuserAttr = document.body.getAttribute('data-superuser');
        console.log('data-superuser attribute:', superuserAttr);
        return superuserAttr === 'True' || superuserAttr === 'true';
    }

    console.log('isSuperuser:', isSuperuser());

    var searchSection = document.getElementById('searchSection');
    if (searchSection) {
        if (isSuperuser()) {
            console.log('User is a superuser, showing search section');
            searchSection.style.display = 'block';

            var searchForm = document.getElementById('searchForm');
            var searchInput = document.getElementById('searchInput');
            var searchResults = document.getElementById('searchResults');

            if (searchForm && searchInput && searchResults) {
                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    var query = searchInput.value.trim();
                    if (query) {
                        fetch(`/search_sponsors?query=${encodeURIComponent(query)}`)
                            .then(response => {
                                if (!response.ok) {
                                    if (response.status === 403) {
                                        throw new Error('Forbidden');
                                    }
                                    throw new Error('Network response was not ok');
                                }
                                return response.json();
                            })
                            .then(data => {
                                displaySearchResults(data);
                            })
                            .catch(error => {
                                console.error('Error searching sponsors:', error);
                                if (error.message === 'Forbidden') {
                                    searchResults.innerHTML = '<p>You do not have permission to search sponsors.</p>';
                                }
                            });
                    }
                });
            } else {
                console.error('Search form elements not found');
            }

            function displaySearchResults(sponsors) {
                if (searchResults) {
                    searchResults.innerHTML = '';
                    if (sponsors.length === 0) {
                        searchResults.innerHTML = '<p>No sponsors found.</p>';
                    } else {
                        var ul = document.createElement('ul');
                        ul.className = 'list-group';
                        sponsors.forEach(sponsor => {
                            var li = document.createElement('li');
                            li.className = 'list-group-item';
                            li.innerHTML = `
                                <h5>${sponsor.name}</h5>
                                <p>Date: ${sponsor.date}</p>
                                <p>Phone: ${sponsor.phone}</p>
                                <p>Email: ${sponsor.email}</p>
                            `;
                            ul.appendChild(li);
                        });
                        searchResults.appendChild(ul);
                    }
                }
            }
        } else {
            console.log('User is not a superuser, hiding search section');
            searchSection.style.display = 'none';
        }
    } else {
        console.log('Search section not found in the DOM');
    }
});
