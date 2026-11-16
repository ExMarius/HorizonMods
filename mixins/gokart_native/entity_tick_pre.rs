fn gokart_entity_tick_pre(
    game: &mut crate::game::Game<'_>,
    dimension: &str,
    entity: u32,
    kind: &str,
    canceled: &mut bool,
) {
    crate::game::gokart_glue::entity_tick_pre(game, dimension, entity, kind, canceled);
}
