import subprocess

def run_command(command):
    """
    주어진 콘솔 명령어를 실행하고 출력 결과를 반환합니다.
    """
    try:
        # 명령어를 실행하고 결과를 캡처합니다.
        result = subprocess.run(command, check=True, shell=True, text=True, capture_output=True)

        # 명령어 실행 결과를 반환합니다.
        return result.stdout

    except subprocess.CalledProcessError as e:
        # 명령어 실행 중 에러가 발생한 경우 에러 메시지를 반환합니다.
        return f"An error occurred: {e.stderr}"
