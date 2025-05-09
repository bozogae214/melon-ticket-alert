import requests
import json
import time

#######################################################
########### 아래 값 채워준 뒤 실행해주시면 됩니다. #############
#######################################################
prodId = "211309"
pocCode = "SC0002"
scheduleNo = "100001"
cookie = "PCID=17246732088216913842539; PC_PCID=17246732088216913842539; _fwb=75ERfT1y01FZYsweBNzPiv.1726137882113; ab180ClientId=29b71157-b103-4a7b-b43f-b1f04433e468; TKT_POC_ID=WP15; airbridge_migration_metadata__melon=%7B%22version%22%3A%221.10.69%22%7D; _T_ANO=O0lafJ70et0GF6TWL9RvwHUfDV/+xkH1C5d/h2HUtb2x8WYMKcKBAqSkCgVl9LXDtV2J2GrGdqv+AopEwEGuwC4fkjOe6MMiB5KLKzb9AeVYwkIzghgnJ5aCNkTuqTxcKAThBsyY+H9NhZiiKIEKldXfJDscqdeOBlK9aXUuceeeqZ4C2B0E+r9RFjM3EgJK0oY7J82UBoBjFn4HTrZiaKGhqI0j88VY7kTQtsabbefzbvxR/OPEYxbfIxNLfWz0Z0yk5jaAgIGetqjr+Q1MGIyzTsj3t94U2nISHLQItWsh40y9aRwo+F+3r1yGTnqVDRmnouFUd591ZWmk3DClwg==; airbridge_session=%7B%22id%22%3A%22aca2abdf-0b18-4cd3-8ea8-b593280a5165%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1746801771658%2C%22end%22%3A1746801782429%7D; MAC=s7IM+yDj04dPWttOum9/HjL5agSurNl9YCj3qzyL9V24WOxlLn8p2yNyd5Y1sOz3; MLCP=NTk3NTc2MjklM0JhZXJhbjEwMDYlM0IlM0IwJTNCZXlKaGJHY2lPaUpJVXpJMU5pSjkuZXlKcGMzTWlPaUp0WlcxaVpYSXViV1ZzYjI0dVkyOXRJaXdpYzNWaUlqb2liV1ZzYjI0dGFuZDBJaXdpYVdGMElqb3hOelEyT0RBeE9ESXdMQ0p0WlcxaVpYSkxaWGtpT2lJMU9UYzFOell5T1NJc0ltRjFkRzlNYjJkcGJsbE9Jam9pVGlKOS5GQlpGa3JVZzJrV3M0eXFHZHhpYk1rSDc3YktlTXl5WWgyY19EOWtjV2xzJTNCJTNCMjAyNTA1MDkyMzQzNDAlM0JhZXJhbl8lM0IwJTNCYWVyYW4xMDA2JTNCNCUzQg==; MUS=694888852; keyCookie=59757629; store_melon_cupn_check=59757629; NetFunnel_ID=WP15; wcs_bt=s_585b06516861:1746804051; JSESSIONID=1F73FDC34581849A2A366ACEDD1C2A1A
"
slack_webhook_url = ""
#######################################################
#######################################################

header = {
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'Content-Length': '75',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': cookie,
    'Host': 'ticket.melon.com',
    'Referer': 'https://ticket.melon.com/reservation/popup/stepBlock.htm',
    'User-Agent': 'X'
}

def get_block_list() -> list:
    url = "https://ticket.melon.com/tktapi/product/getAreaMap.json?v=1&callback=getBlockGradeSeatMapCallBack" 
    
    body = {
        'prodId': prodId,
        'pocCode': pocCode,
        'scheduleNo': scheduleNo
    }
    
    response = requests.post(url,headers=header,data=body)
    block_datas = json.loads(response.text.replace("/**/getBlockGradeSeatMapCallBack(","").replace(");", "")) 
            
    return block_datas['seatData']['da']['sb']
    

def get_remain_seat_in_block(block) -> int:
    url = "https://ticket.melon.com/tktapi/product/seat/seatMapList.json?v=1&callback=getSeatListCallBack" 
   
    body = {
        'prodId': prodId,
        'pocCode': pocCode,
        'scheduleNo': scheduleNo,
        'blockId': block['sbid'], #getAreaMap.json > seatData > st > sbid
        'corpCodeNo': ''
    }

    response = requests.post(url,headers=header,data=body)
    map_datas = json.loads(response.text.replace("/**/getSeatListCallBack(","").replace(");", ""))
    count = 0
    
    if "seatData" in map_datas:
        for st in map_datas['seatData']['st'][0]['ss']:
            if st['sid'] != None: 
                count += 1    
    
    return count

def send_message(message: str) -> None:
    response = requests.post(slack_webhook_url, json={'text' : message})

def main() -> None:
    for i in range(30):
        blocks = get_block_list()
        for block in blocks:
            count = get_remain_seat_in_block(block)
            if count > 0:
                send_message(block['sntv']['a'] + "구역에 잔여좌석 " + str(count) + "개 발생!")
        time.sleep(2)
        
main()
