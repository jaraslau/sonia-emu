use std::slice;

#[derive(Debug)]
pub enum Axis {
    X,
    Y,
    RX,
    RY,
    Z,
    RZ,
}

impl Axis {
    pub(super) fn to_evdev_axis(&self) -> input_linux::AbsoluteAxis {
        use Axis::*;

        match &self {
            X => input_linux::AbsoluteAxis::X,
            Y => input_linux::AbsoluteAxis::Y,
            RX => input_linux::AbsoluteAxis::RX,
            RY => input_linux::AbsoluteAxis::RY,
            Z => input_linux::AbsoluteAxis::Z,
            RZ => input_linux::AbsoluteAxis::RZ,
        }
    }

    pub(super) fn all_axes() -> slice::Iter<'static, Self> {
        use Axis::*;
        [X, Y, RX, RY, Z, RZ].iter()
    }
}
