use std::slice;

#[derive(Debug, Copy, Clone)]
pub enum Button {
    LeftNorth,
    LeftSouth,
    LeftEast,
    LeftWest,

    LeftSpecial,

    RightNorth,
    RightSouth,
    RightEast,
    RightWest,

    RightSpecial,

    L1,
    R1,
    L2,
    R2,
    L3,
    R3,

    Guide,
}

impl Button {
    #[inline]
    pub(super) fn to_evdev_button(&self) -> input_linux::Key {
        use input_linux::Key::*;
        use Button::*;

        match self {
            LeftNorth => ButtonDpadUp,
            LeftSouth => ButtonDpadDown,
            LeftEast => ButtonDpadLeft,
            LeftWest => ButtonDpadRight,

            LeftSpecial => ButtonStart,

            RightNorth => ButtonNorth,
            RightSouth => ButtonSouth,
            RightEast => ButtonEast,
            RightWest => ButtonWest,

            RightSpecial => ButtonSelect,

            L1 => ButtonTL,
            R1 => ButtonTR,
            L2 => ButtonTL2,
            R2 => ButtonTR2,
            L3 => ButtonThumbl,
            R3 => ButtonThumbr,

            Guide => ButtonMode,
        }
    }

    pub(super) fn all_buttons() -> slice::Iter<'static, Self> {
        use Button::*;
        const ALL: [Button; 17] = [
            LeftNorth,
            LeftSouth,
            LeftEast,
            LeftWest,
            LeftSpecial,
            RightNorth,
            RightSouth,
            RightEast,
            RightWest,
            RightSpecial,
            L1,
            R1,
            L2,
            R2,
            L3,
            R3,
            Guide,
        ];
        ALL.iter()
    }
}