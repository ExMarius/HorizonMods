fn gokart_register_commands(commands: &mut Vec<horizon_client::mod_api::NativeCommand>) {
    crate::game::gokart_glue::commands(commands);
}
