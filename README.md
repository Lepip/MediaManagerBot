# MediaManagerBot
Media manager for tg.

Welcome to the Playlist Manager.

Possible commands:

- ```/add [playlist_name]``` — adds a replied song to the specified playlist.
For example: you upload 2 songs to Telegram as songs. Then you reply to the message with those songs and write `/add playlist1`. Now those songs are appended to a playlist named `playlist1`.
- `/playlists` — shows a list of all playlists in this chat.
- <code>/get [playlist_name]</code> — sends you all the songs in a playlist.
- <code>/remove_playlist [playlist_name]</code> — removes a playlist.
- <code>/remove_song [playlist_name] [song_id]</code> — removes the song numbered [song_id] from a playlist.
