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
                modalBody.innerHTML = `
                    <p><strong>Name:</strong> ${info.event.title}</p>
                    <p><strong>Phone:</strong> ${sponsor.phone}</p>
                    <p><strong>Email:</strong> ${sponsor.email}</p>
                    <p><strong>Date:</strong> ${info.event.startStr}</p>
                `;
                var sponsorModal = new bootstrap.Modal(document.getElementById('sponsorModal'));
                sponsorModal.show();
            }
        });
        calendar.render();
    }

    // Add test sponsor button only if the container exists
    var sponsorContainer = document.querySelector('.col-md-4');
    if (sponsorContainer) {
        var testSponsorBtn = document.createElement('button');
        testSponsorBtn.textContent = 'Create Test Sponsor';
        testSponsorBtn.className = 'btn btn-secondary mt-3';
        testSponsorBtn.addEventListener('click', function() {
            window.location.href = '/create_test_sponsor';
        });
        sponsorContainer.appendChild(testSponsorBtn);
    }
});
