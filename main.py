import requests
from bs4 import BeautifulSoup
import pickle
import re, datetime

# 뉴스 중복 확인
def duplication_check(new_news, saved_news_list):
  if new_news in saved_news_list:
    return False
  else:
    saved_news_list.append(new_news)
    return True

# 기사 날짜, 시간 표현
def get_released_time(current_time, time_info):
  return_string = ''
  r = re.compile('^[\d]*')
  m = r.search(time_info)
  number = int(time_info[:m.end()])
  korean = time_info[m.end()]
  
  # 뉴스사마다 날짜를 담은 태그가 다르고 페이지에 현재 날짜가 기사 입력 날짜보다 먼저 나오는
  # 경우도 있어(뉴스1) 정규표현식으로도 정확한 기사 입력날짜를 얻기 힘듦.
  # 기사의 발행 시각(released time)구하기
  if korean == '분': # n분 전
    released_time = current_time - datetime.timedelta(minutes=number)
    return_string = released_time.strftime('%Y-%m-%d %H시%M분')
  elif korean == '시': # n시간 전
    released_time = current_time - datetime.timedelta(hours=number)
    return_string = released_time.strftime('%Y-%m-%d %H시')
  elif korean == '일': # n일 전
    released_time = current_time - datetime.timedelta(days=number)
    return_string = released_time.strftime('%Y-%m-%d')
  else: # 몇 초전 기사일 수도 있음
    released_time = current_time
  
  return return_string

# 검색 페이지 request  
url = 'https://search.naver.com/search.naver?where=news&query=%ED%8E%84%EC%96%B4%EB%B9%84%EC%8A%A4&sm=tab_tmr&nso=so:r,p:all,a:all&sort=0'
res = requests.get(url)
res.raise_for_status()
current_time = datetime.datetime.today()

# 뉴스 컨테이너 객체 설정
soup = BeautifulSoup(res.text, 'lxml')
news_container = soup.find('ul', attrs={'class':'list_news'})
list_news = news_container.find_all('li', attrs={'class':'bx'})

# 저장된 뉴스 제목 리스트 불러옴
try:
  saved_news_file = open('saved_news_list.pickle', 'rb')
  saved_news_list = pickle.load(saved_news_file)
  saved_news_file.close()
except Exception:
  saved_news_list = list()
  print('new list created')
finally:
  print('list loaded successfully')

# 파일로 작성
with open('pana.html', 'a', encoding='utf-8') as f:
  for news in list_news:
    try:
      news_link = news.find('a', attrs={'class':'news_tit'})
      time_info = news.find('span', text=re.compile(' 전$')) # class가 info인 span을 이용하면 신문의 몇면 몇단의 기사인지를 알려주는 내용도 있음
      if duplication_check(news_link.get_text()[:14], saved_news_list): # 제목이 길기 때문에 앞의 14글자만 비교
        f.write('<h3><a href="' + news_link['href'] + '" target="blank">' + news_link['title'] + ',  ' +
        get_released_time(current_time, time_info.get_text()) + '</a></h3>')
        f.write('<br/>')
        f.write('\n')
    except:
      pass # 일정기간 지난 뉴스는 time_info에 '~전'이 아니라 '2021.12.14'처럼 날짜의 형태로 나올 수 있음
      
# saved_news_list.pickle 파일 갱신
with open('saved_news_list.pickle', 'wb') as f:
  pickle.dump(saved_news_list, f)
  print('dump successed')

