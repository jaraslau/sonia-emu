#[derive(Debug, Clone, Copy)]
struct Packet {
    prefix: u8,
    input_id: u8,
    value: i32,
}

#[derive(Debug, Clone, Copy)]
impl Packet {
    pub fn from_bytes(buf: [u8; 6]) -> Option<Self> {
        match buf[0] {
            b'b' | b'j' => Some(Self {
                prefix: buf[0],
                input_id: buf[1],
                value: i32::from_be_bytes(buf[2..6].try_into().unwrap()),
            }),
            _ => None,
        }
    }
}