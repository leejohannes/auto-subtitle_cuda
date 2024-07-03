import os
import ffmpeg
import whisper
import argparse
import warnings
import tempfile
from .utils import filename, str2bool, write_srt


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", nargs="+", type=str,
                        help="paths to video files to transcribe")
    parser.add_argument("--model", default="small",
                        choices=whisper.available_models(), help="name of the Whisper model to use")
    parser.add_argument("--output_dir", "-o", type=str,
                        default=".", help="directory to save the outputs")
    parser.add_argument("--output_mkv", type=str2bool, default=False,
                        help="whether to output the new subtitled video as an .mkv container (True) or an .mp4 container (False)")
    parser.add_argument("--output_srt", type=str2bool, default=False,
                        help="whether to output the .srt file along with the video files")
    parser.add_argument("--subtitle_format", type=str, default="srt", choices=["srt","vtt"],
                        help="subtitle file format type")
    parser.add_argument("--output_txt", type=str2bool, default=False,
                        help="whether to save the subtitles in a txt file")
    parser.add_argument("--srt_only", type=str2bool, default=False,
                        help="only generate the .srt file and not create overlayed video")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="whether to print out the progress and debug messages")

    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--language", type=str, default="auto", choices=["auto","af","am","ar","as","az","ba","be","bg","bn","bo","br","bs","ca","cs","cy","da","de","el","en","es","et","eu","fa","fi","fo","fr","gl","gu","ha","haw","he","hi","hr","ht","hu","hy","id","is","it","ja","jw","ka","kk","km","kn","ko","la","lb","ln","lo","lt","lv","mg","mi","mk","ml","mn","mr","ms","mt","my","ne","nl","nn","no","oc","pa","pl","ps","pt","ro","ru","sa","sd","si","sk","sl","sn","so","sq","sr","su","sv","sw","ta","te","tg","th","tk","tl","tr","tt","uk","ur","uz","vi","yi","yo","zh"], 
    help="What is the origin language of the video? If unset, it is detected automatically.")

    parser.add_argument("--word_timestamps", type=str2bool, default=False, help="(experimental) extract word-level timestamps and refine the results based on them")

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    output_dir: str = args.pop("output_dir")
    output_srt: bool = args.pop("output_srt")
    subtitle_format: str = args.pop("subtitle_format")
    output_txt: bool = args.pop("output_txt")
    srt_only: bool = args.pop("srt_only")
    language: str = args.pop("language")
    output_mkv: bool = args.pop("output_mkv")
    verbose: bool = args.pop("verbose")
    
    os.makedirs(output_dir, exist_ok=True)

    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        args["language"] = language
        
    model = whisper.load_model(model_name)
    audios = get_audio(args.pop("video"))
    subtitles = get_subtitles(
        audios, output_srt or srt_only, subtitle_format,output_txt, output_dir, lambda audio_path: model.transcribe(audio_path, **args,verbose=verbose)        
    )

    if srt_only:
        return

    ext = "mkv" if output_mkv else "mp4"

    for path, srt_path in subtitles.items():

        out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(path))[0]}.{ext}")
        print(f"Adding subtitles to {os.path.basename(path)}...")
    
        stream = ffmpeg.input(path)
        audio = stream.audio
        videoWithSub = stream.video.filter('subtitles', filename=srt_path,force_style='OutlineColour=&H40000000,BorderStyle=3') 

        if output_mkv:
            stream = ffmpeg.output(ffmpeg.input(srt_path), stream, out_path, vcodec='copy', scodec='copy')
        else:
            stream = ffmpeg.output(audio, videoWithSub, out_path, vcodec='libx264', acodec='copy')

        ffmpeg.run(stream, quiet= not verbose, overwrite_output=True)
        print(f"Saved subtitled video to {os.path.abspath(out_path)}.")


def get_audio(paths):
    temp_dir = tempfile.gettempdir()

    audio_paths = {}

    for path in paths:
        print(f"Extracting audio from {filename(path)}...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")

        ffmpeg.input(path).output(
            output_path,
            acodec="pcm_s16le", ac=1, ar="16k"
        ).run(quiet=True, overwrite_output=True)

        audio_paths[path] = output_path

    return audio_paths



def get_subtitles(audio_paths: list, output_srt: bool,subtitle_format: str,output_txt: bool, output_dir: str, transcribe: callable):
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        srt_path = output_dir if output_srt else tempfile.gettempdir()

        if(subtitle_format=="srt"):
            srt_path = os.path.join(srt_path, f"{filename(path)}.srt")
        else: # vtt 
            srt_path = os.path.join(srt_path, f"{filename(path)}.vtt")
        
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )

        warnings.filterwarnings("ignore")
        result = transcribe(audio_path)
        warnings.filterwarnings("default")

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt,subtitle_format=subtitle_format)

        subtitles_path[path] = srt_path

        if output_txt:
            text_path = os.path.join(output_dir, f"{filename(path)}.txt")
            with open(text_path, "w", encoding="utf-8") as text_file:
                for segment in result["segments"]:
                    print(segment["text"], file=text_file)
            print(f"Saving subtitles to text file: {text_path}")

    return subtitles_path


if __name__ == '__main__':
    main()