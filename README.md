# What I changed
1. For windows  ffmpeg
   ```
   pip install ffmpeg-python
   pip uninstall ffmpeg
   ```
   and it won't combine the subtitle with video <p/>
   since it using `%temp%` folder
   ---
   1.1 add `--hard` `--temp`<p/>
   `--hard` if you still wanna hard subtitle give a `true`.<p/>
   `--temp` if you wanna using temp folder save .wav give a `true`,too.<p/>
   the logic is (output_srt or srt_only or (not set_temp))<p/>
   if you feel I'm wrong plz pull it and make another version,lol<p/>
   ---

3. Add `--device` that run whisper on your `nVidia` graphic card or cpu,</p>
   change default setting of `--srt_only` and `--model`, since the combine option not woring on windows... and GPU is easy to handel turbo model </p>
   deault is cuda, if you dont have plz using `cpu` lowercase and without quota</p>
![image](https://github.com/user-attachments/assets/956437b6-08b3-4a28-810c-e75c46a7390f)
`whisper` turbo model on 3070 laptop


4. the environment...</p>
   whether you set up a torch with your own or</p>
   using my set-up for `unsloth`</p>
   https://github.com/leejohannes/unsloth_Windows_conda </p>
   and </p>
   you may add the path </p>
   ```
   unsloth_Windows_conda_Path
   unsloth_Windows_conda_Path\Scripts
   ```
   to your windows user path, if you don't know how please reference to </p>
   ['Setting the path and variables on Windows'](https://www.google.com/search?q=Setting+the+path+and+variables+on+Windows)

5. if you get this problem `RuntimeError: Numpy is not available`
   ```
   pip install "numpy<2"
   ```

# Install update
```
pip install ffmpeg-python
```
make sure you download `ffmpeg` and put the path to $Path </p>
to download [`ffmpeg`](https://github.com/BtbN/FFmpeg-Builds/releases)/p>
*win64-lgpl-shared.zip will be smaller enough to use

```
pip install git+https://github.com/leejohannes/auto-subtitle_cuda.git
```
and...you may remove old auto-subtitle
```
pip uninstall auto-subtitle
```

# Usage update
for windows with cuda
```
auto_subtitle /path/to/video.mp4
```
for cpu user
```
auto_subtitle /path/to/video.mp4 -d cpu --model small
```

---
original README.md

# Automatic subtitles in your videos

This repository uses `ffmpeg` and [OpenAI's Whisper](https://openai.com/blog/whisper) to automatically generate and overlay subtitles on any video.

## Installation

To get started, you'll need Python 3.7 or newer. Install the binary by running the following command:
```
    pip install git+https://github.com/leejohannes/auto-subtitle_cuda.git
```
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
