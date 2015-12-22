#-*- coding: utf-8 -*-
import json
import codecs
from random import shuffle
from slackclient import SlackClient
from settings import TOKEN

menus = []

def run(sc):
    if sc.rtm_connect():
        while True:
            for data in sc.rtm_read():
                message_parse(sc, data)
                print data
        else:
            print '연결에 실패했습니다. 토큰 값을 확인해보십시오.'

def message_parse(sc, data):
    bad_keywords = [u'바보', u'멍청', u'또라이', u'구려', u'쓰레기', u'병신', u'지랄', u'시발']
    hungry_keywords = [u'밥먹어', u'오늘은 일식 어때요?', u'오늘은 중식 어때요?', u'오늘은 양식 어때요?', u'오늘은 한식 어때요?', u'오늘은 굶죠', u'다이어트 안해요?', u'이런걸로 말걸지마요']
    if 'type' in data:
        if data['type'] == 'hello':
            for channel in sc.server.channels:
                channel.send_message(u'반갑습니다. 저는 메뉴 추천 봇 헝그리입니다.\n')
                channel.send_message(u'저를 부르실 때는 꼭 `헝그리`라고 적어주세요.\n그 외 명령어로는\n`도움`, `도와줘`, `헬프`: 도움말 보기\n`메뉴`, `리스트`: 추가된 메뉴 리스트 보기\n`추가 [메뉴이름]`: 메뉴 추가\n`삭제 [메뉴이름]`: 메뉴 삭제\n`배고파`: 그냥 재치있는 답변\n가 있습니다. 좋은 하루 되십시오.')
        elif data['type'] == 'channel_joined':
            sc.server.channels.find(data['channel']['name']).send_message(u'반갑습니다. 저는 메뉴 추천 봇 헝그리입니다.\n')
            sc.server.channels.find(data['channel']['name']).send_message(u'저를 부르실 때는 꼭 `헝그리`라고 적어주세요.\n그 외 명령어로는\n`도움`, `도와줘`, `헬프`: 도움말 보기\n`메뉴`, `리스트`: 추가된 메뉴 리스트 보기\n`추가 [메뉴이름]`: 메뉴 추가\n`삭제 [메뉴이름]`: 메뉴 삭제\n`배고파`: 그냥 재치있는 답변\n가 있습니다. 좋은 하루 되십시오.')
        elif data['type'] == 'message':
            text = data['text']
            if 'hungry' in text or u'헝그리' in text:
                if 'hungry' == text or u'헝그리' == text:
                    sc.rtm_send_message(data['channel'], u'왜?')
                    return
                if u'도움' in text or u'도와줘' in text or u'헬프' in text:
                    sc.rtm_send_message(data['channel'], u'저를 부르실 때는 꼭 `헝그리`라고 적어주세요.\n그 외 명령어로는\n`도움`, `도와줘`, `헬프`: 도움말 보기\n`메뉴`, `리스트`: 추가된 메뉴 리스트 보기\n`추가 [메뉴이름]`: 메뉴 추가\n`삭제 [메뉴이름]`: 메뉴 삭제\n`배고파`: 그냥 재치있는 답변\n가 있습니다. 좋은 하루 되십시오.')
                elif u'배고파' in text:
                    shuffle(hungry_keywords)
                    sc.rtm_send_message(data['channel'], hungry_keywords[0])
                elif u'추천' in text:
                    try:
                        shuffle(menus)
                        sc.rtm_send_message(data['channel'], u'오늘의 추천 메뉴는 '+menus[0]+u'입니다.')
                    except IndexError:
                        sc.rtm_send_message(data['channel'], u'등록된 메뉴가 없는댑쇼.')
                    return
                elif u'추가' in text:
                    split_texts = text.split()
                    print split_texts
                    for val in split_texts:
                        if val in u'추가':
                            try:
                                regist_menu(sc, data, split_texts[2])
                            except IndexError:
                                sc.rtm_send_message(data['channel'], u"뭘 등록하라는거죠?")
                            break
                elif u'삭제' in text:
                    split_texts = text.split()
                    print split_texts
                    for val in split_texts:
                        if val in u'삭제':
                            try:
                                unregist_menu(sc, data, split_texts[2])
                            except IndexError:
                                sc.rtm_send_message(data['channel'], u"뭘 삭제하라는거죠?")
                            break
                elif u'메뉴' in text or u'리스트' in text:
                    if not menus:
                        sc.rtm_send_message(data['channel'], u'등록된 메뉴가 없습니다.')
                    else:
                        sc.rtm_send_message(data['channel'], u'등록된 메뉴로는 \n'+unicode(u', '.join(menus))+u' 등이 있습니다.')
                else:
                    for val in bad_keywords:
                        if val in text:
                            sc.rtm_send_message(data['channel'], u'그런 말을 하다니.. 미워!')
                            return
                    sc.rtm_send_message(data['channel'], u'난 바보라서 그게 뭔지 몰라~')

def regist_menu(sc, data, menu_string):
    for val in menus:
        if val == menu_string:
            sc.rtm_send_message(data['channel'], u"이미 등록된 메뉴입니다.")
            return
    menu_file = open('menu.txt', 'a')
    menu_file.write(menu_string.encode('utf-8')+'\n')
    menus.append(menu_string)
    sc.rtm_send_message(data['channel'], menu_string+u" 등록했습니다.")
    menu_file.close()

def unregist_menu(sc, data, menu_string):
    menu_file = codecs.open('menu.txt', 'r', 'utf-8')
    for val in menu_file:
        if val.strip() == menu_string:
            menus.remove(val.strip())
            sc.rtm_send_message(data['channel'], menu_string+u" 메뉴를 삭제했습니다.")
            menu_file.close()
            return

    menu_file.close()
    sc.rtm_send_message(data['channel'], u"해당 메뉴가 없습니다.")

if __name__ == '__main__':
    menu_file = codecs.open('menu.txt', 'r', 'utf-8')
    for menu_string in menu_file:
        if menu_string != '\n':
            menus.append(menu_string.strip())
    menu_file.close()
    sc = SlackClient(TOKEN)
    run(sc)
