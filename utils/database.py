import asyncpg
from utils.config import cfg


class Database:
    def __init__(self):
        self.conn: asyncpg.Connection = ...

    async def connect(self):
        self.conn: asyncpg.Connection = await asyncpg.connect(
            host=cfg['db_host'],
            port=cfg['db_port'],
            user=cfg['db_user'],
            database=cfg['db_name'],
            password=cfg['db_password']
        )

    async def add_playlist_song(self, chat_id: int, song_id: str, playlist: str):
        await self.conn.execute(
            "INSERT INTO songs(chat_id, song_id, playlist) VALUES ($1, $2, $3)",
            chat_id, song_id, playlist
        )

    async def get_playlist(self, chat_id: int, playlist: str) -> list[str]:
        res = await self.conn.fetch(
            "SELECT * FROM songs WHERE chat_id=$1 AND playlist=$2",
            chat_id, playlist
        )
        return [entry.get('song_id') for entry in res]

    async def remove_song(self, chat_id: int, song_id: str, playlist: str):
        await self.conn.execute(
            "DELETE FROM songs WHERE chat_id = $1 AND song_id = $2 AND playlist = $3",
            chat_id, song_id, playlist
        )

    async def remove_playlist(self, chat_id: int, playlist: str):
        await self.conn.execute(
            "DELETE FROM songs WHERE chat_id = $1 AND playlist = $2",
            chat_id, playlist
        )

    async def get_playlists(self, chat_id: int) -> list[str]:
        res = await self.conn.fetch(
            "SELECT playlist FROM songs WHERE chat_id=$1",
            chat_id
        )
        return list(set(entry.get('playlist') for entry in res))

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()
