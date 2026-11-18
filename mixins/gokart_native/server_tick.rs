fn gokart_server_tick(
    game: &mut crate::game::Game<'_>,
    phase: horizon_client::mod_api::ServerTickPhase,
) {
    crate::game::gokart_glue::server_tick(game, phase);
}
