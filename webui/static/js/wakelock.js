let wakeLock = null;

async function requestWakeLock() {
  try {
    if ('wakeLock' in navigator) {
      wakeLock = await navigator.wakeLock.request('screen');
    } else {
      console.warn('WakeLock API is not supported by your browser.');
    }
  } catch (err) {
    console.error(`Failed to acquire wakelock: ${err.message}`);
  }
}

async function releaseWakeLock() {
  if (wakeLock !== null) {
    await wakeLock.release();
    wakeLock = null;
  }
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    requestWakeLock();
  } else {
    releaseWakeLock();
  }
});

window.addEventListener('load', () => {
  requestWakeLock();
});

