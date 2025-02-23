use std::{env, error};
use std::net::TcpListener;
use std::io::{BufRead, BufReader};

mod joystick;

fn main() -> Result<(), Box<dyn error::Error>> {
    let args: Vec<_> = env::args().collect();
    let port = if args.len() > 1 {
        args[1].clone()
    } else {
        "5001".to_string()
    };

    let joystick = joystick::Joystick::new()?;

    println!(
        "Created joystick with device path {}",
        joystick.device_path()?.to_string_lossy()
    );

    let listener = TcpListener::bind(format!("127.0.0.1:{}", port))?;
    println!("Listening at {port}");

    let (socket, addr) = listener.accept()?;
    println!("{addr:?} connected");

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
        1 => LeftWest,
        2 => LeftEast,
        3 => LeftSouth,
        4 => LeftSpecial,
        5 => RightSouth,
        6 => RightSpecial,
        7 => RightEast,
        8 => RightWest,
        9 => RightNorth,
        10 => R2,
        11 => R1,
        12 => L2,
        13 => L1,
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

