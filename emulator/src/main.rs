use std::{env, error};
use std::os::unix::net::UnixListener;
use std::io::{BufRead, BufReader};

mod joystick;

fn main() -> Result<(), Box<dyn error::Error>> {
    let joystick = joystick::Joystick::new()?;
    let args: Vec<_> = env::args().collect();
    let path = if args.len() > 1 {
        args[1].clone()
    } else {
        "/tmp/sonia-emu.sock".to_owned()
    };

    println!(
        "Created joystick with device path {}",
        joystick.device_path()?.to_string_lossy()
    );

    let _ = std::fs::remove_file(&path);
    let listener = UnixListener::bind(&path)?;
    println!("Listening at {}", &path);

    let (socket, _addr) = listener.accept()?;
    println!("Client connected!");

    let mut buffer = String::new();
    let mut reader = BufReader::new(socket.try_clone()?);

    loop {
        reader.read_line(&mut buffer)?;
        let parts: Vec<&str> = buffer.split_whitespace().collect();
        let i = parts[1].parse::<usize>().unwrap();
        
        match parts[0] {
            "b" => joystick.button_press(button_map(i), parts[2] == "1")?,
            "j" => {
                let value = parts[2].parse::<f64>().unwrap();
                joystick.move_axis(axis_map(i), value as i32)?
            },
            _ => joystick.synchronise()?,
        }

        joystick.synchronise()?;
        buffer.clear();
    }
}

fn button_map(i: usize) -> joystick::Button {
    use joystick::Button::*;
    match i {
        0 => LeftNorth,
        1 => LeftEast,
        2 => LeftWest,
        3 => LeftSouth,
        4 => LeftSpecial,
        5 => RightSouth,
        6 => RightSpecial,
        7 => RightEast,
        8 => RightNorth,
        9 => RightWest,
        10 => R2,
        11 => R1,
        12 => L2,
        13 => L1,
        14 => R3,
        15 => L3,
        16 => Guide,
        _ => unreachable!(),
    }
}

fn axis_map(i: usize) -> joystick::Axis {
    use joystick::Axis::*;
    match i {
        0 => X,
        1 => Y,
        2 => RX,
        3 => RY,
        _ => unreachable!(),
    }
}
