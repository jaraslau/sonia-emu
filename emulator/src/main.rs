use std::{env, error};
use std::os::unix::net::UnixListener;
use std::io::{BufRead, BufReader};

mod joystick;

fn main() -> Result<(), Box<dyn error::Error>> {
    let joystick = joystick::Joystick::new()?;
    let args: Vec<_> = env::args().collect();
    let path = if args.len() > 1 {
        &args[1]
    } else {
        "/tmp/sonia-emu.sock"
    };
    
    println!(
        "Created joystick with device path {}",
        joystick.device_path()?.to_string_lossy()
    );
    
    let _ = std::fs::remove_file(path);
    let listener = UnixListener::bind(path)?;
    println!("Listening at {}", path);
    
    loop {
        match listener.accept() {
            Ok((socket, _)) => {
                println!("Client connected!");
                if let Err(e) = handle_client(socket, &joystick) {
                    eprintln!("Client error: {}", e);
                }
                println!("Client disconnected");
            }
            Err(e) => {
                eprintln!("Accept error: {}", e);
                break;
            }
        }
    }
    
    Ok(())
}

#[inline]
fn handle_client(
    socket: std::os::unix::net::UnixStream,
    joystick: &joystick::Joystick,
) -> Result<(), Box<dyn error::Error>> {
    let mut buffer = Vec::with_capacity(32);
    let mut reader = BufReader::with_capacity(4096, socket);
    
    loop {
        buffer.clear();
        let n = reader.read_until(b'\n', &mut buffer)?;
        
        if n == 0 {
            break;
        }
        
        if n <= 1 {
            continue;
        }
        
        let line = &buffer[..n.saturating_sub(1)];
        
        let mut iter = line.split(|&b| b == b' ');
        
        match iter.next() {
            Some(b"b") => {
                if let (Some(id), Some(state)) = (iter.next(), iter.next()) {
                    if let (Some(btn_id), Some(pressed)) = (parse_u8(id), parse_u8(state)) {
                        joystick.button_press(button_map(btn_id), pressed != 0)?;
                    }
                }
            }
            Some(b"j") => {
                if let (Some(id), Some(value)) = (iter.next(), iter.next()) {
                    if let (Some(axis_id), Some(pos)) = (parse_u8(id), parse_i32(value)) {
                        joystick.move_axis(axis_map(axis_id), pos)?;
                    }
                }
            }
            _ => {}
        }
        
        joystick.synchronise()?;
    }
    
    Ok(())
}

#[inline(always)]
fn parse_u8(bytes: &[u8]) -> Option<u8> {
    let mut result = 0u8;
    for &b in bytes {
        if b.is_ascii_digit() {
            result = result.wrapping_mul(10).wrapping_add(b - b'0');
        } else {
            return None;
        }
    }
    Some(result)
}

#[inline(always)]
fn parse_i32(bytes: &[u8]) -> Option<i32> {
    if bytes.is_empty() {
        return None;
    }
    
    let (negative, start) = if bytes[0] == b'-' {
        (true, 1)
    } else {
        (false, 0)
    };
    
    let mut result = 0i32;
    for &b in &bytes[start..] {
        if b.is_ascii_digit() {
            result = result.wrapping_mul(10).wrapping_add((b - b'0') as i32);
        } else {
            return None;
        }
    }
    
    Some(if negative { -result } else { result })
}

static BUTTON_MAP: [joystick::Button; 17] = {
    use joystick::Button::*;
    [
        LeftNorth,
        LeftEast,
        LeftWest,
        LeftSouth,
        LeftSpecial,
        RightSouth,
        RightSpecial,
        RightEast,
        RightNorth,
        RightWest,
        R2,
        R1,
        L2,
        L1,
        R3,
        L3,
        Guide,
    ]
};

static AXIS_MAP: [joystick::Axis; 6] = {
    use joystick::Axis::*;
    [X, Y, RX, RY, Z, RZ]
};

#[inline(always)]
fn button_map(i: u8) -> joystick::Button {
    BUTTON_MAP.get(i as usize).copied().unwrap_or(joystick::Button::Guide)
}

#[inline(always)]
fn axis_map(i: u8) -> joystick::Axis {
    AXIS_MAP.get(i as usize).copied().unwrap_or(joystick::Axis::X)
}
