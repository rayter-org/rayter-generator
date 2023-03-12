import os
from io import StringIO
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest import TestCase
from unittest.mock import patch

from textwrap import dedent

from rayter_generator.main import _main

class TestGenerator(TestCase):
    def setUp(self):
        super().setUp()
        self.games_path = TemporaryDirectory()
        self.output_path = TemporaryDirectory()

        with open(os.path.join(self.games_path.name, "babble.txt"), "w") as f:
            f.write(dedent("""
                game_name Babble

                game 2023-02-20 17:06
                PlayerOne   350
                PlayerTwo   320

                game 2023-02-24 13:00
                PlayerOne   346
                PlayerTwo   390
                PlayerThree 94

                game 2023-03-12 15:00
                PlayerOne   512
                PlayerTwo   100
            """))

        with open(os.path.join(self.output_path.name, "players_metadata.json"), "w") as f:
            f.write(dedent("""
                {
                    "PlayerOne": {
                        "displayName": "Player One DisplayName"
                    }
                }
            """))

    def tearDown(self):
        self.games_path.cleanup()
        self.output_path.cleanup()
        super().tearDown()

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_website(self, mock_stdout, mock_stderr):
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])
        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "babble", "index.html")))

        with open(os.path.join(self.output_path.name, "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("Babble", contents)

        with open(os.path.join(self.output_path.name, "babble", "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("PlayerOne", contents)

        mock_stdout.seek(0)
        mock_stderr.seek(0)
        self.assertIn("babble/index.html", mock_stdout.read())

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_website_with_config(self, mock_stdout, mock_stderr):
        with NamedTemporaryFile() as config_file:
            config_file.write(dedent("""
                site_name = "TestName"
            """).encode("utf-8"))
            config_file.flush()

            _main([
                "--games-path", self.games_path.name,
                "--output", self.output_path.name,
                "--config", config_file.name,
            ])
            with open(os.path.join(self.output_path.name, "index.html"), "r") as config_file:
                contents = config_file.read()
            self.assertIn("TestName", contents)

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_ignore_files_with_no_games(self, mock_stdout, mock_stderr):
        with open(os.path.join(self.games_path.name, "sometext.txt"), "w") as text_file:
            text_file.write(dedent("""
                This is just some text in a file.
            """))
        with open(os.path.join(self.games_path.name, "epmty.txt"), "w") as empty_file:
            empty_file.write(dedent(""))

        # Should not raise an exception
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])

        with open(os.path.join(self.output_path.name, "index.html"), "r") as f:
            contents = f.read()
        self.assertNotIn("sometext", contents)
        self.assertNotIn("empty", contents)

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_player_pages(self, mock_stdout, mock_stderr):
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])

        with open(os.path.join(self.output_path.name, "player", "PlayerOne", "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("Babble", contents)

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_player_metadata(self, mock_stdout, mock_stderr):
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
            "--players", os.path.join(self.output_path.name, "players_metadata.json"),
        ])

        with open(os.path.join(self.output_path.name, "player", "PlayerOne", "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("Player One DisplayName", contents)

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_game_json(self, mock_stdout, mock_stderr):
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])
        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "babble", "game.json")))

        with open(os.path.join(self.output_path.name, "babble", "game.json"), "r") as f:
            contents = f.read()
        self.assertIn("PlayerOne", contents)
        self.assertIn("rating_history", contents)


    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_player_images(self, mock_stdout, mock_stderr):
        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])

        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "player", "PlayerOne", "image.png")))
        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "player", "PlayerTwo", "image.png")))

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_global_chart(self, mock_stdout, mock_stderr):
        with open(os.path.join(self.games_path.name, "catch_the_rabbit.txt"), "w") as f:
            f.write(dedent("""
                game_name Catch the Rabbit

                game 2023-02-20 17:06
                PlayerOne   1
                PlayerTwo   10
                PlayerThree 0

                game 2023-02-24 13:00
                PlayerOne   4
                PlayerTwo   2

                game 2023-03-12 15:00
                PlayerOne   2
                PlayerTwo   23
            """))

        with open(os.path.join(self.games_path.name, "reverse_chess.txt"), "w") as f:
            f.write(dedent("""
                game_name Reverse Chess

                game 2023-02-20 17:06
                PlayerOne   1
                PlayerTwo   10

                game 2023-02-24 13:00
                PlayerOne   4
                PlayerTwo   2

                game 2023-03-12 15:00
                PlayerOne   2
                PlayerTwo   23
                PlayerThree 1
            """))

        _main([
            "--games-path", self.games_path.name,
            "--output", self.output_path.name,
        ])

        with open(os.path.join(self.output_path.name, "index.html"), "r") as f:
            contents = f.read()
        self.assertIn('class="position"', contents)
        self.assertIn('PlayerOne', contents)
        self.assertIn('PlayerTwo', contents)
        self.assertNotIn('PlayerThree', contents)

