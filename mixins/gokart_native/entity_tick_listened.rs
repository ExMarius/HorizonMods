fn gokart_entity_tick_listened(game: &mut crate::game::Game<'_>, listened: &mut bool) {
    crate::game::gokart_glue::entity_tick_listened(game, listened);
}
