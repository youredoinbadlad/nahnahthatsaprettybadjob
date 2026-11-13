import requests
import random

def get_word_info(word):
    """
    Free Dictionary API를 호출하여 영단어 존재 여부 및 뜻 가져오기
    반환값: (결과_상태_코드, 뜻_또는_메시지)
    - 200: 정상 단어
    - 404: 사전에 없는 단어
    - 500: API/네트워크 오류
    """
    clean_word = word.strip().lower()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{clean_word}"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 404:
            return 404, "사전에 존재하지 않는 영단어입니다."
            
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                meanings = data[0].get('meanings', [])
                for meaning in meanings:
                    definitions = meaning.get('definitions', [])
                    for def_obj in definitions:
                        if 'definition' in def_obj:
                            return 200, def_obj['definition']
            
            return 200, "Definition available in English dictionary."
            
        return 500, f"HTTP 오류 발생 (코드: {response.status_code})"
        
    except requests.exceptions.Timeout:
        return 500, "네트워크 요청 시간이 초과되었습니다."
    except Exception as e:
        return 500, f"API 통신 오류: {e}"

def find_computer_word(start_char, used_words):
    """
    Datamuse API를 이용해 start_char로 시작하는 실제 영단어를 실시간 검색
    """
    url = f"https://api.datamuse.com/words?sp={start_char.lower()}*"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            words_data = response.json()
            random.shuffle(words_data)
            
            for item in words_data:
                word = item['word'].lower()
                if word.isalpha() and len(word) >= 2 and word not in used_words:
                    status, meaning = get_word_info(word)
                    if status == 200:
                        return word, meaning
    except Exception:
        pass
    return None, None

def select_difficulty():
    """
    사용자로부터 난이도를 입력받아 목표 단어 수를 반환하는 함수
    """
    difficulties = {
        "1": ("매우 쉬움", 5),
        "2": ("쉬움", 10),
        "3": ("중간", 25),
        "4": ("어려움", 50),
        "5": ("매우 어려움", 100)
    }
    
    print("=== 🎯 난이도를 선택하세요 ===")
    print("1. 매우 쉬움 (5개)")
    print("2. 쉬움 (10개)")
    print("3. 중간 (25개)")
    print("4. 어려움 (50개)")
    print("5. 매우 어려움 (100개)")
    
    while True:
        choice = input("선택 (1~5 입력): ").strip()
        if choice in difficulties:
            name, target = difficulties[choice]
            print(f"\n👉 [{name}] 난이도를 선택하셨습니다. (목표: {target}개)\n")
            return target
        else:
            print("❌ 1부터 5 사이의 숫자를 입력해 주세요.")

def play_game():
    print("=== 🔤 Computer vs Player: English Word Chain Game ===")
    print("규칙: 컴퓨터와 번갈아가며 영단어 끝말잇기를 진행합니다.\n")
    
    # 난이도 선택
    target_score = select_difficulty()
    
    used_words = []
    correct_count = 0    # 맞힌 단어 수
    wrong_count = 0      # 틀린 횟수
    max_wrong = 5        # 최대 허용 틀린 횟수
    
    # 시작 단어 설정
    current_word = "apple"
    _, meaning = get_word_info(current_word)
    used_words.append(current_word)
    
    print(f"🖥️ 컴퓨터 시작 단어: [{current_word}]")
    print(f"📖 Meaning: {meaning}\n")
    
    while wrong_count < max_wrong and correct_count < target_score:
        last_char = current_word[-1].lower()
        lives_left = max_wrong - wrong_count
        
        user_input = input(f"👤 Player (['{last_char.upper()}'로 시작] | 남은 기회: {'❤️' * lives_left} | 진행도: {correct_count}/{target_score}): ").strip().lower()
        
        if user_input == 'q':
            print("\n게임이 중단되었습니다.")
            return
            
        # 1. 중복 단어 검사 (기회 차감 없음)
        if user_input in used_words:
            print("❌ 이미 사용된 단어입니다. 다시 입력해 주세요.\n")
            continue

        # 2. 첫 글자 일치 검사 (기회 차감)
        if not user_input.startswith(last_char):
            wrong_count += 1
            print(f"❌ 단어의 첫 글자가 '{last_char.upper()}'(이)가 아닙니다. ({wrong_count}/{max_wrong})\n")
            continue
            
        # 3. 단어 유효성 및 API 상태 검사
        print("🔍 사전에 단어가 있는지 확인 중...")
        status, meaning = get_word_info(user_input)
        
        # 404: 사전에 없는 경우 -> 기회 차감
        if status == 404:
            wrong_count += 1
            print(f"❌ 사전에 없는 영단어입니다. ({wrong_count}/{max_wrong})\n")
            continue
        # 500: API 오류/네트워크 문제 -> 기회 차감 없음 (다시 시도)
        elif status == 500:
            print(f"⚠️ API 통신 오류가 발생했습니다. 기회 차감 없이 다시 시도합니다. ({meaning})\n")
            continue
            
        # 플레이어 정답 처리 (status == 200)
        used_words.append(user_input)
        correct_count += 1
        print(f"✅ 정답! 📖 [Meaning] {user_input}: {meaning}\n")
        
        # 목표 달성 시 승리
        if correct_count >= target_score:
            print(f"🎉🎉🎉 축하합니다! 목표 단어 수 {target_score}개를 모두 맞혀 최종 승리하셨습니다! 🎉🎉🎉")
            break
        
        # 컴퓨터 순서
        comp_last_char = user_input[-1].lower()
        print(f"🖥️ 컴퓨터가 '{comp_last_char.upper()}'(으)로 시작하는 단어를 찾고 있습니다...")
        comp_word, comp_meaning = find_computer_word(comp_last_char, used_words)
        
        if comp_word:
            used_words.append(comp_word)
            current_word = comp_word
            print(f"🖥️ 컴퓨터 단어: [{comp_word}]")
            print(f"📖 Meaning: {comp_meaning}\n")
        else:
            print("🎉 컴퓨터가 더 이상 이어갈 단어를 찾지 못했습니다! 당신의 승리입니다!")
            break

    # 게임 종료 결과 출력
    if wrong_count >= max_wrong:
        print("\n💥 기회를 모두 소진하여 GAME OVER 되었습니다! 💥")
    
    print("\n=== 🏆 Final Result ===")
    print(f"최종 맞힌 단어 수: {correct_count} / {target_score}개")
    print(f"오늘 학습한 영단어 목록 ({len(used_words)}개): {', '.join(used_words)}")

def main():
    while True:
        play_game()
        print("\n" + "="*40)
        replay = input("🔄 다시 플레이하시겠습니까? (Y를 누르면 재시작, 아무 키나 누르면 종료): ").strip().lower()
        if replay != 'y':
            print("게임을 이용해 주셔서 감사합니다. 종료합니다!")
            break
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main()
