use std::slice;

#[derive(Debug, Copy, Clone)]
pub enum Axis {
    X,
    Y,
    RX,
    RY,
    Z,
    RZ,
}

impl Axis {
    #[inline]
    pub(super) fn to_evdev_axis(self) -> input_linux::AbsoluteAxis {
        use input_linux::AbsoluteAxis;
        use Axis::*;

        match self {
            X => AbsoluteAxis::X,
            Y => AbsoluteAxis::Y,
            RX => AbsoluteAxis::RX,
            RY => AbsoluteAxis::RY,
            Z => AbsoluteAxis::Z,
            RZ => AbsoluteAxis::RZ,
        }
    }

    pub(super) fn all_axes() -> slice::Iter<'static, Self> {
        const ALL: [Axis; 6] = [Axis::X, Axis::Y, Axis::RX, Axis::RY, Axis::Z, Axis::RZ];
        ALL.iter()
    }
}
