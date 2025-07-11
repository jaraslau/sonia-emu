document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket('ws://' + location.host + '/ws');

    function setupTriggerSlider(slider) {
            const thumb = slider.querySelector('.trigger-thumb');
            const dataId = slider.dataset.id;
            let activeTouchId = null;
            let sliderRect = null;
            let isDragging = false;
            const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
            const updateThumbPosition = (clientY) => {
                    const offset = clamp(clientY - sliderRect.top, 0, sliderRect.height);
            const pressure = (1 - offset / sliderRect.height) * 2 - 1;
            const clampedBottom = ((pressure + 1) / 2) * sliderRect.height;

            thumb.style.bottom = `${clampedBottom}px`;
            sendData({ type: 'trigger', id: dataId, z: pressure }, socket);
        };

        const endDrag = (e) => {
            for (const touch of e.changedTouches) {
                    if (touch.identifier === activeTouchId) {
                            activeTouchId = null;
                            thumb.style.transition = 'bottom 0.2s ease-out';
                            thumb.style.bottom = `0px`;
                            sendData({ type: 'trigger', id: dataId, z: -1 }, socket);

                            document.removeEventListener('touchmove', onMove);
                            document.removeEventListener('touchend', endDrag);

                            setTimeout(() => {
                                    thumb.style.transition = '';
                            }, 200);

                            break;
                    }
            }
        };

        const onMove = (e) => {
            if (activeTouchId === null) return;
            for (const touch of e.changedTouches) {
                    if (touch.identifier === activeTouchId) {
                            updateThumbPosition(touch.clientY);
                            break;
                    }
            }
        };
        const startDrag = (e) => {
            if (activeTouchId !== null) return;
            const touch = e.changedTouches[0];
            activeTouchId = touch.identifier;
            sliderRect = slider.getBoundingClientRect();

            updateThumbPosition(touch.clientY);

            document.addEventListener('touchmove', onMove, { passive: false });
            document.addEventListener('touchend', endDrag);
            document.addEventListener('touchcancel', endDrag);
        };

        slider.addEventListener('touchstart', startDrag, { passive: false });
    }

    function sendData(data, ws) {
        if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(data));
        }
        else {
                fetch('/fallback', {
                        method: 'POST',
                        headers: {
                                'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                })
                .catch(error => {
                        console.error('Error sending data to backend:', error);
                });
        }
    }

    document.querySelectorAll('.trigger-slider').forEach(setupTriggerSlider);
});
