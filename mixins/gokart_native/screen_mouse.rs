fn gokart_screen_mouse(
    game: &crate::game::Game<'_>,
    screen: &horizon_client::mod_api::NativeScreenView<'_>,
    button: i32,
    canceled: &mut bool,
) {
    crate::game::gokart_glue::screen_mouse(game, screen, button, canceled);
}
