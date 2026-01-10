from pathlib import Path
import re

pathlist = Path("../music/som").glob("*.ogg")

with open("../music/som/som_music.asset", "w", encoding='utf-8') as songs:
    with open("../music/som/som_music.txt", "w", encoding='utf-8') as music:
        music.write("music_station = \"som_music\"\n")
        for path in pathlist:
            name = path
            song_def = f"""
music = {{
    name = "{name.stem}"
    file = "{name.name}"
    volume = 0.8
}}
"""
            songs.write(song_def)
            music_def = f"""
music = {{
    song = "{name.stem}"
    chance = {{
        factor = 1
        
    }}
}}
"""
            music.write(music_def)
