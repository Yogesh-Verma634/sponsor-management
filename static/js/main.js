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
                            extendedProps: {
                                id: sponsor.id,
                                phone: sponsor.phone,
                                email: sponsor.email
                            }
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
                    modalBody.innerHTML = `
                        <p><strong>Name:</strong> ${info.event.title}</p>
                        <p><strong>Phone:</strong> ${sponsor.phone}</p>
                        <p><strong>Email:</strong> ${sponsor.email}</p>
                        <p><strong>Date:</strong> ${info.event.startStr}</p>
                    `;
                    var sponsorModal = new bootstrap.Modal(document.getElementById('sponsorModal'));
                    sponsorModal.show();
                }
            }
        });
        calendar.render();
    }

    function isSuperuser() {
        return document.body.dataset.isSuperuser === 'true';
    }

    var searchSection = document.getElementById('searchSection');
    if (searchSection) {
        if (isSuperuser()) {
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
            searchSection.remove();
        }
    }
});
