// DOM Elements
const podcastForm = document.getElementById('podcast-form');
const currentJobContainer = document.getElementById('current-job-container');
const currentJobStatus = document.getElementById('current-job-status');
const podcastsList = document.getElementById('podcasts-list');
const noPodcastsMessage = document.getElementById('no-podcasts-message');

// Templates
const podcastCardTemplate = document.getElementById('podcast-card-template').content;
const currentJobTemplate = document.getElementById('current-job-template').content;

// Status styles
const statusStyles = {
    'queued': 'bg-gray-200 text-gray-800 idle',
    'running': 'bg-blue-200 text-blue-800 running',
    'completed': 'bg-green-200 text-green-800 completed',
    'failed': 'bg-red-200 text-red-800 error'
};

// Stage labels
const stageLabels = {
    'research': 'Researching topics',
    'summarize': 'Summarizing findings',
    'script': 'Writing podcast script',
    'voice': 'Generating audio',
    'complete': 'Completed'
};

// Handle form submission
podcastForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value.trim() || 'Current Events';
    const host1 = document.getElementById('host1').value.trim() || 'Alex';
    const host2 = document.getElementById('host2').value.trim() || 'Jamie';
    
    try {
        const response = await fetch('/create-podcast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                hosts: [host1, host2]
            })
        });
        
        if (!response.ok) throw new Error('Failed to create podcast');
        
        const data = await response.json();
        alert(`Podcast creation started! Job ID: ${data.job_id}`);
        
        // Clear form
        document.getElementById('topic').value = '';
        
        // Update UI immediately
        fetchPodcasts();
        
    } catch (error) {
        console.error('Error creating podcast:', error);
        alert('Failed to create podcast. Please try again.');
    }
});

// Fetch all podcasts
async function fetchPodcasts() {
    try {
        const response = await fetch('/api/podcasts');
        if (!response.ok) throw new Error('Failed to fetch podcasts');
        
        const data = await response.json();
        updatePodcastsList(data.podcasts);
        updateCurrentJob(data.podcasts, data.current_job);
        
    } catch (error) {
        console.error('Error fetching podcasts:', error);
    }
}

// Update the podcasts list
function updatePodcastsList(podcasts) {
    // Hide the "no podcasts" message if we have podcasts
    if (podcasts.length > 0) {
        noPodcastsMessage.style.display = 'none';
    } else {
        noPodcastsMessage.style.display = 'block';
    }
    
    // Clear existing podcasts except for the "no podcasts" message
    while (podcastsList.firstChild) {
        if (podcastsList.firstChild === noPodcastsMessage) break;
        podcastsList.removeChild(podcastsList.firstChild);
    }
    
    // Add all podcasts
    for (const podcast of podcasts) {
        // Skip the current job, as it's displayed separately
        if (podcast.status === 'running' && currentJobContainer.dataset.jobId === podcast.id) {
            continue;
        }
        
        const card = document.importNode(podcastCardTemplate, true);
        
        // Update card content
        card.querySelector('.podcast-topic').textContent = podcast.topic;
        card.querySelector('.podcast-hosts').textContent = podcast.hosts.join(', ');
        card.querySelector('.podcast-status').textContent = podcast.status.charAt(0).toUpperCase() + podcast.status.slice(1);
        card.querySelector('.podcast-status').className = `podcast-status px-2 py-1 text-xs rounded-full ${statusStyles[podcast.status] || ''}`;
        card.querySelector('.podcast-progress').style.width = `${podcast.progress}%`;
        card.querySelector('.podcast-progress-text').textContent = podcast.progress;
        card.querySelector('.podcast-view-link').href = `/podcast/${podcast.id}`;
        
        // Add card to list (at the beginning)
        podcastsList.insertBefore(card, podcastsList.firstChild);
    }
}

