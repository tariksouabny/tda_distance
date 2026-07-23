import json
import os
import tempfile
import unittest

from src.config import load_config, parse_args


class TestConfig(unittest.TestCase):
    def test_load_config_from_file_and_cli_overrides(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "settings.json")
            with open(config_path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "pipeline": {
                            "crash_eve_date": "2020-04-19",
                            "lookback": 30,
                            "start_date": "2018-01-01",
                            "end_date": "2020-03-01",
                            "show_plots": False,
                        }
                    },
                    handle,
                )

            config = load_config(config_path=config_path, overrides={"lookback": 12, "show_plots": True})

            self.assertEqual(config.crash_eve_date, "2020-04-19")
            self.assertEqual(config.lookback, 12)
            self.assertEqual(config.start_date, "2018-01-01")
            self.assertEqual(config.end_date, "2020-03-01")
            self.assertTrue(config.show_plots)

    def test_parse_args_supports_commands(self):
        args = parse_args(["run", "--lookback", "25", "--show-plots"])
        self.assertEqual(args.command, "run")
        self.assertEqual(args.lookback, 25)
        self.assertTrue(args.show_plots)


if __name__ == "__main__":
    unittest.main()
