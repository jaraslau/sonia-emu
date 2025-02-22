document.addEventListener('DOMContentLoaded', () => {
    const joysticks = [
        {
            container: document.getElementById('left-joystick-container'),
            joystick: document.getElementById('left-joystick'),
            name: 'Left',
            touchId: null
        },
        {
            container: document.getElementById('right-joystick-container'),
            joystick: document.getElementById('right-joystick'),
            name: 'Right',
            touchId: null
        }
    ];

    joysticks.forEach((joystickObj) => {
        const { container, joystick, name } = joystickObj;
        const containerRadius = container.offsetWidth / 2;
        const joystickRadius = joystick.offsetWidth / 2;
        const maxDistance = containerRadius + joystickRadius;

        container.addEventListener('touchstart', (e) => startDrag(e, joystickObj), { passive: false });
        container.addEventListener('touchmove', (e) => drag(e, joystickObj, maxDistance), { passive: false });
        document.addEventListener('touchend', (e) => stopDrag(e, joystickObj));
        document.addEventListener('touchcancel', (e) => stopDrag(e, joystickObj));
    });

    function startDrag(event, joystickObj) {
        event.preventDefault();
        const touch = getRelevantTouch(event, joystickObj);
        if (!touch) return;

        joystickObj.touchId = touch.identifier;
        joystickObj.joystick.style.transition = 'none';
    }

    function drag(event, joystickObj, maxDistance) {
        if (joystickObj.touchId === null) return;

        const touch = getTouchById(event, joystickObj.touchId);
        if (!touch) return;

        const rect = joystickObj.container.getBoundingClientRect();
        const containerRadius = joystickObj.container.offsetWidth / 2;

        const x = touch.clientX - rect.left - containerRadius;
        const y = touch.clientY - rect.top - containerRadius;

        const distance = Math.min(Math.sqrt(x * x + y * y), maxDistance);
        const angle = Math.atan2(y, x);

        const offsetX = Math.cos(angle) * distance;
        const offsetY = Math.sin(angle) * distance;

        joystickObj.joystick.style.transform = `translate(calc(-50% + ${offsetX}px), calc(-50% + ${offsetY}px))`;

        const normalizedX = offsetX / maxDistance;
        const normalizedY = offsetY / maxDistance;

        console.log(`${joystickObj.name} Joystick:`, { x: normalizedX, y: normalizedY });
    }

    function stopDrag(event, joystickObj) {
        const touch = getTouchById(event, joystickObj.touchId);
        if (!touch) return;

        joystickObj.touchId = null;
        joystickObj.joystick.style.transition = 'transform 0.2s ease-out';
        joystickObj.joystick.style.transform = 'translate(-50%, -50%)';
    }

    function getRelevantTouch(event, joystickObj) {
        for (let touch of event.touches) {
            const rect = joystickObj.container.getBoundingClientRect();
            if (
                touch.clientX >= rect.left &&
                touch.clientX <= rect.right &&
                touch.clientY >= rect.top &&
                touch.clientY <= rect.bottom
            ) {
                return touch;
            }
        }
        return null;
    }

    function getTouchById(event, touchId) {
        for (let touch of event.changedTouches) {
            if (touch.identifier === touchId) {
                return touch;
            }
        }
        return null;
    }
  document.querySelectorAll('.button').forEach(button => {
    button.addEventListener('click', () => {
        const buttonId = button.getAttribute('data-id');
        console.log(`Button ${buttonId} pressed`);
    });
  });
});
