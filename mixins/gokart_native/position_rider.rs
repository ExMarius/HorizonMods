fn gokart_position_rider(game: &mut crate::game::Game<'_>) -> core::ops::ControlFlow<()> {
    crate::game::gokart_glue::position_rider(game)
}
