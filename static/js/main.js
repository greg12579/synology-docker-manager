// Notification system
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');

    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}

// Refresh containers
function refreshContainers() {
    location.reload();
}

// Start container
async function startContainer(containerId) {
    try {
        const response = await fetch(`/api/container/${containerId}/start`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(refreshContainers, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Error starting container: ' + error.message, 'error');
    }
}

// Stop container
async function stopContainer(containerId) {
    if (!confirm('Are you sure you want to stop this container?')) {
        return;
    }

    try {
        const response = await fetch(`/api/container/${containerId}/stop`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(refreshContainers, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Error stopping container: ' + error.message, 'error');
    }
}

// Restart container
async function restartContainer(containerId) {
    if (!confirm('Are you sure you want to restart this container?')) {
        return;
    }

    try {
        const response = await fetch(`/api/container/${containerId}/restart`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(refreshContainers, 2000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Error restarting container: ' + error.message, 'error');
    }
}

// Update container
async function updateContainer(containerId) {
    if (!confirm('This will pull the latest image and recreate the container. Continue?')) {
        return;
    }

    showNotification('Updating container... This may take a minute.', 'info');

    try {
        const response = await fetch(`/api/container/${containerId}/update`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(refreshContainers, 2000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Error updating container: ' + error.message, 'error');
    }
}

// Regenerate description using AI
async function regenerateDescription(containerId) {
    showNotification('Generating AI description...', 'info');

    try {
        const response = await fetch(`/api/container/${containerId}/regenerate-description`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showNotification('Description: ' + data.description, 'success');
            setTimeout(refreshContainers, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Error regenerating description: ' + error.message, 'error');
    }
}

// Auto-refresh every 30 seconds
setInterval(refreshContainers, 30000);