// Update the current job display
function updateCurrentJob(podcasts, currentJobId) {
    if (!currentJobId) {
        currentJobStatus.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                No active podcast generation
            </div>
        `;
        currentJobContainer.dataset.jobId = '';
        return;
    }
    
    // Find the current job
    const currentJob = podcasts.find(podcast => podcast.id === currentJobId);
    if (!currentJob) return;
    
    // Store the job ID
    currentJobContainer.dataset.jobId = currentJob.id;
    
    // Create the job display
    const jobDisplay = document.importNode(currentJobTemplate, true);
    
    // Update job content
    jobDisplay.querySelector('.job-topic').textContent = currentJob.topic;
    jobDisplay.querySelector('.job-status').textContent = currentJob.status.charAt(0).toUpperCase() + currentJob.status.slice(1);
    jobDisplay.querySelector('.job-status').className = `job-status px-3 py-1 text-sm font-medium rounded-full ${statusStyles[currentJob.status] || ''}`;
    jobDisplay.querySelector('.job-progress').style.width = `${currentJob.progress}%`;
    jobDisplay.querySelector('.job-stage').textContent = stageLabels[currentJob.current_stage] || currentJob.current_stage || '-';
    jobDisplay.querySelector('.job-hosts').textContent = currentJob.hosts.join(', ');
    jobDisplay.querySelector('.job-view-link').href = `/podcast/${currentJob.id}`;
    
    // Add latest updates
    const updatesContainer = jobDisplay.querySelector('.job-updates');
    if (currentJob.updates && currentJob.updates.length > 0) {
        updatesContainer.innerHTML = '';
        
        // Get the 5 most recent updates
        const recentUpdates = currentJob.updates.slice(-5).reverse();
        
        for (const update of recentUpdates) {
            const updateEl = document.createElement('div');
            updateEl.className = 'text-sm';
            
            // Format the timestamp
            const date = new Date(update.time);
            const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            updateEl.innerHTML = `
                <span class="text-gray-500">${time}</span>
                <span class="ml-2">${update.message}</span>
            `;
            
            updatesContainer.appendChild(updateEl);
        }
    } else {
        updatesContainer.innerHTML = '<div class="text-sm text-gray-500">No updates yet</div>';
    }
    
    // Update the display
    currentJobStatus.innerHTML = '';
    currentJobStatus.appendChild(jobDisplay);
}

// Initial fetch
fetchPodcasts();

// Set up polling
setInterval(fetchPodcasts, 3000);

// Voice selection functionality
document.addEventListener('DOMContentLoaded', function() {
  const voiceSelectionDiv = document.getElementById('voice-selection');
  const advancedOptionsToggle = document.getElementById('advanced-options-toggle');
  
  // Only run if these elements exist
  if (voiceSelectionDiv && advancedOptionsToggle) {
    // Toggle advanced options
    advancedOptionsToggle.addEventListener('click', function() {
      voiceSelectionDiv.classList.toggle('hidden');
      
      // Load voices if showing the section
      if (!voiceSelectionDiv.classList.contains('hidden')) {
        loadVoices();
      }
    });
    
    // Load available voices from API
    function loadVoices() {
      fetch('/api/voices')
        .then(response => response.json())
        .then(data => {
          const host1Select = document.getElementById('host1-voice');
          const host2Select = document.getElementById('host2-voice');
          
          if (host1Select && host2Select && data.voices) {
            // Clear existing options
            host1Select.innerHTML = '';
            host2Select.innerHTML = '';
            
            // Add auto option
            const autoOption = document.createElement('option');
            autoOption.value = 'auto';
            autoOption.textContent = 'Auto-select appropriate voice';
            host1Select.appendChild(autoOption.cloneNode(true));
            host2Select.appendChild(autoOption);
            
            // Add all available voices
            data.voices.forEach(voice => {
              const option = document.createElement('option');
              option.value = voice.name.toLowerCase();
              option.textContent = voice.name;
              host1Select.appendChild(option.cloneNode(true));
              host2Select.appendChild(option);
            });
          }
        })
        .catch(error => {
          console.error('Error loading voices:', error);
        });
    }
    
    // Preview voice buttons
    document.getElementById('preview-host1')?.addEventListener('click', function() {
      previewVoice('host1');
    });
    
    document.getElementById('preview-host2')?.addEventListener('click', function() {
      previewVoice('host2');
    });
    
    // Update host name displays when host input fields change
    document.getElementById('host1')?.addEventListener('input', function() {
      document.querySelectorAll('.host1-name').forEach(el => {
        el.textContent = this.value || 'Host 1';
      });
    });
    
    document.getElementById('host2')?.addEventListener('input', function() {
      document.querySelectorAll('.host2-name').forEach(el => {
        el.textContent = this.value || 'Host 2';
      });
    });
    
    // Function to preview a voice
    function previewVoice(hostId) {
      const voiceSelect = document.getElementById(`${hostId}-voice`);
      const audioElement = document.getElementById(`preview-${hostId}-audio`);
      const previewBtn = document.getElementById(`preview-${hostId}`);
      
      if (voiceSelect && audioElement && previewBtn) {
        const selectedVoice = voiceSelect.value;
        if (selectedVoice && selectedVoice !== 'auto') {
          previewBtn.textContent = 'Loading...';
          previewBtn.disabled = true;
          
          fetch(`/api/voice-preview/${selectedVoice}`)
            .then(response => response.json())
            .then(data => {
              if (data.success && data.metadata_path) {
                // Extract base filename and use it for audio path
                const audioPath = data.metadata_path.replace('_metadata.json', '.mp3');
                audioElement.src = `/audio/${audioPath.split('/').pop()}`;
                audioElement.classList.remove('hidden');
                audioElement.load();
                audioElement.play();
              } else {
                console.error('Failed to generate voice preview');
              }
            })
            .catch(error => {
              console.error('Error previewing voice:', error);
            })
            .finally(() => {
              previewBtn.textContent = 'Preview Voice';
              previewBtn.disabled = false;
            });
        }
      }
    }
  }
});