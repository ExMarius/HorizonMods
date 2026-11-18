fn gokart_attack_entity(
    game: &mut crate::game::Game<'_>,
    entity: i32,
    kind: &str,
    pos: [f64; 3],
    canceled: &mut bool,
) {
    crate::game::gokart_glue::attack_entity(game, entity, kind, pos, canceled);
}
