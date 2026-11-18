fn gokart_hud(
    game: &mut crate::game::Game<'_>,
    batch: &mut horizon_client::hud::HudBatch,
    corners: &mut horizon_client::mod_api::Corners,
) {
    crate::game::gokart_glue::hud(game, batch, corners);
}
