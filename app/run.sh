#!/bin/bash

# 현재 작업 디렉토리 설정
dir_path="/code/app"

cd $dir_path

python3 "$dir_path/BasicCrawler.py"

# 실행 결과 확인
if [ $? -eq 0 ]; then
    echo "BasicCrawler 성공"
else
    echo "BasicCrawler 실패"
fi

python3 "$dir_path/LibCrawler.py"
if [ $? -eq 0 ]; then
    echo "LibCrawler 성공"
else
    echo "LibCrawler 실패"
fi

exit 0