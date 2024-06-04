from datetime import datetime
from pydantic import BaseModel
import pytz

class Notice(BaseModel):
    published_date: datetime

# 한국 표준 시간대 (KST) 설정
korea_tz = pytz.timezone('Asia/Seoul')

# naive datetime 생성
my_naive_datetime = datetime(2024, 6, 4, 10, 30)

# tzinfo 설정
localized_date = korea_tz.localize(my_naive_datetime)

# 모델 인스턴스 생성
a = Notice(published_date=localized_date)
