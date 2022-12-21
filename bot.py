import html
import logging

from aiogram import Bot, Dispatcher, executor, types
from utils.config import cfg
from utils.database import Database
from utils.middleware import AlbumMiddleware

debug_is_possible = False
debug = False
bot = Bot(token=cfg['bot_token'], parse_mode='HTML')
dp = Dispatcher(bot)
media_storage = {}

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="debug")
async def handle_start_command(message: types.Message):
    global debug
    if debug_is_possible:
        debug = not debug
        if debug:
            await message.reply(f"Debug on")
        else:
            await message.reply(f"Debug off")
    else:
        await message.reply("Debug mode is unavailable")


@dp.message_handler(commands="start")
async def handle_start_command(message: types.Message):
    await message.reply(
        "Welcome to the Playlist Manager.\n\n"
        "Possible commands:\n"
        f"* <code>/add [playlist_name]</code> — adds a replied song to the specified playlist.\n"
        f"* <code>/playlists</code> — shows a list of all playlists in this chat.\n"
        f"* <code>/get [playlist_name]</code> — sends you all the songs in a playlist.\n"
        f"* <code>/remove_playlist [playlist_name]</code> — removes a playlist.\n"
        f"* <code>/remove_song [playlist_name] [song_id]</code> — removes the song number [song_id] from a playlist.\n"
    )


@dp.message_handler(commands="add")
async def handle_add_command(message: types.Message):
    """Usage: <code>/add [playlist_name]</code>. Link songs via replying."""
    args = message.text.split(maxsplit=1)
    if len(args) != 2 or message.reply_to_message is None:
        await message.answer("Usage: <code>/add [playlist_name]</code>. Link songs via replying.")
        return
    if message.reply_to_message.from_user.id == (await bot.get_me()).id:
        await message.answer("Error: I can't access my own messages. "
                             "To use them you should first forward them by yourself.")
        return
    playlist: str = args[-1]

    if message.reply_to_message.media_group_id is None:
        if not message.reply_to_message.audio:
            await message.answer("Error: Reply message is not a song.")
            return
        async with Database() as db:
            await db.add_playlist_song(
                chat_id=message.chat.id,
                song_id=message.reply_to_message.audio.file_id,
                playlist=playlist
            )
        await message.answer(f"Song has been successfully added to \"{html.escape(playlist)}\" playlist")
    else:
        if debug:
            await message.answer(message.reply_to_message.media_group_id + "\n" + str(media_storage))
        if message.reply_to_message.media_group_id not in media_storage:
            await message.answer("Error: Couldn't access media. Only media after bot is started is supported.")
            return
        async with Database() as db:
            for song_id in media_storage[message.reply_to_message.media_group_id]:
                await db.add_playlist_song(
                    chat_id=message.chat.id,
                    song_id=song_id,
                    playlist=playlist
                )
        await message.answer(f"Songs have been successfully added to \"{html.escape(playlist)}\" playlist")


@dp.message_handler(is_media_group=True, content_types=types.ContentType.ANY)
async def handle_audios(_message: types.Message, album: list[types.Message]):
    for msg in album:
        if not msg.audio:
            continue
        if msg.media_group_id not in media_storage:
            media_storage[msg.media_group_id] = []
        if debug:
            await _message.answer(msg.media_group_id)
        media_storage[msg.media_group_id].append(msg.audio.file_id)


@dp.message_handler(commands="get")
async def handle_get_command(message: types.Message):
    """Usage: <code>/get [playlist_name]</code>."""
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Usage: <code>/get [playlist_name]</code>.")
        return
    playlist: str = args[-1]
    async with Database() as db:
        songs = await db.get_playlist(
            chat_id=message.chat.id,
            playlist=playlist
        )
    if len(songs) == 0:
        await message.answer(f"Didn't find playlist \"{html.escape(playlist)}\".")
        return
    media_group = [types.InputMediaAudio(media=song_id) for song_id in songs]
    for i in range((len(media_group) + 9) // 10):
        await message.answer_media_group(media_group[i * 10:(i + 1) * 10])


@dp.message_handler(commands="playlists")
async def handle_playlists_command(message: types.Message):
    """Usage: <code>/playlists</code>."""
    async with Database() as db:
        playlists = await db.get_playlists(
            chat_id=message.chat.id
        )
    if len(playlists) == 0:
        await message.answer(f"There are no playlists in this chat.")
        return
    playlists_list = "<b>* Playlists:</b>\n\n" + "\n".join(html.escape(playlist) for playlist in playlists)
    await message.answer(playlists_list)


@dp.message_handler(commands="remove_playlist")
async def handle_rplaylist_command(message: types.Message):
    """Usage: <code>/remove_playlist [playlist_name]</code>."""
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Usage: <code>/remove_playlist [playlist_name]</code>.")
        return
    playlist: str = args[-1]
    async with Database() as db:
        await db.remove_playlist(
            chat_id=message.chat.id,
            playlist=playlist
        )
    await message.answer(f"Playlist \"{html.escape(playlist)}\" successfully deleted.")


@dp.message_handler(commands="remove_song")
async def handle_rsong_command(message: types.Message):
    """Usage: <code>/remove_song [playlist_name] [song_index_in_playlist]</code>."""
    args = message.text.split(maxsplit=1)
    sub_args = args[-1].rsplit(maxsplit=1)
    if len(args) != 2 or len(sub_args) != 2 or not sub_args[-1].isdigit():
        await message.answer("Usage: <code>/remove_song [playlist_name] [song_index_in_playlist]</code>.")
        return
    song_num: int = int(sub_args[-1])
    playlist: str = sub_args[0]

    async with Database() as db:
        songs = await db.get_playlist(
            chat_id=message.chat.id,
            playlist=playlist
        )
        if len(songs) == 0:
            await message.answer(f"There is no playlist \"{html.escape(playlist)}\" in this chat.")
            return
        if song_num not in range(1, len(songs) + 1):
            await message.answer(f"Song index must be in between 1 and {len(songs)} for this playlist.")
            return
        await db.remove_song(
            chat_id=message.chat.id,
            song_id=songs[song_num - 1],
            playlist=playlist
        )
    await message.answer(f"Song successfully deleted.")


if __name__ == "__main__":
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=False)
