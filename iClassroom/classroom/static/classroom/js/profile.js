// Avatar functionality
// Add this temporarily to profile.js to test
console.log("Script loaded!");

    document.addEventListener('DOMContentLoaded', function() {
        console.log("DOM fully loaded");
        // Get all elements
        const avatarContainer = document.querySelector('.profile-avatar-container');
        const avatarOverlay = document.getElementById('avatarOverlay');
        const avatarModal = document.getElementById('avatarModal');
        const avatarInput = document.getElementById('avatarInput');
        const modalClose = document.querySelector('.modal-close');
        const loadingOverlay = document.getElementById('loadingOverlay');

        document.body.addEventListener('click', function(e) {
        // Show modal when clicking avatar area
         // Open modal when clicking avatar area
    if (e.target.closest('.profile-avatar-container')) {
      e.preventDefault();
      avatarModal.classList.add('active');
    }

        // Handle overlay specifically
        if (avatarOverlay) {
            avatarOverlay.addEventListener('click', function(e) {
                e.stopPropagation();
                avatarModal.classList.add('active');
            });
        }

        // Close modal when clicking close button or outside
    if (e.target.closest('.modal-close') || 
        (e.target === avatarModal && !e.target.closest('.avatar-modal'))) {
      avatarModal.classList.remove('active');
    }
  });

        // Handle file upload
        if (avatarInput) {
            avatarInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    uploadAvatar(file);
                }
            });
        }

        // Upload function
        function uploadAvatar(file) {
            const formData = new FormData();
            formData.append('avatar', file);
            formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

            loadingOverlay.classList.add('active');

            fetch('{% url "upload_avatar" %}', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                loadingOverlay.classList.remove('active');
                
                if (data.success) {
                    updateAvatarImages(data.avatar_url);
                    closeAvatarModal();
                    showMessage('success', data.message);
                } else {
                    showMessage('error', data.error);
                }
            })
            .catch(error => {
                loadingOverlay.classList.remove('active');
                showMessage('error', 'An error occurred while uploading the image.');
                console.error('Error:', error);
            });
        }

        // Remove avatar function
        function removeAvatar() {
            if (confirm('Are you sure you want to remove your profile picture?')) {
                loadingOverlay.classList.add('active');

                fetch('{% url "remove_avatar" %}', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    loadingOverlay.classList.remove('active');
                    
                    if (data.success) {
                        updateAvatarToInitials();
                        closeAvatarModal();
                        showMessage('success', data.message);
                    } else {
                        showMessage('error', data.error);
                    }
                })
                .catch(error => {
                    loadingOverlay.classList.remove('active');
                    showMessage('error', 'An error occurred while removing the image.');
                    console.error('Error:', error);
                });
            }
        }

        // Update avatar images
        function updateAvatarImages(avatarUrl) {
            const profileAvatar = document.getElementById('profileAvatar');
            const avatarPreview = document.getElementById('avatarPreview');
            
            // Update main profile avatar
            if (profileAvatar) {
                profileAvatar.innerHTML = `<img src="${avatarUrl}" alt="Profile Picture" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
            }
            
            // Update modal preview
            if (avatarPreview) {
                avatarPreview.innerHTML = `<img src="${avatarUrl}" alt="Profile Picture" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
            }
        }

        // Update avatar to show initials
        function updateAvatarToInitials() {
            const profileAvatar = document.getElementById('profileAvatar');
            const avatarPreview = document.getElementById('avatarPreview');
            const initials = '{{ user.first_name.0|default:"U" }}{{ user.last_name.0|default:"" }}';
            
            // Update main profile avatar
            if (profileAvatar) {
                profileAvatar.innerHTML = `<span class="profile-initial-large">${initials}</span>`;
                profileAvatar.style.background = '#6366f1';
                profileAvatar.style.display = 'flex';
                profileAvatar.style.alignItems = 'center';
                profileAvatar.style.justifyContent = 'center';
            }
            
            // Update modal preview
            if (avatarPreview) {
                avatarPreview.innerHTML = `<span class="avatar-initial-preview">${initials}</span>`;
                avatarPreview.style.background = '#6366f1';
                avatarPreview.style.display = 'flex';
                avatarPreview.style.alignItems = 'center';
                avatarPreview.style.justifyContent = 'center';
            }
        }

        // Show message function
        function showMessage(type, message) {
            const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = message;
            
            messagesContainer.appendChild(messageDiv);
            
            // Remove message after 5 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 5000);
        }

        // Create messages container if it doesn't exist
        function createMessagesContainer() {
            const container = document.createElement('div');
            container.className = 'messages';
            const mainContent = document.querySelector('.main-content');
            const profileContainer = document.querySelector('.profile-container');
            
            if (mainContent && profileContainer) {
                mainContent.insertBefore(container, profileContainer);
            }
            return container;
        }
        
    }); // This closes the DOMContentLoaded event listener