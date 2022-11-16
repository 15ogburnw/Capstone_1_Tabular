from models import db, User, Instrument, Playlist, PlaylistUser, Song, PlaylistSong
from app import app

db.drop_all()
db.create_all()

# User.query.delete()

# # Add example users
# user1 = User.register(username='HockeyLover445', password='password',
#                       email='hockeylover445@gmail.com', first_name='Garrett', last_name='Smith')
# user1.id = 1000

# user2 = User.register(username='c_Taylor', password='password',
#                       email='ctaylor1994@gmail.com', first_name='Chad', last_name='Taylor')
# user2.id = 2000

# user3 = User.register(username='Mattergy', password='password',
#                       email='mattergy@gmail.com', first_name='Matt', last_name=None)
# user3.id = 3000

# db.session.add_all([user1, user2, user3])
# db.session.commit()

# # Add instruments
# Instrument.query.delete()

# acoustic = Instrument(name='Acoustic Guitar',
#                       icon="la:guitar")
# electric = Instrument(name='Electric Guitar',
#                       icon="mdi:guitar-electric")
# drums = Instrument(name='Drums', icon="fa-solid:drum")
# piano = Instrument(name='Piano/Keyboard',
#                    icon="gg:piano")


# db.session.add_all([acoustic, electric, drums, piano])
# db.session.commit()


# # Assign an instrument to user1
# user1 = User.query.filter_by(username='HockeyLover445').one()
# acoustic = Instrument.query.filter_by(name='Acoustic Guitar').one()

# user1.instrument = acoustic
# db.session.commit()


# # Add some example playlists to user1

# playlist1 = Playlist(name='Bob Marley Songs', user_id=1000)
# p1id = 1000
# playlist1.id = p1id
# playlist2 = Playlist(name='Classic Rock', user_id=1000)
# p2id = 2000
# playlist2.id = p2id

# db.session.add_all([playlist1, playlist2])
# db.session.commit()

# # Assign Playlists to user1

# pu1 = PlaylistUser(playlist_id=1000, user_id=1000)
# pu2 = PlaylistUser(playlist_id=2000, user_id=1000)

# db.session.add_all([pu1, pu2])
# db.session.commit()


# # Add some songs

# song1 = Song(title="Could You Be Loved", artist="Bob Marley",
#              tab_url="https://www.songsterr.com/a/wa/song?id=27215")
# s1id = 27215
# song1.id = s1id
# song2 = Song(title='Concrete Jungle', artist='Bob Marley',
#              tab_url='https://www.songsterr.com/a/wa/song?id=12459')
# s2id = 12459
# song2.id = s2id

# song3 = Song(title='Whole Lotta Love', artist='Led Zeppelin',
#              tab_url='https://www.songsterr.com/a/wa/song?id=449')
# s3id = 449
# song3.id = s3id
# song4 = Song(title='Angie', artist='The Rolling Stones',
#              tab_url='https://www.songsterr.com/a/wa/song?id=61')
# s4id = 61
# song4.id = s4id

# db.session.add_all([song1, song2, song3, song4])
# db.session.commit()

# # Assign songs to playlists

# ps1 = PlaylistSong(playlist_id=1000, song_id=s1id)
# ps2 = PlaylistSong(playlist_id=1000, song_id=s2id)
# ps3 = PlaylistSong(playlist_id=2000, song_id=s3id)
# ps4 = PlaylistSong(playlist_id=2000, song_id=s4id)

# db.session.add_all([ps1, ps2, ps3, ps4])
# db.session.commit()
