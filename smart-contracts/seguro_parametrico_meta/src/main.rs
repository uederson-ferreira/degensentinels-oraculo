use std::env;
use seguro_parametrico_sc::AbiProvider;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() > 1 && args[1] == "abi" {
        let abi_json = AbiProvider::abi_json();
        println!("{}", abi_json);
    } else {
        eprintln!("❌ Comando inválido. Use:\n\n    cargo run abi");
    }
}
