fn gokart_tick_player_model(ret: (), game: &mut crate::game::Game<'_>) {
    let () = ret;
    crate::game::gokart_glue::tick_player_model_post(game);
}
