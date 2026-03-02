# YouTube Learning Plugin for OpenClaw Agents

A plugin that enables AI agents to learn from YouTube videos by downloading, transcribing, and extracting knowledge.

## Author

**D3n14l0f53rv1c3**

## Features

- Download video metadata without downloading full video
- Extract topics from video titles, descriptions, and tags
- Download auto-generated transcripts (English/German)
- Save learning to knowledge base
- Works on all OpenClaw agents

## Requirements

- Python 3.x
- yt-dlp (installed on all agents)

## Installation

```bash
pip3 install --user yt-dlp
```

## Usage

```bash
python3 learn_from_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Output

- `learning_TIMESTAMP.json` - Machine-readable metadata
- `learning_TIMESTAMP.md` - Human-readable summary
- `transcripts/` - Downloaded transcripts

## Topic Categories

- `security:hack`, `security:wifi`, `security:bluetooth`
- `dev:python`, `dev:javascript`, `dev:rust`
- `hardware:esp32`, `hardware:arduino`, `hardware:sdr`

## License

MIT License

## Credits

Created for OpenClaw multi-agent system
