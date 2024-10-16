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
    # model change to turbo
    parser.add_argument("--model", default="turbo",
                        choices=whisper.available_models(), help="name of the Whisper model to use")
    # add --device
    parser.add_argument("--device","-d", type=str,default="cuda",
                        help="cuda or cpu to run Whisper, didn't set will let environment to choose")                    
    parser.add_argument("--output_dir", "-o", type=str,
                        default=".", help="directory to save the outputs")
    parser.add_argument("--output_srt", type=str2bool, default=False,
                        help="whether to output the .srt file along with the video files")
    parser.add_argument("--srt_only", type=str2bool, default=True,
                        help="only generate the .srt file and not create overlayed video, \"True\" to function it")
    parser.add_argument("--verbose", type=str2bool, default=False,
                        help="whether to print out the progress and debug messages")
    # add --temp
    parser.add_argument("--temp", type=str2bool, default=False,
                        help=".wav file in temp folder or same with video path True or False")
    # add --hard
    parser.add_argument("--hard", type=str2bool, default=False,
                        help="Define subtilte soft or hard, hrad one is overlap on original graph")
    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--language", type=str, default="auto", choices=["auto","af","am","ar","as","az","ba","be","bg","bn","bo","br","bs","ca","cs","cy","da","de","el","en","es","et","eu","fa","fi","fo","fr","gl","gu","ha","haw","he","hi","hr","ht","hu","hy","id","is","it","ja","jw","ka","kk","km","kn","ko","la","lb","ln","lo","lt","lv","mg","mi","mk","ml","mn","mr","ms","mt","my","ne","nl","nn","no","oc","pa","pl","ps","pt","ro","ru","sa","sd","si","sk","sl","sn","so","sq","sr","su","sv","sw","ta","te","tg","th","tk","tl","tr","tt","uk","ur","uz","vi","yi","yo","zh"], 
    help="What is the origin language of the video? If unset, it is detected automatically.")

    args = parser.parse_args().__dict__
    model_name: str = args.pop("model")
    # add --device
    device: str =  args.pop("device")
    output_dir: str = args.pop("output_dir")
    output_srt: bool = args.pop("output_srt")
    srt_only: bool = args.pop("srt_only")
    set_temp: bool = args.pop("temp")
    hard: bool = args.pop("hard")
    language: str = args.pop("language")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if model_name.endswith(".en"):
        warnings.warn(
            f"{model_name} is an English-only model, forcing English detection.")
        args["language"] = "en"
    # if translate task used and language argument is set, then use it
    elif language != "auto":
        args["language"] = language
    # add --device
    model = whisper.load_model(model_name, device)
    audios = get_audio(args.pop("video"),set_temp,output_dir)
    subtitles = get_subtitles(
        audios, (output_srt or srt_only or (not set_temp)), output_dir, lambda audio_path: model.transcribe(audio_path, **args)
    )

    if srt_only:
        return

    for path, srt_path in subtitles.items():
        out_path = os.path.join(output_dir, f"{filename(path)}.mp4")

        print(f"Adding subtitles to {filename(path)}...")

        video = ffmpeg.input(path)
        audio = video.audio
        print(" ! ! !\n please set --output_dir or -o, the original video cannot be overwrite\n \
and I do suggest you using other way to put subtilte \n since it really not good for watching\n ! ! ! ")
        '''
        I wanna give a vf for NV but...I cannot make it... and soft subtitle with codec copy quite fast
        And using h264_nvenc will get this error
        filter 'graph 0 input from stream 0:0' and the filter 'auto_scale_0'
        if you wanna know what happend remove # below and give "--hard true --srt_only False -o anyname"
        '''
        #cmd= ['ffmpeg','-hwaccel','cuda','-hwaccel_output_format','cuda'] if (device=="cuda") else 'ffmpeg'
        #nvenc_det= '_nvenc' if (device=='cuda') else ''
        if hard:
            (ffmpeg
            .concat(video.filter('subtitles', srt_path,force_style="OutlineColour=&H40000000,BorderStyle=3"),audio, v=1, a=1)
            .output(out_path,vcodec='h264')
            #.output(out_path,vcodec='h264'+nvenc_det)
            #.run(cmd,quiet=False, overwrite_output=True))
            .run(quiet=False, overwrite_output=True)
            )
        else:
            cmd =['ffmpeg','-i', srt_path]
            (ffmpeg
            .input(path)
            .output(out_path,vcodec='copy',acodec='copy')
            .run(cmd,quiet=False, overwrite_output=True)
            )
        print(f"Saved subtitled video to {os.path.abspath(out_path)}.")


def get_audio(paths,set_temp,output_dir):
    temp_dir = tempfile.gettempdir() if set_temp else output_dir

    audio_paths = {}

    for path in paths:
        print(f"Extracting audio from {filename(path)}...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")
        ffmpeg.input(path).output(
            output_path,
            acodec="pcm_s16le", ac=1, ar="16k"
        ).run(quiet=False, overwrite_output=True)
        audio_paths[path] = output_path

    return audio_paths


def get_subtitles(audio_paths: list, output_srt: bool, output_dir: str, transcribe: callable):
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        srt_path = output_dir if output_srt else tempfile.gettempdir()
        srt_path = os.path.join(srt_path, f"{filename(path)}.srt")
        
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )

        warnings.filterwarnings("ignore")
        result = transcribe(audio_path)
        warnings.filterwarnings("default")

        with open(srt_path, "w", encoding="utf-8") as srt:
            write_srt(result["segments"], file=srt)

        subtitles_path[path] = srt_path

    return subtitles_path


if __name__ == '__main__':
    main()
