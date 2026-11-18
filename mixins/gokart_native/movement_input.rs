fn gokart_movement_input(
    game: &crate::game::Game<'_>,
    forward: &mut f32,
    strafe: &mut f32,
    jump: &mut bool,
    sneak: &mut bool,
) {
    crate::game::gokart_glue::movement_input(game, forward, strafe, jump, sneak);
}
