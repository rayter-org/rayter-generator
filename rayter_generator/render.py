import json
import os
import random
import requests
import shutil
import puremagic
import py_avataaars

def render_game_page(env, game, players):
    filename = os.path.join(env.output_path, game['slug'], 'index.html')
    env.render_template("game.html", {
        "name": game["game_name"],
        "ratings": game["ratings"],
        "game_name": game["game_name"],
        "slug": game["slug"],
        "players": players,
        "STATIC_URL": "../static/",
    }, output_path=filename)


def render_game_json(env, game):
    filename = os.path.join(env.output_path, game['slug'], 'game.json')
    with open(filename, 'w') as f:
        json.dump(game, f)

def render_player_page(env, player):
    filename = os.path.join(env.output_path, 'player', player['slug'], 'index.html')
    env.render_template("player.html", {
        "player": player,
        "STATIC_URL": "../../static/",
    }, output_path=filename)

# FIXME: This function is quite long. Should the main parts be broken out into
#        a separate file?
def render_player_image(env, player):
    dir_path = os.path.join(env.output_path, 'player', player['slug'])
    # Ensure the player folder exists.
    os.makedirs(dir_path, exist_ok=True)

    if player['imageUrl'] is None:
        # If there is no image, generate a random avatar using py_avataaars.

        # Create a seed from the player's name in order to make the avatar
        # deterministic.
        seed_string = "123" + player['name']
        seed = 0
        for c in seed_string:
            seed += (ord(c) % 100000)
        random.seed(seed)

        # Make facial hair less common.
        use_facial_hair = random.randint(0, 9) == 0

        # Create the random avatar.
        avatar = py_avataaars.PyAvataaar(
            style=py_avataaars.AvatarStyle.TRANSPARENT,
            skin_color=random.choice(list(py_avataaars.SkinColor)),
            hair_color=random.choice(list(py_avataaars.HairColor)),
            facial_hair_type=random.choice(list(py_avataaars.FacialHairType)) if use_facial_hair else py_avataaars.FacialHairType.DEFAULT,
            facial_hair_color=random.choice(list(py_avataaars.HairColor)),
            top_type=random.choice(list(py_avataaars.TopType)),
            hat_color=random.choice(list(py_avataaars.Color)),
            mouth_type=random.choice(list(py_avataaars.MouthType)),
            eye_type=random.choice(list(py_avataaars.EyesType)),
            eyebrow_type=random.choice(list(py_avataaars.EyebrowType)),
            nose_type=random.choice(list(py_avataaars.NoseType)),
            accessories_type=random.choice(list(py_avataaars.AccessoriesType)),
            clothe_type=random.choice(list(py_avataaars.ClotheType)),
            clothe_color=random.choice(list(py_avataaars.Color)),
            clothe_graphic_type=random.choice(list(py_avataaars.ClotheGraphicType)),
        )
        # And render it to the file.
        filename = 'image.png'
        file_path = os.path.join(dir_path, filename)

        print("Writing " + file_path)
        avatar.render_png_file(file_path)
    else:
        # Use the user's preferred image.
        image_url = player['imageUrl']

        # Create the correct extension.
        extension = image_url.split('.')[-1]
        # If the extension is too long, assume there was no extension.
        # Set it to a temporary extension and guess the type from the content
        # when we have downloaded the file.
        if len(extension) > 4:
            extension = 'temp'

        filename = 'image' + '.' + extension
        file_path = os.path.join(dir_path, filename)

        print("Getting " + image_url)

        # Some sites block requests without a user agent.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

        # Download the image.
        response = requests.get(image_url, headers=headers)

        # Write the image to the file.
        print("Writing " + file_path)
        with open(file_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)

        # If the extension was temporary, guess the type from the content.
        if extension == 'temp':
            new_extension = puremagic.from_file(file_path)
            if new_extension is None:
                new_extension = '.png'

            # Rename the file to the correct extension.
            # Puremagic returns the extension with a dot so we don't need to add one.
            filename = 'image' + new_extension
            new_path = os.path.join(dir_path, filename)
            print("Mving 2 " + new_path)
            os.rename(file_path, new_path)

    # Update the player record with the new filename.
    player['image'] = filename

def render_index_page(env, games, players, global_chart):
    games.sort(key=lambda g: g["count"], reverse=True)
    filename = os.path.join(env.output_path, 'index.html')
    env.render_template("index.html", {
        "games": games,
        "players": players,
        "global_chart": global_chart,
        "log": [],
        "STATIC_URL": "static/",
    }, output_path=filename)
