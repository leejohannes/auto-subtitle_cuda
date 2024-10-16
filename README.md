#what I changed
1. For windows  ffmpeg
```
pip install ffmpeg-python
pip uninstall ffmpeg
```
and it won't combine the subtitle with video
since it using %temp% folder

2. Add `--cuda` that run whisper on your `nVidia` graphic card
   ![image](https://github.com/user-attachments/assets/c8e24fe9-a0ff-4107-b7a7-c5d0858f9f50)




# Automatic subtitles in your videos

This repository uses `ffmpeg` and [OpenAI's Whisper](https://openai.com/blog/whisper) to automatically generate and overlay subtitles on any video.

## Installation

To get started, you'll need Python 3.7 or newer. Install the binary by running the following command:

    pip install git+https://github.com/leejohannes/auto-subtitle_cuda.git

You'll also need to install [`ffmpeg`](https://ffmpeg.org/), which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg
```
~~# on Windows using Chocolatey (https://chocolatey.org/)~~
~~choco install ffmpeg~~


## Usage

The following command will generate a `subtitled/video.mp4` file contained the input video with overlayed subtitles.

    auto_subtitle /path/to/video.mp4 -o subtitled/

The default setting (which selects the `small` model) works well for transcribing English. You can optionally use a bigger model for better results (especially with other languages). The available models are `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large`.

    auto_subtitle /path/to/video.mp4 --model medium

Adding `--task translate` will translate the subtitles into English:

    auto_subtitle /path/to/video.mp4 --task translate

Run the following to view all available options:

    auto_subtitle --help

## License

This script is open-source and licensed under the MIT License. For more details, check the [LICENSE](LICENSE) file.
