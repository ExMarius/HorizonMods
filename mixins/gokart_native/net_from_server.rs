fn gokart_net_from_server(
    game: &mut crate::game::Game<'_>,
    channel: &str,
    data: &[u8],
) {
    crate::game::gokart_glue::net_from_server(game, channel, data);
}
