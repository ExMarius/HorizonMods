fn gokart_item_bar(
    game: &crate::game::Game<'_>,
    stack: &horizon_client::items::ItemStack,
    bar: &mut Option<(i32, u32)>,
) {
    crate::game::gokart_glue::item_bar(game, stack, bar);
}
