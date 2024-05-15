#!/bin/bash

# 현재 작업 디렉토리 설정
dir_path=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

echo $dir_path
# 실행
source "$dir_path/.venv/bin/activate"
python3 "$dir_path/BasicCrawler.py"

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo "BasicCrawler 성공"
else
    echo "BasicCrawler 실패"
fi

python3 "$dir_path/LibCrawer.py"
if [ $? -eq 0 ]; then
    echo "LibCrawer 성공"
else
    echo "LibCrawer 실패"