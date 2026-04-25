mod axis;
mod button;
mod error;

pub use axis::Axis;
pub use button::Button;
pub use error::Error;

use input_linux::sys;

use std::{fs, path};

pub struct Joystick {
    device: input_linux::UInputHandle<fs::File>,
}

impl Joystick {
    pub fn new() -> Result<Self, Error> {
        let device = create_joystick_device()?;
        Ok(Joystick { device })
    }

    #[inline]
    pub fn device_path(&self) -> Result<path::PathBuf, Error> {
        Ok(self.device.evdev_path()?)
    }

    #[inline]
    pub fn move_axis(&self, axis: Axis, position: i32) -> Result<(), Error> {
        if !(-512..=512).contains(&position) {
            return Err(Error::OutOfRangeError {
                min: -512,
                max: 512,
                actual: position,
            });
        }

        self.write_event(input_linux::AbsoluteEvent::new(
            EVENT_TIME,
            axis.to_evdev_axis(),
            position,
        ))
    }

    #[inline]
    pub fn button_press(&self, button: Button, is_pressed: bool) -> Result<(), Error> {
        let value = if is_pressed {
            input_linux::KeyState::PRESSED
        } else {
            input_linux::KeyState::RELEASED
        };

        self.write_event(input_linux::KeyEvent::new(
            EVENT_TIME,
            button.to_evdev_button(),
            value,
        ))
    }

    #[inline]
    pub fn synchronise(&self) -> Result<(), Error> {
        self.write_event(input_linux::SynchronizeEvent::report(EVENT_TIME))
    }

    #[inline(always)]
    fn write_event(&self, event: impl std::convert::AsRef<sys::input_event>) -> Result<(), Error> {
        self.device.write(&[*event.as_ref()])?;
        Ok(())
    }
}

// Const event time to avoid repeated allocations
const EVENT_TIME: input_linux::EventTime = input_linux::EventTime::new(0, 0);

fn create_joystick_device() -> Result<input_linux::UInputHandle<fs::File>, Error> {
    let uinput_file = fs::File::create("/dev/uinput")?;
    let device = input_linux::UInputHandle::new(uinput_file);

    let input_id = input_linux::InputId {
        bustype: sys::BUS_VIRTUAL,
        vendor: 34,
        product: 10,
        version: 1,
    };

    const AXIS_INFO: input_linux::AbsoluteInfo = input_linux::AbsoluteInfo {
        value: 0,
        minimum: -512,
        maximum: 512,
        fuzz: 0,
        flat: 0,
        resolution: 50,
    };

    device.set_evbit(input_linux::EventKind::Absolute)?;
    device.set_evbit(input_linux::EventKind::Key)?;
    device.set_keybit(input_linux::Key::ButtonTrigger)?;

    for button in Button::all_buttons() {
        device.set_keybit(button.to_evdev_button())?;
    }

    let mut axis_setups = Vec::with_capacity(6);
    for axis in Axis::all_axes() {
        axis_setups.push(input_linux::AbsoluteInfoSetup {
            axis: axis.to_evdev_axis(),
            info: AXIS_INFO,
        });
    }

    device.create(&input_id, b"sonia-emu", 0, &axis_setups)?;

    Ok(device)
}
