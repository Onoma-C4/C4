from generate import Generator 
import requests, re, json, os
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

def get_bookcontent_from_url(url):
        now_book = requests.get(url).text
        start_pattern = r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .* \*\*\*"
        end_pattern = r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .* \*\*\*"
        start_matches = list(re.finditer(start_pattern, now_book))
        end_matches = list(re.finditer(end_pattern, now_book))
        for start, end in zip(start_matches, end_matches):
            nowbook_content = now_book[start.end():end.start()].strip()
        return nowbook_content
    
#######################################33
import requests, re
from itertools import groupby

def reduce_spaces(data):
    return [key for key, group in groupby(data, key=lambda x: x == ' ') for _ in ([key] if not key else [' '])]

def get_bookcontent_from_url(url):
        now_book = requests.get(url).text
        start_pattern = r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .* \*\*\*"
        end_pattern = r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK .* \*\*\*"
        start_matches = list(re.finditer(start_pattern, now_book))
        end_matches = list(re.finditer(end_pattern, now_book))
        for start, end in zip(start_matches, end_matches):
            nowbook_content = now_book[start.end():end.start()].strip()
        return nowbook_content

def chunk_text(text):
    chapter_spliter_count = text.count("CHAPTER")
    chunks = []
    chapters = text.split("CHAPTER")
    for i in range(len(chapters)):
        if len(chapters[i]) > 300:
            chunks.append("CHAPTER"+chapters[i])

    if len(chunks) == chapter_spliter_count:
        #컨텐츠 테이블이 없는 책
        return chunks
    else :
        return chunks[1:]
#######################################

if __name__ == "__main__":
    def get_url_from_num(num):
        return f'https://www.gutenberg.org/cache/epub/{num}/pg{num}.txt'
    
    book_url_num_list = [45975, 73011, 73707, 73760, 1190, 3174, 7100, 30123, 73708, 73866] # 하위 11
    
    book_url_list = [get_url_from_num(num) for num in book_url_num_list]#여따가 구텐베르그 책들 경로를 다 집어넣으면, 걔네들의 자연어 db(intent triplet)이 만들어짐 json파일로

    get_intent_module = Generator("chatopenai_4o", 0.1, instruction_path='/data1/fabulator/GRAPH_STUDY/Relation_Intent_Story_Generation/instructions/get_intent_between_2story_val.txt')
    
    for nowbook_url in book_url_list:
        nowbook_num = nowbook_url.split('/pg')[0].split('/')[-1]
        nowbook_data = []
        nowbook_TRIPLET_path = f'/data1/fabulator/GRAPH_STUDY/Relation_Intent_Story_Generation/validation_DB_text/{nowbook_num}_storyT0_INTENT_storyT1_TRIPLET.json'
        
        if not os.path.exists(nowbook_TRIPLET_path):
            with open(nowbook_TRIPLET_path, 'w') as file:
                json.dump([], file)  
                
        nowbook_content = get_bookcontent_from_url(nowbook_url)
        
        chunks = chunk_text(nowbook_content)
        nowbook_chapter_count = chunks[-1].split('.')[0].split('\r')[0]
    
        for i in range(len(chunks)-1):
            chapter_T0 = chunks[i] 
            chapter_T1 = chunks[i+1] 
            intent = get_intent_module.generate({'nowbook_chapter_count' : nowbook_chapter_count, 'chapter_0': chapter_T0, 'chapter_1': chapter_T1})
            
            intent = intent.split("###OUTPUT")[-1]
            
            nowbook_data.append({'book_url' : nowbook_url,'CHAPTER_T0': chapter_T0,'GOLD_INTENT': intent,'CHAPTER_T1': chapter_T1})
            
            
            tokens_final_retreival_input = enc.encode(f'CHAPTER_T0 : {chapter_T0} GOLD_INTENT : {intent} CHAPTER_T1 : {chapter_T1}')
            print(f"최종 생성에서 retrieval된 triplet의 입력 토큰 수 : {len(tokens_final_retreival_input)}")
            
            with open('/data1/fabulator/GRAPH_STUDY/Relation_Intent_Story_Generation/instructions/get_intent_between_2story_val.txt', "r") as f:
                val_data_create_instruction = f.read()
            tokens_data_create = enc.encode(f'CHAPTER_T0 : {chapter_T0} CHAPTER_T1 : {chapter_T1} instruction : {val_data_create_instruction}')
            print(f"triplet을 생성하는데 사용한 총 토큰 수(instruction포함) : {len(tokens_data_create)}")
            
            
            with open(nowbook_TRIPLET_path, 'w') as file:
                json.dump(nowbook_data, file, indent=4)
            
    
     