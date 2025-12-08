"""
users 테이블의 username 컬럼에서 UNIQUE 인덱스 제거
username은 중복 가능, email만 고유해야 함
"""
from sqlalchemy import text
from app.database import web_engine

def remove_username_unique_index():
    """username 컬럼의 UNIQUE 인덱스 제거"""
    try:
        with web_engine.connect() as connection:
            # 기존 UNIQUE 인덱스 확인 및 제거
            try:
                # ix_users_username 인덱스 제거
                connection.execute(text("""
                    ALTER TABLE users
                    DROP INDEX ix_users_username
                """))
                print("[SUCCESS] ix_users_username 인덱스가 제거되었습니다.")
            except Exception as idx_error:
                # 인덱스가 없거나 다른 이름일 수 있음
                error_msg = str(idx_error)
                if "Unknown key" in error_msg or "doesn't exist" in error_msg:
                    print("[INFO] ix_users_username 인덱스가 존재하지 않습니다. 다른 이름의 인덱스를 확인합니다.")
                    # 다른 가능한 인덱스 이름들 확인
                    result = connection.execute(text("""
                        SHOW INDEX FROM users WHERE Column_name = 'username'
                    """))
                    indexes = result.fetchall()
                    if indexes:
                        print(f"[INFO] 발견된 username 인덱스: {indexes}")
                        for idx in indexes:
                            idx_name = idx[2]  # Key_name 컬럼
                            if idx[1] == 0:  # Non_unique가 0이면 UNIQUE 인덱스
                                connection.execute(text(f"""
                                    ALTER TABLE users
                                    DROP INDEX {idx_name}
                                """))
                                print(f"[SUCCESS] {idx_name} UNIQUE 인덱스가 제거되었습니다.")
                    else:
                        print("[INFO] username 컬럼에 UNIQUE 인덱스가 없습니다.")
                else:
                    print(f"[WARNING] 인덱스 제거 중 오류: {idx_error}")
            
            # 일반 인덱스는 유지 (성능을 위해)
            # username에 일반 인덱스가 없으면 추가
            try:
                connection.execute(text("""
                    CREATE INDEX idx_users_username ON users(username)
                """))
                print("[SUCCESS] username에 일반 인덱스가 추가되었습니다.")
            except Exception as create_error:
                if "Duplicate key name" in str(create_error):
                    print("[INFO] username 인덱스가 이미 존재합니다.")
                else:
                    print(f"[WARNING] 인덱스 생성 중 오류: {create_error}")
            
            connection.commit()
            print("[SUCCESS] username 컬럼 설정이 완료되었습니다. (중복 가능)")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("users 테이블의 username UNIQUE 인덱스 제거 중...")
    remove_username_unique_index()
    print("완료!")


