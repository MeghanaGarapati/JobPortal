document.addEventListener('DOMContentLoaded', function() {
    
    // --- CSRF TOKEN HELPER ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- CLIENT-SIDE REAL-TIME SEARCH & FILTER (Job Listings Portal) ---
    const searchInput = document.getElementById('job-search');
    const jobCards = document.querySelectorAll('.job-card-wrapper');
    const typeFilter = document.getElementById('filter-type');
    const levelFilter = document.getElementById('filter-level');
    const skillTags = document.querySelectorAll('.skill-filter-tag');
    let activeSkillTag = null;

    function filterJobs() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const selectedType = typeFilter ? typeFilter.value : '';
        const selectedLevel = levelFilter ? levelFilter.value : '';

        jobCards.forEach(card => {
            const title = card.getAttribute('data-title').toLowerCase();
            const company = card.getAttribute('data-company').toLowerCase();
            const tags = card.getAttribute('data-tags').toLowerCase();
            const type = card.getAttribute('data-type');
            const level = card.getAttribute('data-level');
            const textContent = card.innerText.toLowerCase();

            const matchesQuery = !query || 
                                 title.includes(query) || 
                                 company.includes(query) || 
                                 tags.includes(query) || 
                                 textContent.includes(query);

            const matchesType = !selectedType || type === selectedType;
            const matchesLevel = !selectedLevel || level === selectedLevel;
            const matchesSkill = !activeSkillTag || tags.includes(activeSkillTag.toLowerCase());

            if (matchesQuery && matchesType && matchesLevel && matchesSkill) {
                card.style.display = 'block';
                card.classList.add('fade-in-animation');
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (searchInput) searchInput.addEventListener('input', filterJobs);
    if (typeFilter) typeFilter.addEventListener('change', filterJobs);
    if (levelFilter) levelFilter.addEventListener('change', filterJobs);

    // Skill tags clicking filters immediately
    skillTags.forEach(tag => {
        tag.addEventListener('click', function(e) {
            e.preventDefault();
            if (activeSkillTag === this.getAttribute('data-skill')) {
                activeSkillTag = null;
                this.classList.remove('active', 'btn-primary');
                this.classList.add('badge-glass-tag');
            } else {
                skillTags.forEach(t => {
                    t.classList.remove('active', 'btn-primary');
                    t.classList.add('badge-glass-tag');
                });
                activeSkillTag = this.getAttribute('data-skill');
                this.classList.remove('badge-glass-tag');
                this.classList.add('active', 'btn-primary');
            }
            filterJobs();
        });
    });

    // --- APPLICATION FORM AJAX SUBMISSION ---
    const applyForm = document.getElementById('apply-job-form');
    const applicationModal = document.getElementById('applyModal');
    
    if (applyForm) {
        applyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = applyForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            
            // Clear previous errors
            applyForm.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
            applyForm.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            const formData = new FormData(applyForm);
            const actionUrl = applyForm.getAttribute('action');
            
            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(async response => {
                const data = await response.json();
                if (!response.ok) {
                    throw { status: response.status, data };
                }
                return data;
            })
            .then(data => {
                // Success: Close Modal & Show Success Banner
                const bsModal = bootstrap.Modal.getInstance(applicationModal);
                if (bsModal) {
                    bsModal.hide();
                }
                
                // Show Success Alert Overlay
                showSuccessNotification(data.message || 'Application submitted successfully!');
                applyForm.reset();
            })
            .catch(err => {
                if (err.data && err.data.errors) {
                    const errors = err.data.errors;
                    
                    // Display field-specific errors
                    for (const [fieldName, errorMessages] of Object.entries(errors)) {
                        const inputElement = applyForm.querySelector(`[name="${fieldName}"]`);
                        if (inputElement) {
                            inputElement.classList.add('is-invalid');
                            const feedback = document.createElement('div');
                            feedback.className = 'invalid-feedback';
                            feedback.innerText = errorMessages.join(' ');
                            inputElement.parentNode.appendChild(feedback);
                        } else {
                            // Non-field error (e.g. Integrity Error from existing email application)
                            if (fieldName === 'email') {
                                const emailInput = applyForm.querySelector('[name="email"]');
                                emailInput.classList.add('is-invalid');
                                const feedback = document.createElement('div');
                                feedback.className = 'invalid-feedback';
                                feedback.innerText = errorMessages.join(' ');
                                emailInput.parentNode.appendChild(feedback);
                            }
                        }
                    }
                } else {
                    alert('An unexpected error occurred. Please try again.');
                }
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    }

    // Modal apply button triggers dynamic job title binding
    if (applicationModal) {
        applicationModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const jobId = button.getAttribute('data-job-id');
            const jobTitle = button.getAttribute('data-job-title');
            
            const modalTitle = applicationModal.querySelector('.modal-title-job-name');
            modalTitle.textContent = jobTitle;
            
            // Re-bind action url path
            applyForm.setAttribute('action', `/job/${jobId}/apply/`);
        });
    }

    // Custom success toast/notification
    function showSuccessNotification(message) {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.top = '24px';
        notification.style.right = '24px';
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            <div class="alert alert-success glass-alert shadow-lg d-flex align-items-center mb-0 fade-in-animation" style="border-left: 4px solid var(--status-shortlist);">
                <i class="bi bi-patch-check-fill fs-4 text-success me-3"></i>
                <div>
                    <h6 class="mb-0 text-white font-weight-bold">Success!</h6>
                    <span class="small text-secondary">${message}</span>
                </div>
            </div>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 4000);
    }

    // --- RECRUITER PIPELINE DYNAMIC STATS UPDATE ---
    const pipelineActionItems = document.querySelectorAll('.pipeline-status-option');
    
    pipelineActionItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const newStatus = this.getAttribute('data-status');
            const applicationId = this.getAttribute('data-app-id');
            const cardElement = document.getElementById(`app-card-${applicationId}`);
            
            if (!cardElement) return;

            const url = `/recruiter/application/${applicationId}/status/`;
            const formData = new FormData();
            formData.append('status', newStatus);

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Slide card out from previous column, move to new column, and slide in.
                    cardElement.style.opacity = '0';
                    cardElement.style.transform = 'scale(0.9)';
                    
                    setTimeout(() => {
                        // Find destination column list
                        let colId = '';
                        let badgeClass = '';
                        switch(newStatus) {
                            case 'Applied':
                                colId = 'list-Applied';
                                badgeClass = 'status-applied';
                                break;
                            case 'Under Review':
                                colId = 'list-Review';
                                badgeClass = 'status-review';
                                break;
                            case 'Shortlisted':
                                colId = 'list-Shortlisted';
                                badgeClass = 'status-shortlist';
                                break;
                            case 'Rejected':
                                colId = 'list-Rejected';
                                badgeClass = 'status-rejected';
                                break;
                        }

                        const targetColList = document.getElementById(colId);
                        if (targetColList) {
                            // Update badge text and classes on card
                            const statusBadge = cardElement.querySelector('.status-badge-element');
                            if (statusBadge) {
                                statusBadge.className = `badge-status status-badge-element ${badgeClass}`;
                                statusBadge.innerText = newStatus;
                            }
                            
                            // Move card
                            targetColList.appendChild(cardElement);
                            
                            // Slide card back in
                            setTimeout(() => {
                                cardElement.style.opacity = '1';
                                cardElement.style.transform = 'scale(1)';
                                recalculateKanbanCounts();
                            }, 50);
                        }
                    }, 300);
                    
                    showSuccessNotification(data.message);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error(err);
                alert('An error occurred during updating the applicant status.');
            });
        });
    });

    // Helper function to update count badges and metrics on dashboard
    function recalculateKanbanCounts() {
        const statuses = [
            { id: 'list-Applied', badgeId: 'count-Applied' },
            { id: 'list-Review', badgeId: 'count-Review' },
            { id: 'list-Shortlisted', badgeId: 'count-Shortlisted' },
            { id: 'list-Rejected', badgeId: 'count-Rejected' }
        ];

        let totalShortlisted = 0;
        let totalRejected = 0;

        statuses.forEach(status => {
            const list = document.getElementById(status.id);
            const countBadge = document.getElementById(status.badgeId);
            if (list && countBadge) {
                const count = list.querySelectorAll('.kanban-card').length;
                countBadge.innerText = count;

                if (status.id === 'list-Shortlisted') totalShortlisted = count;
                if (status.id === 'list-Rejected') totalRejected = count;
            }
        });

        // Update top-level metrics
        const totalShortlistedMetric = document.getElementById('metric-shortlisted-count');
        const totalRejectedMetric = document.getElementById('metric-rejected-count');
        
        if (totalShortlistedMetric) totalShortlistedMetric.innerText = totalShortlisted;
        if (totalRejectedMetric) totalRejectedMetric.innerText = totalRejected;
    }
});
