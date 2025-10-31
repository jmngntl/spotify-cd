document.addEventListener('DOMContentLoaded', function() {
const videoElement = document.getElementById('background-video');
const videoSources = [
    'vids/6698403-uhd_4096_2160_25fps copy.mp4',
    'vids/7135106-uhd_3840_2160_30fps.mp4',
    'vids/10597787-uhd_4096_2160_25fps copy.mp4'
    // Add more video paths as needed
];

function setRandomVideo() {
    const randomIndex = Math.floor(Math.random() * videoSources.length);
    videoElement.src = videoSources[randomIndex];
    videoElement.load(); // Reloads the video with the new source
    videoElement.play(); // Ensures playback starts
}

// Set a random video on page load
setRandomVideo();

// (Optional) Set a new random video when the current one ends
videoElement.addEventListener('ended', setRandomVideo);
});