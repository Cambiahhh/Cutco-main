import argparse
import sys
from pathlib import Path

# Add project root to sys.path to import mvp_platform
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from mvp_platform import ffmpeg_skill

def main():
    parser = argparse.ArgumentParser(description="Run FFmpeg processing tasks for Video Production Agent.")
    parser.add_argument("--action", choices=["trim", "extract", "subtitles", "voiceover", "voiceover_subtitles"], required=True, help="The action to perform")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", required=True, help="Output video/audio file path")
    
    # Trim parameters
    parser.add_argument("--start", default="0", help="Start time for trim")
    parser.add_argument("--end", default="10", help="End time for trim")
    
    # Whisper parameters
    parser.add_argument("--model", default="base", help="Whisper model size")
    
    # Voiceover parameters
    parser.add_argument("--text", help="Text to synthesize for voiceover")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="Voice ID")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
        
    result = {"success": False, "error": "Unknown action"}
        
    try:
        if args.action == "trim":
            result = ffmpeg_skill.trim_video(str(input_path), args.start, args.end, str(output_path))
        elif args.action == "extract":
            result = ffmpeg_skill.extract_audio(str(input_path), str(output_path), format="mp3")
        elif args.action == "subtitles":
            result = ffmpeg_skill.create_subtitled_video(str(input_path), str(output_path), model=args.model)
        elif args.action == "voiceover":
            if not args.text:
                print("Error: --text is required for voiceover action.")
                sys.exit(1)
            result = ffmpeg_skill.create_voiceover_video(str(input_path), args.text, str(output_path), voice=args.voice)
        elif args.action == "voiceover_subtitles":
            if not args.text:
                print("Error: --text is required for voiceover_subtitles action.")
                sys.exit(1)
            # Step 1: Voiceover to temp file
            temp_output = output_path.parent / f"temp_{output_path.name}"
            vo_res = ffmpeg_skill.create_voiceover_video(str(input_path), args.text, str(temp_output), voice=args.voice)
            if not vo_res["success"]:
                result = vo_res
            else:
                # Step 2: Subtitles to final file
                result = ffmpeg_skill.create_subtitled_video(str(temp_output), str(output_path), model=args.model)
                if temp_output.exists():
                    temp_output.unlink()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
        
    if result.get("success"):
        print(f"Success! Output saved to: {result.get('output_path', output_path)}")
        if "message" in result:
            print(result["message"])
    else:
        print(f"Error executing {args.action}: {result.get('error', 'unknown error')}")
        if "stdout" in result:
            print(f"Stdout:\n{result['stdout']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
