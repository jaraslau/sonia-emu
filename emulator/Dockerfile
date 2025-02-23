# syntax=docker/dockerfile:1

FROM rust:1.49 as build

RUN USER=root cargo new --bin sonia-emu
WORKDIR /sonia-emu

COPY ./Cargo.lock ./Cargo.lock
COPY ./Cargo.toml ./Cargo.toml

RUN cargo build --release
RUN rm src/*.rs

COPY ./src ./src

RUN rm ./target/release/deps/sonia-emu*
RUN cargo build --release

FROM rust:1.49-slim-buster

COPY --from=build /sonia-emu/target/release/sonia-emu .

CMD ["./sonia-emu"]
