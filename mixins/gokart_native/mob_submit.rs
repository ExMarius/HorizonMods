fn gokart_mob_submit(
    game: &crate::game::Game<'_>,
    mob: &horizon_client::mod_api::NativeMobRender<'_>,
    draw: &mut horizon_client::mod_api::BlockEntityDraw,
    drawn: &mut bool,
) {
    crate::game::gokart_glue::mob_submit(game, mob, draw, drawn);
}
