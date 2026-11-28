fn gokart_input_key(
    game: &mut crate::game::Game<'_>,
    event: &horizon_client::mod_api::winit::event::KeyEvent,
) {
    crate::game::gokart_glue::input_key(game, event);
}
