fn gokart_interact_entity(
    game: &mut crate::game::Game<'_>,
    entity: i32,
    kind: &str,
    stack: Option<&horizon_client::items::ItemStack>,
    claimed: &mut bool,
) {
    crate::game::gokart_glue::interact_entity(game, entity, kind, stack, claimed);
}
