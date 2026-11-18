fn gokart_entity_tick_post(
    game: &mut crate::game::Game<'_>,
    dimension: &str,
    entity: u32,
    kind: &str,
) {
    crate::game::gokart_glue::entity_tick_post(game, dimension, entity, kind);
}
