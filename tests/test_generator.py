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

        with open(os.path.join(self.games_path.name, "scrabble.txt"), "w") as f:
            f.write(dedent("""
                # Scrabble
                game_name Scrabble

                game 2023-02-20 17:06
                Peter   350
                Jonatan   320

                game 2023-02-24 13:00
                Peter   346
                Jonatan   390
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
        self.assertTrue(os.path.exists(os.path.join(self.output_path.name, "scrabble", "index.html")))

        with open(os.path.join(self.output_path.name, "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("Scrabble", contents)

        with open(os.path.join(self.output_path.name, "scrabble", "index.html"), "r") as f:
            contents = f.read()
        self.assertIn("Jonatan", contents)

        mock_stdout.seek(0)
        mock_stderr.seek(0)
        self.assertIn("scrabble/index.html", mock_stdout.read())

    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_generate_website_with_config(self, mock_stdout, mock_stderr):
        with NamedTemporaryFile() as f:
            f.write(dedent("""
                site_name = "TestName"
            """).encode("utf-8"))
            f.flush()

            _main([
                "--games-path", self.games_path.name,
                "--output", self.output_path.name,
                "--config", f.name,
            ])
            with open(os.path.join(self.output_path.name, "index.html"), "r") as f:
                contents = f.read()
            self.assertIn("TestName", contents)
